default:
    @just --list

install:
    uv sync

cli-demo:
    uv run python -m colorcraft "a friendly dragon playing in a garden"

cli prompt output="coloring_page" format="png":
    uv run python -m colorcraft "{{prompt}}" --output {{output}} --format {{format}}

web:
    uv run python app.py

web-dev:
    FLASK_DEBUG=true uv run python app.py

docker-build:
    docker build -t colorcraft .

docker-build-registry:
    docker build -t zot.app.kaskel.net/colorcraft/web:latest .

docker-run:
    docker run -p 5000:5000 -e OPENAI_API_KEY="${OPENAI_API_KEY}" colorcraft

docker-run-registry:
    docker run -p 5000:5000 -e OPENAI_API_KEY="${OPENAI_API_KEY}" zot.app.kaskel.net/colorcraft/web:latest

docker-push:
    docker push zot.app.kaskel.net/colorcraft/web:latest

docker-deploy: docker-build-registry docker-push

docker-clean:
    docker rmi colorcraft || true
    docker rmi zot.app.kaskel.net/colorcraft/web:latest || true

sample-pdf:
    uv run python -m colorcraft "a magical castle with towers and flags" --format pdf --output sample_castle

sample-png:
    uv run python -m colorcraft "a cute puppy playing with a ball" --format png --output sample_puppy

check-api-key:
    @if [ -z "${OPENAI_API_KEY}" ]; then echo "❌ OPENAI_API_KEY environment variable is not set"; exit 1; else echo "✅ OPENAI_API_KEY is set"; fi

check: check-api-key
    @echo "✅ All checks passed"

deploy:
    @echo "Deploying"
    ssh tern "zsh --stdin" < scripts/deploy
