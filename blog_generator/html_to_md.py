#!/usr/bin/env python3
"""
HTML to Markdown converter
Usage: python html_to_md.py
"""

import os
import re
import shutil
from datetime import datetime
from bs4 import BeautifulSoup

def html_to_markdown(html_content):
    """Convert HTML content to Markdown"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract title
    title_tag = soup.find('title')
    title = title_tag.get_text().strip() if title_tag else "Untitled"
    
    # Extract main content (try common content selectors)
    content = soup.find('main') or soup.find('article') or soup.find('div', class_='content') or soup.find('body')
    
    if not content:
        return f"# {title}\n\nNo content found."
    
    today = datetime.now().strftime('%Y-%m-%d')
    markdown = f"---\ntitle: {title}\ndate: {today}\nstatus: published\n---\n\n"
    
    # Convert HTML elements to markdown
    for element in content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'strong', 'b', 'em', 'i', 'a', 'img', 'ul', 'ol', 'li']):
        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(element.name[1])
            markdown += f"{'#' * level} {element.get_text().strip()}\n\n"
        elif element.name == 'p':
            text = element.get_text().strip()
            if text:
                markdown += f"{text}\n\n"
        elif element.name in ['strong', 'b']:
            markdown += f"**{element.get_text().strip()}**"
        elif element.name in ['em', 'i']:
            markdown += f"*{element.get_text().strip()}*"
        elif element.name == 'a':
            href = element.get('href', '')
            text = element.get_text().strip()
            markdown += f"[{text}]({href})"
        elif element.name == 'img':
            src = element.get('src', '')
            alt = element.get('alt', '')
            markdown += f"![{alt}]({src})\n\n"
    
    return markdown

def convert_html_files():
    """Convert all HTML files in kaons directory to markdown"""
    kaons_dir = "/home/ravia/work/projects/blogstack/kaons"
    output_dir = "/home/ravia/work/projects/blogstack/output"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Copy all image directories
    for item in os.listdir(kaons_dir):
        item_path = os.path.join(kaons_dir, item)
        if os.path.isdir(item_path) and item.endswith('_files'):
            dest_path = os.path.join(output_dir, item)
            if os.path.exists(dest_path):
                shutil.rmtree(dest_path)
            shutil.copytree(item_path, dest_path)
            print(f"Copied images: {item}")
    
    # Find HTML files
    html_files = [f for f in os.listdir(kaons_dir) if f.endswith('.html')]
    
    for html_file in html_files:
        html_path = os.path.join(kaons_dir, html_file)
        
        # Read HTML file
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Convert to markdown
        markdown_content = html_to_markdown(html_content)
        
        # Create output filename
        md_filename = html_file.replace('.html', '.md')
        md_path = os.path.join(output_dir, md_filename)
        
        # Write markdown file
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"Converted: {html_file} -> {md_filename}")

if __name__ == "__main__":
    convert_html_files()