from bs4 import BeautifulSoup
from typing import List
import re

THREAD_MARKERS = [
    "-----Original Message-----",
    "On .* wrote:",
    "From:",
    "Sent:",
]

def parse_to_header(to_header: str | None) -> List[str]:
    if not to_header:
        return []
    return [addr.strip() for addr in to_header.split(",")]


def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["style", "script", "head", "meta", "noscript"]):
        tag.decompose()

    for img in soup.find_all("img"):
        img.decompose()

    text = soup.get_text(separator="\n")
    lines = [l.strip() for l in text.splitlines() if 40 < len(l.strip()) < 300]

    return "\n".join(lines[:15])

def remove_thread_history(text: str) -> str:
    for marker in THREAD_MARKERS:
        split = re.split(marker, text, maxsplit=1, flags=re.IGNORECASE)
        text = split[0]
    return text

SIGNATURE_MARKERS = [
    "sent from my",
    "best regards",
    "thanks,",
    "warm regards",
    "confidentiality notice",
]

def strip_signature(text: str) -> str:
    lines = text.splitlines()
    cleaned = []

    for line in lines:
        if any(m in line.lower() for m in SIGNATURE_MARKERS):
            break
        cleaned.append(line)

    return "\n".join(cleaned)



def split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in text.split("\n\n") if p.strip()]
