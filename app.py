from flask import Flask, request, render_template, send_file, jsonify, url_for
import os
import secrets
import time

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

download_links = {}

@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        uploaded = request.files.get('doc')
        if not uploaded:
            return jsonify({'error': 'No file uploaded'}), 400

        ext = os.path.splitext(uploaded.filename)[1]
        filename = secrets.token_hex(8) + ext
        path = os.path.join(UPLOAD_FOLDER, filename)
        uploaded.save(path)

        hours_str = request.form.get('hours', '').strip()
        minutes_str = request.form.get('minutes', '').strip()

        try:
            hours = int(hours_str) if hours_str else 0
            minutes = int(minutes_str) if minutes_str else 0
            if hours < 0 or minutes < 0 or minutes >= 60:
                raise ValueError
        except ValueError:
            return jsonify({'error': 'Invalid expiry duration input'}), 400

        total_seconds = hours * 3600 + minutes * 60
        expires_at = time.time() + total_seconds if total_seconds > 0 else None

        token = secrets.token_urlsafe(16)
        download_links[token] = {
            'filepath': path,
            'used': False,
            'expires_at': expires_at
        }

        file_info = {
            'filename': uploaded.filename,
            'size': round(os.path.getsize(path) / 1024, 2),  # in KB
            'type': uploaded.mimetype or 'Unknown'
        }

        return jsonify({
'success_url': url_for('upload_success', token=token, _external=True),
            'file_info': file_info
        }), 200

    return render_template('upload_form.html')

@app.route('/upload_success/<token>')
def upload_success(token):
    info = download_links.get(token)
    if not info:
        return "Invalid or expired token", 404
    file_info = {
        'filename': os.path.basename(info['filepath']),
        'size': round(os.path.getsize(info['filepath']) / 1024, 2),
        'type': '', 
    }
    link = url_for('download', token=token, _external=True)
    return render_template('upload_success.html', link=link, file_info=file_info)


@app.route('/download/<token>')
def download(token):
    info = download_links.get(token)
    now = time.time()

    if (not info or info['used'] or
       (info['expires_at'] is not None and now > info['expires_at'])):
        return render_template('expired.html')

    info['used'] = True
    return send_file(info['filepath'], as_attachment=True)


@app.route('/expired')
def expired():
    return render_template('expired.html')

if __name__ == '__main__':
    app.run(debug=True)
