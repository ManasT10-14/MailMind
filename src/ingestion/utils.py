import base64
import re


def decode_base64(data):
    return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

def normalize_text(text: str) -> str:
    text = re.sub(r'[\u200B-\u200D\uFEFF]', '', text)


    text = text.replace('\xa0', ' ')

    text = re.sub(r'\s+', ' ', text)


    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()