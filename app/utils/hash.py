import hashlib

def hash_text(text: str) -> str:
    """
    Create a stable SHA256 hash for a text chunk.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
