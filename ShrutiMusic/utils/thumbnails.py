import random
import logging
import os
import re
import io
import math
import traceback
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageChops
from youtubesearchpython.__future__ import VideosSearch

logging.basicConfig(level=logging.INFO)

# ========= Utilities =========

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def changeImageSize(maxWidth, maxHeight, image):
    # keep aspect ratio (previous code stretched)
    w, h = image.size
    r = min(maxWidth / w, maxHeight / h)
    new = (int(w * r), int(h * r))
    return image.resize(new, Image.LANCZOS)

def wrap_text_by_width(text, font, max_width):
    # break lines by pixel width
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if font.getlength(test) <= max_width or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    # only 2 lines for thumbnail titles
    return (lines + [""])[:2]

def random_color():
    return (random.randint(32, 224), random.randint(32, 224), random.randint(32, 224))

def dominant_colors(img, k=3):
    # quick & light dominant color extraction
    small = img.convert("RGB").resize((64, 64), Image.BILINEAR)
    pal = small.convert('P', palette=Image.ADAPTIVE, colors=k)
    palette = pal.getpalette()[:k*3]
    cols = [tuple(palette[i:i+3]) for i in range(0, len(palette), 3)]
    # sort by perceived luminance for start/end gradient selection
    def lum(c): return 0.2126*c[0] + 0.7152*c[1] + 0.0722*c[2]
    cols = sorted(cols, key=lum)
    if len(cols) < 2:
        c = cols[0] if cols else random_color()
        return c, tuple(max(0, x-40) for x in c)
    return cols[0], cols[-1]

def generate_diag_gradient(w, h, c1, c2, alpha=0.35):
    base = Image.new("RGBA", (w, h), (*c1, 255))
    top = Image.new("RGBA", (w, h), (*c2, 255))
    # diagonal mask
    mask = Image.new("L", (w, h))
    px = mask.load()
    for y in range(h):
        for x in range(w):
            t = (x + y) / (w + h)
            px[x, y] = int(255 * t)
    grad = Image.composite(top, base, mask)
    return Image.blend(Image.new("RGBA", (w, h), (0,0,0,0)), grad, alpha)

def add_vignette(img, strength=0.45):
    w, h = img.size
    vign = Image.new('L', (w, h), 0)
    draw = ImageDraw.Draw(vign)
    # radial falloff
    max_r = math.hypot(w/2, h/2)
    for r in range(int(max_r), 0, -8):
        a = int(255 * (1 - (r / max_r)) ** 2)
        draw.ellipse((w/2 - r, h/2 - r, w/2 + r, h/2 + r), fill=a)
    dark = Image.new('RGBA', (w, h), (0,0,0,int(255*strength)))
    return Image.composite(dark, img, ImageChops.invert(vign))

def apply_bloom(img, threshold=180, blur=18, intensity=0.65):
    # brighten highlights for premium glow
    bright = img.convert("RGB")
    # mask bright areas
    lum = bright.convert("L")
    mask = lum.point(lambda p: 255 if p > threshold else 0)
    glow = bright.filter(ImageFilter.GaussianBlur(blur))
    glow.putalpha(mask)
    out = img.copy()
    out = Image.alpha_composite(out, Image.new("RGBA", img.size, (255,255,255,0)))
    return Image.blend(out, glow, intensity)

def rounded_rect(draw, xy, radius, fill, outline=None, width=1):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def outer_glow_circle(diameter, color=(255, 90, 90), thickness=22, blur=22):
    size = diameter + thickness*2
    canvas = Image.new("RGBA", (size, size), (0,0,0,0))
    glow = Image.new("L", (size, size), 0)
    g = ImageDraw.Draw(glow)
    g.ellipse((thickness, thickness, size-thickness, size-thickness), fill=255)
    glow = glow.filter(ImageFilter.GaussianBlur(blur))
    ring = Image.new("RGBA", (size, size), (*color, 255))
    ring.putalpha(glow)
    return ring

def crop_center_circle(img, output_size, crop_scale=1.5):
    # no border; glow handled separately
    w, h = img.size
    cx, cy = w/2, h/2
    L = int(output_size * crop_scale)
    box = (int(cx - L/2), int(cy - L/2), int(cx + L/2), int(cy + L/2))
    cropped = img.crop(box).resize((output_size, output_size), Image.LANCZOS)
    mask = Image.new("L", (output_size, output_size), 0)
    ImageDraw.Draw(mask).ellipse((0,0,output_size,output_size), fill=255)
    circle = Image.new("RGBA", (output_size, output_size), (0,0,0,0))
    circle.paste(cropped, (0,0), mask)
    return circle

def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def draw_text_with_shadow(img, xy, text, font, fill=(255,255,255), shadow=(0,0,0), blur=6, offset=(0,0)):
    w, h = img.size
    temp = Image.new("RGBA", (w, h), (0,0,0,0))
    d = ImageDraw.Draw(temp)
    d.text((xy[0]+offset[0], xy[1]+offset[1]), text, font=font, fill=shadow)
    temp = temp.filter(ImageFilter.GaussianBlur(blur))
    base = Image.alpha_composite(img, temp)
    d2 = ImageDraw.Draw(base)
    d2.text(xy, text, font=font, fill=fill)
    return base

def glossy_progress_bar(draw, x, y, length, height, pct, base_color):
    # back track
    radius = height//2
    rounded_rect(draw, (x, y, x+length, y+height), radius, fill=(255,255,255,60))
    # colored fill
    fill_len = int(length * max(0.0, min(1.0, pct)))
    if fill_len > 0:
        grad = Image.new("RGBA", (fill_len, height), (0,0,0,0))
        gd = ImageDraw.Draw(grad)
        top = tuple(min(255, c+40) for c in base_color)
        bot = tuple(max(0, c-10) for c in base_color)
        for i in range(height):
            tcol = tuple(int(top[j] + (bot[j]-top[j])*(i/height)) for j in range(3)) + (230,)
            gd.line([(0,i),(fill_len,i)], fill=tcol)
        # specular highlight
        hl = Image.new("RGBA", (fill_len, height//2), (255,255,255,80))
        grad.paste(hl, (0,0), hl)
        draw.bitmap((x, y), grad)
    # knob
    kx = x + fill_len
    draw.ellipse((kx-10, y+height/2-10, kx+10, y+height/2+10), fill=base_color+(255,))

# ========= Main =========

async def gen_thumb(videoid: str):
    """
    Premium glow thumbnail generator (v5)
    """
    try:
        ensure_dir("cache")
        out_path = f"cache/{videoid}_v5.png"
        if os.path.isfile(out_path):
            return out_path

        url = f"https://www.youtube.com/watch?v={videoid}"
        results = VideosSearch(url, limit=1)
        # fetch metadata
        title = "Unsupported Title"
        duration = "Live"
        thumbnail = None
        views = "Unknown Views"
        channel = "Unknown Channel"

        for result in (await results.next())["result"]:
            t = result.get("title")
            if t:
                t = re.sub(r"\s+", " ", t).strip()
                title = t
            duration = result.get("duration") or "Live"
            thumbs = result.get("thumbnails") or []
            if thumbs:
                thumbnail = thumbs[0]["url"].split("?")[0]
            vc = result.get("viewCount") or {}
            views = vc.get("short") or "Unknown Views"
            ch = result.get("channel") or {}
            channel = ch.get("name") or "Unknown Channel"
            break

        if not thumbnail:
            logging.error("No thumbnail found.")
            return None

        # download image (single read; avoid double .read())
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status != 200:
                    logging.error(f"Thumb fetch failed: {resp.status}")
                    return None
                content = await resp.read()

        base_img = Image.open(io.BytesIO(content)).convert("RGB")
        youtube = base_img
        main_w, main_h = 1280, 720

        # base sized image and stylized background
        image1 = changeImageSize(main_w, main_h, youtube)
        canvas = Image.new("RGBA", (main_w, main_h))
        # blurred darkened bg
        bg = image1.convert("RGBA").filter(ImageFilter.BoxBlur(18))
        bg = ImageEnhance.Brightness(bg).enhance(0.55)

        # dynamic gradient from dominant colors
        c1, c2 = dominant_colors(youtube)
        grad = generate_diag_gradient(main_w, main_h, c1, c2, alpha=0.40)
        bg = Image.alpha_composite(bg, grad)

        # subtle pattern: overlay a faint noise for texture
        noise = Image.effect_noise((main_w, main_h), 12).convert("L").point(lambda p: int(p*0.22))
        bg = Image.composite(Image.new("RGBA", (main_w, main_h), (255,255,255,12)), bg, noise)

        # vignette + bloom
        bg = add_vignette(bg, strength=0.40)
        bg = apply_bloom(bg, threshold=175, blur=14, intensity=0.45)

        # place circular crop with neon outer glow
        circle_size = 440
        circle = crop_center_circle(youtube, circle_size, crop_scale=1.45)
        glow_col = c2  # brighter of the two
        ring = outer_glow_circle(circle_size, color=glow_col, thickness=26, blur=26)
        circle_pos = (110, 140)
        bg.alpha_composite(ring, (circle_pos[0]- (ring.size[0]-circle_size)//2,
                                  circle_pos[1]- (ring.size[1]-circle_size)//2))
        bg.alpha_composite(circle, circle_pos)

        # fonts (fallback safe)
        arial = load_font("ShrutiMusic/assets/font2.ttf", 34)
        meta_font = load_font("ShrutiMusic/assets/font.ttf", 34)
        title_font = load_font("ShrutiMusic/assets/font3.ttf", 56)

        # glass panel behind title/meta (glassmorphism)
        panel_x, panel_y = 600, 160
        panel_w, panel_h = 620, 240
        panel = Image.new("RGBA", (panel_w, panel_h), (255,255,255,60))
        # frosted blur: sample bg slice, blur, then overlay translucent white
        bg_slice = bg.crop((panel_x, panel_y, panel_x+panel_w, panel_y+panel_h)).filter(ImageFilter.GaussianBlur(12))
        glass = Image.blend(bg_slice, panel, 0.35)
        # border
        draw = ImageDraw.Draw(glass)
        rounded_rect(draw, (0,0,panel_w-1,panel_h-1), radius=22, fill=None, outline=(255,255,255,120), width=2)
        bg.alpha_composite(glass, (panel_x, panel_y))

        # title (wrapped)
        max_title_w = panel_w - 40
        lines = wrap_text_by_width(title, title_font, max_title_w)
        tx, ty = panel_x + 20, panel_y + 16
        # draw title with soft shadow
        bg = draw_text_with_shadow(bg, (tx, ty), lines[0], title_font, fill=(255,255,255), shadow=(0,0,0,255), blur=8)
        if lines[1]:
            bg = draw_text_with_shadow(bg, (tx, ty + title_font.size + 6), lines[1], title_font, fill=(255,255,255), shadow=(0,0,0,255), blur=8)

        # meta row
        meta_y = panel_y + panel_h - 62
        meta_text = f"{channel}   •   {views[:23]}"
        bg = draw_text_with_shadow(bg, (tx, meta_y), meta_text, meta_font, fill=(230,230,230), shadow=(0,0,0,255), blur=6)

        # progress bar (premium glossy)
        line_x, line_y = panel_x, 420
        line_len, line_ht = 620, 18
        draw2 = ImageDraw.Draw(bg)
        if duration != "Live":
            pct = random.uniform(0.18, 0.82)
            glossy_progress_bar(draw2, line_x, line_y, line_len, line_ht, pct, base_color=glow_col)
        else:
            glossy_progress_bar(draw2, line_x, line_y, line_len, line_ht, 1.0, base_color=(230, 40, 40))

        # timecodes
        bg = draw_text_with_shadow(bg, (line_x, line_y + 24), "00:00", arial, fill=(255,255,255), shadow=(0,0,0,255), blur=6)
        t_right = line_x + line_len - int(arial.getlength(duration))
        bg = draw_text_with_shadow(bg, (t_right, line_y + 24), duration, arial, fill=(255,255,255), shadow=(0,0,0,255), blur=6)

        # playback control strip (if asset available) + glow
        try:
            play_icons = Image.open("ShrutiMusic/assets/play_icons.png").convert("RGBA").resize((620, 64), Image.LANCZOS)
            # soft glow
            play_glow = play_icons.copy()
            alpha = play_glow.split()[-1].filter(ImageFilter.GaussianBlur(8))
            glow_layer = Image.new("RGBA", play_glow.size, (*glow_col, 160))
            glow_layer.putalpha(alpha)
            bg.alpha_composite(glow_layer, (panel_x, 460))
            bg.alpha_composite(play_icons, (panel_x, 460))
        except Exception:
            pass  # optional

        # final gentle contrast and saturation pop
        pop = ImageEnhance.Contrast(bg).enhance(1.06)
        pop = ImageEnhance.Color(pop).enhance(1.08)

        out = pop.convert("RGB")
        out.save(out_path, quality=95, subsampling=1, optimize=True)
        return out_path

    except Exception as e:
        logging.error(f"Error generating thumbnail for video {videoid}: {e}")
        traceback.print_exc()
        return None
