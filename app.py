from flask import Flask, request, jsonify, render_template
from video_processor import VideoProcessor
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

GROQ_API_KEY = os.getenv('GROQ_API_KEY')
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY must be set in environment variables")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_video():
    try:
        data = request.get_json()
        if not data or 'video_url' not in data:
            return jsonify({'error': 'No video URL provided'}), 400

        processor = VideoProcessor(GROQ_API_KEY)
        transcript = processor.process_video(data['video_url'])
        if not transcript:
            return jsonify({'error': 'Failed to get video transcript'}), 400

        summary = processor.generate_summary(transcript)
        if not summary:
            return jsonify({'error': 'Failed to generate summary'}), 400

        return jsonify({
            'transcript': transcript,
            'summary': summary
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask_question():
    try:
        data = request.get_json()
        if not data or 'question' not in data or 'transcript' not in data:
            return jsonify({'error': 'Missing question or transcript'}), 400

        processor = VideoProcessor(GROQ_API_KEY)
        answer = processor.answer_question(data['question'], data['transcript'])
        if not answer:
            return jsonify({'error': 'Failed to answer question'}), 400

        return jsonify({'answer': answer})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 