from flask import Flask, request, redirect, send_file, jsonify
import yt_dlp
import os
import random
import string
import shutil

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def generate_random_filename():
    random_part = ''.join(random.choices(string.ascii_letters, k=10))
    return f"{random_part}_JuiceSave.mp4"

@app.route("/download", methods=["GET"])
def download_video():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    # Перевірка наявності ffmpeg
    if not shutil.which("ffmpeg"):
        return jsonify({"error": "FFmpeg is not installed or not found in PATH. Please install FFmpeg."}), 500

    temp_filename = generate_random_filename()
    temp_file_path = os.path.join(DOWNLOAD_FOLDER, temp_filename)

    try:
        ydl_opts = {
            "format": "bestvideo[height<=1080]+bestaudio/best",  # Вибираємо відео до 1080p + аудіо
            "outtmpl": temp_file_path,  # Використовуємо нашу назву
            "merge_output_format": "mp4",  # Формат mp4
            "noplaylist": True,
            "quiet": False,  # Логи для дебагу
            "verbose": True,  # Детальні логи
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            },
            "cachedir": False,
            "no_part": True,
            "postprocessor_args": {
                "ffmpeg": ["-c:v", "copy", "-c:a", "aac"],  # Копіюємо відео, перекодовуємо аудіо в AAC
            },
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                return jsonify({"error": "Failed to extract video info"}), 500

        if not os.path.exists(temp_file_path):
            return jsonify({"error": "File was not created"}), 500

        return redirect(f"/download-file?filename={temp_filename}")

    except Exception as e:
        print(f"Error while downloading video: {e}")
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as e:
                print(f"Error removing temp file: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/download-file", methods=["GET"])
def download_file():
    filename = request.args.get("filename")
    if not filename:
        return jsonify({"error": "No filename provided"}), 400

    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    response = send_file(file_path, as_attachment=True)

    try:
        os.remove(file_path)
    except Exception as e:
        print(f"Error removing file after sending: {e}")

    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
