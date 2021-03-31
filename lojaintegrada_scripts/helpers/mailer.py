import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send(email_to, subject, body='', files_to_send=tuple()):
  login = os.getenv("GMAIL_LOGIN")
  password = os.getenv("GMAIL_PASSWD")
  email_from = f"{login}@gmail.com"

  msg = MIMEMultipart()
  msg["From"] = 'Notta Bot'
  msg["To"] = 'Cliente LojaIntegrada'
  msg["Subject"] = subject
  msg.attach(MIMEText(body, _subtype='plain'))

  for file_hash in files_to_send:
    with open(file_hash['file']) as fp:
      attachment = MIMEText(fp.read(), _subtype='csv')

    attachment.add_header("Content-Disposition", "attachment", filename=f"{file_hash['name']}.csv")
    msg.attach(attachment)

  server = smtplib.SMTP("smtp.gmail.com", 587)
  server.ehlo()
  server.starttls()
  server.login(login, password)
  server.sendmail(email_from, email_to, msg.as_string())
  server.quit()
