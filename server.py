from flask import Flask, request, jsonify, render_template
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/foo": {"origins": "https://gvbim-forge-viewer-base-functions-teste.onrender.com"}})

logs = []

def log_message(message):
    logs.append(message)

def load_data(file):
    encodings = ['utf-8', 'ISO-8859-1', 'windows-1252']
    delimiters = [',', ';', '\t']
    file_extension = file.filename.split('.')[-1].lower()
    
    if file_extension == 'csv':
        for encoding in encodings:
            for delimiter in delimiters:
                try:
                    return pd.read_csv(file, encoding=encoding, delimiter=delimiter, header=3), encoding
                except (UnicodeDecodeError, pd.errors.ParserError):
                    continue
        raise ValueError("Não foi possível ler o arquivo CSV com as codificações e delimitadores testados.")
    elif file_extension == 'xlsx':
        try:
            return pd.read_excel(file, header=3), 'utf-8'
        except Exception as e:
            raise ValueError(f"Não foi possível ler o arquivo XLSX: {e}")
    else:
        raise ValueError("Tipo de arquivo não suportado. Por favor, faça upload de um arquivo CSV ou XLSX.")

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        log_message('No file part')
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        log_message('No selected file')
        return 'No selected file', 400
    try:
        data, encoding = load_data(file)
        log_message(f'File uploaded successfully: {file.filename}')
        return jsonify(message='File uploaded and data processed successfully', encoding=encoding)
    except ValueError as e:
        log_message(f'Error processing file: {e}')
        return str(e), 400

@app.route('/logs')
def show_logs():
    return render_template('logs.html', logs=logs)

if __name__ == '__main__':
    app.run()
