import os
import sqlite3
import uuid
import json
import traceback
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for
from PIL import Image
from PIL.ExifTags import TAGS
import click
import webview # <-- Import pywebview

# --- App and Database Configuration ---
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
DB_FILE = 'metadata.db'

# --- Datetime Handling (No changes here) ---
def adapt_datetime(dt):
    return dt.isoformat()

def convert_datetime(iso_str):
    return datetime.fromisoformat(iso_str.decode('utf-8'))

sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("DATETIME", convert_datetime)

# --- Database Helper Functions (No changes here) ---
def get_db_connection():
    conn = sqlite3.connect(DB_FILE, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_type TEXT,
                size_kb REAL,
                created_time DATETIME,
                modified_time DATETIME,
                accessed_time DATETIME,
                exif_data TEXT
            )
        ''')
    conn.close()

@app.cli.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized the database.')

# --- Metadata Extraction (No changes here) ---
def extract_metadata(file_storage):
    filename = file_storage.filename
    file_type = filename.split('.')[-1].lower() if '.' in filename else 'unknown'
    
    file_storage.seek(0, os.SEEK_END)
    size_bytes = file_storage.tell()
    size_kb = round(size_bytes / 1024, 2)
    file_storage.seek(0)

    now = datetime.now()
    
    exif_data_str = None
    if file_type in ['jpg', 'jpeg', 'tiff', 'png', 'gif']:
        try:
            img = Image.open(file_storage)
            exif_data = {}
            if hasattr(img, '_getexif'):
                exif_info = img._getexif()
                if exif_info:
                    for tag, value in exif_info.items():
                        decoded = TAGS.get(tag, tag)
                        try:
                            exif_data[str(decoded)] = str(value)
                        except (TypeError, ValueError):
                            exif_data[str(decoded)] = repr(value)
            if exif_data:
                exif_data_str = json.dumps(exif_data)
        except Exception:
            exif_data_str = None

    return {
        'filename': filename,
        'file_type': file_type,
        'size_kb': size_kb,
        'created_time': now,
        'modified_time': now,
        'accessed_time': now,
        'exif_data': exif_data_str
    }

# --- Flask Routes (No changes here) ---
@app.route('/')
def index():
    # We now point to 'upload.html' as the starting page for the app
    return render_template('index.html')

@app.route('/upload')
def upload_page():
    return render_template('upload.html')

@app.route('/process-files', methods=['POST'])
def process_files():
    try:
        files = request.files.getlist('files[]')
        if not files or not files[0].filename:
            return jsonify({'error': 'No files were selected for upload.'}), 400

        run_id = str(uuid.uuid4())
        conn = get_db_connection()
        cursor = conn.cursor()
        
        last_inserted_id = None
        
        for file in files:
            if file and file.filename:
                metadata = extract_metadata(file)
                cursor.execute('''
                    INSERT INTO metadata (run_id, filename, file_type, size_kb, created_time, modified_time, accessed_time, exif_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (run_id, metadata['filename'], metadata['file_type'], metadata['size_kb'], metadata['created_time'], metadata['modified_time'], metadata['accessed_time'], metadata['exif_data']))
                
                last_inserted_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        if len(files) == 1:
            redirect_url = url_for('file_result', file_id=last_inserted_id)
        else:
            redirect_url = url_for('folder_result', run_id=run_id)
            
        return jsonify({'success': True, 'redirect_url': redirect_url})

    except Exception as e:
        print("An error occurred in /process-files:")
        traceback.print_exc()
        return jsonify({'error': f'A server error occurred: {str(e)}'}), 500

@app.route('/results/folder/<run_id>')
def folder_result(run_id):
    conn = get_db_connection()
    files = conn.execute('SELECT * FROM metadata WHERE run_id = ? ORDER BY filename', (run_id,)).fetchall()
    
    file_type_counts = {}
    total_files = len(files)
    for file in files:
        ftype = file['file_type'] if file['file_type'] else 'unknown'
        file_type_counts[ftype] = file_type_counts.get(ftype, 0) + 1

    chart_data = {
        'labels': list(file_type_counts.keys()),
        'data': list(file_type_counts.values())
    }
    
    summary_list = list(zip(chart_data['labels'], chart_data['data']))
    
    conn.close()
    return render_template('results_folder.html', files=files, total_files=total_files, chart_data=chart_data, summary_list=summary_list, run_id=run_id)

@app.route('/results/file/<int:file_id>')
def file_result(file_id):
    conn = get_db_connection()
    file = conn.execute('SELECT * FROM metadata WHERE id = ?', (file_id,)).fetchone()
    conn.close()

    if not file:
        return "File not found", 404
        
    exif_data_parsed = None
    if file['exif_data']:
        try:
            exif_data_parsed = json.loads(file['exif_data'])
        except json.JSONDecodeError:
            exif_data_parsed = {"error": "Could not parse EXIF data."}

    return render_template('results_file.html', file=file, exif_data_parsed=exif_data_parsed)

# --- Main Execution: MODIFIED FOR PYWEBVIEW ---


# --- Main Execution: MODIFIED FOR PYWEBVIEW ---
if __name__ == '__main__':
    # Initialize the database if it doesn't exist
    if not os.path.exists(DB_FILE):
        init_db()

    # Create the pywebview window. This will host the Flask app.
    # The 'app' object is passed directly to pywebview, which will handle the server.
    webview.create_window(
        'Metadata Timeline Generator', # Window title
        app,                         # The Flask app object
        width=1280,
        height=800,
        resizable=True,
        min_size=(800, 600)
    )
    # Start the event loop
    webview.start(debug=True) # Set debug=False for production