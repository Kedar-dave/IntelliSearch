import os
import bson
import json
import torch
import PyPDF2
import pickle
from icecream import ic
from bson import ObjectId
from bson.binary import Binary
from dotenv import load_dotenv
from collections import Counter
from multipledispatch import dispatch
from torch.multiprocessing import Pool
from txtai.embeddings import Embeddings
from moviepy.editor import VideoFileClip
# from db import MongoDB
from util import file_finder, text_cleaning, transform_text
from deepgram import DeepgramClientOptions, DeepgramClient, PrerecordedOptions, FileSource
# import streamlit as st
__author__ = "Kedar"
__version__ = "0.1"

load_dotenv()
torch.device("cuda:0")
class VideoProcessor:
    def __init__(self):
        self.videoData: list = list()
        DEEPGRAM_API_KEY = os.environ.get("DG_API_KEY")
        config: DeepgramClientOptions = DeepgramClientOptions(verbose=False)
        self.deepgram: DeepgramClient = DeepgramClient(
            DEEPGRAM_API_KEY, config)
        self.options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
            utterances=True,
            punctuate=True,
            diarize=True)
        self.KEYS = [
            "transaction_key", "request_id", "sha256", "created",
            "models", "warnings", "model_info", "summary_info", "words",
            "search", "confidence", "punctuated_word", "speaker", "speaker_confidence", "summaries",
            "entities", "translations", "topics", "detected_language",
            "utterances", "summary"]
    def __del__(self):
        try:
            os.remove("temp.mp3")
        except:
            pass

    # @st.cache_data streamlitcode
    def get_video_data(self) -> list:
        return self.videoData

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

    def video_to_text_batch(self, videoFolderPath: str) -> bool:
        # convertbar = st.progress( streamlitcode
        #     0, text="Converting Videos to text. Please Wait...") streamlitcode
        videoFiles = file_finder(
            videoFolderPath, (".mp4", ".mov", ".mkv", ".avi"))
        # counter = 0 streamlitcode
        # numOfFiles = len(videoFiles) streamlitcode
        for videoName in videoFiles:
            self.video_to_text(videoName,videoFolderPath)
        #     counter += 1 streamlitcode
        #     status = counter/numOfFiles streamlitcode
        #     convertbar.progress( streamlitcode
        #         status, text="Converting Videos to text. Please Wait...") streamlitcode
        # convertbar.empty() streamlitcode

    def video_to_text(self, videoName:str,videoFolderPath:str="../data") -> bool:
        videoPath = os.path.normpath(os.path.join(videoFolderPath, videoName))
        ic(videoPath)

        with VideoFileClip(videoPath) as video:
            audioClip = video.audio
            audioClip.write_audiofile("temp.mp3",codec="mp3", verbose=False, logger=None)
            transcript = self.__transcribe("temp.mp3")
            keywords = transform_text(transcript["transcript"])
            self.__set_video_data(
                videoName, transcript["transcript"], keywords, transcript["duration"])
        

    def __transcribe(self, audioFile: str) -> dict:

        with open(audioFile, "rb") as file:
            bufferData = file.read()

        payload: FileSource = {"buffer": bufferData}

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
                elif key in self.KEYS:
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
    
class DocumentProcessor:

    def __init__(self):
        self.pdfData: list = list()
        # self.db = MongoDB()
        # self.db.clear_collection()
    # @st.cache_data streamlitcode
    def get_pdf_data(self) -> list:
        return self.pdfData

    def __set_pdf_data(self, name: str, text: str, pdf: bson.binary.Binary, pages: int, ):
        
        pdfDict = {
            "_id": str(ObjectId()),
            "name": name,
            "type": "document",
            "text": text,
            "pdf": pdf,
            "pages": pages
        }
        # self.db.insert_document(pdfDict)
        self.pdfData.append(pdfDict)

    def check_redundancy(self):
        pass
    @dispatch(str)
    def to_text(self, pdfFolderPath: str):
        """
        Converts a folder of documents to textual data
        Parameters:
            pdfFolderPath: Path of the document folder
        """
        # convertbar = st.progress( streamlitcode
        #     0, text="Converting PDFs to text. Please Wait...") streamlitcode
        pdfFiles = file_finder(pdfFolderPath, (".pdf"))
        # numOfFiles = len(pdfFiles) streamlitcode
        # counter = 0 streamlitcode
        print(f"Number of files:{len(pdfFiles)}")
        for pdfName in pdfFiles:
            self.to_text(pdfName, pdfFolderPath)
        #     counter += 1 streamlitcode
        #     status = counter/numOfFiles streamlitcode
        #     convertbar.progress( streamlitcode
        #         status, text='Converting PDFs to text. Please Wait...') streamlitcode
        # convertbar.empty() streamlitcode
        print(f"Files Converted:{len(self.pdfData)}")


    @dispatch(str,str)
    def to_text(self,pdfName:str, pdfFolderPath:str):
        """
        Converts a single document to textual data
        Parameters:
            pdfName: Name of the pdf file along with its extension ex:( demo.pdf )
            pdfFolderPath: Path of the folder containing the document 
        """
        
        for doc in self.pdfData:
            if doc["name"] == pdfName:
                break
        pdfPath = os.path.join(pdfFolderPath, pdfName)
        text, pages, pdf = self.__ocr(pdfPath)
        text = text_cleaning(text)
        self.__set_pdf_data(pdfName, text, pdf, pages)
    
    def __ocr(self, pdfPath: str):
        text = ""
        with open(pdfPath, "rb") as file:
            pdfBinary = Binary(file.read())
            pdfReader = PyPDF2.PdfReader(file)
            pages = len(pdfReader.pages)
            for pageNumber in range(pages):
                page = pdfReader.pages[pageNumber]
                text += page.extract_text()
        return text, pages, pdfBinary
    
    def save_pdf(self,name:str):
        os.makedirs('./cache/', exist_ok=True)
        with open(f"./cache/{name}.pkl", "wb") as file:
            pickle.dump(self.pdfData,file)
    
    def load_pdf(self,name:str):
        data = list()
        with open(f"./cache/{name}.pkl", "rb") as file:
            data = pickle.load(file)
        for obj in data:
            self.pdfData.append(obj)
        print("Pdf Loaded")


class Vectorizer:

    def __init__(self, data):
        self.embeddings = Embeddings({
                "path": "sentence-transformers/all-mpnet-base-v2",
            })
        
        self.pdf = data
    def add(self, data):
        for doc in data:
            pos = str(doc["_id"])
            self.embeddings.upsert((pos,doc,None))
    
    def load_index(self,name:str):
        path = "./index/" + name
        self.embeddings.load(path)
        print("Index Loaded")
    def save_index(self,name:str):
        os.makedirs('./index/', exist_ok=True)
        path = "./index/" + name
        self.embeddings.save(path)
    def index(self):
        self.embeddings.index(self.pdf)
    def semantic_search(self, query:str, limits:int = 50, cutoff:float = 0.0):
        searchNums = self.embeddings.search(query,limits)

        # indices =[results[0] for results in searchNums]
        # scores = [results[1] for results in searchNums]
        
        # print("Name\t\t: Similarity Index : Index Number")
        # print("-"*50)
        # for res in searchNums:
            # ic(res[0])
            # if res[1]> cutoff:
                # print(f"{self.pdf[res[0]]['name'][:20].ljust(20)} : {res[1]:0,.3f} : {res[0]}")
        return searchNums
    
    

    def process_document(self, doc: dict, query_lower: str, exact_phrase: bool) -> dict:
        text_lower = doc.get('text', '').lower()  # For documents
        transcription_lower = doc.get(
            'transcription', '').lower()  # For videos

        if exact_phrase:
            if (doc['type'] == 'document' and query_lower == text_lower) or \
                    (doc['type'] == 'video' and query_lower == transcription_lower):
                return doc
        else:
            # Split the query into individual words
            query_words = query_lower.split()
            # Check if all query words are present in the document's text or transcription
            if all(word in text_lower for word in query_words) and doc['type'] == 'document':
                return doc
            elif all(word in transcription_lower for word in query_words) and doc['type'] == 'video':
                return doc

        return None