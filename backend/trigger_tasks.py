import argparse
import sys

from dotenv import load_dotenv
from app import create_app
from app.tasks.export import export_trekking_history
from app.tasks.reminders import send_daily_reminders
from app.tasks.reports import generate_monthly_report

load_dotenv()

def main():
    parser = argparse.ArgumentParser(
        description="Trigger Celery background tasks manually without Flask shell."
    )
    parser.add_argument(
        "--reminders",
        action="store_true",
        help="Trigger daily reminder emails task",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Trigger monthly admin activity report task",
    )
    parser.add_argument(
        "--export",
        type=int,
        metavar="USER_ID",
        help="Trigger CSV export task for a specific user ID",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Trigger both reminders and monthly report tasks",
    )

    args = parser.parse_args()

    if not (args.reminders or args.report or args.export is not None or args.all):
        parser.print_help()
        sys.exit(1)

    app = create_app()
    with app.app_context():
        if args.reminders or args.all:
            print("Triggering send_daily_reminders task...")
            res = send_daily_reminders.delay()
            print(f"   Task ID: {res.id}")

        if args.report or args.all:
            print("Triggering generate_monthly_report task...")
            res = generate_monthly_report.delay()
            print(f"   Task ID: {res.id}")

        if args.export is not None:
            print(f"Triggering export_trekking_history task for User #{args.export}...")
            res = export_trekking_history.delay(args.export)
            print(f"   Task ID: {res.id}")

    print("All requested task(s) dispatched to Celery worker.")


if __name__ == "__main__":
    main()
