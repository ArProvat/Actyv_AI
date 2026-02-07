from fastapi import File
from app.config.settings import settings
from langchain_core.document_loaders import TextLoader , PDFLoader , DocxLoader , CSVLoader , JSONLoader 
import tempfile

class FileHandler:
     @staticmethod
     async def file_handler(file: bytes, extension: str): 
     try:
          supported = ['.pdf', '.docx', '.txt', '.csv', '.json']
          if extension not in supported:
               return "Unsupported file format"

          with tempfile.NamedTemporaryFile(delete=True, suffix=extension) as temp_file:
               temp_file.write(file)
               temp_file.flush()  
               
               temp_file_path = temp_file.name
               
               if extension == '.pdf': loader = PDFLoader(temp_file_path)
               elif extension == '.docx': loader = DocxLoader(temp_file_path)
               elif extension == '.txt': loader = TextLoader(temp_file_path)
               elif extension == '.csv': loader = CSVLoader(temp_file_path)
               elif extension == '.json': loader = JSONLoader(temp_file_path)

               docs = loader.load()
               full_text = " ".join([doc.page_content for doc in docs])

               return full_text[:1500] if len(full_text) > 1500 else full_text

     except Exception as e:
          return f"Error processing file: {str(e)}"

