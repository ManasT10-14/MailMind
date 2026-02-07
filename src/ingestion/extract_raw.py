import base64
import os
from src.ingestion.utils import decode_base64
ATTACHMENT_DIR = "attachments"
os.makedirs(ATTACHMENT_DIR, exist_ok=True)

def extract_raw_bodies(service, msg_id, payload):
    plain_text = None
    html_text = None
    attachments = []

    def walk(parts):
        nonlocal plain_text, html_text

        for part in parts:
            mime = part.get("mimeType")
            filename = part.get("filename")

            if filename and part["body"].get("attachmentId"):
                att_id = part["body"]["attachmentId"]
                att = service.users().messages().attachments().get(
                    userId="me", messageId=msg_id, id=att_id
                ).execute()

                data = base64.urlsafe_b64decode(att["data"])
                path = os.path.join(ATTACHMENT_DIR, filename)

                with open(path, "wb") as f:
                    f.write(data)

                attachments.append({"filename": filename, "path": path})

            elif part["body"].get("data"):
                data = decode_base64(part["body"]["data"])
                if mime == "text/plain":
                    plain_text = data
                elif mime == "text/html":
                    html_text = data

            if part.get("parts"):
                walk(part["parts"])

    if payload.get("parts"):
        walk(payload["parts"])
    elif payload.get("body", {}).get("data"):
        mime = payload.get("mimeType")
        data = decode_base64(payload["body"]["data"])
        if mime == "text/plain":
            plain_text = data
        elif mime == "text/html":
            html_text = data

    return plain_text, html_text, attachments

