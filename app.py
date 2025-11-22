# app.py
# MemeGen Pro — Streamlit Meme Generator (Upload image + HF caption generator)


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
st.markdown("Create memes fast — upload an image, enter a topic/style and get an AI caption (free HuggingFace inference).")


# -------------------------
# HuggingFace text-generation model (public inference endpoint)
# No API key required for public endpoints; subject to HF usage limits.
# You can change HF_MODEL to another public model if you prefer.
# -------------------------
HF_MODEL = "Qwen/Qwen2.5-1.5B-Instruct" # recommended default
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"


# -------------------------
# Helpers
# -------------------------


def call_hf_text_model(prompt: str, max_length: int = 60):
"""Call HuggingFace Inference API for text generation.
The public inference endpoint returns JSON; structure may vary per model, so we try a few ways to extract text.
"""
payload = {"inputs": prompt, "parameters": {"max_new_tokens": max_length, "return_full_text": False}}
try:
r = requests.post(HF_API_URL, json=payload, timeout=30)
except Exception as e:
return None, f"Request failed: {e}"


if r.status_code != 200:
# return the error text for debugging
return None, f"HF API error {r.status_code}: {r.text}"


try:
data = r.json()
except Exception as e:
return None, f"Invalid JSON response: {e}"


# Models sometimes return a list of {generated_text: ...} or a string. Try to handle common cases.
if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
text = data[0].get("generated_text") or data[0].get("text")
if text:
return text.strip(), None
if isinstance(data, dict) and "generated_text" in data:
return data["generated_text"].strip(), None
if isinstance(data, str):
return data.strip(), None


# Fallback: try to str() the JSON
return str(data).strip(), None




def generate_caption(topic: str, style: str = "funny") -> str:
prompt = (
f"Write a short meme caption about '{topic}' in a {style} style. Keep it punchy, one or two short lines, good for a meme."
)
text, err = call_hf_text_model(prompt)
if err or not text:
# Fallback local captions (small deterministic list) if HF fails
fallback = [
"When you realize it's Monday again...",
"Me: *tries once*\nAlso me: *already an expert*",
"That face you make when Wi‑Fi dies",
"I asked for coffee, got an emotional support mug instead",
]
return fallback[hash(topic) % len(fallback)]
# Clean and shorten
text = text.replace("\n", " ").strip()
# Sometimes models produce long text; keep only first two short sentences / 120 chars
if len(text) > 140:
text = textwrap.shorten(text, width=120, placeholder="...")
st.markdown("Made with ❤ — MemeGen Pro. Deployed easily to Steamlit Cloud rfrom GitHub.")
