# Copyright (c) 2025 Nand Yaduwanshi <NoxxOP>
# Location: Supaul, Bihar
#
# All rights reserved.
#
# Premium upgraded thumbnail generator
# Modern neon style with gradient, glow, badges, and play icons

import random
import logging
import os
import re
import traceback
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from youtubesearchpython.__future__ import VideosSearch

logging.basicConfig(level=logging.INFO)

# -----------------------------
# Helper Functions
# -----------------------------
def change_image_size(maxWidth, maxHeight, image):
    ratio = min(maxWidth / image.width, maxHeight / image.height)
    return image.resize((int(image.width * ratio), int(image.height * ratio)))

def truncate(text):
    words = text.split()
    text1, text2 = "", ""
    for w in words:
        if len(text1) + len(w) < 30:
            text1 += " " + w
        elif len(text2) + len(w) < 30:
            text2 += " " + w
    return text1.strip(), text2.strip()

def random_color():
    return (random.randint(50,255), random.randint(50,255), random.randint(50,255))

def generate_advanced_gradient(width, height):
    base = Image.new('RGBA', (width, height), (0,0,0,255))
    for i in range(3):
        start_color = random_color()
        end_color = random_color()
        layer = Image.new('RGBA', (width, height), start_color)
        top = Image.new('RGBA', (width, height), end_color)
        mask = Image.new('L', (width, height))
        mask_data = [int((y/height)*255) for y in range(height) for _ in range(width)]
        mask.putdata(mask_data)
        layer.paste(top, (0,0), mask)
        base = Image.alpha_composite(base, layer)
    return base

def crop_circle_with_glow(img, size, border_width=15):
    img = img.resize((size-border_width*2, size-border_width*2))
    mask = Image.new('L', (size-border_width*2, size-border_width*2), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0,0,size-border_width*2,size-border_width*2), fill=255)
    img.putalpha(mask)
    
    final = Image.new("RGBA", (size, size), (0,0,0,0))
    border = Image.new("RGBA", (size, size), (0,0,0,0))
    draw_border = ImageDraw.Draw(border)
    draw_border.ellipse((0,0,size,size), outline=random_color(), width=border_width)
    border = border.filter(ImageFilter.GaussianBlur(8))
    final.paste(border, (0,0), border)
    final.paste(img, (border_width,border_width), img)
    return final

def draw_text_neon(background, draw, position, text, font, fill=(255,255,255)):
    # Neon glow effect
    for r in [6,4,2]:
        glow = Image.new('RGBA', background.size, (0,0,0,0))
        glow_draw = ImageDraw.Draw(glow)
        glow_draw.text(position, text, font=font, fill=fill)
        glow = glow.filter(ImageFilter.GaussianBlur(r))
        background.paste(glow, (0,0), glow)
    draw.text(position, text, font=font, fill=fill)

def draw_badge(background, text, position, size=(120,40)):
    badge = Image.new('RGBA', size, (255,0,150,220))
    draw = ImageDraw.Draw(badge)
    draw.rounded_rectangle((0,0,size[0],size[1]), radius=15, fill=(255,0,150,220))
    font = ImageFont.truetype("ShrutiMusic/assets/font2.ttf", 20)
    draw.text((10,5), text, font=font, fill=(255,255,255))
    background.paste(badge, position, badge)

# -----------------------------
# Main Thumbnail Generator
# -----------------------------
async def gen_thumb(videoid: str):
    try:
        if not os.path.exists("cache"):
            os.makedirs("cache")
        cache_file = f"cache/{videoid}_premium.png"
        if os.path.isfile(cache_file):
            return cache_file

        url = f"https://www.youtube.com/watch?v={videoid}"
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            title = result.get("title") or "Unsupported Title"
            title = re.sub("\W+", " ", title).title()
            duration = result.get("duration") or "LIVE"
            thumbnail_data = result.get("thumbnails")
            thumbnail = thumbnail_data[0]["url"].split("?")[0] if thumbnail_data else None
            views = result.get("viewCount", {}).get("short", "Unknown Views")
            channel = result.get("channel", {}).get("name", "Unknown Channel")

        # Fetch thumbnail
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status != 200:
                    return None
                content = await resp.read()
                filepath = f"cache/thumb_{videoid}.png"
                async with aiofiles.open(filepath, "wb") as f:
                    await f.write(content)

        youtube_img = Image.open(filepath)
        youtube_img = change_image_size(1280, 720, youtube_img)
        background = youtube_img.convert("RGBA").filter(ImageFilter.BoxBlur(20))
        background = ImageEnhance.Brightness(background).enhance(0.6)

        gradient = generate_advanced_gradient(1280, 720)
        background = Image.blend(background, gradient, alpha=0.25)
        draw = ImageDraw.Draw(background)

        # Fonts
        arial = ImageFont.truetype("ShrutiMusic/assets/font2.ttf", 30)
        title_font = ImageFont.truetype("ShrutiMusic/assets/font3.ttf", 50)

        # Circle thumbnail
        circle_thumb = crop_circle_with_glow(youtube_img, 400, 20)
        background.paste(circle_thumb, (120,160), circle_thumb)

        # Draw text
        text_x = 565
        title1, title2 = truncate(title)
        draw_text_neon(background, draw, (text_x,180), title1, title_font)
        draw_text_neon(background, draw, (text_x,250), title2, title_font)
        draw_text_neon(background, draw, (text_x, 350), f"{channel}  |  {views[:23]}", arial)

        # Draw badges
        if duration.lower() == "live":
            draw_badge(background, "LIVE", (text_x, 400))
        else:
            draw_badge(background, "TRENDING", (text_x, 400))

        # Play icon
        play_icon = Image.open("ShrutiMusic/assets/play_icons.png").resize((580,62))
        background.paste(play_icon, (text_x, 450), play_icon)

        os.remove(filepath)
        background.save(cache_file)
        return cache_file

    except Exception as e:
        logging.error(f"Error generating thumbnail for video {videoid}: {e}")
        traceback.print_exc()
        return None

# ===========================================
# ©️ 2025 Nand Yaduwanshi (aka @NoxxOP)
# 🔗 GitHub : https://github.com/NoxxOP/ShrutiMusic
# 📢 Telegram Channel : https://t.me/ShrutiBots
# ===========================================
