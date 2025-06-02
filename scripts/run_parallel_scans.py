# run_parallel_scans.py
import asyncio
import os
import socket
import platform
import uuid
import time
from datetime import datetime

def get_system_info():
    """Get system-specific information"""
    hostname = socket.gethostname()
    return {
        "hostname": hostname,
        "system_type": platform.system(),
        "mac_address": ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                           for elements in range(0,8*6,8)][::-1]),
        "ip_address": socket.gethostbyname(hostname)
    }

async def run_script(script_name: str):
    """Run a Python script asynchronously"""
    print(f"Starting {script_name}...")
    start_time = time.time()
    
    process = await asyncio.create_subprocess_exec(
        'python3',
        f'scripts/{script_name}',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await process.communicate()
    
    execution_time = time.time() - start_time
    print(f"{script_name} completed in {execution_time:.2f} seconds")
    
    if stderr:
        print(f'{script_name} errors:\n{stderr.decode()}')
    
    return process.returncode

async def main():
    total_start_time = time.time()
    print(f"Starting parallel scans at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Set system info as environment variables
    system_info = get_system_info()
    os.environ.update({
        'SYSTEM_HOSTNAME': system_info['hostname'],
        'SYSTEM_TYPE': system_info['system_type'],
        'SYSTEM_MAC': system_info['mac_address'],
        'SYSTEM_IP': system_info['ip_address']
    })
    print(f"System information collected for host: {system_info['hostname']}")
    
    # Run both scripts in parallel
    print("\nExecuting vulnerability scans in parallel...")
    results = await asyncio.gather(
        run_script('python_environments.py'),
        run_script('node_environments.py'),
        return_exceptions=True
    )
    
    total_time = time.time() - total_start_time
    print(f"\nTotal execution time: {total_time:.2f} seconds")
    
    # Check for any failures
    if any(isinstance(result, Exception) for result in results):
        print("One or more scans failed")
        return 1
    
    print("All scans completed successfully")
    return 0

if __name__ == "__main__":
    exit(asyncio.run(main()))