#!/usr/bin/env python3
"""
Simple test script to verify backend API functionality.
"""

import requests
import time

def test_backend():
    """Test the backend API endpoints."""
    base_url = "http://localhost:8001"
    
    print("🧪 Testing Backend API...")
    
    # Test health endpoint
    try:
        print("📡 Testing health endpoint...")
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False
    
    # Test file upload endpoint with dummy data
    try:
        print("📤 Testing file upload endpoint...")
        # Create a dummy file for testing
        test_data = b"dummy pdf content for testing"
        files = {"file": ("test.pdf", test_data, "application/pdf")}
        
        response = requests.post(f"{base_url}/api/test-upload", files=files, timeout=10)
        if response.status_code == 200:
            print("✅ File upload endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ File upload endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ File upload test failed: {e}")
        return False
    
    print("🎉 All tests passed!")
    return True

if __name__ == "__main__":
    # Wait a moment for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    success = test_backend()
    if not success:
        print("\n💡 Troubleshooting tips:")
        print("   1. Make sure the backend server is running")
        print("   2. Check if port 8001 is available")
        print("   3. Verify your virtual environment is active")
        exit(1)
    
    print("\n✅ Backend is working correctly!") 