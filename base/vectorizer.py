import os
import shutil
from bson import ObjectId
from txtai.embeddings import Embeddings
from typing_extensions import Any, Tuple
from base.util import to_int,to_objectid
from base.constants import CLOUD_CONFIG, CONNECTION_STRING, DIRECTORY
from azure.storage.blob import BlobServiceClient

class Vectorizer:

    def __init__(self):
        try:
            
            self.embeddings = Embeddings({
                                        "path" : "sentence-transformers/all-mpnet-base-v2",
                                    })
        except Exception as e:
            print(f"Vectorizer Initialization Error:{e}")

    def count(self) ->  Any | int:
        return self.embeddings.count()

    def __load_local(self,name: str):
        """
        Loads an existing index from given location of folder
        """
        path = "./index/" + name
        self.embeddings.load(path)
        print(f" Local Index Loaded. { name = }")

    
    def __save_local(self,name: str):
        """
        Saves an existing index to given location of folder
        """
        os.makedirs('./index/', exist_ok=True)
        path = "./index/" + name
        self.embeddings.save(path)
        print(f" Index Saved Locally. { name = }")

    
    def save_cloud(self,name: str):
        try: 
            path = "./index/" + name + ".tar.xz" 
            self.embeddings.save(path=path, cloud=CLOUD_CONFIG)
            print(f" Index {name} uploaded to Azure.")
        except Exception as e:
            print(f" Index {name} upload to Azure Failed.\n {e}")

    def load_cloud(self,name: str):
        try:
            path = "./index/" + name + ".tar.xz"
            if self.embeddings.exists(cloud=CLOUD_CONFIG) == True:
                self.embeddings.load(path=path,cloud=CLOUD_CONFIG)
                print(f" Index {name} loaded from Azure.\n Num of Indexed Documents: {self.count()}")
        except Exception as e:
            print(f" Index {name} does not exist.\n {e}")

    def semantic_index(self, data) -> bool:
        """
        Appends index records as batch
        """
        try:
            dataList = [(to_int(doc.pop('_id')), doc, None) for doc in data]

            self.embeddings.upsert(dataList)
            return True

        except Exception as e:
            print(f" {e}")
            return False
        
    def delete_file(self, hex_id: ObjectId) -> bool:
        try:
            _id = to_int(hex_id)
            deletedIds = self.embeddings.delete([_id])  # Wrap the single ObjectId in a list
            print(f" File: {hex_id} Deleted")
            return True
            
        except Exception as e:
            print(f" {e}")
            return False

    def delete_index(self, name: str) -> bool:
        try:
            cloudServiceClient = BlobServiceClient.from_connection_string(CONNECTION_STRING)
            containerClient = cloudServiceClient.get_container_client(CLOUD_CONFIG["container"])
            for blob in containerClient.list_blobs():
                containerClient.delete_blob(blob.name)
    
            shutil.rmtree(DIRECTORY)

            print(f" Index: {name.upper()} deleted!!")
            return True        
        except FileNotFoundError:
            print(f"Directory '{DIRECTORY}' does not exist.")
            return False

        except OSError as e:
            print(f"Error occurred while deleting directory '{DIRECTORY}': {e}")
            return False

        except Exception as e:
            print(f" {e}")
            return False

    def semantic_search(self, query:str, limit:int = 50) -> Tuple[list[ObjectId], list[float]]:
        """
        Searches the index(es) for the given query and returns results as a lists of index, semantic similarity scores
        """
        searchNums = self.embeddings.search(query,limit)

        intIndices =[results[0] for results in searchNums]
        hexIndices = [to_objectid(ele) for ele in intIndices]        
        
        scores = [results[1] for results in searchNums]
        searchNums = [(id,score) for id, score in zip(hexIndices,scores)]
        
        return hexIndices, scores
