import requests
import base64
from typing import Dict, Any


class OpenAIImageClient:
    """Client for OpenAI Image Generation API."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/images/generations"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

    def generate_coloring_page(self, prompt: str) -> bytes:
        """Generate a coloring page image from a prompt."""

        # Enhance the prompt for coloring page style
        enhanced_prompt = self._enhance_prompt_for_coloring_page(prompt)

        payload = {
            "model": "gpt-image-1",
            "prompt": enhanced_prompt,
            "n": 1,
            "size": "1024x1536",  # Portrait A4-like ratio
            "output_format": "png",
            "background": "opaque",
            "quality": "medium",
            "moderation": "low",
        }

        response = requests.post(self.base_url, headers=self.headers, json=payload)
        response.raise_for_status()

        data = response.json()

        if not data.get("data") or not data["data"][0].get("b64_json"):
            raise ValueError("No image data received from OpenAI API")

        # Decode base64 image
        image_data = base64.b64decode(data["data"][0]["b64_json"])
        return image_data

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
