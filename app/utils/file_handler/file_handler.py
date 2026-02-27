from fastapi import File
from app.config.settings import settings
from langchain_community.document_loaders import  PyMuPDFLoader , JSONLoader 
from langchain_community.document_loaders.csv_loader import CSVLoader
from docx import Document
import tempfile
import os

class FileHandler:
     @staticmethod
     async def file_handler(file: bytes, extension: str):
          try:
               supported = ['.pdf', '.docx', '.csv', '.json']
               if extension not in supported:
                    return "Unsupported file format"

               with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as temp_file:
                    temp_file.write(file)
                    temp_file.flush()
                    temp_file_path = temp_file.name

               loader = None
               doc = None
               full_text = ""

               try:
                    if extension == '.pdf':
                         loader = PyMuPDFLoader(temp_file_path)
                    elif extension == '.docx':
                         doc = Document(temp_file_path)
                    elif extension == '.csv':
                         loader = CSVLoader(temp_file_path)
                    elif extension == '.json':
                         loader = JSONLoader(temp_file_path)

                    if loader:
                         docs = loader.load()
                         full_text = " ".join([d.page_content for d in docs])
                    elif doc:
                         full_text = " ".join([para.text for para in doc.paragraphs])
                    else:
                         # ✅ Read from path string, not the object
                         with open(temp_file_path, 'r', errors='ignore') as f:
                              full_text = f.read()

               finally:
                    # ✅ Always clean up the temp file manually
                    os.unlink(temp_file_path)

               return full_text[:2000] if len(full_text) > 2000 else full_text

          except Exception as e:
               return f"Error processing file: {str(e)}"