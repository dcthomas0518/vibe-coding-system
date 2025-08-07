#!/usr/bin/env python3
"""Test if ChromaDB and sentence-transformers are properly installed"""

import sys
import subprocess

def test_with_sudo():
    """Test imports using sudo python3"""
    test_script = '''
import chromadb
import sentence_transformers
print("✅ ChromaDB version:", chromadb.__version__)
print("✅ Sentence-transformers installed successfully!")
print("✅ All dependencies are available!")
'''
    
    # Write test script to temp file
    with open('/tmp/test_imports.py', 'w') as f:
        f.write(test_script)
    
    # Run with sudo
    print("Testing with sudo python3...")
    result = subprocess.run(['sudo', 'python3', '/tmp/test_imports.py'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print(result.stdout)
        return True
    else:
        print("Error:", result.stderr)
        return False

def test_direct():
    """Try direct import"""
    try:
        import chromadb
        import sentence_transformers
        print("✅ Direct import successful!")
        print(f"✅ ChromaDB version: {chromadb.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Direct import failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing OS-002.1 dependencies...\n")
    
    # Try direct import first
    if not test_direct():
        print("\nPackages were installed with sudo, creating wrapper...")
        
        # Create a wrapper that uses sudo python
        wrapper_content = '''#!/usr/bin/env python3
"""Wrapper to run OS-002.1 with sudo python3"""
import subprocess
import sys
import os

# Get the actual script to run
script = os.path.join(os.path.dirname(__file__), "run_indexer.py")
cmd = ["sudo", "python3", script] + sys.argv[1:]

# Run with sudo
result = subprocess.run(cmd)
sys.exit(result.returncode)
'''
        
        with open('/home/dthomas_unix/vibe-coding-system/os_modules/os_002_1_vector_search/run_with_sudo.py', 'w') as f:
            f.write(wrapper_content)
        
        print("✅ Created run_with_sudo.py wrapper")
        print("\nTo use OS-002.1, run: python3 run_with_sudo.py")