from flask import Flask, render_template, request
import nltk
import docx
import textract
import re

app = Flask(__name__)

nltk.download('punkt')  # Загрузка необходимых данных для токенизации

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_file', methods=['POST'])
def process_file():
    if 'file' not in request.files:
        return 'No file uploaded', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    if file:
        if file.filename.endswith('.docx'):
            doc = docx.Document(file)
            text = '\n'.join([p.text for p in doc.paragraphs])
        elif file.filename.endswith('.doc'):
            text = textract.process(file)
            text = text.decode('utf-8') if isinstance(text, bytes) else text

        tokens = nltk.word_tokenize(text.lower())  # Токенизация текста
        freq_dist = nltk.FreqDist(tokens)  # Подсчет частоты встречаемости слов

        sorted_word_freq = sorted(freq_dist.items())

        return render_template('result.html', word_freq=sorted_word_freq)

if __name__ == '__main__':
    app.run(debug=True)
