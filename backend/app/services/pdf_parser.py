import PyPDF2
import pdfplumber
from typing import Dict, Optional
import re


class PDFParser:
    @staticmethod
    def extract_text_pypdf2(file_path: str) -> str:
        """
        Extract text from PDF using PyPDF2 (faster but less accurate).
        """
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"Failed to extract text with PyPDF2: {str(e)}")
        
        return text.strip()
    
    @staticmethod
    def extract_text_pdfplumber(file_path: str) -> str:
        """
        Extract text from PDF using pdfplumber (more accurate, handles tables).
        """
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            raise Exception(f"Failed to extract text with pdfplumber: {str(e)}")
        
        return text.strip()
    
    @staticmethod
    def extract_text(file_path: str, method: str = "pdfplumber") -> str:
        """
        Extract text from PDF using specified method.
        
        Args:
            file_path: Path to PDF file
            method: 'pypdf2' or 'pdfplumber' (default)
        
        Returns:
            Extracted text content
        """
        if method == "pypdf2":
            return PDFParser.extract_text_pypdf2(file_path)
        else:
            return PDFParser.extract_text_pdfplumber(file_path)
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean extracted text by removing extra whitespace and formatting issues.
        """
        # Remove multiple newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove multiple spaces
        text = re.sub(r' +', ' ', text)
        
        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        return text.strip()
    
    @staticmethod
    def parse_cv(file_path: str) -> Dict[str, str]:
        """
        Parse CV and extract structured information.
        
        Returns:
            Dictionary with raw_text and cleaned_text
        """
        raw_text = PDFParser.extract_text(file_path)
        cleaned_text = PDFParser.clean_text(raw_text)
        
        return {
            "raw_text": raw_text,
            "cleaned_text": cleaned_text,
            "char_count": len(cleaned_text),
            "word_count": len(cleaned_text.split())
        }
    
    @staticmethod
    def parse_project_report(file_path: str) -> Dict[str, str]:
        """
        Parse project report and extract structured information.
        
        Returns:
            Dictionary with raw_text and cleaned_text
        """
        raw_text = PDFParser.extract_text(file_path)
        cleaned_text = PDFParser.clean_text(raw_text)
        
        return {
            "raw_text": raw_text,
            "cleaned_text": cleaned_text,
            "char_count": len(cleaned_text),
            "word_count": len(cleaned_text.split())
        }
