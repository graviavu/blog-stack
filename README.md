# Markdown to HTML Converter

A simple Python utility that converts Markdown files to styled HTML documents.

## Features

- Convert Markdown files to HTML with a single command
- Automatically applies basic styling to the generated HTML
- Supports standard Markdown syntax including headers, lists, code blocks, and images

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/markdown-to-html.git
   cd markdown-to-html
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Basic usage:
```
python md_to_html.py input.md
```

This will create an HTML file with the same name as your Markdown file.

To specify a custom output filename:
```
python md_to_html.py input.md output.html
```

## Example

```
python md_to_html.py blog_post.md blog_post.html
```

## Requirements

- Python 3.6+
- markdown package