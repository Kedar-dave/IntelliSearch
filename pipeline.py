from base import FileType
from io import BufferedReader, BytesIO
from bson import ObjectId
from typing import Tuple
from base import DocumentProcessor, Vectorizer, Database

#TODO
class Pipeline():
    
    def __init__(self, indexName: str):
        self.indexName = indexName
        self.doc = DocumentProcessor()
        self.vec = Vectorizer()
        self.db = Database()
        self.vec.load_cloud(self.indexName)

    def insert_pdf(self, pdfName: str, pdfFile: BufferedReader) -> bool:
        try:
            self.doc.ocr(pdfName, pdfFile)
            self.vec.semantic_index(self.doc.pdfData)
            self.vec.save_cloud(self.indexName)
            self.db.insert(self.doc.pdfList[0])
            self.clear_processor_data() 

            return True
        
        except Exception as e:
            print(f" {e}")
            return False

    def batch_insert_pdf(self, pdfNames: list[str], pdfFiles: list[BufferedReader]) -> bool:
    
        try:
            for name, file in zip(pdfNames, pdfFiles):
                self.doc.ocr(name, file)
            self.vec.semantic_index(self.doc.pdfData)
            self.vec.save_cloud(self.indexName)
            self.db.insert(self.doc.pdfList)
            self.clear_processor_data()
            
            return True
        
        except Exception as e:
            print(f" {e}")
            return False
        
    def search(self, query: str, limit: int = 50) -> Tuple[list,list]:
        try:
            indices, scores = self.vec.semantic_search(query, limit)
            print(indices)
            files = self.db.retrieve_results(indices)

            return files, scores

        except Exception as e:
            print(f" {e}")
    
    def delete(self, _id: ObjectId) -> bool:
        try:
            prev = self.vec.count()
            areFilesDeleted: bool =  self.db.delete(_id) and self.vec.delete_index(_id)
            if areFilesDeleted:
                self.vec.save_cloud(self.indexName)
                if prev - self.vec.count() == 1:
                    return areFilesDeleted
            else:
                return False
        except Exception as e:
            print(f" {e}")
            return False
        
    def get_file(self, id: ObjectId) -> Tuple[str, FileType, BytesIO]:
        
        return self.db.retrieve_file(id)
    
    def clear_processor_data(self):
        self.doc.pdfList.clear()
        self.doc.pdfData.clear()