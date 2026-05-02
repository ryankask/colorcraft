default:
    @just --list

install:
    uv sync

cli-demo:
    uv run python -m colorcraft --prompt "a friendly dragon playing in a garden"

cli prompt output="coloring_page" format="png":
    uv run python -m colorcraft --prompt "{{prompt}}" --output {{output}} --format {{format}}

cli-image image prompt="" output="coloring_page" format="png":
    uv run python -m colorcraft --image {{image}} {{ if prompt != "" { "--prompt \"" + prompt + "\"" } else { "" } }} --output {{output}} --format {{format}}

web:
    uv run python -m colorcraft.web_app

web-dev:
    FLASK_DEBUG=true uv run python -m colorcraft.web_app

podman-build:
    podman build -t colorcraft .

podman-build-registry:
    podman build -t zot.app.kaskel.net/colorcraft/web:latest .

podman-run:
    podman run -p 5000:5000 -e OPENAI_API_KEY="${OPENAI_API_KEY}" colorcraft

podman-run-registry:
    podman run -p 5000:5000 -e OPENAI_API_KEY="${OPENAI_API_KEY}" zot.app.kaskel.net/colorcraft/web:latest

podman-push:
    podman push zot.app.kaskel.net/colorcraft/web:latest

podman-deploy: podman-build-registry podman-push

podman-clean:
    podman rmi colorcraft || true
    podman rmi zot.app.kaskel.net/colorcraft/web:latest || true

sample-pdf:
    uv run python -m colorcraft --prompt "a magical castle with towers and flags" --format pdf --output sample_castle

sample-png:
    uv run python -m colorcraft --prompt "a cute puppy playing with a ball" --format png --output sample_puppy

check-api-key:
    @if [ -z "${OPENAI_API_KEY}" ]; then echo "❌ OPENAI_API_KEY environment variable is not set"; exit 1; else echo "✅ OPENAI_API_KEY is set"; fi

check: check-api-key
    @echo "✅ All checks passed"

deploy:
    @echo "Deploying"
    ssh tern "zsh --stdin" < scripts/deploy
