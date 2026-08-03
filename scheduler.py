import os
import sys
import argparse
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from manager.planner import generate_and_save_today_menu

def trigger_menu_generation():
    """Trigger menu generation and print status."""
    time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{time_str}] Triggering daily menu generation...")
    try:
        menu = generate_and_save_today_menu()
        print(f"[{time_str}] Successfully generated menu for: {menu.get('date', 'unknown')}")
        if menu.get("demo_mode"):
            print("⚠️ NOTE: Generated in DEMO mode. Set GEMINI_API_KEY for real AI generation.")
        return True
    except Exception as e:
        print(f"[{time_str}] ERROR during scheduled menu generation: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="AI Diet Menu Planner Scheduler & CLI")
    parser.add_argument('--now', action='store_true', help="Generate today's menu immediately and exit")
    parser.add_argument('--hour', type=int, default=7, help="Scheduled hour (0-23, default: 7)")
    parser.add_argument('--minute', type=int, default=0, help="Scheduled minute (0-59, default: 0)")
    
    args = parser.parse_args()
    
    if args.now:
        print("Running menu generator immediately...")
        success = trigger_menu_generation()
        sys.exit(0 if success else 1)
        
    scheduler = BlockingScheduler()
    # Add a job that triggers every day at the designated hour:minute
    scheduler.add_job(
        trigger_menu_generation, 
        'cron', 
        hour=args.hour, 
        minute=args.minute,
        id='daily_menu_planner'
    )
    
    print(f"AI Diet Menu Planner Scheduler started.")
    print(f"Will generate daily fat-loss menu at {args.hour:02d}:{args.minute:02d} local time.")
    print("Press Ctrl+C to exit.")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\nScheduler stopped.")

if __name__ == '__main__':
    main()
