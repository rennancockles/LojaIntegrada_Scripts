import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def send(email_to, subject, body='', files_to_send=tuple()):
  login = os.getenv("GMAIL_LOGIN")
  password = os.getenv("GMAIL_PASSWD")
  email_from = f"{login}@gmail.com"

  msg = MIMEMultipart()
  msg["From"] = 'Notta Bot'
  msg["To"] = 'Cliente LojaIntegrada'
  msg["Subject"] = subject
  msg.attach(MIMEText(body, _subtype='plain'))

  for file_dict in files_to_send:
    file_name = file_dict['file']
    extension = file_name.rsplit('.', 1)[1]
    if extension == 'csv':
      with open(file_name, encoding='utf-8') as fp:
        attachment = MIMEText(fp.read(), _subtype=extension, _charset='utf-8')
        attachment.add_header("Content-Disposition", "attachment", filename=f"{file_dict['name']}.{extension}")
    else:
      with open(file_name, 'rb') as fp:
        attachment = MIMEBase('application', "octet-stream")
        attachment.set_payload(fp.read())
        encoders.encode_base64(attachment)
        attachment.add_header("Content-Disposition", "attachment", filename=f"{file_dict['name']}.{extension}")

    msg.attach(attachment)

  server = smtplib.SMTP("smtp.gmail.com", 587)
  server.ehlo()
  server.starttls()
  server.login(login, password)
  server.sendmail(email_from, email_to, msg.as_string())
  server.quit()
