import os
import time
import psutil
from bson import ObjectId
from dotenv import load_dotenv
from base import (
    DocumentProcessor, 
    VideoProcessor, 
    Vectorizer, 
    Database)
from base.constants import MimeType
from flask import (
    Flask, 
    request, 
    jsonify, 
    send_file,
    render_template)


# Create a Flask application
app = Flask(__name__)
load_dotenv()
docProcessor = DocumentProcessor()
vidProcessor = VideoProcessor(verbose=False)
vectors = Vectorizer()
db = Database()

INDEXNAME = str(os.getenv("INDEX"))
vectors.load_cloud(INDEXNAME)

app = Flask(__name__)


@app.route('/api/insert', methods=['POST'])
def insert():
    global start
    try:
        start = time.time()  
        files = request.files.getlist('files[]') 
        names = request.form.getlist('names[]')  
        mimeTypes = request.form.getlist('mime_types[]')  
        collectionTypes = set(mimeTypes)
        
        if len(files) != len(names) or len(files) != len(mimeTypes):
            raise ValueError("File data lists have different lengths.")
        
        for file, name, mime_type in zip(files, names, mimeTypes):
            match mime_type:
                case MimeType.PDF:
                    docProcessor.ocr(name, file)
                case (MimeType.MP4, MimeType.AVI, MimeType.MOV, MimeType.MKV):
                    vidProcessor.deepgram_transcribe(name, file)
                case _:
                    continue

        isProcessed: bool = False
        isPdfProcessed: bool = False
        isVidProcessed: bool = False
        if collectionTypes.intersection([MimeType.PDF]):
            if vectors.semantic_index(docProcessor.pdfData): 
                if db.batch_insert(docProcessor.pdfs): 
                    docProcessor.clear()
                    isPdfProcessed = True
        if collectionTypes.intersection([MimeType.MP4, MimeType.AVI, MimeType.MOV, MimeType.MKV]):
             if vectors.semantic_index(vidProcessor.videoData): 
                if db.batch_insert(vidProcessor.videos): 
                    vidProcessor.clear()
                    isVidProcessed = True

        isProcessed = isPdfProcessed or isVidProcessed
        if isProcessed:
            vectors.save_cloud(INDEXNAME)
            return jsonify({'msg': f'{len(files)} files Uploaded \nFile Names: {names}'}), 200

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500


@app.route('/api/delete', methods=['POST'])
def delete():
    global start
    try:
        start = time.time()
        data = request.json
        _id = ObjectId(data.get('id'))
        prevCount = vectors.count()
        ifFilesDeleted: bool = db.delete(_id) and vectors.delete_file(_id)
        currCount = vectors.count() 
        if ifFilesDeleted and ((prevCount - currCount)==1):
            vectors.save_cloud(INDEXNAME)
            end = time.time()
            intervalTime = end - start
            return jsonify({"msg": f" Document with id:{_id} Deleted"}), 200
        else:

            return jsonify({"msg": f"Document with id:{_id} not Found"}), 404
    except Exception as e:
        print(f" {e}")

@app.route('/api/search', methods=['POST'])
def search():
    """
    file_id is a list of bson ObjectIds
    """
    global start
    try:
        start = time.time()
        data = request.json
        query = data.get('query')
        limit = int(data.get('limit'))          
        hexIndices, scores = vectors.semantic_search(query, limit)
        files = db.retrieve_results(hexIndices)
        end = time.time()
        searchTime = float("{:.4f}".format(end - start))
        if files:
            return jsonify({'files': files, 'scores':scores, 'searchTime': searchTime}), 200
        else:
            return "Files not found", 404
        
    except Exception as e:
        return print(str(e)), 500


@app.route('/api/getfile', methods=["POST"])
def serve_file():
    global start
    try:
        start = time.time()
        data = request.json
        _id = ObjectId(data.get('file_id'))
        filename, mime_type, file  = db.retrieve_file(_id)
       
        response = send_file(
                        path_or_file= file, 
                        mimetype=mime_type, 
                        as_attachment=False, 
                        download_name=filename)
        
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        
        return response
        
    except Exception as e:
        return jsonify({'error': 'An error occurred while serving the file'}), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.after_request
def log_usage(response):
    global start
    try:
        process = psutil.Process()
        
        # Sample CPU and memory usage before and after the request processing
        cpu_before, mem_before = get_usage(process)
        response_time = time.time() - start
        cpu_after, mem_after = get_usage(process)
        
        # Calculate maximum CPU and memory usage during the request
        max_cpu_percent = max(cpu_before, cpu_after)
        max_mem_percent = max(mem_before, mem_after)
        
        print(f"Response Time: {response_time} seconds")
        print(f"CPU Usage: {max_cpu_percent}%")
        print(f"Memory Usage: {max_mem_percent} MB")
        
    except Exception as e:
        print("Error occurred while logging usage:", e)
    
    return response

def get_usage(process: psutil.Process):
    cpu_percent = process.cpu_percent()
    mem = process.memory_info()
    mem_percent = mem.rss / (1024 ** 2)  # Converting bytes to MB
    return cpu_percent, mem_percent

if __name__ == '__main__':
    port_env = int(os.getenv("PORT"))
    PORT = port_env if port_env else 9000
    host_env = os.getenv("HOST")
    HOST = host_env if host_env else '0.0.0.0'
    debug_env = bool(os.getenv("DEBUG"))
    DEBUG = debug_env if debug_env else False
    app.run(host=HOST,port=PORT, debug=DEBUG)
    # app.run(port=5000, debug=True)
    # Use Gunicorn to serve the Flask app with multiple workers
    # gunicorn -w 4 -b 0.0.0.0:5000 your_app_module:app

    # -w 4: Specifies the number of worker processes. Adjust this number according to your server's CPU cores.
    # -b 0.0.0.0:5000: Specifies the host and port to bind to.
    # your_app_module:app: Specifies the module and app instance to run. Replace your_app_module with the name of your Python module containing the Flask app.