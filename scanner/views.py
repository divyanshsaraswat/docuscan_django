from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from PIL import Image
import pytesseract
import io
from fpdf import FPDF
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from googletrans import Translator


def summarize_text(text, sentence_count=3):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentence_count)
    return ' '.join(str(sentence) for sentence in summary)


@login_required
def home(request):
    extracted_text = summary = translated = None
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        uploaded_file_path = fs.path(filename)

        extracted_text = pytesseract.image_to_string(Image.open(uploaded_file_path))

        try:
            summary = summarize_text(extracted_text)
        except Exception:
            summary = 'Text too short or not suitable for summarization.'

        translator = Translator()
        try:
            translated = translator.translate(extracted_text, dest='hi').text
        except:
            translated = 'Translation failed.'

        request.session['extracted_text'] = extracted_text

    return render(request, 'scanner/home.html', {
        'text': extracted_text,
        'summary': summary,
        'translated': translated,
    })


@login_required
def download_txt(request):
    text = request.session.get('extracted_text', '')
    response = HttpResponse(text, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="extracted_text.txt"'
    return response


@login_required
def download_pdf(request):
    text = request.session.get('extracted_text', '')
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in text.split('\n'):
        pdf.cell(200, 10, txt=line, ln=True)
    response = HttpResponse(pdf.output(dest='S').encode('latin-1'), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="extracted_text.pdf"'
    return response