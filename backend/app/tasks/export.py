import csv
import io
import os
import smtplib
from datetime import datetime, timezone
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from celery import shared_task

from app.extensions import db
from app.models import Booking, Trek, User


EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "exports")


@shared_task(name="app.tasks.export.export_trekking_history", bind=True)
def export_trekking_history(self, user_id: int):
    user = db.session.get(User, user_id)
    if not user:
        return {"status": "error", "detail": f"User {user_id} not found."}

    bookings = (
        db.session.query(Booking)
        .join(Trek, Booking.trek_id == Trek.id)
        .filter(Booking.user_id == user_id)
        .order_by(Booking.booking_date.desc())
        .all()
    )

    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow([
        "Booking ID",
        "Trek Name",
        "Location",
        "Difficulty",
        "Duration (days)",
        "Start Date",
        "End Date",
        "Booking Date",
        "Status",
    ])

    for b in bookings:
        trek = b.trek
        writer.writerow([
            b.id,
            trek.trek_name,
            trek.location,
            trek.difficulty.value if hasattr(trek.difficulty, "value") else str(trek.difficulty),
            trek.duration,
            trek.start_date.isoformat() if trek.start_date else "",
            trek.end_date.isoformat() if trek.end_date else "",
            b.booking_date.isoformat() if b.booking_date else "",
            b.status.value if hasattr(b.status, "value") else str(b.status),
        ])

    csv_content = csv_buffer.getvalue()
    csv_buffer.close()

    os.makedirs(EXPORT_DIR, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{user_id}_{timestamp}.csv"
    filepath = os.path.join(EXPORT_DIR, filename)

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        f.write(csv_content)

    _send_export_email(user, csv_content, filename)

    return {"status": "success", "filename": filename, "rows": len(bookings)}


def _send_export_email(user: User, csv_content: str, filename: str):
    smtp_host = os.environ.get("SMTP_HOST", "localhost")
    smtp_port = int(os.environ.get("SMTP_PORT", 1025))
    smtp_from = os.environ.get("SMTP_FROM", "noreply@trekking.app")

    msg = MIMEMultipart()
    msg["Subject"] = "Your Trekking History Export is Ready"
    msg["From"] = smtp_from
    msg["To"] = user.email

    body = MIMEText(
        f"Hi {user.name},\n\n"
        f"Your trekking history export is ready! The CSV file is attached to this email.\n\n"
        f"Happy trails!\n"
        f"— Trekking Management App",
        "plain",
    )
    msg.attach(body)

    attachment = MIMEApplication(csv_content.encode("utf-8"), _subtype="csv")
    attachment.add_header("Content-Disposition", "attachment", filename=filename)
    msg.attach(attachment)

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.sendmail(smtp_from, [user.email], msg.as_string())
    except Exception as exc:
        print(f"[export] Failed to email export to {user.email}: {exc}")
