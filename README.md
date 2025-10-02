# BlogStack - Markdown Blog Site Generator

A Python utility that converts Markdown files to HTML and generates complete blog sites from GitHub repositories.

## Features

- Convert individual Markdown files to styled HTML
- Clone GitHub repositories and generate complete blog sites
- Automatically finds and converts blogs in `/blogs` directory
- Handles both published and unpublished blogs
- Generates home page with blog preview cards and images
- Extracts metadata (title, date, author, tags) from YAML frontmatter
- Centralized image management with duplicate handling
- Google Analytics integration with per-repository tracking
- Responsive design with proper heading and paragraph spacing
- HTML to Markdown conversion utility

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/blogstack.git
   cd blogstack/blog_generator
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
3. Convert all `.md` files to HTML with frontmatter processing
4. Copy and organize images to centralized `/images/` directory
5. Generate home page with blog preview cards
6. Organize blogs by status (published/draft)
7. Create the site in `../dist/repo-name/` directory

### Convert HTML to Markdown
```
python html_to_md.py
```

Converts HTML files in `kaons/` directory to Markdown files in `output/` directory with:
- YAML frontmatter generation
- Image directory copying
- Current date metadata

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

Add YAML frontmatter to your Markdown files:
```markdown
---
title: My Blog Post Title
date: 2024-01-15
author: Your Name
status: published
tags: [tech, tutorial]
---

Your blog content here...
```

## Google Analytics Integration

Create `analytics.conf` file with repository-to-tracking-ID mapping:
```
MindWorks=G-XXXXXXXXX
my-blog-repo=G-XXXXXXXXXX
```

The system will automatically add Google Analytics tracking to all pages based on the repository name.

## Requirements

- Python 3.6+
- Git (for repository cloning)
- Dependencies listed in `requirements.txt`:
  - markdown>=3.4.0
  - PyYAML>=6.0
  - GitPython>=3.1.0
  - beautifulsoup4>=4.9.0

## File Structure

```
blogstack/
├── blog_generator/
│   ├── md_to_html.py          # Main blog generator
│   ├── html_to_md.py          # HTML to Markdown converter
│   ├── blog_post.template     # Blog post HTML template
│   ├── blog_home.template     # Home page HTML template
│   ├── analytics.template     # Google Analytics script template
│   ├── analytics.conf         # GA tracking ID configuration
│   └── requirements.txt       # Python dependencies
└── output/                    # Generated sites and converted files
```