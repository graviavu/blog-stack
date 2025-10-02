#!/usr/bin/env python3
"""
Blog generator with YAML frontmatter support
Usage: python blog_generator.py --repo <github_url>
"""

import sys
import markdown
import os
import subprocess
import shutil
from datetime import datetime
import re
import yaml

def clone_repo(repo_url, target_dir="temp_repo"):
    """Clone a GitHub repository"""
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    
    try:
        subprocess.run(["git", "clone", repo_url, target_dir], check=True, capture_output=True)
        return target_dir
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e}")
        sys.exit(1)

def extract_metadata(md_content):
    """Extract metadata from YAML frontmatter"""
    if not md_content.startswith('---'):
        return "Untitled", None, "draft", "", []
    
    try:
        parts = md_content.split('---', 2)
        if len(parts) < 3:
            return "Untitled", None, "draft", "", []
        
        frontmatter = parts[1].strip()
        metadata = yaml.safe_load(frontmatter)
        
        title = metadata.get('title', 'Untitled')
        date_str = metadata.get('date')
        status = metadata.get('status', 'draft')
        author = metadata.get('author', '')
        tags = metadata.get('tags', [])
        
        date = None
        if date_str:
            try:
                date = datetime.strptime(str(date_str), '%Y-%m-%d')
            except ValueError:
                pass
        
        return title, date, status, author, tags
    except:
        return "Untitled", None, "draft", "", []

def find_md_files(directory):
    """Find all markdown files in directory and subdirectories"""
    md_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))
    return md_files

def copy_assets(blogs_dir, output_dir):
    """Copy images to centralized /images directory"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.bmp', '.ico'}
    images_dir = os.path.join(output_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)
    
    copied_images = {}
    
    for root, dirs, files in os.walk(blogs_dir):
        for file in files:
            file_ext = os.path.splitext(file)[1].lower()
            if file_ext in image_extensions:
                src_path = os.path.join(root, file)
                dst_path = os.path.join(images_dir, file)
                
                counter = 1
                while os.path.exists(dst_path):
                    name, ext = os.path.splitext(file)
                    dst_path = os.path.join(images_dir, f"{name}_{counter}{ext}")
                    counter += 1
                
                shutil.copy2(src_path, dst_path)
                copied_images[file] = os.path.basename(dst_path)
                print(f"Copied image: {file} -> /images/{os.path.basename(dst_path)}")
    
    return copied_images

def update_image_references(md_content, copied_images):
    """Update markdown image references to use /images/ path"""
    pattern = r'!\[([^\]]*)\]\(([^\)]+)\)'
    
    def replace_image(match):
        alt_text = match.group(1)
        image_path = match.group(2)
        image_filename = os.path.basename(image_path)
        
        if image_filename in copied_images:
            new_filename = copied_images[image_filename]
            return f'![{alt_text}](/images/{new_filename})'
        else:
            return f'![{alt_text}](/images/{image_filename})'
    
    return re.sub(pattern, replace_image, md_content)

def generate_home_page(published_blogs, output_dir):
    """Generate the home page using the blog template"""
    articles_html = ""
    for blog in published_blogs[:10]:
        try:
            with open(blog['md_file'], 'r', encoding='utf-8') as f:
                md_content = f.read()
            content_parts = md_content.split('---', 2)
            if len(content_parts) >= 3:
                content = content_parts[2].strip()
            else:
                content = md_content
            
            excerpt = content[:150] + "..." if len(content) > 150 else content
            excerpt = re.sub(r'[#*`]', '', excerpt)
        except:
            excerpt = "No preview available..."
        
        date_str = blog['date'].strftime('%B %d, %Y') if blog['date'] else 'No date'
        
        articles_html += f"""
                <article class="article-card" onclick="location.href='/{blog['path']}'">
                    <div class="article-image">🧠</div>
                    <div class="article-content">
                        <h3 class="article-title">{blog['title']}</h3>
                        <div class="article-date">{date_str}</div>
                        <p class="article-excerpt">{excerpt}</p>
                        <a href="/{blog['path']}" class="read-more">Read More →</a>
                    </div>
                </article>"""
    
    template_path = os.path.join(os.path.dirname(__file__), 'blog_home_template.html')
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
    except:
        template_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Neural Networks Hub</title>
</head>
<body>
    <h1>Neural Networks Hub</h1>
    <div class="articles-grid">
        {articles}
    </div>
</body>
</html>"""
    
    # Replace template articles with actual blog data
    home_content = re.sub(
        r'<div class="articles-grid">.*?</div>',
        f'<div class="articles-grid">{articles_html}\n            </div>',
        template_content,
        flags=re.DOTALL
    )
    
    with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(home_content)

def generate_blog_site(repo_dir, output_dir="site"):
    """Generate blog site from repository"""
    blogs_dir = os.path.join(repo_dir, "blogs")
    if not os.path.exists(blogs_dir):
        print("No 'blogs' directory found in repository")
        return
    
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    
    # Create published and draft directories
    os.makedirs(os.path.join(output_dir, 'published'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'draft'), exist_ok=True)
    
    copied_images = copy_assets(blogs_dir, output_dir)
    md_files = find_md_files(blogs_dir)
    
    published_blogs = []
    all_blogs = []
    
    # Process all markdown files
    for md_file in md_files:
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        title, date, status, author, tags = extract_metadata(md_content)
        
        # Determine output directory based on status
        output_subdir = 'published' if status == 'published' else 'draft'
        
        blog_info = {
            'title': title,
            'path': f'{output_subdir}/{os.path.basename(md_file).replace(".md", ".html")}',
            'date': date,
            'status': status,
            'author': author,
            'tags': tags,
            'md_file': md_file
        }
        
        all_blogs.append(blog_info)
        if status == 'published':
            published_blogs.append(blog_info)
        
        # Generate HTML file
        html_path = os.path.join(output_dir, blog_info['path'])
        os.makedirs(os.path.dirname(html_path), exist_ok=True)
        
        # Remove frontmatter from content
        content_parts = md_content.split('---', 2)
        if len(content_parts) >= 3:
            content_only = content_parts[2].strip()
        else:
            content_only = md_content
        
        updated_md_content = update_image_references(content_only, copied_images)
        html_content = markdown.markdown(updated_md_content)
        
        html_doc = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
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
        .meta {{
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #eee;
        }}
        .nav {{
            margin-bottom: 20px;
        }}
        .nav a {{
            color: #007acc;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="nav">
        <a href="/index.html">← Back to Home</a>
    </div>
    <div class="meta">
        <strong>{title}</strong><br>
        {f'By {author} | ' if author else ''}{date.strftime('%B %d, %Y') if date else 'No date'} | Status: {status}
    </div>
{html_content}
</body>
</html>
"""
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_doc)
    
    # Sort published blogs by date (newest first)
    published_blogs.sort(key=lambda x: x['date'] or datetime.min, reverse=True)
    
    # Generate home page
    generate_home_page(published_blogs, output_dir)
    
    print(f"Generated blog site in '{output_dir}' directory")
    print(f"Found {len(published_blogs)} published blogs and {len(all_blogs)} total blogs")

def main():
    if len(sys.argv) < 3 or sys.argv[1] != "--repo":
        print("Usage: python blog_generator.py --repo <github_url>")
        sys.exit(1)
    
    repo_url = sys.argv[2]
    print(f"Cloning repository: {repo_url}")
    repo_dir = clone_repo(repo_url)
    
    try:
        generate_blog_site(repo_dir)
    finally:
        if os.path.exists(repo_dir):
            shutil.rmtree(repo_dir)

if __name__ == "__main__":
    main()