import os
import pymongo.errors
from io import BytesIO  
from typing import Tuple
from bson import ObjectId
from base import MimeType
from dotenv import load_dotenv
from gridfs import GridFS, GridOut
from pymongo.mongo_client import MongoClient

class Database:
    def __init__(self):
        try:
            load_dotenv()
            self.client = MongoClient(str(os.getenv("URI")))
            
            self.dbName = os.getenv("DB_NAME")
            
            self.db = self.client[self.dbName]
            self.fs = GridFS(self.db)
            
            self.client.admin.command('ping')
            print(f" MongoDB Connection Estabilished!!\n {self.dbName.upper()} server pinged.")
        
        except Exception as e:
            print(e)
    
    def batch_insert(self, data: list) -> bool:
        """
        Inserts file objects (Dicts of converted data)
        """
        try:
            
            files = [
                self.fs.put(ele.pop("file"), _id=ele.pop("_id"), filename=ele.pop("name"), mime_type=ele.pop("mime_type"), metadata=ele)
            for ele in data
            ]
            
            print(f" Successfully inserted {len(data)} files.")
            return True
        
        except pymongo.errors.PyMongoError as pe:
            print(f" Error inserting documents: {pe}")
            return False
        
    def insert(self, data:dict) -> bool:
        """
        Inserts a file object(Dicts of converted data)
        """
        try:
            file  = data.pop("file")
            name = data.pop("name")
            uid = data.pop("_id")
            mime_type = data.pop("mime_type")
            self.fs.put(file, _id=uid, filename=name, mime_type=mime_type, metadata=data)
            
            print(f" Successfully inserted {name}.")
            return True
        
        except pymongo.errors.PyMongoError as pe:
            print(f" Error inserting documents: {pe}")
            return False
    
    def delete(self, id: ObjectId) -> bool:
        try:
            # Check if the file exists in GridFS
            if self.fs.exists({"_id": id}):
                # Delete the file from GridFS
                self.fs.delete(id)
                return True
            else:
                print(f"File with id {id} not found in GridFS.")
                return False
        except pymongo.errors.PyMongoError as e:
            print(f"Error deleting file from GridFS: {e}")
            return False

    def delete_database(self):
        try:
            self.client.drop_database(self.dbName)
            print(f" Database '{self.dbName}' has been successfully deleted.")
        except Exception as e:
            print(f" An error occurred while deleting the database: {e}")

    def retrieve_results(self, ids: list[ObjectId]) -> list[dict]:
        try:
            files = []
            for uid in ids:
                file = self.fs.find_one({"_id": uid})
                if file:
                    file_data = {
                        "_id": str(file._id),
                        "name": file.filename,
                        "size": int(file.length),
                        "metadata": file.metadata,
                        "mime_type": file.mime_type
                    }
                    files.append(file_data)
                else:
                    print(f"File with ObjectId {uid} not found in Database.")
            return files
        
        except Exception as e:
            print(f"Error: {e}")


    def retrieve_file(self, id: ObjectId) -> Tuple[str, MimeType, BytesIO]:
        try:
            file = self.fs.find_one({"_id": id})  # Fetch the file object
            if file:
                file_data = BytesIO(file.read())
                return file.filename, MimeType(file.mime_type), file_data 
            else:
                print(f"File with ObjectId {id} not found.")
                return None
        except Exception as e:
            print(f"Error: {e}")

    def get_all_file_ids(self) ->list[ObjectId]:
        try:
            file_ids = [file._id for file in self.fs.find()]
            return file_ids
        except Exception as e:
            print(e)

    def __download(self, file: GridOut, folderPath: str):
        filePath = folderPath + file.filename  
        
        with open(filePath, 'wb') as f:
            obj = self.fs.get(file._id)
            f.write(obj.read())
        
        print(f" File {file.filename} downloaded successfully.")