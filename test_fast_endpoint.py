#!/usr/bin/env python3
"""
Test script for the fast image processing endpoint
"""
import requests
import time
import os

def test_fast_endpoint():
    """Test the fast processing endpoint with a sample image"""
    
    # Check if server is running
    try:
        response = requests.get('http://127.0.0.1:5000/')
        print("✅ Server is running")
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start the server first.")
        return
    
    # Look for a test image in uploads folder
    uploads_dir = 'uploads'
    if not os.path.exists(uploads_dir):
        print(f"❌ Uploads directory '{uploads_dir}' not found")
        return
    
    # Find any image file
    image_files = [f for f in os.listdir(uploads_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    
    if not image_files:
        print("❌ No image files found in uploads directory")
        print("Please add a comic book image to the uploads folder first")
        return
    
    test_image = os.path.join(uploads_dir, image_files[0])
    print(f"📸 Using test image: {test_image}")
    
    # Test regular endpoint
    print("\n🔄 Testing regular endpoint (/process_image)...")
    start_time = time.time()
    
    try:
        with open(test_image, 'rb') as f:
            files = {'image': f}
            response = requests.post('http://127.0.0.1:5000/process_image', files=files, timeout=60)
        
        regular_time = time.time() - start_time
        print(f"⏱️  Regular processing time: {regular_time:.2f} seconds")
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Regular endpoint working")
        else:
            print(f"❌ Regular endpoint failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Regular endpoint error: {e}")
    
    # Test fast endpoint
    print("\n🚀 Testing fast endpoint (/process_image_fast)...")
    start_time = time.time()
    
    try:
        with open(test_image, 'rb') as f:
            files = {'image': f}
            response = requests.post('http://127.0.0.1:5000/process_image_fast', files=files, timeout=60)
        
        fast_time = time.time() - start_time
        print(f"⏱️  Fast processing time: {fast_time:.2f} seconds")
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Fast endpoint working")
            data = response.json()
            if 'processingTime' in data:
                print(f"🎯 Server-reported processing time: {data['processingTime']}")
        else:
            print(f"❌ Fast endpoint failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Fast endpoint error: {e}")
    
    # Compare results
    if 'regular_time' in locals() and 'fast_time' in locals():
        improvement = ((regular_time - fast_time) / regular_time) * 100
        print(f"\n📈 Speed improvement: {improvement:.1f}% faster")

if __name__ == "__main__":
    test_fast_endpoint()
