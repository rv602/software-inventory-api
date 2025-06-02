#!/usr/bin/env python3
import os
import sys
import argparse
from crontab import CronTab
from datetime import datetime
import logging
import pytz

def get_local_timezone():
    """Get the local timezone name"""
    return datetime.now().astimezone().tzname()

def setup_logging():
    """Setup logging directory and configuration"""
    # Create logs directory structure
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs', 'cron')
    os.makedirs(log_dir, exist_ok=True)
    
    # Setup logging configuration
    logging.basicConfig(
        filename=os.path.join(log_dir, 'scan_cron.log'),
        level=logging.INFO,
        format='[%(asctime)s] %(message)s',
        datefmt='%B %d, %Y %I:%M:%S %p'
    )

# Initialize logging
setup_logging()

def format_time(dt):
    """Format datetime in a human-readable way"""
    if not dt:
        return "Not available"
    return dt.strftime("%B %d, %Y at %I:%M:%S %p")

def setup_cron_job(interval_minutes):
    """Set up cron job to run the parallel scans script"""
    try:
        # Initialize crontab for the current user
        cron = CronTab(user=True)
        
        # Remove any existing jobs with our comment
        existing_job = next((job for job in cron if job.comment == 'software_inventory_scan'), None)
        if existing_job:
            logging.info("Removing existing scan schedule")
            cron.remove(existing_job)
        
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_log = os.path.join(project_root, 'logs', 'cron', 'scan_output.log')
        
        # Create new job with proper paths
        job = cron.new(
            command=f'cd {project_root} && '
            f'python3 scripts/run_parallel_scans.py >> {output_log} 2>&1',
            comment='software_inventory_scan'
        )
        
        # Set job schedule
        job.minute.every(interval_minutes)
        
        # Write the crontab
        cron.write()
        
        # Log success with clear timing information
        schedule_msg = f"Scan scheduled successfully:"
        schedule_details = f"- Will run every {interval_minutes} minutes"
        next_run = job.schedule(date_from=datetime.now()).get_next()
        next_run_msg = f"- Next scan scheduled for: {format_time(next_run)} {get_local_timezone()}"
        
        logging.info("\n".join([schedule_msg, schedule_details, next_run_msg]))
        print("\n".join([schedule_msg, schedule_details, next_run_msg]))
        
        return True
    except Exception as e:
        error_msg = f"Failed to set up scan schedule: {str(e)}"
        logging.error(error_msg)
        print(f"Error: {error_msg}")
        return False

def get_job_status():
    """Get status of the scan cron job"""
    try:
        cron = CronTab(user=True)
        job = next((job for job in cron if job.comment == 'software_inventory_scan'), None)
        
        if not job:
            return "No scheduled scans found in the system"
        
        # Get schedule in a readable format
        schedule_parts = str(job.slices).split()
        if schedule_parts[0].startswith('*/'):
            minutes = int(schedule_parts[0].replace('*/', ''))
            schedule = f"Every {minutes} minutes"
        else:
            schedule = "Every minute"
        
        # Calculate next run time
        next_run = job.schedule(date_from=datetime.now()).get_next()
        
        # Get last run time from log
        log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                               'logs', 'cron', 'scan_cron.log')
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                last_run_time = None
                for line in reversed(lines):
                    if "Starting parallel scans" in line:
                        last_run_time = line.split(']')[0].strip('[')
                        break
        except FileNotFoundError:
            last_run_time = None
        
        status = f"""
📊 Software Inventory Scan Status
================================
🕒 Schedule: {schedule}
🔄 Last Scan: {last_run_time or 'No scans completed yet'}
⏰ Next Scan: {format_time(next_run)} {get_local_timezone()}

📝 Scan Logs:
- Execution logs: logs/cron/scan_cron.log
- Scan output: logs/cron/scan_output.log
        """
        return status
    except Exception as e:
        return f"Error checking scan status: {str(e)}"

def cancel_all_jobs():
    """Cancel all scheduled scan jobs"""
    try:
        cron = CronTab(user=True)
        # Find and remove all scan jobs
        removed = 0
        for job in cron:
            if job.comment == 'software_inventory_scan':
                cron.remove(job)
                removed += 1
        
        # Write the changes
        cron.write()
        
        if removed > 0:
            msg = f"Successfully cancelled {removed} scheduled scan{'s' if removed > 1 else ''}"
            logging.info(msg)
            print(msg)
        else:
            print("No scheduled scans found to cancel")
        
        return True
    except Exception as e:
        error_msg = f"Failed to cancel scans: {str(e)}"
        logging.error(error_msg)
        print(f"Error: {error_msg}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Setup and manage automated software inventory scans',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Schedule scans every 30 minutes:
    python3 setup_scan_cron.py --setup 30
    
  Check current scan status:
    python3 setup_scan_cron.py --status
    
  Cancel all scheduled scans:
    python3 setup_scan_cron.py --cancel
        """
    )
    parser.add_argument('--setup', type=int, help='Schedule scans to run every N minutes')
    parser.add_argument('--status', action='store_true', help='Show current scan schedule and status')
    parser.add_argument('--cancel', action='store_true', help='Cancel all scheduled scans')
    
    args = parser.parse_args()
    
    if args.setup:
        if args.setup < 1:
            print("Error: Interval must be at least 1 minute")
            sys.exit(1)
        setup_cron_job(args.setup)
    elif args.status:
        print(get_job_status())
    elif args.cancel:
        cancel_all_jobs()
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 