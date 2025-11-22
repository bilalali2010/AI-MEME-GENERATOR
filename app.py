import streamlit as st
import base64
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# ---------------------------
# CONFIG
# ---------------------------
API_URL = "https://api.together.xyz/v1/chat/completions"  # Free model
MODEL_NAME = "deepseek-r1:free"

# ---------------------------
# AI CAPTION GENERATION
# ---------------------------
def generate_caption(user_prompt, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are an AI that writes short, funny meme captions."},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 60
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        return "Error generating caption. Check API key."

    return response.json()["choices"][0]["message"]["content"].strip()

# ---------------------------
# ADD CAPTION TO IMAGE
# ---------------------------
def add_caption_to_image(image, caption_text):
    img = image.convert("RGB")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()

    text = caption_text
    w, h = img.size
    text_w, text_h = draw.textsize(text, font=font)
    x = (w - text_w) / 2
    y = h - text_h - 20

    draw.text((x, y), text, fill="white", stroke_width=3, stroke_fill="black", font=font)

    return img

# ---------------------------
# STREAMLIT UI
# ---------------------------
st.set_page_config(page_title="AI Meme Generator", layout="wide")
st.title("😂 AI Meme Generator (Free Model)")
st.write("Upload an image → Generate caption → Download meme")

api_key = st.text_input("Enter API Key (Together API)")
user_input = st.text_input("Describe meme style or topic", "Make a funny caption about exams")
image_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

if image_file:
    image = Image.open(image_file)
    st.image(image, caption="Uploaded Image", width=400)

if st.button("Generate Meme Caption", disabled=not (image_file and api_key)):
    with st.spinner("Generating caption..."):
        caption = generate_caption(user_input, api_key)

    st.subheader("Generated Caption:")
    st.success(caption)

    meme = add_caption_to_image(image, caption)

    st.image(meme, caption="Meme Output", width=500)

    buf = BytesIO()
    meme.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.download_button(
        label="Download Meme",
        data=byte_im,
        file_name="meme.png",
        mime="image/png"
    )

st.markdown("---")
st.info("You can deploy this repo directly on Streamlit Cloud. Just push this file to GitHub.")
