from gmail_auth import get_gmail_service

service = get_gmail_service()

results = service.users().messages().list(
    userId="me",
    maxResults=5,
    labelIds=["INBOX"]
).execute()

messages = results.get("messages", [])

for msg in messages:
    msg_data = service.users().messages().get(
        userId="me",
        id=msg["id"]
    ).execute()

    headers = msg_data["payload"]["headers"]

    subject = next(h["value"] for h in headers if h["name"] == "Subject")
    sender = next(h["value"] for h in headers if h["name"] == "From")

    print("From:", sender)
    print("Subject:", subject)
    print("-" * 40)
