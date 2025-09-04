# -*- coding: utf-8 -*-
import requests
from lxml import html
import dotenv
import os
import datetime
import urllib.parse
from pathlib import Path

# load the environment variables
dotenv.load_dotenv()

# get configuration from environment variables
year = int(os.getenv('YEAR', 2024))
url = os.getenv('URL')
filename = os.getenv('FILENAME', f"crawled-page-{year}.html")
image_folder = os.getenv('IMAGE_FOLDER', 'images')

print(f"Scraping page: {url}")
print(f"Saving HTML file: {filename}")
print(f"Image save directory: {image_folder}")

# create images directory if it doesn't exist
os.makedirs(image_folder, exist_ok=True)

# initialize the data list
downloaded_images = []

# check if the page exists
if not os.path.exists(filename):
    print("Fetching page from network...")
    
    # fetch the page if it doesn't exist
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # save the page to a file
        with open(filename, 'w', encoding='UTF-8') as f:
            f.write(response.text)
        
        page_content = response.text
        print(f"Page saved to: {filename}")
        
    except requests.RequestException as e:
        print(f"Failed to fetch page: {e}")
        exit(1)

else:
    print("Reading page from local file...")
    # if the page exists, read it from the file
    with open(filename, 'r', encoding='UTF-8') as f:
        page_content = f.read()

# parse the page to html
tree = html.fromstring(page_content)

# get all image elements
images = tree.xpath('//img[@src]')

print(f"Found {len(images)} image elements")

# function to download image
def download_image(img_url, save_path):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': url
        }
        response = requests.get(img_url, headers=headers, stream=True)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
    except Exception as e:
        print(f"Failed to download image {img_url}: {e}")
        return False

# download each image
for i, img in enumerate(images):
    src = img.get('src')
    alt = img.get('alt', f'image_{i}')
    
    if not src:
        continue
    
    # handle relative URLs
    if src.startswith('//'):
        img_url = 'https:' + src
    elif src.startswith('/'):
        base_url = urllib.parse.urljoin(url, '/')
        img_url = urllib.parse.urljoin(base_url, src)
    elif not src.startswith('http'):
        img_url = urllib.parse.urljoin(url, src)
    else:
        img_url = src
    
    # skip data URLs and SVGs
    if src.startswith('data:') or 'svg' in src.lower():
        continue
    
    # get file extension from URL
    parsed_url = urllib.parse.urlparse(img_url)
    path = parsed_url.path
    ext = os.path.splitext(path)[1]
    
    # if no extension, try to get from query params or default to .jpg
    if not ext:
        if 'format=' in parsed_url.query:
            format_param = [param for param in parsed_url.query.split('&') if param.startswith('format=')]
            if format_param:
                ext = '.' + format_param[0].split('=')[1]
        else:
            ext = '.jpg'
    
    # clean filename
    safe_alt = "".join(c for c in alt if c.isalnum() or c in (' ', '-', '_')).rstrip()
    if not safe_alt:
        safe_alt = f'image_{i}'
    
    filename_img = f"{safe_alt}{ext}"
    save_path = os.path.join(image_folder, filename_img)
    
    # handle duplicate filenames
    counter = 1
    original_save_path = save_path
    while os.path.exists(save_path):
        name, ext = os.path.splitext(original_save_path)
        save_path = f"{name}_{counter}{ext}"
        counter += 1
    
    print(f"Downloading: {img_url}")
    print(f"Saving as: {save_path}")
    
    if download_image(img_url, save_path):
        downloaded_images.append({
            'url': img_url,
            'alt': alt,
            'saved_path': save_path
        })
        print(f"Success")
    else:
        print(f"Failed")
    
    print("-" * 50)

print(f"\nSummary:")
print(f"Successfully downloaded {len(downloaded_images)} images")
print(f"Images saved in: {os.path.abspath(image_folder)} directory")

# save download summary
summary_file = 'download_summary.txt'
with open(summary_file, 'w', encoding='UTF-8') as f:
    f.write(f"Image Download Summary - {datetime.datetime.now()}\n")
    f.write(f"Source page: {url}\n")
    f.write(f"Total downloaded: {len(downloaded_images)} images\n\n")
    
    for i, img_info in enumerate(downloaded_images, 1):
        f.write(f"{i}. {img_info['alt']}\n")
        f.write(f"   URL: {img_info['url']}\n")
        f.write(f"   Save path: {img_info['saved_path']}\n\n")

print(f"Download summary saved to: {summary_file}")
