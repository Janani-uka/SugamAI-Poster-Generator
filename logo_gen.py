from PIL import Image, ImageDraw, ImageFont
import os

def create_logo(text="SugamAI", filename="static/logos/mylogo.png"):
    os.makedirs("static/logos", exist_ok=True)

    # Canvas
    img = Image.new("RGBA", (400, 400), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Draw concentric circles for gradient effect
    for i in range(0, 200, 5):  # step avoids overlap errors
        color = (147, 51, 234, 180 - i//2)  # purple shades
        draw.ellipse([i, i, 400-i, 400-i], fill=color)

    # Take first letter of text
    letter = text[0].upper()
    try:
        font = ImageFont.truetype("arialbd.ttf", 160)
    except:
        font = ImageFont.load_default()

    # Measure text using bbox
    bbox = draw.textbbox((0, 0), letter, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # Center the text
    draw.text(((400-w)//2, (400-h)//2), letter, font=font, fill=(255, 255, 255, 255))

    img.save(filename)
    print(f"✅ Logo saved at {filename}")

# Run this to generate your unique logo
if __name__ == "__main__":
    create_logo("SugamAI")
