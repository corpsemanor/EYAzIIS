from flask import Flask, render_template, request, jsonify, abort
import nltk
import json
import os
import docx
import textract
from werkzeug.utils import secure_filename
import collections
import pymorphy2
import tempfile
import docx2txt
from spire.doc import *
from spire.doc.common import *
flag = 0
app = Flask(__name__)
app.config['RESULTS_FOLDER'] = 'results'

pos_translation = {
    'ADJF': 'Прилагательное (полное)',
    'ADJS': 'Прилагательное (краткое)',
    'COMP': 'Компаратив',
    'CONJ': 'Союз',
    'GRND': 'Деепричастие',
    'INFN': 'Инфинитив',
    'INTJ': 'Междометие',
    'NOUN': 'Существительное',
    'NPRO': 'Местоимение-существительное',
    'NUMR': 'Числительное',
    'ADVB': 'Наречие',
    'PRED': 'Предикатив',
    'PREP': 'Предлог',
    'PRTF': 'Причастие (полное)',
    'PRTS': 'Причастие (краткое)',
    'VERB': 'Глагол',
    'PRTF': 'Причастие (полное)',
    'PRTS': 'Причастие (краткое)',
}


if not os.path.exists(app.config['RESULTS_FOLDER']):
    os.makedirs(app.config['RESULTS_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

import pymorphy2


@app.route('/process_file', methods=['POST'])
def process_file():
    if 'file' not in request.files:
        return 'No file uploaded', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    if file:
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file.filename)

        file.save(temp_file_path)

        morph_analyzer = pymorphy2.MorphAnalyzer()

        if file.filename.endswith('.docx'):
            doc = docx.Document(temp_file_path)
            text = '\n'.join([p.text for p in doc.paragraphs])
        elif file.filename.endswith('.doc'):
            # Handle .doc files
            pass

        os.remove(temp_file_path)
        os.rmdir(temp_dir)

        tokens = nltk.word_tokenize(text.lower())
        word_forms = [(token, morph_analyzer.parse(token)[0].tag.POS) for token in tokens if token.isalpha()]
        lexemes_freq = collections.Counter()

        word_freq = {}

        for word_form, pos_tag in word_forms:
            lexeme = morph_analyzer.parse(word_form)[0].normal_form
            pos_tag_ru = pos_translation.get(pos_tag, 'Неизвестно')
            lexemes_freq[(word_form, lexeme, pos_tag_ru)] += 1
            word_freq[word_form] = {'lexeme': lexeme, 'pos_tag': pos_tag_ru, 'frequency': lexemes_freq[(word_form, lexeme, pos_tag_ru)], 'note': ''}


        json_filename = os.path.join(app.config['RESULTS_FOLDER'], os.path.splitext(file.filename)[0] + '.json')


        print("file:",json_filename)
        wordw = request.form.get('qwsd')
        if not os.path.exists(json_filename):

            with open(json_filename, 'w', encoding='utf-8') as json_file:
                json.dump(word_freq, json_file, ensure_ascii=False)
        else:
           
            with open(json_filename, 'r', encoding='utf-8') as json_file:
                word_freq = json.load(json_file)
        # Передача данных в шаблон
        return render_template('result.html', word_freq=word_freq, json_filename=json_filename)


@app.route('/previous_results')
def previous_results():
    if not os.path.exists(app.config['RESULTS_FOLDER']):
        return 'Папка с результатами не найдена'

    previous_results = []
    for filename in os.listdir(app.config['RESULTS_FOLDER']):
        if filename.endswith('.json'):
            previous_results.append((filename, os.path.join(app.config['RESULTS_FOLDER'], filename)))
    
    return render_template('previous_results.html', previous_results=previous_results)

@app.route('/view_result/<filename>')
def view_result(filename):
    json_filepath = os.path.join(app.config['RESULTS_FOLDER'], filename)
    if not os.path.exists(json_filepath):
        abort(404)

    with open(json_filepath) as json_file:
        data = json.load(json_file)
    
    return render_template('result.html', word_freq=data)


@app.route('/process_morphology', methods=['POST'])
def process_morphology():

    global flag
    flag =1

    print("=============================")

    json_filename = request.form.get('json_filename')
    corrected_filename = json_filename.replace('results', 'results/')

    word = request.form.get('word')
    note = request.form.get('note')

    print(corrected_filename)

    with open(corrected_filename, 'r', encoding='utf-8') as json_file:
        word_freq = json.load(json_file)

    # os.remove('results\гиис3.json')

    #  if word in word_freq:
    word_freq[word]['note'] = note
    
    # print(word_freq)

    with open(corrected_filename, 'w', encoding='utf-8') as json_file:
        json.dump(word_freq, json_file, ensure_ascii=False)
    print("=============================")

    return 'Note added successfully'



if __name__ == '__main__':
    app.run(debug=True)
