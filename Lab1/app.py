from flask import Flask, render_template, request, jsonify, abort
import nltk
import json
import os
import docx
import textract
from werkzeug.utils import secure_filename
import collections


app = Flask(__name__)
app.config['RESULTS_FOLDER'] = 'results'

# Проверка наличия папки для сохранения результатов
if not os.path.exists(app.config['RESULTS_FOLDER']):
    os.makedirs(app.config['RESULTS_FOLDER'])

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
        # Определение пути для сохранения JSON-файла результата
        filename = secure_filename(file.filename)
        json_filename = os.path.join(app.config['RESULTS_FOLDER'], os.path.splitext(filename)[0] + '.json')

        if file.filename.endswith('.docx'):
            doc = docx.Document(file)
            text = '\n'.join([p.text for p in doc.paragraphs])
        elif file.filename.endswith('.doc'):
            text = textract.process(file)
            text = text.decode('utf-8') if isinstance(text, bytes) else text

        tokens = nltk.word_tokenize(text.lower())  # Токенизация текста
        word_forms = nltk.pos_tag(tokens)  # Определение частей речи для каждой словоформы
        lexemes_freq = collections.Counter()  # Счетчик для хранения лексем и их частот

        for word_form, pos_tag in word_forms:
            if pos_tag != 'PUNCT':  # Исключение знаков препинания
                lexeme = nltk.WordNetLemmatizer().lemmatize(word_form)  # Определение лексемы для словоформы
                lexemes_freq[(lexeme, pos_tag)] += 1  # Увеличение частоты для данной лексемы и части речи


        # Преобразование счетчика в отсортированный список кортежей
        word_freq = sorted(lexemes_freq.items())

        # Создание JSON-файла с результатами
        with open(json_filename, 'w') as json_file:
            json.dump(word_freq, json_file)

        return render_template('result.html', word_freq=word_freq)

@app.route('/previous_results')
def previous_results():
    # Проверяем, существует ли папка с результатами
    if not os.path.exists(app.config['RESULTS_FOLDER']):
        return 'Папка с результатами не найдена'

    # Получение списка предыдущих результатов
    previous_results = []
    for filename in os.listdir(app.config['RESULTS_FOLDER']):
        if filename.endswith('.json'):
            previous_results.append((filename, os.path.join(app.config['RESULTS_FOLDER'], filename)))
    
    return render_template('previous_results.html', previous_results=previous_results)

@app.route('/view_result/<filename>')
def view_result(filename):
    # Проверяем, существует ли запрошенный JSON файл
    json_filepath = os.path.join(app.config['RESULTS_FOLDER'], filename)
    if not os.path.exists(json_filepath):
        abort(404)

    # Загружаем содержимое JSON файла
    with open(json_filepath) as json_file:
        data = json.load(json_file)
    
    return render_template('result.html', word_freq=data)

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
