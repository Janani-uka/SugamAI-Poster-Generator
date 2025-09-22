import os
from flask import Flask, render_template, request, send_file, redirect, url_for
from PIL import Image, ImageDraw, ImageFont
import random
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static"
app.config["UPLOAD_BG"] = "static/uploads"
app.config["UPLOAD_LOGO"] = "static/logos"

# Ensure folders exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["UPLOAD_BG"], exist_ok=True)
os.makedirs(app.config["UPLOAD_LOGO"], exist_ok=True)


# -------------------
# Helper Functions
# -------------------

def generate_caption(shop, offer, festival, lang="en"):
    """Generate a caption in multiple languages"""
    captions = {
        "en": [
            f"Celebrate {festival} 🎉 at {shop} - {offer}",
            f"{shop} brings you {festival} Special: {offer}"
        ],
        "ta": [
            f"{festival} சிறப்பு 🎉 {shop} - {offer}",
            f"{shop} - {festival} சலுகை: {offer}"
        ],
        "hi": [
            f"{festival} ऑफर 🎉 {shop} - {offer}",
            f"{shop} के साथ मनाएं {festival} - {offer}"
        ],
    }
    return random.choice(captions.get(lang, captions["en"]))


def generate_poster(shop, offer, festival, caption, bg_path=None, logo_path=None):
    """Generates a stylish, professional-looking poster."""

    # Background map
    bg_map = {
        "Diwali": "static/backgrounds/diwali.jpg",
        "Pongal": "static/backgrounds/pongal.jpg",
        "Eid": "static/backgrounds/eid.jpg"
    }

    # Background selection (uploaded > preset > fallback)
    if bg_path and os.path.exists(bg_path):
        img = Image.open(bg_path).convert("RGB").resize((600, 400))
    elif festival in bg_map and os.path.exists(bg_map[festival]):
        img = Image.open(bg_map[festival]).convert("RGB").resize((600, 400))
    else:
        img = Image.new("RGB", (600, 400), "#e0f7fa")
        gradient = Image.new("RGB", (600, 400), "#80deea")
        img = Image.blend(img, gradient, alpha=0.5)

    d = ImageDraw.Draw(img)

    # Fonts
    try:
        font_title = ImageFont.truetype("arialbd.ttf", 36)
        font_offer = ImageFont.truetype("arialbd.ttf", 34)
        font_shop = ImageFont.truetype("arial.ttf", 26)
        font_caption = ImageFont.truetype("ariali.ttf", 20)  # italic
    except:
        font_title = font_offer = font_shop = font_caption = ImageFont.load_default()

    # Title (Gold, Centered)
    title_text = f"{festival} Special ✨"
    tw, th = d.textbbox((0, 0), title_text, font=font_title)[2:]
    d.text(((600 - tw) // 2, 20), title_text,
           fill=(255, 215, 0), font=font_title,
           stroke_width=2, stroke_fill="black")

    # Shop Name (Blue with white outline)
    d.text((40, 100), f"🏪 {shop}", fill=(0, 51, 102),
           font=font_shop, stroke_width=1, stroke_fill="white")

    # Offer Box (Blue → Teal gradient)
    box_x, box_y, box_w, box_h = 40, 160, 520, 70
    for i in range(box_h):
        color = (
            0,
            int(105 + (200 - 105) * (i / box_h)),   # G fades 105 → 200
            int(148 + (255 - 148) * (i / box_h))   # B fades 148 → 255
        )
        d.line([(box_x, box_y + i), (box_x + box_w, box_y + i)], fill=color)

    d.rectangle([box_x, box_y, box_x + box_w, box_y + box_h],
                outline="white", width=3)

    ow, oh = d.textbbox((0, 0), offer, font=font_offer)[2:]
    d.text((box_x + (box_w - ow) // 2, box_y + 10), offer,
           fill="white", font=font_offer, stroke_width=2, stroke_fill="black")

    # Caption (Dark footer bar)
    d.rectangle([0, 360, 600, 400], fill=(34, 34, 34, 200))
    d.text((20, 370), caption, fill="white", font=font_caption)

    # Add Logo (top-right corner)
    if logo_path and os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA").resize((100, 100))
        img.paste(logo, (480, 20), logo)

    # Save Poster
    poster_path = os.path.join(app.config["UPLOAD_FOLDER"], "poster.png")
    img.save(poster_path)
    return poster_path


# -------------------
# Routes
# -------------------

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        shop = request.form.get("shop")
        offer = request.form.get("offer")
        festival = request.form.get("festival")
        lang = request.form.get("lang", "en")

        # Custom occasion
        if festival == "Custom":
            festival = request.form.get("custom_festival", "Special Event")

        # Background upload
        bg_path = None
        if "bg_image" in request.files:
            file = request.files["bg_image"]
            if file and file.filename != "":
                filename = secure_filename(file.filename)
                bg_path = os.path.join(app.config["UPLOAD_BG"], filename)
                file.save(bg_path)

        # Logo upload
        logo_path = None
        if "logo" in request.files:
            file = request.files["logo"]
            if file and file.filename != "":
                filename = secure_filename(file.filename)
                logo_path = os.path.join(app.config["UPLOAD_LOGO"], filename)
                file.save(logo_path)

        caption = generate_caption(shop, offer, festival, lang)
        generate_poster(shop, offer, festival, caption, bg_path, logo_path)

        return redirect(url_for("poster_page", caption=caption))

    return render_template("index.html")


@app.route("/poster")
def poster_page():
    poster_path = os.path.join(app.config["UPLOAD_FOLDER"], "poster.png")
    caption = request.args.get("caption", "")
    return render_template("poster.html", poster=poster_path, caption=caption)


@app.route("/download")
def download_poster():
    poster_path = os.path.join(app.config["UPLOAD_FOLDER"], "poster.png")
    return send_file(poster_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
