#!/usr/bin/env python3
"""
Test script for new fuzzy search API endpoints.
This verifies the new functionality works without affecting existing features.
"""

import requests
import json
import time

def test_fuzzy_search_endpoints():
    """Test the new fuzzy search API endpoints."""
    base_url = "http://localhost:8001"
    
    print("🧪 Testing New Fuzzy Search API Endpoints")
    print("=" * 50)
    
    # Test cases with different types of queries
    test_cases = [
        {
            "name": "Exact match",
            "query": "paracetamol",
            "expected": "Should find exact match"
        },
        {
            "name": "Typo handling", 
            "query": "paracetmol",
            "expected": "Should suggest paracetamol"
        },
        {
            "name": "Partial match",
            "query": "paracet",
            "expected": "Should find paracetamol variants"
        },
        {
            "name": "With dosage",
            "query": "paracetamol 500mg",
            "expected": "Should extract paracetamol"
        },
        {
            "name": "Another medicine",
            "query": "ibuprofn", 
            "expected": "Should suggest ibuprofen"
        }
    ]
    
    print("\n1. Testing Fuzzy Search Endpoint:")
    print("-" * 30)
    
    for test in test_cases:
        print(f"\n🔍 {test['name']}: '{test['query']}'")
        try:
            response = requests.get(f"{base_url}/api/search/fuzzy/{test['query']}")
            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    results = data["results"]
                    print(f"   ✅ Success - Confidence: {results['confidence']}")
                    print(f"   📊 Found {results['total_found']} matches")
                    
                    for i, match in enumerate(results['matches'][:2], 1):
                        score = match['similarity_score']
                        match_type = match['match_type']
                        print(f"   {i}. {match['name']} (Score: {score}%, Type: {match_type})")
                else:
                    print(f"   ❌ API Error: {data.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"   ⚠️  Server not running. Start it with: ./start.sh")
            return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n2. Testing Suggestions Endpoint:")
    print("-" * 30)
    
    suggestion_tests = ["para", "ibu", "omep", "x"]
    
    for query in suggestion_tests:
        print(f"\n💡 Suggestions for: '{query}'")
        try:
            response = requests.get(f"{base_url}/api/search/suggestions/{query}")
            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    suggestions = data["suggestions"]
                    print(f"   ✅ Found {len(suggestions)} suggestions")
                    for suggestion in suggestions[:3]:
                        print(f"   • {suggestion}")
                else:
                    print(f"   ❌ API Error: {data.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n3. Testing Enhanced Search Endpoint:")
    print("-" * 30)
    
    enhanced_tests = ["paracetamol", "paracetmol", "nonexistent"]
    
    for query in enhanced_tests:
        print(f"\n🔎 Enhanced search for: '{query}'")
        try:
            response = requests.get(f"{base_url}/api/search/enhanced/{query}")
            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    results = data["results"]
                    print(f"   ✅ Confidence: {results['confidence']}")
                    print(f"   📊 Exact match: {results['has_exact_match']}")
                    print(f"   💡 Suggestions: {', '.join(results['suggestions'][:3])}")
                else:
                    print(f"   ❌ API Error: {data.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Fuzzy Search API Testing Complete!")
    print("\n💡 New API Endpoints Available:")
    print(f"   • Fuzzy Search: {base_url}/api/search/fuzzy/{{medicine_name}}")
    print(f"   • Suggestions: {base_url}/api/search/suggestions/{{partial_name}}")
    print(f"   • Enhanced Search: {base_url}/api/search/enhanced/{{medicine_name}}")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Fuzzy Search API Tests...")
    print("⚠️  Note: Make sure the server is running with ./start.sh")
    print()
    
    # Wait a moment for user to start server if needed
    input("Press Enter when server is running, or Ctrl+C to exit...")
    
    test_fuzzy_search_endpoints() 