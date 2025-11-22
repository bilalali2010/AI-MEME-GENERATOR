import io
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


bbox = font.getbbox("A")
line_height = (bbox[3] - bbox[1]) + 6
total_text_height = line_height * len(lines)


new_img = Image.new("RGB", (w, h + total_text_height + 20), color="white")
new_img.paste(img, (0, total_text_height + 20))


draw = ImageDraw.Draw(new_img)


y = 10
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


st.markdown("<hr style='border:1px solid #DDD;'>", unsafe_allow_html=True)


uploaded = st.file_uploader("Upload an image (JPG/PNG)", type=["jpg", "jpeg", "png"])
topic = st.text_input("Meme topic")


st.markdown("<hr style='border:1px solid #DDD;'>", unsafe_allow_html=True)


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
st.image(meme, use_column_width=True, caption=caption)
st.download_button("Download Meme (PNG)", data=buf, file_name="meme.png", mime="image/png")
st.success("Done — download your meme!")


st.markdown("<hr style='border:1px solid #DDD;'>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#777777;'>Made with ❤ — MemeGen Pro using OpenRouter AI.</p>", unsafe_allow_html=True)
