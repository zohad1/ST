# scripts/test_api.py
import requests
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8002"

def test_endpoint(name, method, path, **kwargs):
    """Test a single endpoint"""
    logger.info(f"\n🧪 Testing: {name}")
    logger.info(f"   Method: {method}")
    logger.info(f"   URL: {BASE_URL}{path}")
    
    try:
        response = requests.request(method, f"{BASE_URL}{path}", **kwargs)
        logger.info(f"   Status: {response.status_code}")
        
        if response.status_code < 300:
            logger.info("   ✅ Success")
            data = response.json()
            logger.info(f"   Response: {json.dumps(data, indent=2)[:500]}...")
        else:
            logger.error(f"   ❌ Failed with status {response.status_code}")
            logger.error(f"   Response: {response.text[:500]}")
        
        return response
        
    except requests.exceptions.ConnectionError:
        logger.error("   ❌ Connection failed - is the service running?")
        return None
    except Exception as e:
        logger.error(f"   ❌ Error: {str(e)}")
        return None

def run_tests():
    """Run all API tests"""
    logger.info("=" * 80)
    logger.info("🚀 Campaign Service API Tests")
    logger.info(f"⏰ Time: {datetime.now()}")
    logger.info(f"🌐 Base URL: {BASE_URL}")
    logger.info("=" * 80)
    
    # Test endpoints
    tests = [
        ("Root", "GET", "/"),
        ("Health Check", "GET", "/health"),
        ("Test Endpoint", "GET", "/api/v1/test"),
        ("Dashboard Analytics", "GET", "/api/v1/dashboard/analytics"),
        ("Dashboard Analytics (7 days)", "GET", "/api/v1/dashboard/analytics?timeframe=last_7_days"),
        ("Dashboard Campaigns", "GET", "/api/v1/dashboard/campaigns"),
        ("Dashboard Campaigns (Active)", "GET", "/api/v1/dashboard/campaigns?status=active"),
        ("Creator Performance", "GET", "/api/v1/dashboard/creator-performance"),
    ]
    
    results = []
    for test_name, method, path in tests:
        response = test_endpoint(test_name, method, path)
        success = response is not None and response.status_code < 300
        results.append((test_name, success))
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"{status} - {test_name}")
    
    logger.info(f"\n📈 Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed!")
    else:
        logger.error("⚠️  Some tests failed.")

if __name__ == "__main__":
    # Check if service is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        logger.info("✅ Service is running")
        run_tests()
    except requests.exceptions.ConnectionError:
        logger.error("❌ Service is not running!")
        logger.error(f"Please start the service first:")
        logger.error(f"  python -m uvicorn app.main:app --reload --port 8002")
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")