def classify_email(headers, plain, html, labels):
    if "CATEGORY_PROMOTIONS" in labels:
        return "newsletter"
    if "CATEGORY_SOCIAL" in labels:
        return "notification"
    if html and len(html) > 5000:
        return "newsletter"
    if plain and len(plain) < 300:
        return "transactional"
    return "personal"

# "newsletter","notification","transactional","personal"