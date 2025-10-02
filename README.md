# BlogStack - Markdown Blog Site Generator

A Python utility that converts Markdown files to HTML and generates complete blog sites from GitHub repositories.

## Features

- Convert individual Markdown files to styled HTML
- Clone GitHub repositories and generate complete blog sites
- Automatically finds and converts blogs in `/blogs` directory
- Handles both published and unpublished blogs
- Generates home page with latest blog and hierarchical navigation
- Extracts metadata (title, date) from Markdown files
- Maintains folder structure in generated site

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/blogstack.git
   cd blogstack
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Single File Conversion
```
python md_to_html.py input.md
python md_to_html.py input.md output.html
```

### Generate Blog Site from GitHub Repository
```
python md_to_html.py --repo https://github.com/username/blog-repo.git
```

This will:
1. Clone the repository
2. Look for a `blogs/` directory
3. Convert all `.md` files to HTML
4. Generate a home page with navigation
5. Create the site in a `site/` directory

## Repository Structure

Your blog repository should have this structure:
```
your-repo/
├── blogs/
│   ├── 2024/
│   │   ├── my-first-post.md
│   │   └── another-post.md
│   ├── unpublished/
│   │   └── draft-post.md
│   └── tech/
│       └── python-tips.md
```

## Blog Metadata

Add metadata to your Markdown files:
```markdown
# My Blog Post Title
date: 2024-01-15

Your blog content here...
```

## Requirements

- Python 3.6+
- Git (for repository cloning)
- markdown package