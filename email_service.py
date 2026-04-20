import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# ─────────────────────────────────────────────────────────────────────────────
#  CONFIGURE YOUR EMAIL HERE
#  1. Use your Gmail address as SENDER_EMAIL
#  2. Create a Gmail App Password:
#     → Google Account → Security → 2-Step Verification → App Passwords
#     → Select "Mail" + "Windows Computer" → Generate
#  3. Paste the 16-character app password as SENDER_APP_PASSWORD
# ─────────────────────────────────────────────────────────────────────────────
SENDER_EMAIL       = "your_gmail@gmail.com"     # ← CHANGE THIS
SENDER_APP_PASSWORD = "xxxx xxxx xxxx xxxx"     # ← CHANGE THIS (Gmail App Password)
SENDER_NAME        = "InsightClass Monitor"


def send_password_email(to_email, username, password):
    """
    Send an email to the user with their password.
    Returns (True, "sent") or (False, "error message").
    """
    subject = "🔑 Your InsightClass Password Recovery"

    html_body = f"""
    <div style="font-family:'Segoe UI',sans-serif; max-width:500px; margin:0 auto; padding:20px;">
        <div style="background:#343a40; color:white; padding:20px; border-radius:10px 10px 0 0; text-align:center;">
            <h2 style="margin:0;">🎓 InsightClass Monitor</h2>
            <p style="margin:5px 0; opacity:0.8; font-size:0.9rem;">Password Recovery</p>
        </div>
        <div style="background:#ffffff; padding:30px; border:1px solid #ddd; border-radius:0 0 10px 10px;">
            <p>Hello <b>{username}</b>,</p>
            <p>We received a password recovery request for your account. Here are your login details:</p>

            <div style="background:#f8f9fa; border-left:4px solid #007bff; padding:15px; border-radius:4px; margin:20px 0;">
                <p style="margin:5px 0;"><b>Username:</b> <span style="color:#007bff;">{username}</span></p>
                <p style="margin:5px 0;"><b>Password:</b> <span style="color:#28a745; font-size:1.2rem; font-weight:bold;">{password}</span></p>
            </div>

            <p style="color:#666; font-size:0.9rem;">
                🔒 For your security, we recommend changing your password after logging in.
            </p>
            <p style="color:#666; font-size:0.9rem;">
                If you did not request this, please ignore this email.
            </p>

            <div style="text-align:center; margin-top:25px;">
                <a href="http://localhost:5000" 
                   style="background:#007bff; color:white; padding:12px 30px; border-radius:6px; text-decoration:none; font-weight:bold;">
                    Login Now →
                </a>
            </div>
        </div>
        <p style="text-align:center; color:#999; font-size:0.8rem; margin-top:15px;">
            InsightClass Monitor — Emotion-Aware Learning Assistant
        </p>
    </div>
    """

    # Plain text fallback
    plain_body = f"""
    InsightClass Password Recovery

    Hello {username},

    Your login details:
    Username : {username}
    Password : {password}

    If you did not request this, please ignore this email.
    """

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"{SENDER_NAME} <{SENDER_EMAIL}>"
        msg["To"]      = to_email

        msg.attach(MIMEText(plain_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())

        return True, "sent"

    except smtplib.SMTPAuthenticationError:
        return False, "Email authentication failed. Please check SENDER_EMAIL and SENDER_APP_PASSWORD in email_service.py"
    except smtplib.SMTPException as e:
        return False, f"SMTP error: {str(e)}"
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"
