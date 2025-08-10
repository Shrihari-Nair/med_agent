#!/usr/bin/env python3
"""
Test the actual prescription processing endpoint.
"""

import requests
import time

def test_prescription_processing():
    """Test the prescription processing endpoint."""
    base_url = "http://localhost:8001"
    
    print("🧪 Testing Prescription Processing...")
    
    # Test with the actual endpoint
    try:
        print("📤 Testing prescription processing endpoint...")
        # Create a dummy PDF file for testing
        test_data = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Paracetamol 500mg 10 tablets) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000174 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n268\n%%EOF"
        files = {"prescription": ("test_prescription.pdf", test_data, "application/pdf")}
        
        print("   📋 Sending test prescription...")
        response = requests.post(f"{base_url}/api/process-prescription", files=files, timeout=30)
        
        print(f"   📨 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Prescription processing endpoint working")
            result = response.json()
            print(f"   📊 Found {len(result.get('medicines', []))} medicines")
            if result.get('medicines'):
                for i, med in enumerate(result['medicines'], 1):
                    print(f"      {i}. {med.get('name')} - {med.get('quantity')}")
                    print(f"         Alternatives: {len(med.get('alternatives', []))}")
            return True
        else:
            print(f"❌ Prescription processing failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Prescription processing test failed: {e}")
        return False

if __name__ == "__main__":
    print("⏳ Testing prescription processing...")
    
    success = test_prescription_processing()
    if success:
        print("\n🎉 Prescription processing is working!")
    else:
        print("\n❌ Prescription processing has issues")
        print("\n💡 This might be expected if:")
        print("   1. GOOGLE_API_KEY is not set")
        print("   2. Medicine database is not created")
        print("   3. Dependencies are missing") 