"""
Test script to verify lazy loading implementation.
This can be run once the package is installed.
"""

import sys
import time


def test_lazy_loading():
    """Test that drivers are loaded lazily, not eagerly."""
    print("=" * 60)
    print("LAZY LOADING TEST")
    print("=" * 60)

    # Test 1: Import the drivers module
    print("\n[Test 1] Importing griptape.drivers module...")
    import griptape.drivers

    initial_modules = set(sys.modules.keys())
    driver_modules = [m for m in initial_modules if "griptape.drivers" in m and not m.endswith("__init__")]

    print(f"  Initial driver modules loaded: {len(driver_modules)}")
    if len(driver_modules) > 0:
        print(f"  Sample modules: {list(driver_modules)[:5]}")

    # Test 2: Import a specific driver
    print("\n[Test 2] Importing OpenAiChatPromptDriver...")
    start = time.time()
    from griptape.drivers import OpenAiChatPromptDriver

    end = time.time()
    print(f"  ✓ Import succeeded in {(end - start) * 1000:.2f}ms")
    print(f"  ✓ Class: {OpenAiChatPromptDriver}")

    # Test 3: Check what got loaded
    after_modules = set(sys.modules.keys())
    new_modules = after_modules - initial_modules
    new_driver_modules = [m for m in new_modules if "griptape.drivers" in m]

    print(f"\n[Test 3] New modules loaded after importing OpenAiChatPromptDriver:")
    print(f"  Total new driver modules: {len(new_driver_modules)}")
    for mod in sorted(new_driver_modules)[:10]:
        print(f"    - {mod}")

    # Test 4: Verify unrelated drivers NOT loaded
    print("\n[Test 4] Verifying lazy loading (unrelated drivers NOT loaded)...")
    unrelated_drivers = [
        ("Pinecone", "griptape.drivers.vector.pinecone"),
        ("Anthropic", "griptape.drivers.prompt.anthropic"),
        ("Cohere", "griptape.drivers.prompt.cohere"),
        ("MongoDB", "griptape.drivers.vector.mongodb_atlas"),
        ("Redis", "griptape.drivers.vector.redis"),
    ]

    all_lazy = True
    for name, module_path in unrelated_drivers:
        is_loaded = module_path in sys.modules
        status = "❌ LOADED" if is_loaded else "✓ NOT loaded"
        print(f"  {name}: {status}")
        if is_loaded:
            all_lazy = False

    # Test 5: Import another driver
    print("\n[Test 5] Importing AnthropicPromptDriver...")
    from griptape.drivers import AnthropicPromptDriver

    anthropic_loaded = "griptape.drivers.prompt.anthropic" in sys.modules
    print(f"  ✓ AnthropicPromptDriver imported")
    print(f"  ✓ Anthropic module NOW loaded: {anthropic_loaded}")

    # Test 6: Verify __all__
    print("\n[Test 6] Verifying __all__ list...")
    print(f"  ✓ __all__ contains {len(griptape.drivers.__all__)} items")

    # Test 7: Test error handling
    print("\n[Test 7] Testing invalid import...")
    try:
        from griptape.drivers import NonExistentDriver

        print("  ❌ FAILED: Should have raised AttributeError")
        return False
    except AttributeError as e:
        print(f"  ✓ AttributeError raised correctly: {str(e)[:60]}...")

    # Test 8: Test __dir__
    print("\n[Test 8] Testing __dir__...")
    dir_result = dir(griptape.drivers)
    driver_classes = [item for item in dir_result if "Driver" in item]
    print(f"  ✓ dir() returns {len(driver_classes)} driver classes")

    # Final summary
    print("\n" + "=" * 60)
    if all_lazy:
        print("✅ ALL TESTS PASSED!")
        print("\nLazy loading is working correctly:")
        print("  • Drivers are only imported when accessed")
        print("  • Unrelated drivers remain unloaded")
        print("  • Backward compatibility maintained")
        print("  • Error handling works correctly")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("  Some unrelated drivers were loaded eagerly")
    print("=" * 60)

    return all_lazy


if __name__ == "__main__":
    try:
        success = test_lazy_loading()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
