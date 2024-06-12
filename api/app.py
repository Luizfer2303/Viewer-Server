from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

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

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    try:
        data, encoding = load_data(file)
        # Aqui você pode fazer o que precisar com os dados carregados
        print(data.head())  # Exemplo: imprimir as primeiras linhas
        return jsonify(message='File uploaded and data processed successfully', encoding=encoding)
    except ValueError as e:
        return str(e), 400

if __name__ == '__main__':
    app.run(debug=True)
