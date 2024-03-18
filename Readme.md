# A Project which applies semantic searching capabilities to a given dataset of pdfs

This project implements a Flask-based web application that utilizes semantic searching capabilities to search through a dataset of PDF files. It allows users to upload PDF files, perform searches based on semantic similarity, delete documents, and retrieve documents from the dataset. MongoDB is used to store documents and their metadata.

## Features

- **Upload PDF Files:** Users can upload PDF files to the application.
- **Semantic Search:** The application provides semantic search functionality, allowing users to search for documents based on semantic similarity.
- **Delete Documents:** Users can delete documents from the dataset.
- **Retrieve Documents:** Users can retrieve and download documents from the dataset.
- **User Interface:** The application includes a simple user interface for interacting with the functionalities.

## Components

### Flask Application

The core of the project is a Flask web application that provides various endpoints for handling file upload, semantic searching, document deletion, and document retrieval.

### Document Processor

The Document Processor module handles processing of PDF files. It includes functionality for Optical Character Recognition (OCR) to extract text from PDFs.

### Vectorizer

The Vectorizer module handles vectorization of documents and semantic indexing. It enables semantic search functionality by computing semantic vectors for documents and queries.

### Database

The Database module manages the storage and retrieval of documents. It interfaces with a MongoDB database to store document metadata and file data.

## Usage

1. Install the required dependencies by running `pip install -r requirements.txt`.
2. Set up environment variables, including the MongoDB connection details, the index name, and other configuration parameters.
3. Run the MongoDB server.
4. Run the Flask application using `python flask_app.py`.
5. Access the application in a web browser at `http://localhost:5000`.
6. Use the provided endpoints to upload, search, delete, and retrieve documents.

## Dependencies

- Flask: Web framework for building the application.
- bson: Python library for working with BSON data.
- dotenv: Library for loading environment variables from a .env file.
- pymongo: MongoDB driver for Python.
- Other dependencies as specified in the requirements.txt file.

## Notes

- This project is designed for demonstration purposes and may require additional configuration for production use.
- Ensure that proper error handling and security measures are implemented before deploying in a production environment.

