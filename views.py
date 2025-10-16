# views.py
import os, pdfplumber, docx
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .document_store import process_document  

UPLOAD_DIR = os.path.join(settings.BASE_DIR, 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

def upload_document(request):
    if request.method == 'POST' and request.FILES['document']:
        file = request.FILES['document']
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in ['.pdf', '.docx']:
            return render(request, 'upload.html', {'error': 'Only PDF or Word files allowed.'})

        fs = FileSystemStorage(location=UPLOAD_DIR)
        file_path = fs.save(file.name, file)
        full_path = os.path.join(UPLOAD_DIR, file_path)

        # Extract text
        if ext == '.pdf':
            with pdfplumber.open(full_path) as pdf:
                extracted_text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
        else:  # .docx
            doc = docx.Document(full_path)
            extracted_text = "\n".join([p.text for p in doc.paragraphs])

        
        summary = process_document(full_path, doc_id=file.name) 

        return render(request, 'extracted_text.html', {
            'summary': summary if isinstance(summary, str) else summary.get('summary', ''),
            'extracted_text': extracted_text
        })

    return render(request, 'upload.html')
