from PIL import Image, ImageDraw, ImageFont
import textwrap

# Load the image
img = Image.open(r"C:\Users\lenovo\OneDrive\Desktop\Face swap\Dance winner\Leonardo_Phoenix_10_A_young_girl_named_Maya_is_practicing_danc_0.jpg").convert("RGBA")

# Create overlay for transparency
overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
draw = ImageDraw.Draw(overlay)

# Text and font
text = 'Some girls teased her, "You can’t even move properly djndsnflkfdadsmdklasmndklasnkldnaskldnjasbfk adslc dc kj!"'
font = ImageFont.truetype("arial.ttf", 80)

# Wrap text to fit image width
max_chars_per_line = 60   # you can adjust
lines = textwrap.wrap(text, width=max_chars_per_line)

# Measure each line
line_sizes = [draw.textbbox((0, 0), line, font=font) for line in lines]
line_widths = [bbox[2] - bbox[0] for bbox in line_sizes]
line_heights = [bbox[3] - bbox[1] for bbox in line_sizes]

text_width = max(line_widths)
text_height = sum(line_heights) + (len(lines) - 1) * 15  # 15px spacing between lines

# Position (centered horizontally, near bottom)
padding_x, padding_y = 25, 25
x = (img.width - text_width) // 2
y = img.height - text_height - 100

# Background box around all text
box_coords = [
    x - padding_x,
    y - padding_y,
    x + text_width + padding_x,
    y + text_height + padding_y
]

# Draw rounded rectangle with transparency
draw.rounded_rectangle(box_coords, fill=(75, 100, 255, 160), radius=20)

# Draw each line of text centered
current_y = y
for i, line in enumerate(lines):
    line_width = line_widths[i]
    draw.text(((img.width - line_width) // 2, current_y), line, font=font, fill="white")
    current_y += line_heights[i] + 15  # line spacing

# Merge overlay with original
out = Image.alpha_composite(img, overlay)

# Save final
out.convert("RGB").save("output_fixed.png")
