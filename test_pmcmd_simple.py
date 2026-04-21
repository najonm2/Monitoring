"""
Simple test to check if pmcmd can be executed from Python
This tests if the APL block has been lifted
"""

import subprocess
import os

# Test both pmcmd locations
pmcmd_paths = [
    r'C:\Informatica\CDIPC_Client\clients\tools\utils\PmCmd.exe',
    r'C:\Informatica\CDIPC_Client\clients\PowerCenterClient\CommandLineUtilities\PC\server\bin\PmCmd.exe'
]

print("="*80)
print("Testing Informatica PmCmd.exe Execution")
print("="*80)

for pmcmd_path in pmcmd_paths:
    print(f"\nTesting: {pmcmd_path}")
    print("-"*80)
    
    if not os.path.exists(pmcmd_path):
        print(f"❌ File not found")
        continue
    
    file_size = os.path.getsize(pmcmd_path) / 1024
    print(f"✅ File exists ({file_size:.1f} KB)")
    
    try:
        print("Attempting to run 'pmcmd version' command...")
        print("(waiting max 15 seconds...)")
        
        result = subprocess.run(
            [pmcmd_path, 'version'],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode == 0:
            print(f"✅ SUCCESS! pmcmd executed successfully")
            print(f"Output:\n{result.stdout}")
            print(f"\n✨ This path works! Use it in settings.py")
            break
        else:
            print(f"⚠️ pmcmd ran but returned error code: {result.returncode}")
            print(f"STDERR: {result.stderr}")
            print(f"STDOUT: {result.stdout}")
            
    except subprocess.TimeoutExpired:
        print(f"❌ TIMEOUT: Command hung for 15 seconds")
        print(f"   This usually means:")
        print(f"   1. APL security block is still active")
        print(f"   2. Or pmcmd is waiting for interactive input")
        
    except FileNotFoundError:
        print(f"❌ File not found at execution time")
        
    except PermissionError as e:
        print(f"❌ PERMISSION DENIED: {e}")
        print(f"   APL security block is preventing execution")
        
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")

print("\n" + "="*80)
print("Test Complete")
print("="*80)
print("\nIf you see 'APPLICATION BLOCKED' popup during this test,")
print("the APL approval is still required.")
print("\nFor production use, deploy to Linux server where Informatica")
print("is already installed and approved.")
