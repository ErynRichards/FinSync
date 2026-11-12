# email_service.py
# Sends the password-reset email.
#
# MAIL_BACKEND in .env decides what happens:
#   console - the email is printed in the terminal (for testing on your own computer)
#   smtp    - the email is really sent, e.g. through Gmail with an App Password

# Load the tools needed in this file.
import smtplib
# Use functions and classes from another file.
from email.message import EmailMessage

# Load the tools needed in this file.
import config


# Handle send reset email requests or data.
def send_reset_email(to_email, first_name, reset_link):
    """Send the reset link to the user. Returns True if it worked."""
    subject = "Reset your FinSync password"
    body = f"""Hi {first_name},

We received a request to reset the password for your FinSync account.

Click this link to choose a new password:
{reset_link}

This link expires in {config.RESET_TOKEN_EXPIRY_MINUTES} minutes and can only be used once.

If you did not ask to reset your password, you can ignore this email.

The FinSync team
"""

    # Testing mode: print the email instead of sending it
    if config.MAIL_BACKEND == "console":
        print("\nEMAIL (not sent, console mode)")
        print("To:", to_email)
        print("Subject:", subject)
        print(body)
        # Send the result back to the code that called this function.
        return True

    # Real sending through an SMTP server
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = config.MAIL_USERNAME
    message["To"] = to_email
    message.set_content(body)

    # Try the operation and handle any errors.
    try:
        # Use this resource and close it when finished.
        with smtplib.SMTP(config.MAIL_SERVER, config.MAIL_PORT, timeout=10) as server:
            server.set_debuglevel(1)
            server.starttls()  # encrypt the connection
            server.login(config.MAIL_USERNAME, config.MAIL_PASSWORD)
            server.send_message(message)
        # Send the result back to the code that called this function.
        return True
    except (smtplib.SMTPException, OSError) as error:
        print("Could not send email:", error)
        # Send the result back to the code that called this function.
        return False
