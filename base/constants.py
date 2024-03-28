from enum import StrEnum
from os import getenv
from dotenv import load_dotenv
load_dotenv()
# class EmbeddingsModels(StrEnum):

class MimeType(StrEnum):
    PDF = "application/pdf" # .pdf extension
    MP4 = "video/mp4" # .mp4 extension
    MOV = "video/quicktime"  # .mov extension
    MKV = "video/x-matroska"  # .mkv extension
    AVI = "video/x-msvideo"  # .avi extension
    JPEG = "image/jpeg"
    PNG = "image/png"
    TEXT = "text/plain"
    HTML = "text/html"
    JSON = "application/json"
    XML = "application/xml"
    CSV = "text/csv"
    MP3 = "audio/mpeg"

class TranscriptModels(StrEnum):
    LARGE = "openai/whisper-large-v3"
    MEDIUM = "openai/whisper-medium"
    SMALL = "openai/whisper-small"


DIRECTORY = './index'

CLOUD_CONFIG ={
    "provider": getenv("PROVIDER"),
    "access_key": getenv("ACCESS_KEY"),
    "container": getenv("CONTAINER"),
    "access_secret": getenv("ACCESS_SECRET"), 
    "default_endpoints_protocol": getenv("DEFAULT_ENDPOINTS_PROTOCOL"),
    "endpoint_suffix": getenv("ENDPOINT_SUFFIX"),
    "region": getenv("REGION")
}

CONNECTION_STRING = f"DefaultEndpointsProtocol={CLOUD_CONFIG['default_endpoints_protocol']};" \
                     f"AccountName={CLOUD_CONFIG['access_key']};" \
                     f"AccountKey={CLOUD_CONFIG['access_secret']};" \
                     f"EndpointSuffix={CLOUD_CONFIG['endpoint_suffix']}"

TEMPAUDIOFILE = 'tempAudio.wav'
KEYS = [   "transaction_key", "request_id", "sha256", "created",
            "models", "warnings", "model_info", "summary_info", "words",
            "search", "confidence", "punctuated_word", "speaker", "speaker_confidence", "summaries",
            "entities", "translations", "topics", "detected_language",
            "utterances", "summary"]