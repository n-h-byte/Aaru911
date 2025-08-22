import random
import logging
import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from youtubesearchpython.__future__ import VideosSearch

logging.basicConfig(level=logging.INFO)

def changeImageSize(maxWidth, maxHeight, image):
    ratio = min(maxWidth / image.size[0], maxHeight / image.size[1])
    return image.resize((int(image.size[0] * ratio), int(image.size[1] * ratio)))

def truncate(text, max_len=32):
    words = text.split(" ")
    text1, text2 = "", ""
    for w in words:
        if len(text1) + len(w) < max_len:
            text1 += " " + w
        elif len(text2) + len(w) < max_len:
            text2 += " " + w
    return [text1.strip(), text2.strip()]

def random_color():
    return (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

def generate_gradient(width, height, colors):
    """Multi-color gradient"""
    base = Image.new('RGB', (width, height), colors[0])
    top = Image.new('RGB', (width, height), colors[-1])
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(255 * (y / height))] * width)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

def draw_glow_text(draw, text, position, font, glow_color, text_color):
    x, y = position
    for offset in range(1, 6):  # glow thickness
        draw.text((x - offset, y), text, font=font, fill=glow_color)
        draw.text((x + offset, y), text, font=font, fill=glow_color)
        draw.text((x, y - offset), text, font=font, fill=glow_color)
        draw.text((x, y + offset), text, font=font, fill=glow_color)
    draw.text(position, text, font=font, fill=text_color)

def add_outer_glow(img, glow_color=(255, 0, 0), blur_radius=25):
    glow = img.copy().convert("RGBA")
    r, g, b, a = glow.split()
    glow = Image.merge("RGBA", (Image.new("L", a.size, glow_color[0]),
                                Image.new("L", a.size, glow_color[1]),
                                Image.new("L", a.size, glow_color[2]), a))
    glow = glow.filter(ImageFilter.GaussianBlur(blur_radius))
    bg = Image.new("RGBA", (img.size[0]+100, img.size[1]+100), (0,0,0,0))
    bg.paste(glow, (50,50), glow)
    bg.paste(img, (50,50), img)
    return bg

async def gen_thumb(videoid: str):
    try:
        if not os.path.exists("cache"):
            os.makedirs("cache")

        url = f"https://www.youtube.com/watch?v={videoid}"
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            title = re.sub("\W+", " ", result.get("title", "Unknown Title")).title()
            duration = result.get("duration") or "Live"
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            views = result.get("viewCount", {}).get("short", "Unknown Views")
            channel = result.get("channel", {}).get("name", "Unknown Channel")

        # Download thumbnail
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    filepath = f"cache/thumb{videoid}.png"
                    f = await aiofiles.open(filepath, mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        # Base images
        youtube = Image.open(filepath).convert("RGBA")
        bg = changeImageSize(1280, 720, youtube).filter(ImageFilter.GaussianBlur(25))
        enhancer = ImageEnhance.Brightness(bg)
        bg = enhancer.enhance(0.5)

        # Neon gradient
        gradient = generate_gradient(1280, 720, [random_color(), random_color(), random_color()])
        gradient = gradient.convert("RGBA")
        bg = Image.blend(bg, gradient, 0.4)

        draw = ImageDraw.Draw(bg)
        title_font = ImageFont.truetype("ShrutiMusic/assets/font3.ttf", 60)
        info_font = ImageFont.truetype("ShrutiMusic/assets/font2.ttf", 32)

        # Circular glow thumbnail
        circle = youtube.resize((420,420))
        circle = add_outer_glow(circle, glow_color=random_color())
        bg.paste(circle, (80,150), circle)

        # Text with glow
        t1, t2 = truncate(title)
        draw_glow_text(draw, t1, (550,180), title_font, (255,0,100), (255,255,255))
        if t2:
            draw_glow_text(draw, t2, (550,250), title_font, (255,0,100), (255,255,255))
        draw_glow_text(draw, f"{channel}  |  {views}", (550,340), info_font, (0,255,255), (255,255,255))

        # Progress bar / Live bar
        bar_x, bar_y = 550, 420
        bar_len = 600
        if duration != "Live":
            draw.rectangle([bar_x, bar_y, bar_x+bar_len, bar_y+12], fill=(80,80,80))
            prog_len = random.randint(int(bar_len*0.2), int(bar_len*0.8))
            grad_col = random_color()
            draw.rectangle([bar_x, bar_y, bar_x+prog_len, bar_y+12], fill=grad_col)
            draw.ellipse([bar_x+prog_len-10, bar_y-10, bar_x+prog_len+10, bar_y+20], fill=grad_col)
        else:
            draw.rectangle([bar_x, bar_y, bar_x+bar_len, bar_y+12], fill=(255,0,0))

        draw_glow_text(draw, "00:00", (550,450), info_font, (0,0,0), (255,255,255))
        draw_glow_text(draw, duration, (1100,450), info_font, (0,0,0), (255,255,255))

        # Play button overlay
        play_icon = Image.open("ShrutiMusic/assets/play_icons.png").resize((600,80))
        play_icon = add_outer_glow(play_icon, glow_color=(255,255,0))
        bg.paste(play_icon, (550,500), play_icon)

        out_path = f"cache/{videoid}_tadka.png"
        bg.save(out_path)
        os.remove(filepath)
        return out_path

    except Exception as e:
        logging.error(f"Error: {e}")
        return None
