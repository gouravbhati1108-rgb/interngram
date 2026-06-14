import bleach

ALLOWED_TAGS = ["p", "br", "strong", "em", "ul", "ol", "li"]
ALLOWED_ATTRIBUTES: dict[str, list[str]] = {}


def sanitize_html(text: str) -> str:
    return bleach.clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
