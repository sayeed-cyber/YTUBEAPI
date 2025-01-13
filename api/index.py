# api/index.py
from flask import Flask, jsonify, request, send_file

from flask_cors import CORS

 

import yt_dlp
import os
import uuid
import tempfile

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/api/info', methods=['POST'])
def get_video_info():
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []
            
            for f in info['formats']:
                if f.get('acodec') != 'none' and f.get('vcodec') != 'none':
                    formats.append({
                        'format_id': f['format_id'],
                        'ext': f['ext'],
                        'resolution': f.get('resolution', 'N/A'),
                        'filesize': f.get('filesize', 'N/A'),
                        'format_note': f.get('format_note', '')
                    })
            
            return jsonify({
                'title': info.get('title', ''),
                'thumbnail': info.get('thumbnail', ''),
                'duration': info.get('duration', 0),
                'formats': formats
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/download', methods=['POST'])
def download_video():
    try:
        data = request.get_json()
        url = data.get('url')
        format_id = data.get('format', 'best')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400

        # Use a temporary file with a unique name
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            download_path = temp_file.name
        
        ydl_opts = {
            'format': format_id,
            'outtmpl': download_path,
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # Read the file content
            with open(download_path, 'rb') as f:
                file_content = f.read()
            
            # Clean up
            os.unlink(download_path)
            
            # Return the file content directly
            response = send_file(
                download_path,
                as_attachment=True,
                download_name=f"{info.get('title', 'video')}.mp4",
                mimetype='video/mp4'
            )
            
            return response
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# For local development
if __name__ == '__main__':
    app.run(debug=True)