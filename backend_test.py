#!/usr/bin/env python3
"""
Backend API Testing for ImagePack Application
Tests all API endpoints and functionality
"""

import requests
import sys
import json
import time
from datetime import datetime

class ImagePackAPITester:
    def __init__(self, base_url="https://22154470-17f8-4384-b40c-39e545d1a742.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.download_ids = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)

            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED - {name}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)}")
                    return True, response_data
                except:
                    print(f"   Response: {response.text[:200]}...")
                    return True, {}
            else:
                print(f"❌ FAILED - {name}")
                print(f"   Expected status: {expected_status}, got: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ FAILED - {name} (Timeout)")
            return False, {}
        except Exception as e:
            print(f"❌ FAILED - {name} (Error: {str(e)})")
            return False, {}

    def test_root_endpoint(self):
        """Test the root endpoint"""
        return self.run_test(
            "Root Endpoint",
            "GET",
            "",
            200
        )

    def test_get_stats(self):
        """Test getting download statistics"""
        success, response = self.run_test(
            "Get Statistics",
            "GET",
            "api/stats",
            200
        )
        
        if success:
            # Validate response structure
            expected_keys = ['total_packages_created', 'completed_downloads', 'success_rate']
            for key in expected_keys:
                if key not in response:
                    print(f"⚠️  Warning: Missing key '{key}' in stats response")
                    return False, response
            print(f"   Stats validation: ✅ All required keys present")
        
        return success, response

    def test_create_download_package(self, name=None, project_name=None):
        """Test creating a download package"""
        data = {}
        if name:
            data['name'] = name
        if project_name:
            data['project_name'] = project_name
            
        success, response = self.run_test(
            "Create Download Package",
            "POST",
            "api/download",
            200,
            data=data
        )
        
        if success and 'download_id' in response:
            download_id = response['download_id']
            self.download_ids.append(download_id)
            print(f"   Download ID: {download_id}")
            return True, download_id
        
        return False, None

    def test_download_package(self, download_id):
        """Test downloading a package"""
        print(f"\n🔍 Testing Download Package...")
        print(f"   Download ID: {download_id}")
        
        url = f"{self.base_url}/api/download/{download_id}"
        print(f"   URL: {url}")
        
        self.tests_run += 1
        
        try:
            response = requests.get(url, timeout=30)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                # Check if it's a zip file
                content_type = response.headers.get('content-type', '')
                content_disposition = response.headers.get('content-disposition', '')
                
                print(f"   Content-Type: {content_type}")
                print(f"   Content-Disposition: {content_disposition}")
                print(f"   Content Length: {len(response.content)} bytes")
                
                if 'application/zip' in content_type or 'zip' in content_disposition:
                    self.tests_passed += 1
                    print(f"✅ PASSED - Download Package")
                    return True
                else:
                    print(f"❌ FAILED - Not a zip file")
                    return False
            else:
                print(f"❌ FAILED - Download Package")
                print(f"   Expected status: 200, got: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ FAILED - Download Package (Error: {str(e)})")
            return False

    def test_invalid_download_id(self):
        """Test downloading with invalid ID"""
        return self.run_test(
            "Invalid Download ID",
            "GET",
            "api/download/invalid-id-12345",
            404
        )

    def test_empty_download_request(self):
        """Test creating download with empty request"""
        return self.run_test(
            "Empty Download Request",
            "POST",
            "api/download",
            200,
            data={}
        )

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting ImagePack API Tests")
        print("=" * 50)
        
        # Test 1: Root endpoint
        self.test_root_endpoint()
        
        # Test 2: Get initial stats
        print(f"\n📊 Testing Statistics Endpoint...")
        initial_success, initial_stats = self.test_get_stats()
        initial_downloads = initial_stats.get('completed_downloads', 0) if initial_success else 0
        
        # Test 3: Create download package with data
        print(f"\n📦 Testing Download Package Creation...")
        success, download_id = self.test_create_download_package(
            name="Creative Artist",
            project_name="Portfolio Compression"
        )
        
        # Test 4: Download the package
        if success and download_id:
            print(f"\n⬇️  Testing Package Download...")
            self.test_download_package(download_id)
        
        # Test 5: Create download package without data
        print(f"\n📦 Testing Empty Download Request...")
        self.test_empty_download_request()
        
        # Test 6: Test invalid download ID
        print(f"\n❌ Testing Invalid Download ID...")
        self.test_invalid_download_id()
        
        # Test 7: Check stats after downloads
        print(f"\n📊 Testing Updated Statistics...")
        final_success, final_stats = self.test_get_stats()
        if final_success and initial_success:
            final_downloads = final_stats.get('completed_downloads', 0)
            if final_downloads > initial_downloads:
                print(f"✅ Stats updated correctly: {initial_downloads} → {final_downloads}")
            else:
                print(f"⚠️  Stats may not have updated: {initial_downloads} → {final_downloads}")

        # Print final results
        print(f"\n" + "=" * 50)
        print(f"📊 TEST RESULTS")
        print(f"=" * 50)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.download_ids:
            print(f"\n📋 Generated Download IDs:")
            for i, download_id in enumerate(self.download_ids, 1):
                print(f"   {i}. {download_id}")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = ImagePackAPITester()
    success = tester.run_all_tests()
    
    print(f"\n🕐 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success:
        print(f"\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n💥 Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())