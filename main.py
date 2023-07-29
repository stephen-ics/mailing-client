import os.path
import smtplib
import base64

from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://mail.google.com/']

USER_TOKENS = 'tokens.json'

CREDENTIALS = 'credentials.json'

def getToken() -> str:
    creds = None

    if os.path.exists(USER_TOKENS):
        creds = Credentials.from_authorized_user_file(USER_TOKENS, SCOPES)
        creds.refresh(Request())

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS, SCOPES)
            creds = flow.run_local_server(port=0)

            with open(USER_TOKENS, 'w') as token:
                token.write(creds.to_json())

    return creds.token

def generate_oauth2_string(username, access_token) -> str:
    auth_string = f'user={username}\1auth=Bearer {access_token}\1\1'
    return base64.b64encode(auth_string.encode('ascii')).decode('ascii')

def send_email(host, port, subject, msg, sender, recipients):
    access_token = getToken()
    print(access_token)
    auth_string = generate_oauth2_string(sender, access_token)

    msg = MIMEText(msg)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)

    server = smtplib.SMTP(host, port)
    server.starttls()
    server.docmd('AUTH', 'XOAUTH2 ' + auth_string)
    print(msg.as_string())
    server.sendmail(sender, recipients, msg.as_string())
    server.quit()

def main():
    host = 'smtp.gmail.com'
    port = 587

    user = 'stephenni1234@gmail.com'
    recipient = 'stephenni1234@gmail.com'
    subject = 'Test email Oauth2'
    msg = 'Hello world!'
    sender = user
    recipients = [recipient]

    print(sender)

    send_email(host, port, subject, msg, sender, recipients)

if __name__ == '__main__':
    main()