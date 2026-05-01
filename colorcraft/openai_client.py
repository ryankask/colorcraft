import io
import base64
from openai import OpenAI


class OpenAIImageClient:
    """Client for OpenAI Image Generation API."""

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def generate_coloring_page(self, prompt: str) -> bytes:
        """Generate a coloring page image from a prompt."""

        # Enhance the prompt for coloring page style
        enhanced_prompt = self._enhance_prompt_for_coloring_page(prompt)

        response = self.client.images.generate(
            model="gpt-image-2",
            prompt=enhanced_prompt,
            size="1024x1536",  # Portrait A4-like ratio
            quality="medium",
            background="opaque",
            moderation="low",
        )

        if not response.data or not response.data[0].b64_json:
            raise ValueError("No image data received from OpenAI API")

        # Decode base64 image
        image_data = base64.b64decode(response.data[0].b64_json)
        return image_data

    def edit_coloring_page(self, image_data: bytes, adaptation: str = "") -> bytes:
        prompt = (
            "Convert this image into a black and white line drawing coloring page. "
            "Bold, clear black outlines (2-3px thick). "
            "Enclosed shapes for coloring. "
            "No shading, gradients, or gray tones. "
            "Clean, simple line art. "
            "White background. "
            "Ready to print on A4 paper."
        )
        if adaptation:
            prompt += f" Additional instructions: {adaptation}"

        image_file = io.BytesIO(image_data)
        image_file.name = "image.png"

        response = self.client.images.edit(
            model="gpt-image-2",
            image=image_file,
            prompt=prompt,
        )

        if not response.data or not response.data[0].b64_json:
            raise ValueError("No image data received from OpenAI API")

        return base64.b64decode(response.data[0].b64_json)

    def _enhance_prompt_for_coloring_page(self, prompt: str) -> str:
        """Enhance the user prompt with coloring page specific instructions."""
        coloring_page_style = (
            "Create a black and white line drawing coloring page of "
            f"{prompt}. "
            "Style requirements: "
            "- Bold, clear black outlines (2-3px thick) "
            "- Enclosed shapes and sections for easy coloring "
            "- No shading, gradients, or gray tones "
            "- Clean, simple line art style "
            "- White background "
            "- Ready to print on A4 paper"
        )
        return coloring_page_style
