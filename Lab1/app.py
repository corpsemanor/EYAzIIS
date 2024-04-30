from flask import Flask, render_template, request
import nltk
import docx
import textract
import re

# app = Flask(__name__)

# nltk.download('punkt')  # Загрузка необходимых данных для токенизации

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/process_file', methods=['POST'])
# def process_file():
#     if 'file' not in request.files:
#         return 'No file uploaded', 400

#     file = request.files['file']
#     if file.filename == '':
#         return 'No selected file', 400

#     if file:
#         if file.filename.endswith('.docx'):
#             doc = docx.Document(file)
#             text = '\n'.join([p.text for p in doc.paragraphs])
#         elif file.filename.endswith('.doc'):
#             text = textract.process(file)
#             text = text.decode('utf-8') if isinstance(text, bytes) else text

#         tokens = nltk.word_tokenize(text.lower())  # Токенизация текста
#         freq_dist = nltk.FreqDist(tokens)  # Подсчет частоты встречаемости слов

#         sorted_word_freq = sorted(freq_dist.items())

#         return render_template('result.html', word_freq=sorted_word_freq)

# if __name__ == '__main__':
#     app.run(debug=True)





from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    # Предполагается, что word_freq представляет список кортежей (слово, частота)
    word_freq = [('word1', 10), ('word2', 5), ('word3', 3)]  # Пример данных
    return render_template('index.html', word_freq=word_freq)

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

@app.route('/process_morphology', methods=['POST'])
def process_morphology():
    words = request.form.getlist('word[]')
    parts_of_speech = request.form.getlist('part_of_speech[]')
    genders = request.form.getlist('gender[]')
    numbers = request.form.getlist('number[]')
    cases = request.form.getlist('case[]')

    # Обработка введенной морфологической информации
    for word, pos, gender, number, case in zip(words, parts_of_speech, genders, numbers, cases):
        print(f"Word: {word}, Part of Speech: {pos}, Gender: {gender}, Number: {number}, Case: {case}")

    return 'Morphological information processed successfully'

if __name__ == '__main__':
    app.run(debug=True)
