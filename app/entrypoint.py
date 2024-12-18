import subprocess
import time
import sys

def run_script(script_name):
    print(f"Running {script_name}...")
    result = subprocess.run(['python', f'scripts/{script_name}'], check=True)
    return result.returncode == 0

def main():
    scripts = ['python_environments.py', 'node_environments.py']
    
    for script in scripts:
        if not run_script(script):
            print(f"Error running {script}")
            sys.exit(1)
        print(f"Successfully completed {script}")

if __name__ == "__main__":
    main()