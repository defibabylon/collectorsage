#!/usr/bin/env python3
"""
Simple test to check if Flask endpoints are working
"""

import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def test_endpoint(path, method="GET"):
    """Test a specific endpoint"""
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{path}", timeout=10)
        else:
            response = requests.post(f"{BASE_URL}{path}", timeout=10)
        
        print(f"{method} {path}: {response.status_code}")
        if response.status_code != 404:
            print(f"  Response: {response.text[:200]}...")
        return response.status_code
    except Exception as e:
        print(f"{method} {path}: ERROR - {e}")
        return None

def main():
    print("Testing Flask endpoints...")
    
    # Test various endpoints
    endpoints = [
        ("/", "GET"),
        ("/test", "GET"),
        ("/test-simple-processing", "GET"),
        ("/test-image-processing", "GET"),
        ("/test-process", "POST"),
        ("/process_image", "POST"),
        ("/process_image_fast", "POST"),
        ("/routes", "GET"),
    ]
    
    for path, method in endpoints:
        test_endpoint(path, method)
        time.sleep(0.5)

if __name__ == "__main__":
    main()
