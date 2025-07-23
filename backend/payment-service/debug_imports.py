# debug_stripe_import.py
"""
Debug the Stripe import issue
"""
import sys
import importlib
import pkg_resources

print("🔍 Debugging Stripe Import Issue")
print("=" * 50)

# Check Python version
print(f"\nPython Version: {sys.version}")

# Check if stripe is installed
print("\n📦 Checking Stripe Installation:")
try:
    # Get stripe package info
    stripe_pkg = pkg_resources.get_distribution("stripe")
    print(f"✅ Stripe is installed")
    print(f"   Version: {stripe_pkg.version}")
    print(f"   Location: {stripe_pkg.location}")
except pkg_resources.DistributionNotFound:
    print("❌ Stripe is NOT installed")
    sys.exit(1)

# Try different import methods
print("\n🧪 Testing Different Import Methods:")

# Method 1: Standard import
print("\n1. Standard import:")
try:
    import stripe
    print("✅ Import successful")
    print(f"   Module: {stripe}")
    print(f"   File: {stripe.__file__}")
    print(f"   Version: {stripe.__version__}")
except Exception as e:
    print(f"❌ Import failed: {e}")

# Method 2: Check module contents
print("\n2. Module contents:")
try:
    import stripe
    attrs = [attr for attr in dir(stripe) if not attr.startswith('_')]
    print(f"✅ Found {len(attrs)} attributes")
    
    # Check for key classes
    key_classes = ['Account', 'Balance', 'Customer', 'PaymentIntent']
    for cls in key_classes:
        if hasattr(stripe, cls):
            print(f"   ✅ {cls}: Found")
        else:
            print(f"   ❌ {cls}: Missing")
except Exception as e:
    print(f"❌ Error checking module: {e}")

# Method 3: Try to use stripe directly
print("\n3. Direct API key test:")
try:
    import stripe
    test_key = "sk_test_test123"
    stripe.api_key = test_key
    print(f"✅ API key set: {stripe.api_key[:10]}...")
except Exception as e:
    print(f"❌ Error setting API key: {e}")
    import traceback
    traceback.print_exc()

# Method 4: Check for conflicts
print("\n4. Checking for conflicts:")
# List all modules that start with 'stripe'
stripe_modules = [name for name in sys.modules.keys() if 'stripe' in name.lower()]
print(f"Modules containing 'stripe': {stripe_modules}")

# Check if there's a local file named stripe.py
import os
local_files = os.listdir('.')
if 'stripe.py' in local_files:
    print("⚠️  WARNING: Found local 'stripe.py' file - this will conflict!")
else:
    print("✅ No local stripe.py file found")

# Method 5: Reinstall suggestion
print("\n💡 Suggested Fix:")
print("1. Uninstall stripe completely:")
print("   pip uninstall stripe -y")
print("2. Clear pip cache:")
print("   pip cache purge")
print("3. Reinstall specific version:")
print("   pip install stripe==7.6.0")
print("4. If still failing, try:")
print("   python -m pip install --force-reinstall stripe==7.6.0")

# Method 6: Alternative test
print("\n5. Alternative stripe test:")
try:
    import stripe as stripe_module
    stripe_module.api_key = "sk_test_test"
    print("✅ Alternative import method works")
except Exception as e:
    print(f"❌ Alternative method also fails: {e}")