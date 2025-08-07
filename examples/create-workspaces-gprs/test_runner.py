#!/usr/bin/env python3
"""
Test script to verify the runner functionality with proper error handling.
This script tests the basic functionality without actually creating workspaces.
"""

import json
import os
import sys
import subprocess

def test_config_generation():
    """Test config file generation."""
    print("Testing config file generation...")
    
    # Set test environment variables
    os.environ["EGS_ENDPOINT"] = "http://test-endpoint:8080"
    os.environ["EGS_API_KEY"] = "test-api-key"
    os.environ["EGS_CLUSTER_NAME"] = "test-cluster"
    
    # Import and test the config generation
    from runner import generate_config
    
    teams = ["test-team-1", "test-team-2"]
    kubeconfig = "/tmp/test-kubeconfig.yaml"
    
    generate_config(teams, kubeconfig)
    
    # Verify config file was created
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            config = json.load(f)
        
        assert "test-team-1" in config
        assert "test-team-2" in config
        assert config["test-team-1"]["ENDPOINT"] == "http://test-endpoint:8080"
        assert config["test-team-1"]["API_KEY"] == "test-api-key"
        assert config["test-team-1"]["CLUSTER_NAME"] == ["test-cluster"]
        
        print("✅ Config generation test passed")
        return True
    else:
        print("❌ Config generation test failed")
        return False

def test_env_var_checking():
    """Test environment variable checking."""
    print("Testing environment variable checking...")
    
    from runner import check_env_vars
    
    # Test with missing variables
    if "EGS_ENDPOINT" in os.environ:
        del os.environ["EGS_ENDPOINT"]
    
    try:
        check_env_vars()
        print("❌ Environment variable check should have failed")
        return False
    except SystemExit:
        print("✅ Environment variable check correctly failed with missing variables")
    
    # Test with all variables set
    os.environ["EGS_ENDPOINT"] = "http://test-endpoint:8080"
    os.environ["EGS_API_KEY"] = "test-api-key"
    os.environ["EGS_CLUSTER_NAME"] = "test-cluster"
    
    try:
        check_env_vars()
        print("✅ Environment variable check passed with all variables set")
        return True
    except SystemExit:
        print("❌ Environment variable check failed with all variables set")
        return False

def test_file_existence_check():
    """Test kubeconfig file existence check."""
    print("Testing kubeconfig file existence check...")
    
    from runner import main
    
    # Test with non-existent file
    sys.argv = [
        "test_runner.py",
        "--teams", "test-team",
        "--kubeconfig", "/non/existent/file.yaml",
        "--admin", "create"
    ]
    
    try:
        main()
        print("❌ Should have failed with non-existent kubeconfig")
        return False
    except SystemExit:
        print("✅ Correctly failed with non-existent kubeconfig file")
    
    return True

def cleanup():
    """Clean up test files."""
    if os.path.exists("config.json"):
        os.remove("config.json")
    print("Cleaned up test files")

def main():
    """Run all tests."""
    print("Running tests for runner.py...")
    print("=" * 50)
    
    tests = [
        test_config_generation,
        test_env_var_checking,
        test_file_existence_check
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    cleanup()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 