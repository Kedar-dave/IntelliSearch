from io import BufferedReader
import shutil
import os
import json
from collections import Counter
from dotenv import load_dotenv
from moviepy.editor import VideoFileClip

from txtai.pipeline import Transcription

from deepgram import DeepgramClientOptions, DeepgramClient, PrerecordedOptions, FileSource
from base.util import *

TEMPAUDIOFILE = 'temp.mp3'
KEYS = [
            "transaction_key", "request_id", "sha256", "created",
            "models", "warnings", "model_info", "summary_info", "words",
            "search", "confidence", "punctuated_word", "speaker", "speaker_confidence", "summaries",
            "entities", "translations", "topics", "detected_language",
            "utterances", "summary"]
DEEPGRAM_API_KEY = os.environ.get("DG_API_KEY")
class VideoProcessor:
    def __init__(self):
        load_dotenv()
        self.videoData: list = list()
        self.transcribe = Transcription(gpu=True)

        config: DeepgramClientOptions = DeepgramClientOptions(verbose=False)
        self.deepgram: DeepgramClient = DeepgramClient(
            DEEPGRAM_API_KEY, config)
        self.options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
            utterances=True,
            punctuate=True,
            diarize=True)

    def __del__(self):
        try:
            os.remove("temp.mp3")
        except:
            pass


    def __set_video_data(self, name: str, transcription: str,
                         keywords: list,
                         duration: float) -> None:
        docDict = {
            "type": "video",
            "name": name,
            "transcription": transcription,
            "words": dict(Counter(keywords)),
            "duration": duration
        }
        self.videoData.append(docDict)

    def local_batch_to_text(self, videoFolderPath: str):
        """
        Converts a folder of videos to textual data
        Parameters:
            pdfFolderPath: Path of the document folder
        """
        videoFiles = file_finder(videoFolderPath, (".mp4", ".mov", ".mkv", ".avi"))
        print(f" Number of Files Found:{len(videoFiles)}")
        for videoName in videoFiles:
            self.local_to_text(videoName,videoFolderPath)

    def local_to_text(self, videoName: str,videoFolderPath: str):
        videoPath = os.path.join(videoFolderPath, videoName)

        with VideoFileClip(videoPath) as video:
            audioClip = video.audio
            audioClip.write_audiofile(TEMPAUDIOFILE ,codec="mp3", verbose=False, logger=None)
            with open(TEMPAUDIOFILE, "rb") as file:
                audioFileBuffer = file.read()
            transcript = self.deepgram_transcribe(audioFileBuffer)
            keywords = transform_text(transcript["transcript"])
            self.__set_video_data( videoName, transcript["transcript"], keywords, transcript["duration"])
            os.remove(os.path(TEMPAUDIOFILE))
        

    def deepgram_transcribe(self, audioFileBuffer: BufferedReader) -> dict:

        payload: FileSource = {"buffer": audioFileBuffer}

        fileResponse = self.deepgram.listen.prerecorded.v(
            "1").transcribe_file(payload, self.options)

        res = fileResponse.to_json()
        res = json.loads(res)
        self.__purge_keys(res)
        response = self.__fmt(res)
        return response

    def __purge_keys(self, data: dict):

        if isinstance(data, dict):
            for key in list(data.keys()):
                if key == 'channels' and isinstance(data[key], int):
                    del data[key]
                elif key in KEYS:
                    del data[key]
                else:
                    self.__purge_keys(data[key])
        elif isinstance(data, list):
            for item in data:
                self.__purge_keys(item)

    def __fmt(self, data: dict) -> dict:

        duration = data.get("metadata", {}).get("duration", 0)
        transcript = data.get("results", {}).get("channels", [{}])[
            0].get("alternatives", [{}])[0].get("transcript", "")
        transcript = transcript.replace('\n', ' ')
        response = {
            "duration": duration,
            "transcript": transcript,
        }
        return response