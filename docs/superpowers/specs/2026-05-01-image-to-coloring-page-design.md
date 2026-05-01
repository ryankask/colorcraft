# Image-to-Coloring-Page Feature Design

## Problem

Kids want coloring pages of specific real-world things that are hard to describe in text — a particular BeyBlade X character, a specific toy, a photo of something they found. The current ColorCraft only accepts text prompts, making it impossible to create coloring pages from reference images.

## Solution

Add a second input mode alongside the existing text-only flow: upload or paste a reference image, optionally describe how to adapt it, and generate a coloring page from it.

## UI Design

### Tab switcher

Two tabs at the top of the card, under the header:

**"Describe it" tab** (default, matches current behavior):
- Existing textarea for describing a coloring page
- Generate button as-is
- No changes to current functionality

**"Use a picture" tab**:
- Image input area with two input methods:
  - **Paste support** — page-level `paste` event listener; on iOS or desktop, long-press paste or Cmd+V an image from clipboard
  - **File picker** — a "Browse" button/area that opens the native file dialog (accepts jpg, png, webp, heic)
- Thumbnail preview of the pasted/uploaded image, with an X button to remove it
- Optional text field: "Adapt it (optional)" — placeholder like "e.g., simplify for younger kids, show from the side, add a background"
- Generate button

Tab state persists — switching tabs preserves entered content.

## Backend Design

### New endpoint: `POST /generate-from-image`

Receives:
- Reference image as a file upload (multipart form data)
- Optional `adaptation` text field

Flow:
1. Receive the image, read into bytes
2. If HEIC format, convert to JPEG server-side before sending to OpenAI
3. Call OpenAI `images.edit()` endpoint with `model="gpt-image-2"`, passing the reference image and an enhanced coloring-page prompt
4. Post-process through existing `ImageProcessor.process_for_coloring_page()` pipeline
5. Return same JSON format as `/generate`: `{ success: true, pdf_data: <base64>, filename: <string> }`

### Prompt construction for image mode

Base prompt:
```
Convert this image into a black and white line drawing coloring page.
Bold, clear black outlines (2-3px thick).
Enclosed shapes for coloring.
No shading, gradients, or gray tones.
Clean, simple line art.
White background.
Ready to print on A4 paper.
```

With adaptation text, append:
```
Additional instructions: <user's adaptation text>
```

Without adaptation text, the base prompt alone is sufficient — the model will convert the image to a coloring page as-is.

### Existing `/generate` endpoint

No changes to the endpoint contract. Model upgrade only (see below).

### Model upgrade

Both endpoints move from `gpt-image-1.5` to `gpt-image-2`:
- `/generate` calls `client.images.generate(model="gpt-image-2", ...)` — same call, updated model
- `/generate-from-image` calls `client.images.edit(model="gpt-image-2", image=..., prompt=...)`

Quality stays `medium` for both ($0.041/portrait for gpt-image-2 at medium).

## CLI Design

Add `--image` option to the existing CLI:

```bash
# Existing text-only (unchanged)
colorcraft "a friendly dragon playing in a garden"

# New: image with adaptation text
colorcraft --image beyblade.jpg "simplify for a 5-year-old"

# New: image without adaptation text
colorcraft --image beyblade.jpg
```

When `--image` is provided:
- The `prompt` argument becomes optional — it changes from a required positional argument to an optional flag (adaptation text)
- The image is used as the reference
- Calls `images.edit()` instead of `images.generate()`
- Implementation note: the current `click.argument('prompt')` will need to become a `click.option('--prompt', '-p')` so it can be omitted when `--image` is used without adaptation text

When `--image` is not provided:
- `prompt` is required (current behavior)
- Calls `images.generate()` (current behavior, updated model)

## Error Handling

- **No image provided** in web form → client-side validation, same as current empty-prompt check
- **Image too large** (over 50MB, OpenAI's limit) → reject on upload with clear message
- **Unsupported format** → validate file type on upload, accept JPEG, PNG, WebP, HEIC; reject others
- **Paste event with non-image data** → silently ignore, only process clipboard images
- **OpenAI API error** (content moderation, etc.) → same error handling as current endpoint, surface error to user
- **HEIC conversion failure** → error message suggesting user convert to JPEG and re-upload

## Image Constraints

- Max file size: 50MB
- Accepted formats: JPEG, PNG, WebP, HEIC
- HEIC is converted to JPEG server-side before sending to OpenAI (using `pillow-heif` plugin for Pillow)
- gpt-image-2 always processes input images at high fidelity — no `input_fidelity` parameter needed
- No transparent background support for gpt-image-2 (opaque white is what we want)

## Implementation Order

**Phase 1: CLI + model upgrade** (test the core flow first)
- Upgrade model from `gpt-image-1.5` to `gpt-image-2` in `openai_client.py`
- Add `images.edit()` method to `OpenAIImageClient` for image-to-coloring-page generation
- Add `--image` option to CLI with optional prompt
- Test and validate with real images before building web UI

**Phase 2: Web UI** (after CLI validates the approach)
- Tab switcher UI
- New `/generate-from-image` endpoint
- Paste support and file picker
- HEIC conversion
- Client-side and server-side validation

Out of scope:
- Multi-turn / iterative editing (could be a future enhancement using the Responses API)
- Multiple reference images
- Mask-based partial editing
