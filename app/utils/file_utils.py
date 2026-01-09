import hashlib


def calculate_sha256(file_content: bytes) -> str:
    """Calculate SHA256 checksum of file content"""
    return hashlib.sha256(file_content).hexdigest()
