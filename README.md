# ColorCraft

A CLI tool for generating AI-powered coloring pages for kids using OpenAI's image generation API.

## Features

- Generate black and white line drawings perfect for coloring
- Export as PNG or PDF in A4 format
- Bold, clear outlines optimized for children
- Ready-to-print coloring pages
- Modular design for easy integration into web applications

## Installation

```bash
uv sync
```

## Usage

### Set up your OpenAI API key

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

### Running with Docker

Build and run the web application using Docker:

```bash
# Build the Docker image
docker build -t colorcraft .

# Run the web application
docker run -p 5000:5000 -e OPENAI_API_KEY="your-openai-api-key" colorcraft
```

The web interface will be available at http://localhost:5000

You can also customize the configuration:

```bash
# Run with custom port and debug mode
docker run -p 8080:8080 \
  -e OPENAI_API_KEY="your-openai-api-key" \
  -e FLASK_PORT=8080 \
  -e FLASK_DEBUG=true \
  colorcraft
```

### CLI Usage

#### Generate a coloring page

```bash
# Generate a PNG coloring page
uv run python -m colorcraft "a cute cat playing with a ball"

# Generate a PDF coloring page
uv run python -m colorcraft "a dinosaur in a forest" --format pdf --output dinosaur_page

# Specify custom output filename
uv run python -m colorcraft "a princess castle" --output my_castle --format png
```

#### Command Options

- `prompt` (required): Text description of what you want in the coloring page
- `--output, -o`: Output filename without extension (default: "coloring_page")
- `--format, -f`: Output format, either "png" or "pdf" (default: "png")
- `--api-key`: OpenAI API key (can also be set via OPENAI_API_KEY environment variable)

#### Examples

```bash
# Simple animal coloring page
uv run python -m colorcraft "a friendly elephant"

# More detailed scene
uv run python -m colorcraft "children playing in a playground with swings and slides" --format pdf

# Fantasy theme
uv run python -m colorcraft "a magical unicorn with rainbow mane" --output unicorn_magic
```

## Output

All generated images are:
- Optimized for A4 paper size
- High contrast black and white line art
- Bold outlines (2-3px thick) perfect for coloring
- Clean, simple designs suitable for children
- Ready to print at 300 DPI

## Requirements

- Python 3.13+
- OpenAI API key
- Internet connection for API calls

## Dependencies

- `requests`: For OpenAI API communication
- `Pillow`: For image processing
- `reportlab`: For PDF generation
- `click`: For CLI interface

## Development

This project was developed using [aider](https://aider.chat), an AI pair programming tool.
