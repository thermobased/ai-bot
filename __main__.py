import logging
import asyncio
import os
from ollama import chat
from ollama import ChatResponse
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

with open("token.txt", "r", encoding="utf-8") as file:
    TOKEN = file.read()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="яха баля")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    content = update.message.text
    response: ChatResponse = chat(
        model='llama3.2', 
        messages=[{'role': 'user','content': content}],
        stream = True
)
    msg = await context.bot.send_message(chat_id=update.effective_chat.id, text='.')
    tmp = ''
    for chunk in response:
        tmp = tmp + chunk['message']['content']
        await msg.edit_text(tmp)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    
    application.run_polling()