#!/usr/bin/env python3
# Test client for Mathly API

import requests
import json

BASE_URL = "http://localhost:5001/api"

def test_formula_endpoints():
    """Test the formula endpoints"""
    print("\n--- Testing Formula Endpoints ---")
    
    # Test basic formula endpoint
    print("\nTesting /api/formula/geometry")
    resp = requests.get(f"{BASE_URL}/formula/geometry")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Success! Got {len(data['formula'].split('\\n'))} lines of geometry formulas")
    else:
        print(f"Error: {resp.status_code} - {resp.text}")
    
    # Test topic-specific formula
    print("\nTesting /api/formula/geometry/circle")
    resp = requests.get(f"{BASE_URL}/formula/geometry/circle")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Success! Circle formula: {data['formula']}")
    else:
        print(f"Error: {resp.status_code} - {resp.text}")
    
    # Test formula search
    print("\nTesting /api/formula_search with search term 'energy'")
    resp = requests.post(
        f"{BASE_URL}/formula_search",
        json={"term": "energy"}
    )
    if resp.status_code == 200:
        data = resp.json()
        if 'results' in data:
            print(f"Success! Found {len(data['results'])} formulas matching 'energy'")
            for formula in data['results'][:3]:  # Show just first 3
                print(f"- {formula}")
        else:
            print(f"No results found: {data}")
    else:
        print(f"Error: {resp.status_code} - {resp.text}")

def test_chat():
    """Test the chat endpoint"""
    print("\n--- Testing Chat Endpoint ---")
    
    # Test physics formula question
    print("\nAsking about kinetic energy formula")
    resp = requests.post(
        f"{BASE_URL}/chat",
        json={"input": "What is the formula for kinetic energy in physics?"}
    )
    if resp.status_code == 200:
        data = resp.json()
        print(f"Response: {data['response']}")
    else:
        print(f"Error: {resp.status_code} - {resp.text}")
    
    # Test calculus formula question
    print("\nAsking about derivatives")
    resp = requests.post(
        f"{BASE_URL}/chat",
        json={"input": "What are the common derivative formulas in calculus?"}
    )
    if resp.status_code == 200:
        data = resp.json()
        print(f"Response: {data['response']}")
    else:
        print(f"Error: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    print("Mathly API Test Client")
    print("=====================")
    
    test_formula_endpoints()
    test_chat()
    
    print("\nTests completed!")
