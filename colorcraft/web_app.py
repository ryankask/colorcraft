import os
import base64
from flask import Flask, render_template, request
from .coloring_page import ColoringPageGenerator
from .image_processor import ImageProcessor

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.form.get('prompt', '').strip()

    if not prompt:
        return {'error': 'Please enter a prompt for your coloring page.'}, 400

    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return {'error': 'OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.'}, 500

    try:
        # Generate coloring page
        generator = ColoringPageGenerator(api_key)

        # Generate image data
        image_data = generator.client.generate_coloring_page(prompt)
        processed_image = generator.processor.process_for_coloring_page(image_data)

        # Create PDF bytes using ImageProcessor
        pdf_bytes = ImageProcessor.create_pdf_bytes(processed_image)
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

        return {
            'success': True,
            'pdf_data': pdf_base64,
            'filename': f'coloring_page_{prompt[:20].replace(" ", "_")}.pdf'
        }

    except Exception as e:
        return {'error': f'Error generating coloring page: {str(e)}'}, 500

if __name__ == '__main__':
    # Get configuration from environment variables
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', '5000'))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'

    # In production, use 0.0.0.0 by default
    if os.environ.get('FLASK_ENV') == 'production':
        host = os.environ.get('FLASK_HOST', '0.0.0.0')

    app.run(host=host, port=port, debug=debug)
