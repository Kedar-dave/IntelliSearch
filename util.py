import os 
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

def file_finder(folder_path: str, extensions: tuple) -> list:
    files = [
            file
            for file in os.listdir(folder_path)
            if file.lower().endswith(extensions)
    ]
    return files
def text_cleaning(original_text: list) -> str:
        # Remove special characters and punctuation
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', original_text)

        # Lowercasing
    cleaned_text = cleaned_text.lower()

        # Handling line breaks and whitespace
    cleaned_text = ' '.join(cleaned_text.split())

    return cleaned_text

def tokenization(text: str) -> list:
        # Tokenization using NLTK word_tokenize
    tokens = word_tokenize(text)
    return tokens

def stopword_removal(tokens: list) -> list:
        # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    return filtered_tokens

def lemmatization(tokens: list) -> list:
        # Check function call and value used after call
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return lemmatized_tokens

def transform_text(text: str) -> list:
    cleaned_text = text_cleaning(text)
    tokens = tokenization(cleaned_text)
    filtered_tokens = stopword_removal(tokens)
    lemmatized_tokens = lemmatization(filtered_tokens)
    return lemmatized_tokens

def objectid_to_int(obj_id):
    # Convert ObjectId to hexadecimal string
    # Use hash function to convert the string to an integer
    hex_string = str(obj_id)

    return hash(hex_string)