#!/usr/bin/env python3
"""
Quick test script to verify main routes are working
"""
import requests
import sys

def test_routes():
    """Test main routes"""
    base_url = "http://localhost:5001"
    
    routes_to_test = [
        "/",
        "/auth/login",
        "/calendar/calendar",
        "/manager/classes",
        "/admin/users"
    ]
    
    print("🧪 Testing main routes...")
    
    for route in routes_to_test:
        try:
            url = f"{base_url}{route}"
            response = requests.get(url, timeout=5)
            
            if response.status_code in [200, 302]:  # 302 for redirects
                print(f"✅ {route} - Status: {response.status_code}")
            else:
                print(f"❌ {route} - Status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {route} - Error: {e}")
    
    print("\n🎯 Test completed!")
    print("🌐 Access the application at: http://localhost:5001")
    print("👤 Login credentials:")
    print("   Admin: admin / admin123")
    print("   Manager: manager1 / manager123")
    print("   Teacher: teacher1 / teacher123")

if __name__ == "__main__":
    test_routes()
