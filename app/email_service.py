"""
Email service for password-reset links (Daniel).

MAIL_BACKEND in .env decides what happens:

  console  -> the email (including the link) is printed in the terminal
              running Flask. For LOCAL TESTING ONLY - never use in production,
              because anyone who can read the logs could reset passwords.
  smtp     -> the email is really sent via the SMTP server in .env
              (e.g. Gmail with an App Password - see README).

send_email() returns True if the email was handed to the server (or printed),
False if sending failed. Failures are logged on the server; the user is never
told, so the page cannot be used to probe which emails are registered.
"""
# Load the tools needed in this file.
import logging
# Load the tools needed in this file.
import smtplib
# Load the tools needed in this file.
import ssl
# Use functions and classes from another file.
from email.message import EmailMessage

# Use functions and classes from another file.
from flask import current_app, render_template

log = logging.getLogger(__name__)


# Handle send email requests or data.
def send_email(to_address, subject, text_body, html_body=None) -> bool:
    cfg = current_app.config
    backend = cfg["MAIL_BACKEND"]

    # Check the condition before continuing.
    if backend == "console":
        banner = "=" * 70
        print(f"\n{banner}\n[DEV EMAIL - console backend, NOT actually sent]\n"
              f"To: {to_address}\nSubject: {subject}\n\n{text_body}\n{banner}\n", flush=True)
        # Send the result back to the code that called this function.
        return True

    # Check the condition before continuing.
    if backend != "smtp":
        log.error("Unknown MAIL_BACKEND %r - email not sent", backend)
        # Send the result back to the code that called this function.
        return False

    # Check the condition before continuing.
    if not (cfg["MAIL_SERVER"] and cfg["MAIL_SENDER"]):
        log.error("SMTP is not configured (MAIL_SERVER / MAIL_SENDER missing) - email not sent")
        # Send the result back to the code that called this function.
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"FinSync <{cfg['MAIL_SENDER']}>"
    msg["To"] = to_address
    msg.set_content(text_body)
    # Check the condition before continuing.
    if html_body:
        msg.add_alternative(html_body, subtype="html")

    context = ssl.create_default_context()
    # Try the operation and handle any errors.
    try:
        # Check the condition before continuing.
        if cfg["MAIL_USE_SSL"]:
            server = smtplib.SMTP_SSL(cfg["MAIL_SERVER"], cfg["MAIL_PORT"],
                                      timeout=cfg["MAIL_TIMEOUT"], context=context)
        else:
            server = smtplib.SMTP(cfg["MAIL_SERVER"], cfg["MAIL_PORT"], timeout=cfg["MAIL_TIMEOUT"])
        # Use this resource and close it when finished.
        with server:
            # Check the condition before continuing.
            if cfg["MAIL_USE_TLS"] and not cfg["MAIL_USE_SSL"]:
                server.starttls(context=context)
            # Check the condition before continuing.
            if cfg["MAIL_USERNAME"]:
                server.login(cfg["MAIL_USERNAME"], cfg["MAIL_PASSWORD"])
            server.send_message(msg)
        log.info("Email '%s' handed to SMTP server %s", subject, cfg["MAIL_SERVER"])
        # Send the result back to the code that called this function.
        return True
    except (smtplib.SMTPException, OSError) as exc:
        # Do not log the message body: it contains the reset link.
        log.error("Failed to send email via %s:%s - %s: %s",
                  cfg["MAIL_SERVER"], cfg["MAIL_PORT"], type(exc).__name__, exc)
        # Send the result back to the code that called this function.
        return False


# Handle send password reset email requests or data.
def send_password_reset_email(to_address, first_name, reset_url, expiry_minutes) -> bool:
    context = dict(first_name=first_name or "there", reset_url=reset_url,
                   expiry_minutes=expiry_minutes)
    text_body = render_template("email/reset_password.txt", **context)
    html_body = render_template("email/reset_password.html", **context)
    # Send the result back to the code that called this function.
    return send_email(to_address, "Reset your FinSync password", text_body, html_body)
