from typing import List
from src.ingestion.gmail.gmail_auth import get_gmail_service
from datetime import datetime, timedelta
from src.schema.email_object import EmailObject,Metadata,Intent,Content,NormalizedContent
from src.ingestion.extract_raw import extract_raw_bodies
from src.ingestion.classifier import classify_email
from src.ingestion.parser_cleaner import parse_to_header,clean_html,remove_thread_history,strip_signature,split_paragraphs
from src.ingestion.utils import normalize_text


def read_emails_in_date_range(start_date: str, end_date: str) -> List[EmailObject]:
    service = get_gmail_service()

    start = datetime.strptime(start_date, "%Y-%m-%d") - timedelta(days=1)
    end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
    query = f"after:{start.strftime('%Y/%m/%d')} before:{end.strftime('%Y/%m/%d')}"

    results = []
    response = service.users().messages().list(
        userId="me", q=query, maxResults=100
    ).execute()

    for m in response.get("messages", []):
        msg = service.users().messages().get(
            userId="me", id=m["id"], format="full"
        ).execute()
        internal_ts = int(msg["internalDate"])

        headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
        labels = msg.get("labelIds", [])

        plain, html, attachments = extract_raw_bodies(
            service, m["id"], msg["payload"]
        )

        email_type = classify_email(headers, plain, html, labels)

        if email_type == "newsletter" and html:
            cleaned = clean_html(html)
            cleaned = remove_thread_history(cleaned)
            cleaned = strip_signature(cleaned)
            cleaned = normalize_text(cleaned)
            cleaned = NormalizedContent(text=cleaned,paragraphs=split_paragraphs(cleaned))
            
        else:
            cleaned = plain or clean_html(html or "")
            cleaned = remove_thread_history(cleaned)
            cleaned = strip_signature(cleaned)
            cleaned = normalize_text(cleaned)
            cleaned = NormalizedContent(text=cleaned,paragraphs=split_paragraphs(cleaned))

        email = EmailObject(
            message_id=msg["id"],
            thread_id=msg["threadId"],
            metadata=Metadata(
                sender=headers.get("From", ""),
                to=parse_to_header(headers.get("To")),
                subject=headers.get("Subject", ""),
                date=headers.get("Date", ""),
                labels=labels,
                internal_timestamp=internal_ts
            ),
            intent=Intent(
                email_type=email_type,
                source="heuristic",
                confidence=0.6
            ),
            content=Content(
                cleaned_text=cleaned
            ),
            attachments=attachments
        )

        results.append(email)

    return results

if __name__ == "__main__":
    print(read_emails_in_date_range("2026-02-1","2026-02-5"))