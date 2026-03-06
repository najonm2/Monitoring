"""
Diagnostic script to test Django startup
"""
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("Django Startup Diagnostic")
print("=" * 60)

# Test 1: Check Django
print("\n1. Testing Django import...")
try:
    import django
    print(f"   ✓ Django {django.VERSION} imported successfully")
except Exception as e:
    print(f"   ✗ Django import failed: {e}")
    sys.exit(1)

# Test 2: Check ML packages
print("\n2. Testing ML packages...")
packages = ['numpy', 'pandas', 'sklearn']
for pkg in packages:
    try:
        module = __import__(pkg)
        version = getattr(module, '__version__', 'unknown')
        print(f"   ✓ {pkg} {version} imported successfully")
    except Exception as e:
        print(f"   ✗ {pkg} import failed: {e}")

# Test 3: Setup Django
print("\n3. Setting up Django...")
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitorportal.settings')
    django.setup()
    print("   ✓ Django setup successful")
except Exception as e:
    print(f"   ✗ Django setup failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Import AI modules
print("\n4. Testing AI module imports...")
ai_modules = [
    'portal.ai',
    'portal.ai.orchestrator',
    'portal.ai.base_agent',
    'portal.ai_views',
]
for module_name in ai_modules:
    try:
        module = __import__(module_name, fromlist=[''])
        print(f"   ✓ {module_name} imported successfully")
    except Exception as e:
        print(f"   ✗ {module_name} import failed: {e}")
        import traceback
        traceback.print_exc()

# Test 5: Check URLs
print("\n5. Testing URL configuration...")
try:
    from django.urls import get_resolver
    from django.urls.exceptions import NoReverseMatch
    
    resolver = get_resolver()
    
    # Test AI URLs
    ai_patterns = ['ai_dashboard', 'ai_run_analysis', 'ai_insights']
    for pattern_name in ai_patterns:
        try:
            from django.urls import reverse
            url = reverse(pattern_name)
            print(f"   ✓ URL '{pattern_name}' resolves to: {url}")
        except NoReverseMatch as e:
            print(f"   ✗ URL '{pattern_name}' failed: {e}")
except Exception as e:
    print(f"   ✗ URL configuration error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Diagnostic complete!")
print("=" * 60)
print("\nIf all tests passed, try running:")
print("  python manage.py runserver")
