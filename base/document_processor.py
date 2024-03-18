import os
from io import BufferedReader
import PyPDF2
import pickle
from .mime_types import MimeType
from bson import ObjectId

from base.util import file_finder,text_cleaning
class DocumentProcessor:

    def __init__(self):
        self.pdfData: list = list()
        self.pdfList: list = list()

    def __set_pdf_data(self, name: str, text: str, pdf, pages: int ):

        uid = ObjectId()
        pdfDataObj = {
            "_id": uid,
            "text": text,
        }
        pdfObj = {
            "_id": uid,
            "name": name,
            "mime_type": MimeType.PDF, 
            "file": pdf,
            "pages": pages
        }
        self.pdfList.append(pdfObj)
        self.pdfData.append(pdfDataObj)

    def local_batch_to_text(self, pdfFolderPath: str):
        """
        Converts a folder of documents to textual data
        Parameters:
            pdfFolderPath: Path of the document folder
        """
        pdfFiles = file_finder(pdfFolderPath, (".pdf"))
        print(f" Number of Files Found:{len(pdfFiles)}")
        for pdfName in pdfFiles:
            self.local_to_text(pdfName, pdfFolderPath)

    def local_to_text(self,pdfName:str, pdfFolderPath:str):
        """
        Converts a single document to textual data
        Parameters:
            pdfName: Name of the pdf file along with its extension ex:( demo.pdf )
            pdfFolderPath: Path of the folder containing the document 
        """
        pdfPath = os.path.join(pdfFolderPath, pdfName)
        with open(pdfPath, "rb") as file:
            self.ocr(pdfName, file)        
    
    def ocr(self,pdfName: str, pdfFileBuffer: BufferedReader) -> bool:
        """
        Conversion of each page to text, converting pdf to binary
        """
        try:
            text = ""
            if pdfFileBuffer:
                pdf = pdfFileBuffer.read()
                pdfReader = PyPDF2.PdfReader(pdfFileBuffer)
                pages = len(pdfReader.pages)
                for pageNumber in range(pages):
                    page = pdfReader.pages[pageNumber]
                    text += page.extract_text()
            text = text_cleaning(text)
            self.__set_pdf_data(pdfName, text, pdf, pages)
            return True

        except Exception as e:
            print(f" {e}")
            return False
    
    def clear(self) -> bool:
        try:
            self.pdfData.clear()
            self.pdfList.clear()
            return True
        except Exception as e:
            print(f" {e}")
            return False
    
    def save_pdf(self,name:str):
        os.makedirs('./cache/', exist_ok=True)
        with open(f"./cache/{name}.pkl", "wb") as file:
            pickle.dump(self.pdfList,file)
    
    def load_pdf(self,name:str):
        data = list()
        with open(f"./cache/{name}.pkl", "rb") as file:
            data = pickle.load(file)
        for obj in data:
            self.pdfList.append(obj)
        print("Pdf Loaded")