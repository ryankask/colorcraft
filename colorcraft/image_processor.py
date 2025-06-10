from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import io
import os
from typing import Tuple


class ImageProcessor:
    """Process images for coloring pages and convert to different formats."""
    
    @staticmethod
    def process_for_coloring_page(image_data: bytes) -> Image.Image:
        """Process image to ensure it's suitable for a coloring page."""
        # Load image
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Ensure the image is high contrast black and white
        # This helps ensure clean lines for coloring
        image = ImageProcessor._enhance_contrast(image)
        
        return image
    
    @staticmethod
    def _enhance_contrast(image: Image.Image) -> Image.Image:
        """Enhance contrast to ensure clean black lines on white background."""
        # Convert to grayscale first
        grayscale = image.convert('L')
        
        # Apply threshold to make it pure black and white
        # This ensures clean lines for coloring
        threshold = 128
        black_white = grayscale.point(lambda x: 0 if x < threshold else 255, mode='1')
        
        # Convert back to RGB
        return black_white.convert('RGB')
    
    @staticmethod
    def save_as_png(image: Image.Image, output_path: str) -> str:
        """Save image as PNG in A4 proportions."""
        # Ensure output directory exists
        os.makedirs("output", exist_ok=True)
        
        # A4 dimensions at 300 DPI: 2480 x 3508 pixels
        a4_width, a4_height = 2480, 3508
        
        # Resize image to fit A4 while maintaining aspect ratio
        image_resized = ImageProcessor._resize_to_fit(image, (a4_width, a4_height))
        
        # Create A4 canvas and center the image
        a4_image = Image.new('RGB', (a4_width, a4_height), 'white')
        
        # Calculate position to center the image
        x = (a4_width - image_resized.width) // 2
        y = (a4_height - image_resized.height) // 2
        
        a4_image.paste(image_resized, (x, y))
        
        png_path = f"output/{output_path}.png"
        a4_image.save(png_path, 'PNG', dpi=(300, 300))
        return png_path
    
    @staticmethod
    def save_as_pdf(image: Image.Image, output_path: str) -> str:
        """Save image as PDF in A4 format."""
        # Ensure output directory exists
        os.makedirs("output", exist_ok=True)
        
        pdf_path = f"output/{output_path}.pdf"
        pdf_bytes = ImageProcessor.create_pdf_bytes(image)
        
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        
        return pdf_path
    
    @staticmethod
    def create_pdf_bytes(image: Image.Image) -> bytes:
        """Create PDF bytes from image in A4 format."""
        # Create PDF buffer
        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=A4)
        width, height = A4
        
        # Convert PIL image to bytes for reportlab
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Resize image to fit A4 while maintaining aspect ratio
        img_width, img_height = image.size
        aspect_ratio = img_width / img_height
        
        # Calculate dimensions to fit A4
        if aspect_ratio > width / height:
            # Image is wider, fit to width
            new_width = width - 40  # 20pt margin on each side
            new_height = new_width / aspect_ratio
        else:
            # Image is taller, fit to height
            new_height = height - 40  # 20pt margin on top/bottom
            new_width = new_height * aspect_ratio
        
        # Center the image
        x = (width - new_width) / 2
        y = (height - new_height) / 2
        
        # Draw image on PDF
        c.drawImage(ImageReader(img_buffer), x, y, new_width, new_height)
        c.save()
        
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()
    
    @staticmethod
    def _resize_to_fit(image: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
        """Resize image to fit within target size while maintaining aspect ratio."""
        target_width, target_height = target_size
        img_width, img_height = image.size
        
        # Calculate scaling factor
        scale_w = target_width / img_width
        scale_h = target_height / img_height
        scale = min(scale_w, scale_h)
        
        # Calculate new dimensions
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
