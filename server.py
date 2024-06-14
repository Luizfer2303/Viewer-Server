from flask import Flask, request, jsonify
import pandas as pd
from flask_cors import CORS

class DataLoaderApp:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.spreadsheet_base = None
        self.spreadsheet_base_json = None
        self.data_frame_loaded = False
        self.merged_with_disciplines = pd.DataFrame()
        self.setup_routes()

    def setup_routes(self):
        self.app.add_url_rule('/view', 'json_viewer', self.json_viewer)
        self.app.add_url_rule('/api/upload', 'load_file', self.load_file, methods=['POST','GET','DELETE'])
        self.app.add_url_rule('/api/upload/json', 'load_json', self.load_json, methods=['POST','GET','DELETE'])
        self.app.add_url_rule('/api/update', 'change_dataframe', self.change_dataframe, methods=['POST', 'GET', 'DELETE'])
        self.app.add_url_rule('/api/update/viewer', 'pass_to_extension', self.pass_to_extension, methods=['POST', 'GET', 'DELETE'])
        self.app.add_url_rule('/api/check/connection', 'check_connection', self.check_connection, methods=['POST', 'GET', 'DELETE'])

    def load_data(self, file):
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

    def load_file(self):
        if 'file' not in request.files:
            return 'No file part', 400
        file = request.files['file']
        if file.filename == '':
            return 'No selected file', 400
        try:
            data, encoding = self.load_data(file)
            self.spreadsheet_base = data  # load dataframe
            self.data_frame_loaded = True

            return jsonify(message=f'File uploaded and data processed successfully{data.items()}', encoding=encoding)
        except ValueError as e:
            return str(e), 400

    def load_json(self):
        if not request.is_json:
            return 'No JSON part', 400
        try:
            json_data = request.get_json()
            data = pd.DataFrame(json_data)
            self.spreadsheet_base_json = data
            self.merge_with_disciplines()
            return jsonify(message='JSON uploaded and data processed successfully')
        except ValueError as e:
            return str(e), 400

    def merge_with_disciplines(self):
        merged_data = []
        for index_reference, row_reference in self.spreadsheet_base.iterrows():
            for index_model, row_model in self.spreadsheet_base_json.iterrows():
                if str(row_reference['Pacote de trabalho']) in str(row_model['SETS']):
                    merged_row = {**row_model.to_dict(), **row_reference.to_dict()}
                    merged_data.append(merged_row)
        self.merged_with_disciplines = pd.DataFrame(merged_data)
        self.save_to_csv()

    def save_to_csv(self):
        self.merged_with_disciplines.to_csv('merged_data.csv', index=False)
        print("CSV saved successfully as 'merged_data.csv'")

    def json_viewer(self):
        if self.spreadsheet_base_json is not None:
            return self.spreadsheet_base_json.to_json(orient='records')
        else:
            return jsonify(message="No JSON data available"), 404

    def change_dataframe(self):
        pass

    def pass_to_extension(self):
        pass

    def check_connection(self):
        return jsonify({"message": "Connection successful"})

    def run(self):
        self.app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    app = DataLoaderApp()
    app.run()
