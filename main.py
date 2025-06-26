import os, sys, gspread, smtplib, ssl
from google.oauth2.service_account import Credentials
from email.message import EmailMessage

# 1. Параметры из переменных окружения (берёт из GitHub Secrets)
SENDER_EMAIL    = os.environ["SENDER_EMAIL"]
PASSWORD        = os.environ["EMAIL_PASSWORD"]
RECEIVER_EMAIL  = os.environ["RECEIVER_EMAIL"]

# 2. Настройки Google Sheets
SPREADSHEET_NAME      = "Contacts"
COLUMN_NAME_FOR_EMAIL = "Имя"
COLUMN_NAME_FOR_PHONE = "Номер телефона"

# 3. Проверяем аргумент с путём к creds.json
if len(sys.argv) < 2:
    print("❌ Нужен путь к creds.json")
    sys.exit(1)

creds_path = sys.argv[1]
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# 4. Авторизация
creds   = Credentials.from_service_account_file(creds_path, scopes=scopes)
client  = gspread.authorize(creds)
sheet   = client.open(SPREADSHEET_NAME).sheet1
rows    = sheet.get_all_values()
headers = rows[0]
data    = rows[1:]

# 5. Индексы интересующих колонок
email_idx  = headers.index(COLUMN_NAME_FOR_EMAIL)
phone_idx  = headers.index(COLUMN_NAME_FOR_PHONE)

# 6. Формируем письмо
body = "Отчёт по таблице\n\n"
for i, row in enumerate(data, 1):
    body += f"{i}. Имя: {row[email_idx]} • Телефон: {row[phone_idx]}\n"

msg = EmailMessage()
msg.set_content(body)
msg["Subject"] = f"Отчёт по таблице «{SPREADSHEET_NAME}»"
msg["From"] = SENDER_EMAIL
msg["To"] = RECEIVER_EMAIL

with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as s:
    s.login(SENDER_EMAIL, PASSWORD)
    s.send_message(msg)

print("✅ Письмо отправлено")
