#!/usr/bin/env python3
"""
Markdown to HTML converter and blog site generator
Usage: 
  python md_to_html.py input.md [output.html]  # Convert single file
  python md_to_html.py --repo <github_url>     # Generate blog site from repo
"""

import sys
import markdown
import os
import os.path
import shutil
from datetime import datetime
import re
import yaml
import git

def load_template(template_name):
    """Load template file"""
    template_path = os.path.join(os.path.dirname(__file__), template_name)
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Template file '{template_name}' not found")
        sys.exit(1)

def convert_md_to_html(md_file, html_file=None):
    """Convert a Markdown file to HTML using template"""
    if not html_file:
        base_name = os.path.splitext(md_file)[0]
        html_file = f"{base_name}.html"
    
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{md_file}' not found.")
        sys.exit(1)
    
    html_content = markdown.markdown(md_content)
    template = load_template('simple.template')
    
    html_doc = template.replace('{{TITLE}}', os.path.basename(md_file))
    html_doc = html_doc.replace('{{CONTENT}}', html_content)
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_doc)
    print(f"Successfully converted '{md_file}' to '{html_file}'")
    return html_file

def clone_repo(repo_url, target_dir="temp_repo"):
    """Clone a GitHub repository using GitPython"""
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    
    try:
        git.Repo.clone_from(repo_url, target_dir)
        return target_dir
    except git.exc.GitCommandError as e:
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
                
                # Handle duplicate filenames by adding a counter
                counter = 1
                original_dst = dst_path
                while os.path.exists(dst_path):
                    name, ext = os.path.splitext(file)
                    dst_path = os.path.join(images_dir, f"{name}_{counter}{ext}")
                    counter += 1
                
                shutil.copy2(src_path, dst_path)
                copied_images[file] = os.path.basename(dst_path)
                print(f"Copied image: {file} -> /images/{os.path.basename(dst_path)}")
    
    return copied_images

def extract_repo_name(repo_url):
    """Extract repository name from GitHub URL"""
    # Remove .git suffix and get last part of URL
    repo_name = repo_url.rstrip('/').split('/')[-1]
    if repo_name.endswith('.git'):
        repo_name = repo_name[:-4]
    return repo_name

def generate_blog_site(repo_dir, repo_url):
    """Generate blog site from repository"""
    # Create output directory based on repo name
    repo_name = extract_repo_name(repo_url)
    output_dir = os.path.join('..', 'dist', repo_name)
    blogs_dir = os.path.join(repo_dir, "blogs")
    if not os.path.exists(blogs_dir):
        print("No 'blogs' directory found in repository")
        return
    
    # Create output directory
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    
    # Copy assets (images, etc.) from blogs directory
    copied_images = copy_assets(blogs_dir, output_dir)
    
    # Find all markdown files
    md_files = find_md_files(blogs_dir)
    
    published_blogs = []
    all_blogs = []
    
    # First pass: collect all blog info
    for md_file in md_files:
        rel_path = os.path.relpath(md_file, blogs_dir)
        
        # Read and extract metadata
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        title, date, status, author, tags = extract_metadata(md_content)
        
        # Determine output directory based on status
        if status == 'published':
            output_subdir = 'published'
        else:
            output_subdir = 'draft'
        
        blog_info = {
            'title': title,
            'path': f'{output_subdir}/{os.path.basename(rel_path).replace(".md", ".html")}',
            'date': date,
            'status': status,
            'author': author,
            'tags': tags,
            'md_path': rel_path,
            'md_file': md_file
        }
        
        all_blogs.append(blog_info)
        
        if status == 'published':
            published_blogs.append(blog_info)
    
    # Sort blogs by date (newest first)
    published_blogs.sort(key=lambda x: x['date'] or datetime.min, reverse=True)
    all_blogs.sort(key=lambda x: x['date'] or datetime.min, reverse=True)
    
    # Generate navigation HTML
    
    
    # Second pass: convert all markdown files with navigation
    for blog_info in all_blogs:
        md_file = blog_info['md_file']
        html_path = os.path.join(output_dir, blog_info['path'])
        
        # Create directory structure
        os.makedirs(os.path.dirname(html_path), exist_ok=True)
        
        # Read and convert
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Remove frontmatter before processing
        content_parts = md_content.split('---', 2)
        if len(content_parts) >= 3:
            content_without_frontmatter = content_parts[2].strip()
        else:
            content_without_frontmatter = md_content
        
        # Update image references to use /images/ path
        updated_md_content = update_image_references(content_without_frontmatter, copied_images)
        
        # Convert to HTML
        html_content = markdown.markdown(updated_md_content)
        
        # Use blog post template
        template = load_template('blog_post.template')
        html_doc = template.replace('{{TITLE}}', blog_info['title'])
        html_doc = html_doc.replace('{{SITE_TITLE}}', repo_name)
        # Remove unused navigation placeholder
        html_doc = html_doc.replace('{{NAVIGATION}}', '')
        html_doc = html_doc.replace('{{CONTENT}}', html_content)
        html_doc = html_doc.replace('{{COPYRIGHT}}', f'© 2024 {repo_name}')
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_doc)
    
    # Generate home page
    generate_home_page(published_blogs, all_blogs, output_dir, copied_images, repo_name)
    
    print(f"Generated blog site in '{output_dir}' directory")
    print(f"Found {len(published_blogs)} published blogs and {len(all_blogs)} total blogs")
    print(f"Assets copied to maintain directory structure")
    
    # Create published and draft directories
    os.makedirs(os.path.join(output_dir, 'published'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'draft'), exist_ok=True)

def update_image_references(md_content, copied_images):
    """Update markdown image references to use /images/ path"""
    import re
    
    # Pattern to match markdown images: ![alt](image.jpg)
    pattern = r'!\[([^\]]*)\]\(([^\)]+)\)'
    
    def replace_image(match):
        alt_text = match.group(1)
        image_path = match.group(2)
        
        # Extract just the filename from the path
        image_filename = os.path.basename(image_path)
        
        # Use the copied image name (handles duplicates)
        if image_filename in copied_images:
            new_filename = copied_images[image_filename]
            return f'![{alt_text}](../images/{new_filename})'
        else:
            # If image not found in copied images, use original filename
            return f'![{alt_text}](/images/{image_filename})'
    
    return re.sub(pattern, replace_image, md_content)



def generate_home_page(published_blogs, all_blogs, output_dir, copied_images, repo_name):
    """Generate the home page using the blog template"""
    # Generate article cards HTML
    articles_html = ""
    for blog in published_blogs[:10]:
        try:
            with open(blog['md_file'], 'r', encoding='utf-8') as f:
                md_content = f.read()
            # Remove frontmatter and get excerpt
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
                <article class="article-card" onclick="location.href='{blog['path']}'">
                    <div class="article-image">🧠</div>
                    <div class="article-content">
                        <h3 class="article-title">{blog['title']}</h3>
                        <div class="article-date">{date_str}</div>
                        <p class="article-excerpt">{excerpt}</p>
                        <a href="{blog['path']}" class="read-more">Read More →</a>
                    </div>
                </article>
"""
    
    # Load and use template
    template_path = os.path.join(os.path.dirname(__file__), '.', 'blog_home.template')
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
    except:
        print("Template file not found")
        return
    
    # Replace template variables
    home_content = template_content.replace('{{SITE_TITLE}}', repo_name)
    home_content = home_content.replace('{{ARTICLES_CONTENT}}', articles_html)
    home_content = home_content.replace('{{COPYRIGHT}}', f'© 2024 {repo_name}')


    
    with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(home_content)

def main():
    # Check command line arguments
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} input.md [output.html]")
        print(f"       {sys.argv[0]} --repo <github_url>")
        sys.exit(1)
    
    if sys.argv[1] == "--repo":
        if len(sys.argv) < 3:
            print("Please provide a GitHub repository URL")
            sys.exit(1)
        
        repo_url = sys.argv[2]
        print(f"Cloning repository: {repo_url}")
        repo_dir = clone_repo(repo_url)
        
        try:
            generate_blog_site(repo_dir, repo_url)
        finally:
            # Clean up
            if os.path.exists(repo_dir):
                shutil.rmtree(repo_dir)
    else:
        # Single file conversion
        md_file = sys.argv[1]
        html_file = sys.argv[2] if len(sys.argv) > 2 else None
        convert_md_to_html(md_file, html_file)

if __name__ == "__main__":
    main()