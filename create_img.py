from PIL import Image, ImageDraw, ImageFont
from aiogram import Bot
import io
from config import API_TOKEN

bot = Bot(token=API_TOKEN)


async def create_image(num1, num2):
    width, height = 80, 35
    image = Image.new('RGB', (width, height), color='green')
    draw = ImageDraw.Draw(image)
    question_text = f"{num1} + {num2} = ?"
    font = ImageFont.truetype("ARIAL.TTF", 15)
    draw.text((10, 10), question_text, fill='black', font=font)
    image_stream = io.BytesIO()
    image_path = 'question_image.png'
    image.save(image_path, format='PNG')
    image_stream.seek(0)
    return image_path
