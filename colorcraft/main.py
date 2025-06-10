import click
from .coloring_page import ColoringPageGenerator


@click.command()
@click.argument('prompt')
@click.option('--output', '-o', default='coloring_page', help='Output filename (without extension)')
@click.option('--format', '-f', type=click.Choice(['png', 'pdf']), default='png', help='Output format')
@click.option('--api-key', envvar='OPENAI_API_KEY', required=True, help='OpenAI API key')
def main(prompt, output, format, api_key):
    """Generate a coloring page from a text prompt."""
    click.echo(f"Generating coloring page for: {prompt}")
    
    generator = ColoringPageGenerator(api_key)
    
    try:
        output_path = generator.generate(prompt, output, format)
        click.echo(f"Coloring page saved to: {output_path}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
