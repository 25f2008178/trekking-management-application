import os
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from celery import shared_task
from sqlalchemy import select

from app.extensions import db
from app.models import Booking, BookingStatus, Trek, TrekStatus, User


@shared_task(name="app.tasks.reminders.send_daily_reminders")
def send_daily_reminders():
    now = datetime.now(timezone.utc)
    now_naive = now.replace(tzinfo=None)

    stmt = (
        select(Booking)
        .join(Trek, Booking.trek_id == Trek.id)
        .join(User, Booking.user_id == User.id)
        .where(
            Booking.status == BookingStatus.BOOKED,
            Trek.start_date.isnot(None),
            Trek.start_date >= now_naive,
            Trek.status.in_([TrekStatus.OPEN, TrekStatus.APPROVED]),
        )
    )

    bookings = db.session.execute(stmt).scalars().all()

    if not bookings:
        return {"reminders_sent": 0, "message": "No upcoming booked treks found."}

    smtp_host = os.environ.get("SMTP_HOST", "localhost")
    smtp_port = int(os.environ.get("SMTP_PORT", 1025))
    smtp_from = os.environ.get("SMTP_FROM", "noreply@trekking.app")

    sent_count = 0

    for booking in bookings:
        user = booking.user
        trek = booking.trek

        subject = f"Reminder: Your trek \"{trek.trek_name}\" is coming up!"
        html_body = _build_reminder_html(user, trek)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = smtp_from
        msg["To"] = user.email
        msg.attach(MIMEText(html_body, "html"))

        try:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.sendmail(smtp_from, [user.email], msg.as_string())
            sent_count += 1
        except Exception as exc:
            # Log but don't fail the entire batch for one bad send
            print(f"[reminder] Failed to send to {user.email}: {exc}")

    return {"reminders_sent": sent_count}


def _build_reminder_html(user: User, trek: Trek) -> str:
    start = trek.start_date.strftime("%B %d, %Y at %H:%M UTC") if trek.start_date else "TBD"
    return f"""\
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6f9; margin: 0; padding: 0; }}
        .container {{ max-width: 560px; margin: 40px auto; background: #ffffff; border-radius: 12px;
                      box-shadow: 0 2px 12px rgba(0,0,0,0.08); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #2d6a4f, #40916c); padding: 32px 28px; color: #fff; }}
        .header h1 {{ margin: 0 0 4px; font-size: 22px; }}
        .header p {{ margin: 0; opacity: 0.85; font-size: 14px; }}
        .body {{ padding: 28px; color: #333; line-height: 1.6; }}
        .detail {{ background: #f0faf4; border-left: 4px solid #40916c; padding: 14px 18px;
                  border-radius: 6px; margin: 18px 0; }}
        .detail strong {{ display: inline-block; width: 100px; color: #2d6a4f; }}
        .footer {{ text-align: center; padding: 18px; font-size: 12px; color: #999; }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>⛰️ Trek Reminder</h1>
          <p>Your adventure is just around the corner!</p>
        </div>
        <div class="body">
          <p>Hi <strong>{user.name}</strong>,</p>
          <p>This is a friendly reminder that your upcoming trek is starting soon. Here are the details:</p>
          <div class="detail">
            <p><strong>Trek:</strong> {trek.trek_name}</p>
            <p><strong>Location:</strong> {trek.location}</p>
            <p><strong>Starts:</strong> {start}</p>
            <p><strong>Duration:</strong> {trek.duration} day(s)</p>
          </div>
          <p>Make sure you're packed and ready to go. Have a great adventure! 🏕️</p>
        </div>
        <div class="footer">
          Trekking Management App: Happy Trails!
        </div>
      </div>
    </body>
    </html>
    """
