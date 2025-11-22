# app.py
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


line_height = font.getsize("A")[1] + 6
total_text_height = line_height * len(lines)
y = h - total_text_height - int(h * 0.05)


for line in lines:
line_w, line_h = draw.textsize(line, font=font)
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
