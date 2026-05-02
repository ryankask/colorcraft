import os
import base64
from flask import Flask, render_template, request
from .coloring_page import ColoringPageGenerator
from .image_processor import ImageProcessor

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'heic', 'heif'}
MAX_IMAGE_SIZE = 50 * 1024 * 1024


def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


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
        generator = ColoringPageGenerator(api_key)

        image_data = generator.client.generate_coloring_page(prompt)
        processed_image = generator.processor.process_for_coloring_page(image_data)

        pdf_bytes = ImageProcessor.create_pdf_bytes(processed_image)
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

        return {
            'success': True,
            'pdf_data': pdf_base64,
            'filename': f'coloring_page_{prompt[:20].replace(" ", "_")}.pdf'
        }

    except Exception as e:
        return {'error': f'Error generating coloring page: {str(e)}'}, 500


@app.route('/generate-from-image', methods=['POST'])
def generate_from_image():
    if 'image' not in request.files:
        return {'error': 'Please provide an image.'}, 400

    image_file = request.files['image']

    if image_file.filename == '':
        return {'error': 'No image selected.'}, 400

    if not allowed_image(image_file.filename):
        return {'error': 'Please use a JPG, PNG, WebP, or HEIC image.'}, 400

    image_data = image_file.read()

    if len(image_data) > MAX_IMAGE_SIZE:
        return {'error': f'Image is too large. Please use an image under {MAX_IMAGE_SIZE // (1024*1024)}MB.'}, 400

    adaptation = request.form.get('adaptation', '').strip()

    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return {'error': 'OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.'}, 500

    try:
        generator = ColoringPageGenerator(api_key)

        if image_file.filename.rsplit('.', 1)[1].lower() in {'heic', 'heif'}:
            try:
                from pillow_heif import register_heif_opener
                register_heif_opener()
            except ImportError:
                return {'error': 'HEIC format is not supported. Please convert your image to JPG or PNG and try again.'}, 400

        edited_image_data = generator.client.edit_coloring_page(image_data, adaptation)
        processed_image = generator.processor.process_for_coloring_page(edited_image_data)

        pdf_bytes = ImageProcessor.create_pdf_bytes(processed_image)
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

        return {
            'success': True,
            'pdf_data': pdf_base64,
            'filename': 'coloring_page_from_image.pdf'
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
