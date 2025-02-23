# app.py
from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'json'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'})
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            if filename.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif filename.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            elif filename.endswith('.json'):
                with open(file_path) as f:
                    data = json.load(f)
                df = pd.DataFrame(data)
            
            columns = list(df.columns)
            numeric_cols = list(df.select_dtypes(include=['int64', 'float64']).columns)
            category_cols = list(df.select_dtypes(include=['object']).columns)
            data_dict = df.to_dict(orient='records')
            
            return jsonify({
                'columns': columns,
                'numeric_cols': numeric_cols,
                'category_cols': category_cols,
                'data': data_dict
            })
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)