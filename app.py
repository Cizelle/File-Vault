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

        max_downloads_str = request.form.get('max_downloads', '1').strip()
        try:
            max_downloads = int(max_downloads_str)
            if max_downloads < 1:
                raise ValueError
        except ValueError:
            return jsonify({'error': 'Invalid input for max downloads; must be >= 1'}), 400

        hours = request.form.get('hours', '').strip()
        minutes = request.form.get('minutes', '').strip()

        try:
            hours = int(hours) if hours else 0
            minutes = int(minutes) if minutes else 0
            if hours < 0 or minutes < 0 or minutes > 59:
                raise ValueError
        except ValueError:
            return jsonify({'error': 'Invalid expiry time values'}), 400

        expires_at = time.time() + (hours * 3600 + minutes * 60) if (hours or minutes) else None

        token = secrets.token_urlsafe(16)
        download_links[token] = {
            'filepath': path,
            'remaining': max_downloads,
            'expires_at': expires_at
        }

        file_info = {
            'filename': uploaded.filename,
            'size': round(os.path.getsize(path) / 1024, 2),
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

    now = time.time()
    seconds_left = max(0, int(info['expires_at'] - now)) if info['expires_at'] is not None else None

    def format_duration(seconds):
        if seconds is None:
            return "No expiry"
        minutes, sec = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours > 0:
            return f"{hours}h {minutes}m {sec}s"
        elif minutes > 0:
            return f"{minutes}m {sec}s"
        return f"{sec}s"

    time_remaining_str = format_duration(seconds_left)

    file_info = {
        'filename': os.path.basename(info['filepath']),
        'size': round(os.path.getsize(info['filepath']) / 1024, 2),
        'type': ''
    }

    link = url_for('download', token=token, _external=True)
    return render_template(
        'upload_success.html',
        link=link,
        file_info=file_info,
        remaining=info.get('remaining', 1),
        time_remaining=time_remaining_str
    )

@app.route('/download/<token>')
def download(token):
    info = download_links.get(token)
    now = time.time()

    if (
        not info or
        info['remaining'] < 1 or
        (info['expires_at'] is not None and now > info['expires_at'])
    ):
        return render_template('expired.html')

    info['remaining'] -= 1
    return send_file(info['filepath'], as_attachment=True)

@app.route('/expired')
def expired():
    return render_template('expired.html')

if __name__ == '__main__':
    app.run(debug=True)
