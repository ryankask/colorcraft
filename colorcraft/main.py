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
