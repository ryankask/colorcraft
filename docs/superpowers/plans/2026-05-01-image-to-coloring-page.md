# Image-to-Coloring-Page Implementation Plan (Phase 1: CLI + Model Upgrade)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the OpenAI model to gpt-image-2 and add CLI support for generating coloring pages from reference images.

**Architecture:** Add an `edit_coloring_page` method to `OpenAIImageClient` that calls `images.edit()` with a reference image. Modify the CLI to accept an optional `--image` flag that triggers the image flow. The `ColoringPageGenerator` gets a new `generate_from_image` method. Text-only flow remains unchanged.

**Tech Stack:** Python 3.13+, OpenAI Python SDK, Click, Pillow

---

### Task 1: Upgrade model to gpt-image-2

**Files:**
- Modify: `colorcraft/openai_client.py:18`

- [ ] **Step 1: Update model in `openai_client.py`**

In `colorcraft/openai_client.py`, change the model in `generate_coloring_page`:

```python
        response = self.client.images.generate(
            model="gpt-image-2",
            prompt=enhanced_prompt,
            size="1024x1536",
            quality="medium",
            background="opaque",
            moderation="low",
        )
```

- [ ] **Step 2: Test text-only generation still works**

Run: `uv run python -m colorcraft "a friendly elephant" --output test_model_upgrade`
Expected: Image generated successfully using gpt-image-2. No errors.

- [ ] **Step 3: Commit**

```bash
git add colorcraft/openai_client.py
git commit -m "feat: upgrade OpenAI model from gpt-image-1.5 to gpt-image-2"
```

---

### Task 2: Add `edit_coloring_page` method to `OpenAIImageClient`

**Files:**
- Modify: `colorcraft/openai_client.py`

- [ ] **Step 1: Add the new method to `OpenAIImageClient`**

Add this method to the class in `colorcraft/openai_client.py`, after `generate_coloring_page`:

```python
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

        response = self.client.images.edit(
            model="gpt-image-2",
            image=image_data,
            prompt=prompt,
        )

        if not response.data or not response.data[0].b64_json:
            raise ValueError("No image data received from OpenAI API")

        return base64.b64decode(response.data[0].b64_json)
```

Note: The `image` parameter for `images.edit()` accepts a file-like object or bytes. The OpenAI Python SDK handles both. We pass `image_data` as raw bytes, which the SDK wraps appropriately.

- [ ] **Step 2: Commit**

```bash
git add colorcraft/openai_client.py
git commit -m "feat: add edit_coloring_page method for image-based generation"
```

---

### Task 3: Add `generate_from_image` method to `ColoringPageGenerator`

**Files:**
- Modify: `colorcraft/coloring_page.py`

- [ ] **Step 1: Add the new method**

Add this method to the `ColoringPageGenerator` class in `colorcraft/coloring_page.py`, after the existing `generate` method:

```python
    def generate_from_image(self, image_data: bytes, adaptation: str, output_filename: str, output_format: str) -> str:
        edited_image_data = self.client.edit_coloring_page(image_data, adaptation)
        processed_image = self.processor.process_for_coloring_page(edited_image_data)

        if output_format.lower() == 'pdf':
            return self.processor.save_as_pdf(processed_image, output_filename)
        else:
            return self.processor.save_as_png(processed_image, output_filename)
```

- [ ] **Step 2: Commit**

```bash
git add colorcraft/coloring_page.py
git commit -m "feat: add generate_from_image method to ColoringPageGenerator"
```

---

### Task 4: Update CLI to support `--image` flag

**Files:**
- Modify: `colorcraft/main.py`

- [ ] **Step 1: Refactor CLI to support optional image input**

Replace the entire content of `colorcraft/main.py` with:

```python
import click
from .coloring_page import ColoringPageGenerator


@click.command()
@click.option('--image', '-i', type=click.Path(exists=True), help='Reference image to convert into a coloring page')
@click.option('--prompt', '-p', default='', help='Text prompt (required without --image) or adaptation instructions (with --image)')
@click.option('--output', '-o', default='coloring_page', help='Output filename (without extension)')
@click.option('--format', '-f', type=click.Choice(['png', 'pdf']), default='png', help='Output format')
@click.option('--api-key', envvar='OPENAI_API_KEY', required=True, help='OpenAI API key')
def main(image, prompt, output, format, api_key):
    if not image and not prompt:
        click.echo("Error: Provide a --prompt or an --image (or both).", err=True)
        raise click.Abort()

    generator = ColoringPageGenerator(api_key)

    try:
        if image:
            click.echo(f"Generating coloring page from image: {image}")
            if prompt:
                click.echo(f"  Adaptation: {prompt}")
            with open(image, 'rb') as f:
                image_data = f.read()
            output_path = generator.generate_from_image(image_data, prompt, output, format)
        else:
            click.echo(f"Generating coloring page for: {prompt}")
            output_path = generator.generate(prompt, output, format)

        click.echo(f"Coloring page saved to: {output_path}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
```

Key changes:
- `prompt` changes from a required positional argument to an optional `--prompt` / `-p` flag
- New `--image` / `-i` flag accepting a file path (validated to exist)
- Validation: at least one of `--image` or `--prompt` must be provided
- When `--image` is given, reads the file and calls `generate_from_image`
- When only `--prompt` is given, calls existing `generate` method

- [ ] **Step 2: Test text-only CLI still works**

Run: `uv run python -m colorcraft --prompt "a friendly elephant" --output test_text_only`
Expected: Works as before.

- [ ] **Step 3: Test image-based CLI**

Run: `uv run python -m colorcraft --image <path-to-test-image>.jpg --output test_from_image`
Expected: Generates a coloring page from the reference image.

- [ ] **Step 4: Test image with adaptation text**

Run: `uv run python -m colorcraft --image <path-to-test-image>.jpg --prompt "simplify for a 5-year-old" --output test_with_adaptation`
Expected: Generates a simplified coloring page from the reference image.

- [ ] **Step 5: Test error case (no prompt, no image)**

Run: `uv run python -m colorcraft`
Expected: Error message "Error: Provide a --prompt or an --image (or both)."

- [ ] **Step 6: Commit**

```bash
git add colorcraft/main.py
git commit -m "feat: add --image flag to CLI for reference-image coloring pages"
```

---

### Task 5: Update justfile with new CLI examples

**Files:**
- Modify: `justfile`

- [ ] **Step 1: Add image-based recipes**

Add these recipes to `justfile`, after the existing `cli` recipe:

```just
cli-image image prompt="" output="coloring_page" format="png":
    uv run python -m colorcraft --image {{image}} {{ if prompt != "" { "--prompt \"" + prompt + "\"" } else { "" } }} --output {{output}} --format {{format}}

cli-image-demo:
    uv run python -m colorcraft --image sample_beyblade.jpg --prompt "simplify for a 5-year-old" --output beyblade_coloring
```

- [ ] **Step 2: Update existing `cli` recipe to use `--prompt` flag**

Change the `cli` recipe from:

```just
cli prompt output="coloring_page" format="png":
    uv run python -m colorcraft "{{prompt}}" --output {{output}} --format {{format}}
```

To:

```just
cli prompt output="coloring_page" format="png":
    uv run python -m colorcraft --prompt "{{prompt}}" --output {{output}} --format {{format}}
```

Also update `cli-demo`:

```just
cli-demo:
    uv run python -m colorcraft --prompt "a friendly dragon playing in a garden"
```

- [ ] **Step 3: Commit**

```bash
git add justfile
git commit -m "feat: add justfile recipes for image-based CLI usage"
```
