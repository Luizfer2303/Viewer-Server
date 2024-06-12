from flask import Flask, request, jsonify
import pandas as pd
import logging

app = Flask(__name__)

# Configuração do logger
logging.basicConfig(filename='logs.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

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
        app.logger.error('No file part')
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        app.logger.error('No selected file')
        return 'No selected file', 400
    try:
        data, encoding = load_data(file)
        app.logger.info('File uploaded successfully: %s', file.filename)
        return jsonify(message='File uploaded and data processed successfully', encoding=encoding)
    except ValueError as e:
        app.logger.error('Error processing file: %s', e)
        return str(e), 400

if __name__ == '__main__':
    app.run(debug=True)
