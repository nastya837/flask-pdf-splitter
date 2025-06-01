from flask import Flask, request, send_file
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
import zipfile

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <h1>Разделить PDF</h1>
    <form method="POST" action="/split" enctype="multipart/form-data">
        <input type="file" name="file" accept=".pdf" required>
        <button type="submit">Загрузить и разделить</button>
    </form>
    '''

@app.route('/split', methods=['POST'])
def split_pdf():
    uploaded_file = request.files.get('file')
    if not uploaded_file or not uploaded_file.filename.endswith('.pdf'):
        return 'Ошибка: Загрузите PDF файл.', 400

    pdf_file = BytesIO(uploaded_file.read())
    reader = PdfReader(pdf_file)
    total_pages = len(reader.pages)

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        for start in range(0, total_pages, 50):
            end = min(start + 50, total_pages)
            writer = PdfWriter()
            for i in range(start, end):
                writer.add_page(reader.pages[i])
            part_buffer = BytesIO()
            writer.write(part_buffer)
            part_buffer.seek(0)
            zipf.writestr(f'part_{start + 1}_to_{end}.pdf', part_buffer.read())

    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='split_parts.zip')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
