import fitz  # PyMuPDF
import os

class PDFReader:
    """Simple PDF reader using PyMuPDF to extract text content."""
    
    def __init__(self):
        pass
    
    def extract_text(self, pdf_path):
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text from the PDF
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            Exception: If PDF processing fails
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            # Open the PDF
            doc = fitz.open(pdf_path)
            text = ""
            
            # Extract text from all pages
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()
            
            doc.close()
            return text.strip()
            
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
    
    def get_pdf_info(self, pdf_path):
        """
        Get basic information about the PDF.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            dict: PDF information (pages, size, etc.)
        """
        try:
            doc = fitz.open(pdf_path)
            info = {
                "pages": len(doc),
                "file_size": os.path.getsize(pdf_path),
                "file_name": os.path.basename(pdf_path)
            }
            doc.close()
            return info
        except Exception as e:
            return {"error": str(e)} 