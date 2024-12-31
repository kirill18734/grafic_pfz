import smtplib
import socket
import sys
import traceback
from datetime import datetime
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

import requests

from config.auto_search_dir import *

# Извлечь тему алерта из конфигурации
theme = data_config["ServiceMode"]["AlertName"]
# Отправить сообщение в тестовый общий канал в Телеграме

# определение тестовое ли сообщение
test_mode = data_config["ServiceMode"]["test_mode"]

# если тестовое , то в тестовый канал , если нет , то в оригинал
def send_to_telegram(text):
    if test_mode == "True":
        config_key = 'my_telegram_bot'
    else:
        config_key = 'telegram'

    token = data_config[config_key]['bot_token']
    chat_id = data_config[config_key]['chat_id']

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    response = requests.post(url, json=payload, verify=False)
    return response


# отправка  на email
def send_email(body, receivers_ = '',  attachments=None):
    author = formataddr((str(Header("Monitoring OAiKPO", 'utf-8')), socket.gethostname()))
    receivers = data_config["Addresses"]["receivers"].replace(' ', '').split(",")
    receivers_a = receivers_.replace(' ', '').split(",")
    cc_receivers = data_config["Addresses"]["cc_receivers"].replace(' ',
                                                                    '').split(
        ",")
    receivers_email = receivers if receivers != [''] else receivers_a
    if receivers_email:
        msg = MIMEMultipart()
        msg['Subject'] = Header(theme, 'utf-8')
        msg['From'] = author
        msg['To'] = ";".join(receivers_email)
        msg.attach(MIMEText(body, 'html', 'utf-8'))
        if attachments:
            part = MIMEBase('application', "octet-stream")
            part.set_payload(open(attachments, "rb").read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="Attachments.xlsx"')
            msg.attach(part)
        s = smtplib.SMTP('post22v.corp.loc')
        if cc_receivers is None or cc_receivers == ['']:
            s.sendmail(author, receivers_email, msg.as_string())
        else:
            msg['CC'] = ", ".join(cc_receivers)
            s.sendmail(author, receivers_email + cc_receivers, msg.as_string())
        s.quit()

# отправка ошибки на email
def send_email_error_script():
    error = traceback.format_exc().replace('"', '').replace("'", "")
    receivers_admin = data_config["Addresses"]["receivers_admin"].replace(' ', '').split(",")
    if receivers_admin != ['']:
        error_text = ""
        error_text += "<p><font size=3 color=#FF0000 face=times new roman>Задание "
        error_text += "<b><font color=#000000>{0}</font></b> завершилось с ошибкой. Исправьте ошибки и запустите " \
                      "задание " \
                      "повторно.</font></p>\n".format(path_to_project_folder)
        error_text += "<table border=1 BGCOLOR=#F0F8FF>\n"
        error_text += "<tr BGCOLOR=#E0FFFF><th>Сервер</th><th>Дата обнаружения</th><th>Текст ошибки</th></tr>\n"
        error_text += "<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>\n".format(socket.gethostname(),
                                                                               datetime.now().strftime(
                                                                                   "%d.%m.%Y %H:%M"), error)
        error_text += "</table>\n"
        error_text += "<p>_____________________________________</p>\n"
        error_text += "<p>Отчет сформирован {0} </p>\n".format(os.path.basename(sys.argv[0]))

        author = formataddr((str(Header("Python monitoring", 'utf-8')), socket.gethostname()))
        msg = MIMEText(error_text, 'html', 'utf-8')
        msg['Subject'] = Header(theme, 'utf-8')
        msg['From'] = author
        msg['To'] = ", ".join(receivers_admin)
        s = smtplib.SMTP('post22v.corp.loc')

        s.sendmail(msg['From'], receivers_admin, msg.as_string())
        s.quit()
