import os
import json
import httpx
from bson import ObjectId
from io import BufferedReader 
from typing import Tuple
from dotenv import load_dotenv, find_dotenv
from base.util import file_finder 
from base.constants import MimeType, KEYS, TEMPAUDIOFILE

from deepgram import (
    DeepgramClientOptions, 
    DeepgramClient, 
    PrerecordedOptions, 
    FileSource
)
# from txtai.pipeline import Transcription
from moviepy.editor import VideoFileClip
class VideoProcessor:
    def __init__(self, verbose:bool = False):
        find_dotenv()
        load_dotenv()
        DEEPGRAM_API_KEY = str(os.getenv("DEEPGRAM_API_KEY"))
        self.videoData: list = list()
        self.videos: list = list()
        
        config: DeepgramClientOptions = DeepgramClientOptions(verbose=verbose)
        self.deepgram: DeepgramClient = DeepgramClient(DEEPGRAM_API_KEY, config)
        
        print(" Deepgram Connection Estabilised!!")

    def __set_video_data(self, name: str, transcription: str ,duration: float, video: bytes):
        uid = ObjectId()
        
        videoDataObj = {
            "_id" : uid,
            "text": name + ' ' + transcription,
        }
        self.videoData.append(videoDataObj)
        
        videoObj = {
            "_id": uid,
            "name": name,
            "mime_type": MimeType.MP4,
            "file": video,
            "seconds": duration
        }
        self.videos.append(videoObj)
    
    def clear(self) -> bool:
        try:
            self.videoData.clear()
            self.videos.clear()
            return True
        except Exception as e:
            print(f" {e}")
            return False
    

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
        with open(videoPath, 'rb') as file:
            videoBytes = file.read()
        self.deepgram_transcribe(videoName, videoBytes)    
    
    
    def extract_data(self, videoName: str, video: BufferedReader) -> Tuple[bytes, bytes]:
        try:
            # Extracting bytes from the FileStorage object
            videoBytes = video.read()

            with open(videoName, "wb") as temp_file:
                temp_file.write(videoBytes)

            video_clip = VideoFileClip(videoName)
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(TEMPAUDIOFILE)
            
            with open(TEMPAUDIOFILE, "rb") as audio:
                audioBuffer = audio.read()

            return audioBuffer, videoBytes
            
        except Exception as e:
            print("Error during audio extraction:", e)
            return None


    def deepgram_transcribe(self, videoName: str, video: BufferedReader):
        
        audioFileBuffer, videoBytes = self.extract_data(videoName, video)
    
        payload: FileSource = {"buffer": audioFileBuffer}
        OPTIONS = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
            utterances=True,
            punctuate=True,
            diarize=True)
        fileResponse = self.deepgram.listen.prerecorded.v("1").transcribe_file(payload, OPTIONS, timeout=httpx.Timeout(300.0, connect=10.0))
        res = fileResponse.to_json()
        res = json.loads(res)
        self.__purge_keys(res)
        response = self.__fmt(res)  
        self.__set_video_data(videoName, response["transcript"], response["duration"], videoBytes)
        os.remove(videoName)
        os.remove(TEMPAUDIOFILE)

        print(" Video Processed!")

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