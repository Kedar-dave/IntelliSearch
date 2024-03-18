from enum import StrEnum

class MimeType(StrEnum):
    PDF = "application/pdf"
    VIDEO = "application/video"
    JPEG = "image/jpeg"
    PNG = "image/png"
    TEXT = "text/plain"
    HTML = "text/html"
    JSON = "application/json"
    XML = "application/xml"
    CSV = "text/csv"
    MP3 = "audio/mpeg"