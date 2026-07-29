ALLOWED_MIME_TYPES = {
    'image/png',
    'image/jpeg',
    'image/jpg',
    'application/pdf',
}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB


def validate_upload(content_type: str | None, file_size: int) -> None:
    from app.core.exceptions import ConflictError

    if content_type and content_type not in ALLOWED_MIME_TYPES:
        raise ConflictError(f'Invalid file type: {content_type}. Allowed: PNG, JPG, PDF')

    if file_size > MAX_FILE_SIZE:
        raise ConflictError(f'File too large: {file_size} bytes. Max: 20MB')
