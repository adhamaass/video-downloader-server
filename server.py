from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

@app.route('/info', methods=['POST'])
def get_info():
    try:
        url = request.json.get('url', '').strip()
        if not url:
            return jsonify({'error': 'الرابط مطلوب'}), 400

        ydl_opts = {'quiet': True, 'no_warnings': True}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []
            seen = set()
            for f in info.get('formats', []):
                if not f.get('url'):
                    continue
                res = f.get('resolution') or f.get('format_note', 'audio')
                ext = f.get('ext', 'mp4')
                key = f"{res}-{ext}"
                if key in seen:
                    continue
                seen.add(key)
                formats.append({
                    'format_id': f.get('format_id'),
                    'ext': ext,
                    'resolution': res,
                    'filesize': f.get('filesize'),
                    'url': f['url']
                })
            return jsonify({
                'title': info.get('title', 'فيديو'),
                'thumbnail': info.get('thumbnail', ''),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', ''),
                'formats': formats
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
