import logging
import asyncio
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Get the API token from environment variables (recommended)
API_TOKEN = os.environ.get("API_TOKEN")

# If API_TOKEN is not found in environment variables, define it directly (less secure)
if not API_TOKEN:
    API_TOKEN = "YOUR_TELEGRAM_BOT_API_TOKEN"  # Replace with your actual token

if not API_TOKEN:
    raise ValueError("API_TOKEN not found. Set it as an environment variable or define it directly in the code.")

# Set up logging to help with debugging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory task storage (replace with database for persistence)
tasks = {}

# Define the start function
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    logger.info(f"Received /start from user ID: {user_id}")
    await update.message.reply_text(
        "Welcome to the Task Assignment Bot!\n"
        "Use /help to see available commands."
    )
    if user_id not in tasks:
        tasks[user_id] = []

# Define the help_command function
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Received /help from {update.effective_user.username}")
    await update.message.reply_text(
        "Here are the available commands:\n"
        "/start - Start the bot\n"
        "/help - Display this help message\n"
        "/addtask <task_description> - Add a new task\n"
        "/listtasks - List all your tasks\n"
        "/deltask <task_index> - Delete a task (index starts from 1)"
    )

# Define the add_task function
async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    try:
        task_description = " ".join(context.args)  # Join arguments for spaces in descriptions
        tasks[user_id].append(task_description)
        await update.message.reply_text(f"Task '{task_description}' added.")
    except IndexError:
        await update.message.reply_text("Please provide a task description. Example: /addtask Buy groceries")

# Define the list_tasks function
async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id in tasks and tasks[user_id]:  # Check if the user has any tasks
        task_list = "\n".join(f"{i+1}. {task}" for i, task in enumerate(tasks[user_id]))
        await update.message.reply_text(f"Your tasks:\n{task_list}")
    else:
        await update.message.reply_text("You don't have any tasks yet.")

# Define the delete_task function
async def delete_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    try:
        task_index = int(context.args[0]) - 1
        if user_id in tasks and 0 <= task_index < len(tasks[user_id]):
            deleted_task = tasks[user_id].pop(task_index)
            await update.message.reply_text(f"Task '{deleted_task}' deleted.")
        else:
            await update.message.reply_text("Invalid task index.")
    except (ValueError, IndexError):
        await update.message.reply_text("Please provide a valid task index. Example: /deltask 1")
    except KeyError:
        await update.message.reply_text("You have no tasks to delete")

async def main():
    application = Application.builder().token(API_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("addtask", add_task))
    application.add_handler(CommandHandler("listtasks", list_tasks))
    application.add_handler(CommandHandler("deltask", delete_task))

    # Run the bot
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
