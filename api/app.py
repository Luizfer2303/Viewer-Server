from flask import Flask, jsonify, request, redirect, url_for, send_from_directory
import pandas as pd
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads/spreadsheet'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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

@app.route('/')
def index():
    return 'server running'

@app.route('/uploads/spreadsheet', methods=['POST'])
def load_spreadsheet():

    if 'file' not in request.files:
        return 'no file part'    
    
    file = request.files['file']
    if file.name == '':
        return 'no selected files'
    
    if file:
        try:
            dataFrame, encondin = load_data(file)
            return jsonify({'head':dataFrame.head()})
        except ValueError as e:
            return e

if __name__ == '__main__':
    app.run(debug=True)
