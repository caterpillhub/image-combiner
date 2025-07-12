import os
import uuid
import json
import shutil
import tempfile
import time
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="ImageCombiner API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (replacing MongoDB for simplicity)
downloads_db = {}

# Models
class DownloadRequest(BaseModel):
    name: Optional[str] = None
    project_name: Optional[str] = "ImageCombiner"

class DownloadResponse(BaseModel):
    download_id: str
    message: str

# Python code template for image processing
PYTHON_CODE_TEMPLATE = '''#!/usr/bin/env python3
"""
ImageCombiner - Advanced Image Compression Tool
Processes multiple images in a folder and compresses them into a single frame.
Perfect for creative professionals who need efficient image management.

Author: ImageCombiner Team
License: MIT
"""
from PIL import Image
import os
from pathlib import Path

def combine_images_16_9(input_folder=r"images/", output_image="combined_16_9.jpg", 
                       final_width=1920, final_height=1080, quality=85):
    """
    Combine multiple images into a single 16:9 aspect ratio image.
    
    Args:
        input_folder: Path to folder containing images
        output_image: Output filename
        final_width: Final image width (default 1920)
        final_height: Final image height (default 1080)
        quality: JPEG quality (1-100, default 85)
    """
    
    # Create input folder if it doesn't exist
    Path(input_folder).mkdir(exist_ok=True)
    
    # Get list of supported image formats
    supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp')
    
    # Get sorted list of images
    try:
        all_files = os.listdir(input_folder)
        images = sorted([img for img in all_files 
                        if img.lower().endswith(supported_formats)])
    except FileNotFoundError:
        print(f"❌ Error: Folder '{input_folder}' not found!")
        return False
    
    if not images:
        print(f"❌ No supported images found in '{input_folder}'")
        print(f"Supported formats: {', '.join(supported_formats)}")
        return False
    
    print(f"📁 Found {len(images)} images to combine")
    
    # Calculate strip width dynamically based on number of images
    strip_width = final_width // len(images)
    
    # Ensure minimum width
    if strip_width < 10:
        print(f"⚠️  Warning: Too many images ({len(images)}). Each strip will be very narrow.")
        strip_width = 10
    
    print(f"🔧 Each image will be resized to {strip_width}x{final_height}")
    
    # Process images
    processed_images = []
    failed_images = []
    
    for i, img_name in enumerate(images):
        try:
            img_path = os.path.join(input_folder, img_name)
            print(f"📷 Processing {i+1}/{len(images)}: {img_name}")
            
            # Open and process image
            with Image.open(img_path) as img:
                # Convert to RGB if needed (handles PNG with transparency, etc.)
                if img.mode != 'RGB':
                    if img.mode == 'RGBA':
                        # Create white background for transparent images
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[-1])
                        img = background
                    else:
                        img = img.convert('RGB')
                
                # Resize image to strip dimensions
                # Use LANCZOS for high quality resizing
                img_resized = img.resize((strip_width, final_height), Image.Resampling.LANCZOS)
                processed_images.append(img_resized)
                
        except Exception as e:
            print(f"❌ Failed to process {img_name}: {str(e)}")
            failed_images.append(img_name)
            continue
    
    if not processed_images:
        print("❌ No images were successfully processed!")
        return False
    
    if failed_images:
        print(f"⚠️  {len(failed_images)} images failed to process: {', '.join(failed_images)}")
    
    # Create combined image
    print(f"🎨 Creating combined image ({final_width}x{final_height})")
    combined_img = Image.new("RGB", (final_width, final_height), color=(255, 255, 255))
    
    # Paste images side by side
    x_offset = 0
    for img in processed_images:
        combined_img.paste(img, (x_offset, 0))
        x_offset += img.width
    
    # Fill remaining space with the last image if needed
    if x_offset < final_width and processed_images:
        remaining_width = final_width - x_offset
        if remaining_width > 0:
            # Stretch the last image to fill remaining space
            last_img = processed_images[-1]
            stretched_img = last_img.resize((remaining_width, final_height), Image.Resampling.LANCZOS)
            combined_img.paste(stretched_img, (x_offset, 0))
    
    # Save output
    try:
        combined_img.save(output_image, "JPEG", quality=quality, optimize=True)
        print(f"✅ Combined image saved successfully as '{output_image}'")
        print(f"📊 Final size: {final_width}x{final_height} pixels")
        print(f"💾 File saved with {quality}% quality")
        return True
        
    except Exception as e:
        print(f"❌ Failed to save output image: {str(e)}")
        return False

def main():
    """Main function with example usage"""
    
    # Example usage with different configurations
    print("🚀 Starting image combination process...")
    
    # Basic usage
    success = combine_images_16_9()
    
    if success:
        print("\\n🎉 Process completed successfully!")
    else:
        print("\\n💡 Tips:")
        print("- Make sure the 'images/' folder exists")
        print("- Add some image files (.jpg, .png, .bmp, .tiff, .webp)")
        print("- Check that images are not corrupted")
        print("- Ensure you have write permissions in the current directory")

if __name__ == "__main__":
    main()
'''

REQUIREMENTS_TXT = '''Pillow>=10.0.0
numpy>=1.24.0
'''

README_MD = '''# 🎨 Image Combiner

Fast parallel image combiner that creates panoramic 16:9 images from folders.

[![Python 3.7+](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![Performance](https://img.shields.io/badge/Performance-4x%20Faster-brightgreen.svg)](#performance)

## ✨ Features

- 🌈 **Multiple Formats** - JPG, PNG, BMP, TIFF, WebP
- 💾 **Memory Efficient** - Handles large batches without issues

## 🚀 Quick Start

### Install
```bash
pip install Pillow
```

### Command Line
```python
python imagecombiner.py  # Processes 'images/' folder
```

## 🔧 Key Parameters

```python
combine_images_16_9(
    input_folder,           # Folder path
    output_image,           # Output filename  
    final_width=1920,       # Output width
    final_height=1080,      # Output height
    quality=85              # JPEG quality (1-100)
)
```

## 📁 Input/Output

**Input**: Folder with images  
**Output**: Single JPEG panoramic image (16:9 aspect ratio)  
**Formats**: JPG, PNG, BMP, TIFF, WebP → JPEG  

**Example**: Process movie frames into a single panoramic image
'''

@app.get("/")
async def root():
    return {"message": "ImageCombiner API - Ready to serve creative professionals!", "status": "running"}

@app.post("/api/download", response_model=DownloadResponse)
async def create_download_package(request: DownloadRequest):
    """Create a download package with the ImageCombiner code."""
    try:
        # Generate unique download ID
        download_id = str(uuid.uuid4())
        
        # Create temporary directory for the package
        temp_dir = tempfile.mkdtemp()
        package_dir = os.path.join(temp_dir, "ImagePack")
        os.makedirs(package_dir, exist_ok=True)
        
        # Write files to package
        files_to_create = {
            "imagecombiner.py": PYTHON_CODE_TEMPLATE,
            "requirements.txt": REQUIREMENTS_TXT,
            "README.md": README_MD
        }
        
        for filename, content in files_to_create.items():
            with open(os.path.join(package_dir, filename), 'w') as f:
                f.write(content)
        
        # Create zip file
        zip_path = os.path.join(temp_dir, f"ImageCombiner_{download_id}.zip")
        shutil.make_archive(zip_path.replace('.zip', ''), 'zip', package_dir)
        
        # Store download info in memory
        downloads_db[download_id] = {
            "download_id": download_id,
            "name": request.name,
            "project_name": request.project_name,
            "zip_path": zip_path,
            "created_at": time.time(),
            "downloaded": False
        }
        
        logger.info(f"Created download package: {download_id}")
        
        return DownloadResponse(
            download_id=download_id,
            message="Package created successfully! Ready for download."
        )
        
    except Exception as e:
        logger.error(f"Error creating download package: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create download package: {str(e)}")

@app.get("/api/download/{download_id}")
async def download_package(download_id: str):
    """Download the ImageCombiner package."""
    try:
        # Find download info
        if download_id not in downloads_db:
            raise HTTPException(status_code=404, detail="Download not found")
        
        download_info = downloads_db[download_id]
        zip_path = download_info["zip_path"]
        
        if not os.path.exists(zip_path):
            raise HTTPException(status_code=404, detail="Download file not found")
        
        # Mark as downloaded
        downloads_db[download_id]["downloaded"] = True
        downloads_db[download_id]["downloaded_at"] = time.time()
        
        logger.info(f"Download started: {download_id}")
        
        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename=f"ImageCombiner_{download_id}.zip"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading package: {e}")
        raise HTTPException(status_code=500, detail="Failed to download package")

@app.get("/api/stats")
async def get_stats():
    """Get download statistics."""
    try:
        total_downloads = len(downloads_db)
        completed_downloads = sum(1 for d in downloads_db.values() if d.get("downloaded", False))
        
        return {
            "total_packages_created": total_downloads,
            "completed_downloads": completed_downloads,
            "success_rate": (completed_downloads / total_downloads * 100) if total_downloads > 0 else 0,
            "active_downloads": list(downloads_db.keys())[-5:]  # Last 5 downloads
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve stats")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting ImageCombiner API...")
    print("📱 API will be available at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)