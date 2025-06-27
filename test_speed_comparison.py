#!/usr/bin/env python3
"""
Speed comparison test for CollectorSage image processing endpoints
Tests both /process_image and /process_image_fast endpoints
"""

import requests
import time
import os
import json
from pathlib import Path

# Configuration
BASE_URL = "http://127.0.0.1:8000"
TEST_IMAGE_DIR = "uploads"

def find_test_images():
    """Find available test images in the uploads directory"""
    if not os.path.exists(TEST_IMAGE_DIR):
        print(f"❌ Test image directory '{TEST_IMAGE_DIR}' not found")
        return []
    
    image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    images = []
    
    for file in os.listdir(TEST_IMAGE_DIR):
        if any(file.lower().endswith(ext) for ext in image_extensions):
            images.append(os.path.join(TEST_IMAGE_DIR, file))
    
    return images

def test_server_health():
    """Test if the server is running"""
    try:
        response = requests.get(f"{BASE_URL}/test", timeout=5)
        return True
    except requests.exceptions.RequestException:
        return False

def test_endpoint(endpoint_path, image_path, test_name):
    """Test a specific endpoint with timing"""
    print(f"\n🔄 Testing {test_name} ({endpoint_path})...")
    
    try:
        with open(image_path, 'rb') as f:
            files = {'image': f}
            
            start_time = time.time()
            response = requests.post(f"{BASE_URL}{endpoint_path}", files=files, timeout=60)
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            print(f"⏱️  {test_name} processing time: {processing_time:.2f} seconds")
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if timing info is included in response
                if 'processingTime' in data:
                    print(f"🎯 Server-reported time: {data['processingTime']}")
                
                # Extract comic details if available
                if 'comicDetails' in data:
                    comic = data['comicDetails']
                    print(f"📚 Comic: {comic.get('title', 'N/A')} #{comic.get('issue_number', 'N/A')} ({comic.get('year', 'N/A')})")
                    print(f"💰 Price range: £{comic.get('min_price', 'N/A')} - £{comic.get('max_price', 'N/A')}")
                
                print(f"✅ {test_name} succeeded")
                return processing_time, True, data
            else:
                print(f"❌ {test_name} failed: {response.text}")
                return processing_time, False, None
                
    except requests.exceptions.Timeout:
        print(f"⏰ {test_name} timed out after 60 seconds")
        return 60.0, False, None
    except Exception as e:
        print(f"❌ {test_name} error: {str(e)}")
        return 0, False, None

def main():
    print("🚀 CollectorSage Speed Optimization Test")
    print("=" * 50)
    
    # Check server health
    if not test_server_health():
        print("❌ Server is not running at http://127.0.0.1:5000")
        print("Please start the server with: python main_v2.py")
        return
    
    print("✅ Server is running")
    
    # Find test images
    test_images = find_test_images()
    if not test_images:
        print("❌ No test images found in uploads directory")
        print("Please add some comic book images to the uploads/ directory")
        return
    
    print(f"📸 Found {len(test_images)} test image(s)")
    
    # Test each image
    for i, image_path in enumerate(test_images[:3]):  # Test up to 3 images
        print(f"\n{'='*60}")
        print(f"🖼️  Testing with image {i+1}: {os.path.basename(image_path)}")
        print(f"{'='*60}")
        
        # Test regular endpoint
        regular_time, regular_success, regular_data = test_endpoint(
            "/process_image", image_path, "Regular endpoint"
        )
        
        # Test fast endpoint
        fast_time, fast_success, fast_data = test_endpoint(
            "/process_image_fast", image_path, "Fast endpoint"
        )
        
        # Calculate improvement
        if regular_success and fast_success and regular_time > 0:
            improvement = ((regular_time - fast_time) / regular_time) * 100
            print(f"\n📈 Speed improvement: {improvement:.1f}% faster")
            print(f"⚡ Time saved: {regular_time - fast_time:.2f} seconds")
            
            if improvement >= 60:
                print("🎯 Target improvement achieved (60%+)!")
            elif improvement >= 40:
                print("✅ Good improvement achieved (40%+)")
            else:
                print("⚠️  Improvement below target (<40%)")
        else:
            print("❌ Could not calculate improvement due to failures")
        
        # Compare results quality
        if regular_success and fast_success:
            print("\n🔍 Comparing result quality...")
            
            if regular_data and fast_data:
                reg_comic = regular_data.get('comicDetails', {})
                fast_comic = fast_data.get('comicDetails', {})
                
                # Compare key fields
                fields_match = (
                    reg_comic.get('title') == fast_comic.get('title') and
                    reg_comic.get('issue_number') == fast_comic.get('issue_number') and
                    reg_comic.get('year') == fast_comic.get('year')
                )
                
                if fields_match:
                    print("✅ Results match - same comic details extracted")
                else:
                    print("⚠️  Results differ:")
                    print(f"   Regular: {reg_comic.get('title')} #{reg_comic.get('issue_number')} ({reg_comic.get('year')})")
                    print(f"   Fast: {fast_comic.get('title')} #{fast_comic.get('issue_number')} ({fast_comic.get('year')})")
    
    print(f"\n{'='*60}")
    print("🏁 Test completed!")
    print("💡 Next steps:")
    print("   1. If speed improvements look good, update frontend to use /process_image_fast")
    print("   2. Deploy optimized version to test environment")
    print("   3. Run stakeholder demo with faster processing")

if __name__ == "__main__":
    main()
