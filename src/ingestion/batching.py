from src.schema.email_object import EmailObject
from typing import List,Dict
from collections import defaultdict

def batch_by_intent(emails: List[EmailObject]) -> Dict[str, List[EmailObject]]:
    batch = defaultdict(list)

    for email in emails:
        intent = email.intent.email_type
        batch[intent].append(email)

    return dict(batch)

def batch_by_sender_and_intent(
    emails: List[EmailObject],
) -> Dict[str, Dict[str, List[EmailObject]]]:

    batch = defaultdict(lambda: defaultdict(list))

    for email in emails:
        sender = email.metadata.sender
        intent = email.intent.email_type
        batch[sender][intent].append(email)

    return {sender: dict(intents) for sender, intents in batch.items()}
    


def batch_by_sender_and_time(
    emails: List[EmailObject],
) -> Dict[str, List[EmailObject]]:

    batch = defaultdict(list)


    for email in emails:
        sender = email.metadata.sender
        batch[sender].append(email)

    for sender, sender_emails in batch.items():
        sender_emails.sort(
            key=lambda e: int(e.metadata.internal_timestamp),
            reverse=False 
        )

    return dict(batch)

def get_batch(emails: List[EmailObject], strategy: str):
    if strategy == "intent":
        return batch_by_intent(emails)

    if strategy == "sender_intent":
        return batch_by_sender_and_intent(emails)

    if strategy == "sender_time":
        return batch_by_sender_and_time
    raise ValueError(f"Unknown batching strategy: {strategy}")

