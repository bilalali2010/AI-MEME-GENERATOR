# app.py
# MemeGen Pro — Streamlit Meme Generator (Fixed for Pillow ≥ 10)

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
st.markdown("Create memes fast — upload an image, select caption style, and get an AI-generated caption (free HuggingFace).")

# -------------------------
# HuggingFace free text-generation model
# -------------------------
HF_MODEL = "distilgpt2"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

# -------------------------
# Helpers
# -------------------------

def call_hf_text_model(prompt: str, max_length: int = 60):
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": max_length, "return_full_text": False}}
    try:
        r = requests.post(HF_API_URL, json=payload, timeout=30)
    except Exception as e:
        return None, f"Request failed: {e}"

    if r.status_code != 200:
        return None, f"HF API error {r.status_code}: {r.text}"

    try:
        data = r.json()
    except Exception as e:
        return None, f"Invalid JSON response: {e}"

    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        text = data[0].get("generated_text") or data[0].get("text")
        if text:
            return text.strip(), None
    if isinstance(data, dict) and "generated_text" in data:
        return data["generated_text"].strip(), None
    if isinstance(data, str):
        return data.strip(), None

    return str(data).strip(), None


def generate_caption(topic: str, style: str = "funny") -> str:
    prompt = f"Write a short meme caption about '{topic}' in a {style} style. Keep it punchy, one or two short lines, suitable for a meme."
    text, err = call_hf_text_model(prompt)
    if err or not text:
        fallback = [
            "When you realize it's Monday again...",
            "Me: *tries once*\nAlso me: *already an expert*",
            "That face you make when Wi-Fi dies",
            "I asked for coffee, got an emotional support mug instead",
        ]
        return fallback[hash(topic) % len(fallback)]

    text = text.replace("\n", " ").strip()
    if len(text) > 140:
        text = textwrap.shorten(text, width=120, placeholder="...")
    return text


def draw_text_on_image(image: Image.Image, text: str, font_path: str = None) -> Image.Image:
    img = image.convert("RGBA")
    draw = ImageDraw.Draw(img)
    w, h = img.size

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

    max_chars_per_line = max(20, int(w / (font_size * 0.6)))
    wrapped = textwrap.fill(text, width=max_chars_per_line)
    lines = wrapped.split("\n")

    # Fixed line height calculation using getbbox (works in newer Pillow)
    bbox = font.getbbox("A")
    line_height = (bbox[3] - bbox[1]) + 6
    total_text_height = line_height * len(lines)
    y = h - total_text_height - int(h * 0.05)

    for line in lines:
        # Use textbbox to calculate line width (Pillow ≥ 10 safe)
        bbox_line = draw.textbbox((0, 0), line, font=font, stroke_width=2)
        line_w = bbox_line[2] - bbox_line[0]
        x = (w - line_w) / 2
        draw.text((x, y), line, font=font, fill="black", stroke_width=2, stroke_fill="white")
        y += line_height

    return img.convert("RGB")

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
st.markdown("Made with ❤ — MemeGen Pro. Deploy easily to Streamlit Cloud.")
