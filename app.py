# app.py
# MemeGen Pro — Streamlit Meme Generator with OpenRouter AI (x-ai/grok-4.1-fast:free) and Classic White Strap Top Text Layout

import io
import textwrap
import requests
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

# -------------------------
# App config
# -------------------------
st.set_page_config(page_title="MemeGen Pro", page_icon="🖼️🤖", layout="centered")
st.title("MemeGen Pro")
st.markdown("Create topic-aware memes using OpenRouter AI — upload an image, select caption style, and get an AI-generated caption with classic white top strap layout.")

# -------------------------
# OpenRouter AI setup
# -------------------------
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
MODEL_NAME = "x-ai/grok-4.1-fast:free"
OPENROUTER_URL = "https://api.openrouter.ai/v1/completions"

# -------------------------
# Helpers
# -------------------------

def call_openrouter_text_model(prompt: str, max_tokens: int = 60):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_NAME,
        "input": prompt,
        "max_output_tokens": max_tokens
    }
    try:
        r = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        if "output" in data and len(data["output"]) > 0 and "content" in data["output"][0]:
            return data["output"][0]["content"].strip(), None
        return None, "No output in OpenRouter response"
    except Exception as e:
        return None, str(e)


def generate_caption(topic: str, style: str = "funny") -> str:
    prompt = f"Write a short meme caption about '{topic}' in a {style} style. Keep it punchy, 1-2 lines."
    text, err = call_openrouter_text_model(prompt, max_tokens=60)

    if not text:
        # fallback if API fails
        fallback = [
            f"When you think about {topic}...",
            f"{topic}? Nailed it!",
            f"The struggle with {topic} is real",
            f"{topic} vibes 😎"
        ]
        text = fallback[hash(topic) % len(fallback)]
    return text


def draw_text_on_image(image: Image.Image, text: str, font_path: str = None) -> Image.Image:
    img = image.convert("RGBA")
    w, h = img.size

    # Font
    font_size = max(24, int(w / 15))
    font = None
    if font_path:
        try:
            font = ImageFont.truetype(font_path, font_size)
        except Exception:
            font = None
    if font is None:
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()

    # Wrap text
    max_chars_per_line = max(20, int(w / (font_size * 0.6)))
    wrapped = textwrap.fill(text, width=max_chars_per_line)
    lines = wrapped.split("\n")

    # Calculate height of text block
    bbox = font.getbbox("A")
    line_height = (bbox[3] - bbox[1]) + 6
    total_text_height = line_height * len(lines)

    # Create new image with extra top space for white strap
    new_img = Image.new("RGB", (w, h + total_text_height + 20), color="white")
    new_img.paste(img, (0, total_text_height + 20))

    draw = ImageDraw.Draw(new_img)

    # Draw text on the white strap
    y = 10  # padding from top
    for line in lines:
        bbox_line = draw.textbbox((0, 0), line, font=font)
        line_w = bbox_line[2] - bbox_line[0]
        x = (w - line_w) / 2
        draw.text((x, y), line, font=font, fill="black")
        y += line_height

    return new_img

# -------------------------
# Streamlit UI
# -------------------------

st.sidebar.header("Settings")
style = st.sidebar.selectbox("Caption style", ["funny", "sarcastic", "dark", "wholesome", "dad-joke"]) 
max_tokens = st.sidebar.slider("Max caption tokens", min_value=20, max_value=200, value=60)

uploaded = st.file_uploader("Upload an image (JPG/PNG)", type=["jpg", "jpeg", "png"])
topic = st.text_input("Meme topic (e.g., Monday morning, exams, AI at work)")

if st.button("Generate Caption & Preview"):
    if not uploaded:
        st.error("Please upload an image first.")
    elif not topic.strip():
        st.error("Please enter a topic for the caption.")
    else:
        with st.spinner("Generating caption..."):
            caption = generate_caption(topic.strip(), style=style)
            image = Image.open(uploaded).convert("RGB")
            meme = draw_text_on_image(image, caption)
            buf = io.BytesIO()
            meme.save(buf, format="PNG")
            buf.seek(0)
            st.image(meme, use_column_width=True)
            st.download_button("Download Meme (PNG)", data=buf, file_name="meme.png", mime="image/png")
            st.success("Done — download your meme!")

st.markdown("---")
st.markdown("Made with ❤ — MemeGen Pro using OpenRouter AI.")
