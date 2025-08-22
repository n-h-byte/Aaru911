import random
import logging
import os
import re
import io
import aiofiles
import aiohttp
import traceback
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageSequence
from youtubesearchpython.__future__ import VideosSearch

logging.basicConfig(level=logging.INFO)

# ================= Premium Palette =================
PREMIUM_COLORS = [
    (255, 215, 0),    # Gold
    (64, 224, 208),   # Teal
    (138, 43, 226),   # Purple
    (30, 30, 60),     # Dark Navy
    (0, 255, 180)     # Neon Aqua
]

def premium_color():
    return random.choice(PREMIUM_COLORS)

# ================= Helpers =================
def changeImageSize(maxWidth, maxHeight, image):
    w, h = image.size
    ratio = min(maxWidth / w, maxHeight / h)
    return image.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

def crop_center_circle(img, size):
    w, h = img.size
    cx, cy = w // 2, h // 2
    r = size // 2
    cropped = img.crop((cx - r, cy - r, cx + r, cy + r)).resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    circle = Image.new("RGBA", (size, size))
    circle.paste(cropped, (0, 0), mask)
    return circle

def draw_text_with_soft_shadow(draw, position, text, font, fill):
    x, y = position
    shadow_color = (0, 0, 0, 150)
    offsets = [(1,1), (-1,1), (1,-1), (-1,-1)]
    for ox, oy in offsets:
        draw.text((x+ox, y+oy), text, font=font, fill=shadow_color)
    draw.text((x, y), text, font=font, fill=fill)

def create_premium_background(size=(1280, 720)):
    base = Image.new("RGBA", size, (0,0,0,0))  # Transparent BG
    c1, c2 = premium_color(), premium_color()
    gradient = Image.new("RGBA", size, c1)
    top = Image.new("RGBA", size, c2)
    mask = Image.linear_gradient("L").resize(size)
    gradient = Image.composite(top, gradient, mask)
    return Image.blend(base, gradient, alpha=0.5)

# ================= Main Thumbnail Generator =================
async def gen_thumb(videoid: str, animated=False):
    try:
        os.makedirs("cache", exist_ok=True)
        out_path = f"cache/{videoid}_{'anim' if animated else 'static'}.png"

        if os.path.isfile(out_path):
            return out_path

        # Fetch video info
        url = f"https://www.youtube.com/watch?v={videoid}"
        results = VideosSearch(url, limit=1)
        info = (await results.next())["result"][0]

        title = re.sub(r"\s+", " ", info.get("title", "Unknown Title"))
        duration = info.get("duration") or "Live"
        channel = info.get("channel", {}).get("name", "Unknown Channel")
        views = info.get("viewCount", {}).get("short", "Unknown Views")
        thumbnail_url = info.get("thumbnails", [{}])[0].get("url", "").split("?")[0]

        # Download thumbnail
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail_url) as resp:
                if resp.status != 200:
                    return None
                content = await resp.read()

        youtube_img = Image.open(io.BytesIO(content)).convert("RGB")

        # Create base transparent background
        bg = create_premium_background()

        # Circular video thumbnail
        circle_thumb = crop_center_circle(youtube_img, 380)
        bg.paste(circle_thumb, (120, 150), circle_thumb)

        # Fonts
        title_font = ImageFont.truetype("ShrutiMusic/assets/font3.ttf", 52)
        meta_font = ImageFont.truetype("ShrutiMusic/assets/font2.ttf", 32)

        draw = ImageDraw.Draw(bg)

        # Title + Meta
        draw_text_with_soft_shadow(draw, (540, 200), title[:32], title_font, (255,255,255))
        draw_text_with_soft_shadow(draw, (540, 260), f"{channel} • {views}", meta_font, (220,220,220))

        # Progress bar
        bar_x, bar_y, bar_w = 540, 340, 600
        pct = random.uniform(0.2, 0.9) if duration != "Live" else 1.0
        fill_len = int(bar_w * pct)
        bar_color = premium_color()
        draw.rectangle([bar_x, bar_y, bar_x+bar_w, bar_y+12], fill=(255,255,255,80))
        draw.rectangle([bar_x, bar_y, bar_x+fill_len, bar_y+12], fill=bar_color)

        # Save static
        if not animated:
            bg.save(out_path)
            return out_path

        # ========== Animated Glow Pulse ==========
        frames = []
        for i in range(12):  # 12 frames loop
            frame = bg.copy()
            d = ImageDraw.Draw(frame)
            pulse_color = tuple(min(255, c+30*(i%6-3)) for c in bar_color)
            d.rectangle([bar_x, bar_y, bar_x+fill_len, bar_y+12], fill=pulse_color)
            frames.append(frame)

        gif_path = f"cache/{videoid}_animated.gif"
        frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=100, loop=0, transparency=0)
        return gif_path

    except Exception as e:
        logging.error(f"Error: {e}")
        traceback.print_exc()
        return None
