from .openai_client import OpenAIImageClient
from .image_processor import ImageProcessor


class ColoringPageGenerator:
    """Main class for generating coloring pages."""
    
    def __init__(self, api_key: str):
        self.client = OpenAIImageClient(api_key)
        self.processor = ImageProcessor()
    
    def generate(self, prompt: str, output_filename: str, output_format: str) -> str:
        """Generate a coloring page from a prompt and save it."""
        
        # Generate image using OpenAI API
        image_data = self.client.generate_coloring_page(prompt)
        
        # Process image for coloring page
        processed_image = self.processor.process_for_coloring_page(image_data)
        
        # Save in requested format
        if output_format.lower() == 'pdf':
            return self.processor.save_as_pdf(processed_image, output_filename)
        else:  # default to PNG
            return self.processor.save_as_png(processed_image, output_filename)
