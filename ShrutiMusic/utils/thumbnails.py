import os
import random
import aiohttp
import aiofiles
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

async def download_image(url, path):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(path, 'wb')
                await f.write(await resp.read())
                await f.close()
                return path
    return None

def create_gradient(width, height, start_color, end_color):
    base = Image.new('RGBA', (width, height), start_color)
    top = Image.new('RGBA', (width, height), end_color)
    mask = Image.new('L', (width, height))
    mask_data = [int(255 * (y / height)) for y in range(height) for _ in range(width)]
    mask.putdata(mask_data)
    base.paste(top, (0,0), mask)
    return base

def crop_circle(image, size, border=10, border_color=(255,255,255)):
    image = image.resize((size - 2*border, size - 2*border))
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0,0,*image.size), fill=255)
    final = Image.new('RGBA', (size,size), border_color)
    final.paste(image, (border,border), mask)
    return final

def draw_text_shadow(draw, position, text, font, fill=(255,255,255), shadow=(0,0,0,150)):
    x, y = position
    draw.text((x+2, y+2), text, font=font, fill=shadow)
    draw.text((x, y), text, font=font, fill=fill)

async def generate_thumbnail(video_url, title, channel, views, duration, output_path="output.png"):
    # Download thumbnail image
    thumb_path = "temp_thumb.png"
    # Replace this URL with real video thumbnail URL
    await download_image(video_url, thumb_path)
    video_img = Image.open(thumb_path).convert("RGBA")
    
    # Background
    bg = create_gradient(1280, 720, (30,30,60,255), (50,0,80,255))
    enhancer = ImageEnhance.Brightness(bg)
    bg = enhancer.enhance(0.7)
    
    # Circular Video Thumbnail
    circle = crop_circle(video_img, 400, border=15, border_color=(255,255,255))
    bg.paste(circle, (100,160), circle)
    
    draw = ImageDraw.Draw(bg)
    title_font = ImageFont.truetype("arial.ttf", 50)
    small_font = ImageFont.truetype("arial.ttf", 30)
    
    # Title
    draw_text_shadow(draw, (550, 180), title[:30], title_font)
    draw_text_shadow(draw, (550, 250), title[30:60], title_font)
    
    # Channel + Views
    draw_text_shadow(draw, (550, 330), f"{channel}  |  {views}", small_font)
    
    # Progress bar
    bar_length = 600
    bar_y = 400
    progress = int((random.random()) * bar_length)
    draw.rectangle([550, bar_y, 550+bar_length, bar_y+15], fill=(255,255,255,100))
    draw.rectangle([550, bar_y, 550+progress, bar_y+15], fill=(255,0,100,200))
    
    # Duration
    draw_text_shadow(draw, (550, 420), "00:00", small_font)
    draw_text_shadow(draw, (1140, 420), duration, small_font)
    
    bg.save(output_path)
    os.remove(thumb_path)
    return output_path

# Example usage:
# await generate_thumbnail("https://i.imgur.com/yourthumb.png", "Palang Sagwan Ke | K...", "SRK MUSIC", "520M views", "04:00")
