#!/usr/bin/env python3
"""
Markdown to HTML converter
Usage: python md_to_html.py input.md [output.html]
"""

import sys
import markdown
import os.path

def convert_md_to_html(md_file, html_file=None):
    """
    Convert a Markdown file to HTML
    
    Args:
        md_file (str): Path to the Markdown file
        html_file (str, optional): Path to the output HTML file. If not provided,
                                  it will use the same name as the input file with .html extension
    
    Returns:
        str: Path to the generated HTML file
    """
    # If no output file is specified, use the input filename with .html extension
    if not html_file:
        base_name = os.path.splitext(md_file)[0]
        html_file = f"{base_name}.html"
    
    # Read the markdown file
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{md_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    # Convert markdown to HTML
    html_content = markdown.markdown(md_content)
    
    # Add basic HTML structure
    html_doc = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{os.path.basename(md_file)}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        code {{
            font-family: monospace;
        }}
        img {{
            max-width: 100%;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""
    
    # Write the HTML to a file
    try:
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_doc)
        print(f"Successfully converted '{md_file}' to '{html_file}'")
        return html_file
    except Exception as e:
        print(f"Error writing to file: {e}")
        sys.exit(1)

def main():
    # Check command line arguments
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} input.md [output.html]")
        sys.exit(1)
    
    md_file = sys.argv[1]
    html_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    convert_md_to_html(md_file, html_file)

if __name__ == "__main__":
    main()