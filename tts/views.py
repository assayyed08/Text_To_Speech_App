from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from PyPDF2 import PdfReader
from docx import Document
from pdf2image import convert_from_path
from pytesseract import image_to_string
import tempfile
import os
import re
import logging
from django.conf import settings
from .models import UserDetail, VisitorLog
from django.utils.timezone import now

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

@csrf_exempt
def process_file(request):
    """
    Handles file upload and text extraction.
    Supports .txt, .docx, and .pdf file formats.
    """
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')

        # Validate file upload
        if not uploaded_file:
            logger.warning("No file uploaded.")
            return JsonResponse({'success': False, 'message': 'No file uploaded.'})

        if uploaded_file.size > 10 * 1024 * 1024:  # 10MB limit
            logger.warning("File exceeds 10MB size limit.")
            return JsonResponse({'success': False, 'message': 'File size exceeds 10MB limit.'})

        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        try:
            # Extract text based on file type
            if uploaded_file.name.endswith('.txt'):
                extracted_text = extract_text_from_txt(temp_file_path)
            elif uploaded_file.name.endswith('.docx'):
                extracted_text = extract_text_from_docx(temp_file_path)
            elif uploaded_file.name.endswith('.pdf'):
                extracted_text = extract_text_from_pdf(temp_file_path)
            else:
                logger.warning("Unsupported file type.")
                return JsonResponse({'success': False, 'message': 'Unsupported file type. Please upload .txt, .docx, or .pdf files.'})

            # Clean and return the extracted text
            cleaned_text = clean_text(extracted_text)
            logger.info("File processed successfully.")
            return JsonResponse({'success': True, 'message': 'File processed successfully.', 'text': cleaned_text})

        except Exception as e:
            logger.error(f"Error processing file: {e}")
            return JsonResponse({'success': False, 'message': 'An error occurred while processing the file.'})

        finally:
            os.remove(temp_file_path)  # Ensure temporary file is deleted
            logger.info(f"Temporary file {temp_file_path} deleted.")

    logger.warning("Invalid request method.")
    return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'})

@csrf_exempt
def process_text(request):
    """
    Handles raw text input for cleaning and formatting.
    """
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if not text:
            logger.warning("No text provided.")
            return JsonResponse({'success': False, 'message': 'No text provided.'})

        # Clean the provided text
        cleaned_text = clean_text(text)
        logger.info("Text processed successfully.")
        return JsonResponse({'success': True, 'text': cleaned_text})

    logger.warning("Invalid request method for text processing.")
    return JsonResponse({'success': False, 'message': 'Invalid request method. Use POST.'})

def clean_text(text):
    """
    Cleans extracted text by removing extra spaces and unwanted characters.
    """
    logger.info("Cleaning text.")
    text = re.sub(r'[^\w\s.,!?-]', '', text)  # Remove special characters
    return re.sub(r'\s+', ' ', text).strip()  # Normalize spacing

def extract_text_from_txt(file_path):
    """
    Extracts text from a plain text file.
    """
    logger.info("Extracting text from TXT file.")
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def extract_text_from_docx(file_path):
    """
    Extracts text from a Word document (.docx).
    """
    logger.info("Extracting text from DOCX file.")
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_pdf(file_path):
    """
    Extracts text from a PDF.
    Falls back to OCR if the PDF is image-based.
    """
    logger.info("Extracting text from PDF.")
    # Try text-based PDF extraction
    try:
        reader = PdfReader(file_path)
        text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
        if text.strip():
            return text
    except Exception as e:
        logger.warning(f"Text-based PDF extraction failed: {e}")

    # Fall back to OCR for image-based PDFs
    try:
        pages = convert_from_path(file_path, dpi=300, poppler_path=settings.POPPLER_PATH)
        text = " ".join([image_to_string(page) for page in pages])
        return text
    except Exception as e:
        logger.error(f"OCR failed: {e}")
        return "Failed to extract text from PDF."

def tts_home(request):
    """
    Tracks daily visitors and renders the homepage.
    """
    logger.info("Rendering homepage.")

    # Track daily visitor count
    today = now().date()
    visitor_log, created = VisitorLog.objects.get_or_create(date=today)
    if created:
        visitor_log.visitor_count = 1  # First visitor for today
    else:
        visitor_log.visitor_count += 1  # Increment visitor count
    visitor_log.save()

    return render(request, 'index.html')

def save_user_details(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        contact_number = request.POST.get("contact_number")

        if not (name and email and contact_number):
            return JsonResponse({"success": False, "message": "All fields are required."})

        # Save user details
        UserDetail.objects.create(name=name, email=email, contact_number=contact_number)
        return JsonResponse({"success": True, "message": "Details saved successfully."})
    return JsonResponse({"success": False, "message": "Invalid request."})

def get_visitor_count(request):
    today = now().date()
    visitor_log, created = VisitorLog.objects.get_or_create(date=today)
    return JsonResponse({"visitor_count": visitor_log.visitor_count})


def check_user_details(request):
    """
    Checks if user details are stored in the session.
    """
    details_submitted = request.session.get('user_details_submitted', False)
    return JsonResponse({"details_submitted": details_submitted})
