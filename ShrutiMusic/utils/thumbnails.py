# Copyright (c) 2025 Nand Yaduwanshi <NoxxOP>
# Location: Supaul, Bihar
#
# Enhanced Premium Version - Advanced YouTube Thumbnail Generator
# All rights reserved.

import random
import logging
import os
import re
import math
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from youtubesearchpython.__future__ import Video

logging.basicConfig(level=logging.INFO)

class PremiumThumbnailGenerator:
    def __init__(self):
        self.canvas_width = 1280
        self.canvas_height = 720
        self.modern_colors = {
            'neon_blue': (0, 123, 255),
            'neon_purple': (138, 43, 226),
            'neon_pink': (255, 20, 147),
            'neon_green': (50, 205, 50),
            'neon_orange': (255, 140, 0),
            'cyber_blue': (0, 255, 255),
            'electric_violet': (143, 0, 255),
            'hot_pink': (255, 105, 180)
        }

    def change_image_size(self, max_width, max_height, image):
        width_ratio = max_width / image.size[0]
        height_ratio = max_height / image.size[1]
        ratio = min(width_ratio, height_ratio)
        new_width = int(ratio * image.size[0])
        new_height = int(ratio * image.size[1])
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    def smart_text_truncate(self, text, max_chars_per_line=35):
        words = text.split(" ")
        lines = ["", ""]
        current_line = 0

        for word in words:
            if current_line >= 2:
                break

            if len(lines[current_line]) + len(word) + 1 <= max_chars_per_line:
                if lines[current_line]:
                    lines[current_line] += " " + word
                else:
                    lines[current_line] = word
            elif current_line < 1:
                current_line += 1
                lines[current_line] = word
            else:
                if len(lines[1]) > 30:
                    lines[1] = lines[1][:30] + "..."
                break

        return [line.strip() for line in lines if line.strip()]

    def generate_premium_gradient(self, width, height, colors, gradient_type="diagonal"):
        base = Image.new('RGBA', (width, height), colors[0])

        if gradient_type == "diagonal":
            for i, color in enumerate(colors[1:], 1):
                overlay = Image.new('RGBA', (width, height), color)
                mask = Image.new('L', (width, height))
                mask_data = []

                for y in range(height):
                    for x in range(width):
                        distance = (x + y) / (width + height)
                        alpha = int(255 * distance * (i / len(colors)))
                        alpha = max(0, min(255, alpha))
                        mask_data.append(alpha)

                mask.putdata(mask_data)
                base.paste(overlay, (0, 0), mask)

        elif gradient_type == "radial":
            center_x, center_y = width // 2, height // 2
            max_distance = math.sqrt(center_x**2 + center_y**2)

            for i, color in enumerate(colors[1:], 1):
                overlay = Image.new('RGBA', (width, height), color)
                mask = Image.new('L', (width, height))
                mask_data = []

                for y in range(height):
                    for x in range(width):
                        distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                        alpha = int(255 * (distance / max_distance) * (i / len(colors)))
                        alpha = max(0, min(255, alpha))
                        mask_data.append(alpha)

                mask.putdata(mask_data)
                base.paste(overlay, (0, 0), mask)

        return base

    def create_glassmorphism_effect(self, width, height, base_color, blur_radius=30):
        glass = Image.new('RGBA', (width, height), (*base_color[:3], 80))
        glass = glass.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        return glass

    def create_neon_border_circle(self, img, output_size, border_width=8, glow_intensity=15):
        img = img.convert('RGBA')
        img = self.change_image_size(output_size, output_size, img)

        mask = Image.new('L', (output_size, output_size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, output_size, output_size), fill=255)

        circular_img = Image.new('RGBA', (output_size, output_size), (0, 0, 0, 0))
        circular_img.paste(img, (0, 0), mask)

        glow_size = output_size + (glow_intensity * 2)
        glow_canvas = Image.new('RGBA', (glow_size, glow_size), (0, 0, 0, 0))

        neon_color = random.choice(list(self.modern_colors.values()))
        for i in range(glow_intensity, 0, -2):
            glow_layer = Image.new('RGBA', (glow_size, glow_size), (0, 0, 0, 0))
            glow_draw = ImageDraw.Draw(glow_layer)

            alpha = int(30 * (i / glow_intensity))
            glow_draw.ellipse(
                (glow_intensity - i, glow_intensity - i,
                 glow_size - glow_intensity + i, glow_size - glow_intensity + i),
                fill=(*neon_color, alpha)
            )
            glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=i))
            glow_canvas = Image.alpha_composite(glow_canvas, glow_layer)

        glow_canvas.paste(circular_img, (glow_intensity, glow_intensity), circular_img)

        return glow_canvas, neon_color

    def create_animated_progress_bar(self, draw, position, width, height, progress, accent_color):
        x, y = position
        background_bar = Image.new('RGBA', (width + 20, height + 20), (0, 0, 0, 0))
        bg_draw = ImageDraw.Draw(background_bar)

        bg_draw.rounded_rectangle(
            (10, 10, width + 10, height + 10),
            radius=height // 2,
            fill=(40, 40, 40, 180)
        )

        if progress > 0:
            progress_width = int(width * progress)
            bg_draw.rounded_rectangle(
                (10, 10, progress_width + 10, height + 10),
                radius=height // 2,
                fill=accent_color
            )

            highlight_height = height // 3
            bg_draw.rounded_rectangle(
                (10, 10, progress_width + 10, 10 + highlight_height),
                radius=height // 4,
                fill=tuple(min(255, c + 50) for c in accent_color)
            )

        return background_bar

    def draw_text_with_advanced_shadow(self, background, position, text, font, fill_color,
                                     shadow_color=(0, 0, 0), shadow_offset=(4, 4),
                                     glow_color=None, glow_radius=0):
        x, y = position
        text_layer = Image.new('RGBA', background.size, (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_layer)

        if glow_color and glow_radius > 0:
            for offset_x in range(-glow_radius, glow_radius + 1):
                for offset_y in range(-glow_radius, glow_radius + 1):
                    if offset_x == 0 and offset_y == 0:
                        continue
                    distance = math.sqrt(offset_x**2 + offset_y**2)
                    if distance <= glow_radius:
                        alpha = int(100 * (1 - distance / glow_radius))
                        text_draw.text((x + offset_x, y + offset_y), text, font=font,
                                     fill=(*glow_color, alpha))

        text_draw.text((x + shadow_offset[0], y + shadow_offset[1]), text,
                      font=font, fill=(*shadow_color, 150))

        text_draw.text((x, y), text, font=font, fill=fill_color)

        background = Image.alpha_composite(background.convert('RGBA'), text_layer)
        return background

    def create_premium_ui_elements(self, background, accent_color):
        draw = ImageDraw.Draw(background)
        play_center_x, play_center_y = 640, 500
        play_radius = 40

        for i in range(20, 0, -2):
            alpha = int(20 * (i / 20))
            draw.ellipse(
                (play_center_x - play_radius - i, play_center_y - play_radius - i,
                 play_center_x + play_radius + i, play_center_y + play_radius + i),
                fill=(*accent_color, alpha)
            )

        draw.ellipse(
            (play_center_x - play_radius, play_center_y - play_radius,
             play_center_x + play_radius, play_center_y + play_radius),
            fill=(255, 255, 255, 220)
        )

        triangle_points = [
            (play_center_x - 15, play_center_y - 20),
            (play_center_x - 15, play_center_y + 20),
            (play_center_x + 20, play_center_y)
        ]
        draw.polygon(triangle_points, fill=accent_color)

        return background

    async def generate_premium_thumbnail(self, videoid: str):
        try:
            cache_path = f"cache/{videoid}_premium_v2.png"
            if os.path.isfile(cache_path):
                return cache_path

            # ✅ Get video info directly by ID
            video_data = (await Video.getInfo(videoid))["video"]

            title = re.sub(r"\W+", " ", video_data.get("title", "Untitled")).title()
            duration = video_data.get("duration", "Live")
            thumbnail_url = video_data["thumbnails"][0]["url"].split("?")[0]
            views = video_data.get("viewCount", {}).get("short", "Unknown Views")
            channel = video_data.get("channel", {}).get("name", "Unknown Channel")

            async with aiohttp.ClientSession() as session:
                async with session.get(thumbnail_url) as resp:
                    if resp.status == 200:
                        content = await resp.read()
                        temp_path = f"cache/temp_{videoid}.jpg"
                        async with aiofiles.open(temp_path, mode="wb") as f:
                            await f.write(content)

            youtube_img = Image.open(temp_path)

            gradient_colors = random.sample(list(self.modern_colors.values()), 3)
            background = self.generate_premium_gradient(
                self.canvas_width, self.canvas_height,
                gradient_colors, "diagonal"
            )

            glass_overlay = self.create_glassmorphism_effect(
                self.canvas_width, self.canvas_height,
                gradient_colors[0], blur_radius=50
            )
            background = Image.alpha_composite(background.convert('RGBA'), glass_overlay)

            circular_thumb, accent_color = self.create_neon_border_circle(youtube_img, 300, glow_intensity=20)

            thumb_x = 100
            thumb_y = (self.canvas_height - circular_thumb.height) // 2
            background.paste(circular_thumb, (thumb_x, thumb_y), circular_thumb)

            try:
                title_font = ImageFont.truetype("assets/font3.ttf", 52)
                subtitle_font = ImageFont.truetype("assets/font2.ttf", 28)
                info_font = ImageFont.truetype("assets/font.ttf", 24)
            except:
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
                info_font = ImageFont.load_default()

            text_start_x = 450
            title_lines = self.smart_text_truncate(title, 40)

            y_offset = 180
            for i, line in enumerate(title_lines):
                background = self.draw_text_with_advanced_shadow(
                    background, (text_start_x, y_offset + i * 60), line,
                    title_font, (255, 255, 255), glow_color=accent_color, glow_radius=3
                )

            info_text = f"🎵 {channel} • {views}"
            background = self.draw_text_with_advanced_shadow(
                background, (text_start_x, y_offset + len(title_lines) * 60 + 20),
                info_text, subtitle_font, (200, 200, 200)
            )

            if duration != "Live":
                progress = random.uniform(0.2, 0.8)
                progress_bar = self.create_animated_progress_bar(
                    None, (text_start_x, y_offset + len(title_lines) * 60 + 80),
                    500, 12, progress, accent_color
                )
                background.paste(progress_bar, (text_start_x - 10, y_offset + len(title_lines) * 60 + 70), progress_bar)

                background = self.draw_text_with_advanced_shadow(
                    background, (text_start_x, y_offset + len(title_lines) * 60 + 110),
                    "00:00", info_font, (180, 180, 180)
                )
                background = self.draw_text_with_advanced_shadow(
                    background, (text_start_x + 450, y_offset + len(title_lines) * 60 + 110),
                    duration, info_font, (180, 180, 180)
                )
            else:
                live_bg = Image.new('RGBA', (80, 30), (*accent_color, 255))
                background.paste(live_bg, (text_start_x, y_offset + len(title_lines) * 60 + 80), live_bg)
                background = self.draw_text_with_advanced_shadow(
                    background, (text_start_x + 15, y_offset + len(title_lines) * 60 + 85),
                    "LIVE", info_font, (255, 255, 255)
                )

            background = self.create_premium_ui_elements(background, accent_color)

            noise = Image.new('RGBA', (self.canvas_width, self.canvas_height), (0, 0, 0, 0))
            noise_pixels = []
            for _ in range(self.canvas_width * self.canvas_height):
                if random.random() < 0.02:
                    alpha = random.randint(10, 30)
                    noise_pixels.append((255, 255, 255, alpha))
                else:
                    noise_pixels.append((0, 0, 0, 0))
            noise.putdata(noise_pixels)
            background = Image.alpha_composite(background, noise)

            background.save(cache_path, "PNG", quality=95)
            os.remove(temp_path)

            return cache_path

        except Exception as e:
            logging.error(f"Error generating premium thumbnail for {videoid}: {e}")
            return None

# Main function
async def gen_thumb(videoid: str):
    generator = PremiumThumbnailGenerator()
    return await generator.generate_premium_thumbnail(videoid)

# Alternative alias
async def gen_premium_thumb(videoid: str):
    return await gen_thumb(videoid)

# ===========================================
# ©️ 2025 Nand Yaduwanshi (aka @NoxxOP) - Enhanced Premium Version
# 🔗 GitHub : https://github.com/NoxxOP/ShrutiMusic
# 📢 Telegram Channel : https://t.me/ShrutiBots
# ===========================================

# ❤️ Enhanced Premium Design - Love From ShrutiBots
