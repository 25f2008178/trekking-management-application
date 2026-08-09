"""Monthly trekking activity report emailed to the admin (HTML format)."""

import os
import smtplib
from calendar import monthrange
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from celery import shared_task
from sqlalchemy import func, select

from app.extensions import db
from app.models import (
    Booking,
    BookingStatus,
    Trek,
    TrekDifficulty,
    TrekStatus,
    User,
    Role,
)


@shared_task(name="app.tasks.reports.generate_monthly_report")
def generate_monthly_report():
    """
    Generate an HTML activity report for the current calendar month
    and email it to the admin.
    """
    now = datetime.now(timezone.utc)
    year, month = now.year, now.month

    # Naive datetimes for SQLite compatibility
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, monthrange(year, month)[1], 23, 59, 59)

    # ---- Gather metrics ----
    # Total treks created or active in the period
    total_treks = (
        db.session.query(func.count(Trek.id))
        .filter(Trek.start_date.isnot(None), Trek.start_date >= first_day, Trek.start_date <= last_day)
        .scalar()
    ) or 0

    # Total non-cancelled bookings in the period
    total_participants = (
        db.session.query(func.count(Booking.id))
        .filter(
            Booking.booking_date >= first_day,
            Booking.booking_date <= last_day,
            Booking.status != BookingStatus.CANCELLED,
        )
        .scalar()
    ) or 0

    # Popular treks — top 5 by booking count
    popular_treks_q = (
        db.session.query(
            Trek.trek_name,
            Trek.location,
            func.count(Booking.id).label("booking_count"),
        )
        .join(Booking, Trek.id == Booking.trek_id)
        .filter(
            Booking.booking_date >= first_day,
            Booking.booking_date <= last_day,
            Booking.status != BookingStatus.CANCELLED,
        )
        .group_by(Trek.id)
        .order_by(func.count(Booking.id).desc())
        .limit(5)
        .all()
    )

    # Difficulty breakdown
    difficulty_breakdown = (
        db.session.query(Trek.difficulty, func.count(Trek.id))
        .filter(Trek.start_date.isnot(None), Trek.start_date >= first_day, Trek.start_date <= last_day)
        .group_by(Trek.difficulty)
        .all()
    )

    # Completion rate
    completed_treks = (
        db.session.query(func.count(Trek.id))
        .filter(
            Trek.start_date.isnot(None),
            Trek.start_date >= first_day,
            Trek.start_date <= last_day,
            Trek.status == TrekStatus.COMPLETED,
        )
        .scalar()
    ) or 0

    completion_rate = round((completed_treks / total_treks * 100), 1) if total_treks > 0 else 0.0

    # New user registrations (users with role 'user' created in the period)
    new_users = (
        db.session.query(func.count(User.id))
        .filter(
            User.roles.any(Role.name == "user"),
            User.create_datetime >= first_day,
            User.create_datetime <= last_day,
        )
        .scalar()
    ) or 0

    # Cancelled bookings
    cancelled_bookings = (
        db.session.query(func.count(Booking.id))
        .filter(
            Booking.booking_date >= first_day,
            Booking.booking_date <= last_day,
            Booking.status == BookingStatus.CANCELLED,
        )
        .scalar()
    ) or 0

    # ---- Build & send report ----
    month_label = first_day.strftime("%B %Y")

    report_data = {
        "month_label": month_label,
        "total_treks": total_treks,
        "total_participants": total_participants,
        "popular_treks": popular_treks_q,
        "difficulty_breakdown": difficulty_breakdown,
        "completed_treks": completed_treks,
        "completion_rate": completion_rate,
        "new_users": new_users,
        "cancelled_bookings": cancelled_bookings,
    }

    html = _build_report_html(report_data)

    admin_email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
    smtp_host = os.environ.get("SMTP_HOST", "localhost")
    smtp_port = int(os.environ.get("SMTP_PORT", 1025))
    smtp_from = os.environ.get("SMTP_FROM", "noreply@trekking.app")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Monthly Trekking Report — {month_label}"
    msg["From"] = smtp_from
    msg["To"] = admin_email
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.sendmail(smtp_from, [admin_email], msg.as_string())
    except Exception as exc:
        print(f"[report] Failed to send monthly report: {exc}")
        return {"status": "error", "detail": str(exc)}

    return {
        "status": "sent",
        "month": month_label,
        "total_treks": total_treks,
        "total_participants": total_participants,
    }


def _build_report_html(data: dict) -> str:
    """Build a polished HTML email body for the monthly report."""

    # Popular treks table rows
    popular_rows = ""
    for idx, (name, location, count) in enumerate(data["popular_treks"], start=1):
        popular_rows += (
            f'<tr><td style="padding:8px 12px;border-bottom:1px solid #e9ecef;">{idx}</td>'
            f'<td style="padding:8px 12px;border-bottom:1px solid #e9ecef;">{name}</td>'
            f'<td style="padding:8px 12px;border-bottom:1px solid #e9ecef;">{location}</td>'
            f'<td style="padding:8px 12px;border-bottom:1px solid #e9ecef;text-align:center;">{count}</td></tr>'
        )
    if not popular_rows:
        popular_rows = '<tr><td colspan="4" style="padding:12px;text-align:center;color:#999;">No bookings this period</td></tr>'

    # Difficulty breakdown rows
    difficulty_rows = ""
    for diff, count in data["difficulty_breakdown"]:
        label = diff.value if hasattr(diff, "value") else str(diff)
        colors = {"Easy": "#52b788", "Moderate": "#f4a261", "Hard": "#e76f51"}
        color = colors.get(label, "#6c757d")
        difficulty_rows += (
            f'<tr><td style="padding:8px 12px;border-bottom:1px solid #e9ecef;">'
            f'<span style="display:inline-block;width:10px;height:10px;border-radius:50%;'
            f'background:{color};margin-right:8px;"></span>{label}</td>'
            f'<td style="padding:8px 12px;border-bottom:1px solid #e9ecef;text-align:center;">{count}</td></tr>'
        )
    if not difficulty_rows:
        difficulty_rows = '<tr><td colspan="2" style="padding:12px;text-align:center;color:#999;">No data</td></tr>'

    return f"""\
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6f9; margin: 0; padding: 0; }}
    .container {{ max-width: 640px; margin: 40px auto; background: #ffffff; border-radius: 12px;
                  box-shadow: 0 2px 16px rgba(0,0,0,0.08); overflow: hidden; }}
    .header {{ background: linear-gradient(135deg, #1b4332, #2d6a4f); padding: 36px 32px; color: #fff; }}
    .header h1 {{ margin: 0 0 6px; font-size: 24px; }}
    .header p {{ margin: 0; opacity: 0.8; font-size: 14px; }}
    .body {{ padding: 32px; color: #333; }}
    .metrics {{ display: flex; flex-wrap: wrap; gap: 16px; margin: 24px 0; }}
    .metric {{ flex: 1; min-width: 120px; background: #f0faf4; border-radius: 10px; padding: 18px;
               text-align: center; }}
    .metric .value {{ font-size: 28px; font-weight: 700; color: #2d6a4f; }}
    .metric .label {{ font-size: 12px; color: #6c757d; margin-top: 4px; text-transform: uppercase;
                      letter-spacing: 0.5px; }}
    h2 {{ font-size: 16px; color: #2d6a4f; margin: 28px 0 12px; border-bottom: 2px solid #d8f3dc;
          padding-bottom: 6px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th {{ background: #2d6a4f; color: #fff; padding: 10px 12px; text-align: left; }}
    th:last-child {{ text-align: center; }}
    .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #999;
               border-top: 1px solid #e9ecef; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>📊 Monthly Activity Report</h1>
      <p>{data["month_label"]}</p>
    </div>
    <div class="body">

      <!-- Key Metrics -->
      <div class="metrics">
        <div class="metric">
          <div class="value">{data["total_treks"]}</div>
          <div class="label">Total Treks</div>
        </div>
        <div class="metric">
          <div class="value">{data["total_participants"]}</div>
          <div class="label">Participants</div>
        </div>
        <div class="metric">
          <div class="value">{data["completion_rate"]}%</div>
          <div class="label">Completion Rate</div>
        </div>
        <div class="metric">
          <div class="value">{data["new_users"]}</div>
          <div class="label">New Users</div>
        </div>
      </div>

      <!-- Popular Treks -->
      <h2>🏔️ Popular Treks</h2>
      <table>
        <tr>
          <th>#</th><th>Trek Name</th><th>Location</th><th style="text-align:center;">Bookings</th>
        </tr>
        {popular_rows}
      </table>

      <!-- Difficulty Breakdown -->
      <h2>📈 Difficulty Breakdown</h2>
      <table>
        <tr><th>Difficulty</th><th style="text-align:center;">Count</th></tr>
        {difficulty_rows}
      </table>

      <!-- Additional Stats -->
      <h2>📋 Additional Stats</h2>
      <table>
        <tr>
          <td style="padding:8px 12px;border-bottom:1px solid #e9ecef;">Completed Treks</td>
          <td style="padding:8px 12px;border-bottom:1px solid #e9ecef;text-align:center;font-weight:600;">{data["completed_treks"]}</td>
        </tr>
        <tr>
          <td style="padding:8px 12px;border-bottom:1px solid #e9ecef;">Cancelled Bookings</td>
          <td style="padding:8px 12px;border-bottom:1px solid #e9ecef;text-align:center;font-weight:600;">{data["cancelled_bookings"]}</td>
        </tr>
      </table>

    </div>
    <div class="footer">
      Trekking Management App &mdash; Auto-generated monthly report
    </div>
  </div>
</body>
</html>"""
