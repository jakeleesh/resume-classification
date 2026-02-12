"""
Utility functions for resume text extraction and parsing.
"""

import re
import io
import PyPDF2
from typing import Dict
from fastapi import HTTPException


def get_email(text):
    """Extract email address from resume text."""
    email = re.findall(r'\b[\w.+-]+@[\w.-]+\.\w+', str(text))
    return email[0] if email else "Not Found"


def get_phone(text):
    """Extract phone number from resume text."""
    phone = re.findall(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4})', str(text))
    return phone[0] if phone else "Not Found"


def get_name(text):
    """Extract candidate name from resume text (usually first line)."""
    lines = str(text).split('\n')
    for line in lines:
        if line.strip():
            # Convert to title case for proper formatting
            name = line.strip().title()
            # Add space before capital letters if missing
            name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
            return name
    return "Not Found"


def get_education(text):
    """Extract education information from resume text."""
    degrees = ['bachelor', 'master', 'phd', 'diploma', 'degree', 'bsc', 'msc', 'ba', 'ma', 'b.sc', 'm.sc']
    text_lower = str(text).lower()
    original_text = str(text)
    education_info = []
    
    for degree in degrees:
        if degree in text_lower:
            # Split both original and lowercase for matching
            sentences_lower = re.split(r'[.\n]', text_lower)
            sentences_original = re.split(r'[.\n]', original_text)
            
            for i, sentence in enumerate(sentences_lower):
                if degree in sentence and len(sentence) < 200:
                    # Get the original case version and apply title case
                    edu = sentences_original[i].strip().title()
                    education_info.append(edu)
                    break
            break
    
    return education_info[0] if education_info else "Not Found"


def get_experience(text):
    """Extract years of experience from resume text."""
    exp = re.findall(r'(\d+)\+?\s*(?:-\s*\d+)?\s*years?', str(text).lower())
    if exp:
        return int(exp[0])
    return 0


def get_skills(text):
    """Extract technical skills from resume text."""
    keywords = [
        'python', 'java', 'javascript', 'sql', 'r', 'c++', 'c#',
        'machine learning', 'deep learning', 'data analysis', 'statistics',
        'tableau', 'power bi', 'excel', 'aws', 'azure', 'cloud',
        'git', 'docker', 'kubernetes', 'tensorflow', 'pytorch',
        'html', 'css', 'react', 'angular', 'node.js', 'flask', 'django'
    ]
    text_lower = str(text).lower()
    # Use regex word boundaries to match whole words only (fixes 'r' matching 'ready', etc.)
    found = [word for word in keywords if re.search(r'\b' + re.escape(word) + r'\b', text_lower)]
    return ", ".join(found) if found else "None"


def extract_text_from_pdf(pdf_file: bytes) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_file: PDF file as bytes
        
    Returns:
        Extracted text as string
    """
    try:
        # Create a PDF reader object from the bytes
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
        
        # Extract text from all pages
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        return text
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")


def extract_resume_info(text: str) -> Dict:
    """
    Extract structured information from resume text.
    
    Args:
        text: Resume text
        
    Returns:
        Dictionary with extracted information
    """
    return {
        "name": get_name(text),
        "email": get_email(text),
        "phone": get_phone(text),
        "education": get_education(text),
        "experience_years": get_experience(text),
        "skills": get_skills(text)
    }
