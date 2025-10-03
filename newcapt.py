from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
import json
import re

def add_caption_advanced(image_path, caption, output_path, font_size=80):
    """
    Advanced caption function with exact styling from reference code
    """
    # Load the image
    img = Image.open(image_path).convert("RGBA")
    
    # Create overlay for transparency
    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    # Text and font
    text = caption
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        # Fallback to default font if arial is not available
        font = ImageFont.load_default()

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
    out.convert("RGB").save(output_path)
    print(f"Advanced caption added: {output_path}")

def load_captions_from_file(captions_file_path):
    """
    Load captions from a text file or JSON file
    Supports multiple formats:
    - JSON: List of objects with 'image' and 'caption'
    - Text: Each line as "image_name:caption"
    - Simple text: Each line as caption (uses default naming)
    """
    captions_data = []
    
    if not os.path.exists(captions_file_path):
        print(f"Captions file not found: {captions_file_path}")
        return captions_data
    
    file_extension = os.path.splitext(captions_file_path)[1].lower()
    
    try:
        if file_extension == '.json':
            # JSON format
            with open(captions_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        if 'image' in item and 'caption' in item:
                            captions_data.append({
                                'image': item['image'],
                                'caption': item['caption'],
                                'page_number': item.get('page_number', len(captions_data) + 1)
                            })
        else:
            # Text file format
            with open(captions_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    line = line.strip()
                    if line and not line.startswith('#'):  # Skip empty lines and comments
                        if ':' in line:
                            # Format: "image_name:caption"
                            parts = line.split(':', 1)
                            image_name = parts[0].strip()
                            caption = parts[1].strip()
                            captions_data.append({
                                'image': image_name,
                                'caption': caption,
                                'page_number': i + 1
                            })
                        else:
                            # SIMPLE FORMAT: just caption, no image name
                            # We'll handle this in the processing function
                            captions_data.append({
                                'caption': line,
                                'page_number': i + 1
                            })
    except Exception as e:
        print(f"Error reading captions file: {e}")
    
    return captions_data

def get_image_files_sorted(folder_path):
    """
    Get all image files from folder, sorted naturally
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.gif'}
    image_files = []
    
    for file in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file)):
            ext = os.path.splitext(file)[1].lower()
            if ext in image_extensions:
                image_files.append(file)
    
    # Natural sort for better ordering (1, 2, 10 instead of 1, 10, 2)
    image_files.sort(key=lambda x: [int(c) if c.isdigit() else c.lower() for c in re.split('([0-9]+)', x)])
    return image_files

def process_story_book_simple_format(input_folder, captions_file, output_folder="output"):
    """
    Process images with simple caption format (no image names mentioned)
    Images and captions are matched by order
    """
    import re
    
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Load captions (simple format)
    captions_data = load_captions_from_file(captions_file)
    
    if not captions_data:
        print("No captions found to process!")
        return
    
    # Get all image files sorted
    image_files = get_image_files_sorted(input_folder)
    
    if not image_files:
        print("No image files found in input folder!")
        return
    
    print(f"Found {len(image_files)} images and {len(captions_data)} captions")
    
    # Check if we have enough captions
    if len(captions_data) < len(image_files):
        print(f"Warning: More images ({len(image_files)}) than captions ({len(captions_data)})")
        print("Some images will not be processed")
    elif len(captions_data) > len(image_files):
        print(f"Warning: More captions ({len(captions_data)}) than images ({len(image_files)})")
        print("Some captions will not be used")
    
    # Process images with captions
    processed_count = 0
    for i, image_file in enumerate(image_files):
        if i >= len(captions_data):
            break
            
        caption_info = captions_data[i]
        caption = caption_info['caption']
        page_number = caption_info['page_number']
        
        image_path = os.path.join(input_folder, image_file)
        
        # Generate output filename
        original_ext = os.path.splitext(image_file)[1]
        output_filename = f"page_{page_number:03d}{original_ext}"
        output_path = os.path.join(output_folder, output_filename)
        
        print(f"Processing [{i+1}/{min(len(image_files), len(captions_data))}]")
        print(f"Image: {image_file}")
        print(f"Caption: {caption}")
        
        try:
            add_caption_advanced(image_path, caption, output_path)
            print(f"✓ Page {page_number} completed\n")
            processed_count += 1
        except Exception as e:
            print(f"✗ Failed to process {image_file}: {e}\n")
    
    print(f"Successfully processed {processed_count} pages!")
    print(f"Output folder: {output_folder}")

# Example usage
if __name__ == "__main__":
    
    # Method 1: Simple format (captions only)
    process_story_book_simple_format(
        input_folder="input_images",
        captions_file="caption.txt",
        output_folder="story_output"
    )
    
