import logging
import asyncio
import os
import tempfile
from PIL import Image
from ollama import chat
from ollama import ChatResponse
from telegram import Update
from ultralytics import YOLO
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, CallbackContext

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

model = YOLO("yolov8n.pt")

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
    msg = await context.bot.send_message(chat_id=update.effective_chat.id, text='Just a sec… 🚀')
    tmp = ''
    for chunk in response:
        tmp = tmp + chunk['message']['content']
        await msg.edit_text(tmp)

async def echo_image(update: Update, context: CallbackContext) -> None:
    photo = update.message.photo[-1]
    file = await photo.get_file()

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
        image_path = temp_file.name
        await file.download_to_drive(image_path)

    result = model(image_path)[0]

    im_array = result.plot()
    im_rgb = Image.fromarray(im_array[..., ::-1])

    detections = []
    for box in result.boxes:
        class_id = int(box.cls[0].item())
        class_name = model.names[class_id]
        confidence = round(box.conf[0].item(), 2)
        detections.append(f"{class_name} ({confidence*100:.0f}%)")

    if detections:
        detection_message = "Detected objects:\n" + "\n".join(detections)
    else:
        detection_message = "No objects detected."

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as output_file:
        im_rgb.save(output_file.name, format="JPEG", quality=95)
        await update.message.reply_photo(photo=open(output_file.name, "rb"), caption=detection_message)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    image_handler = MessageHandler(filters.PHOTO, echo_image)
    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(image_handler)
    
    application.run_polling()