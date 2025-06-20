import gspread
from google.oauth2.service_account import Credentials
import smtplib
import ssl
from email.message import EmailMessage

# --- НАСТРОЙКИ GOOGLE ТАБЛИЦЫ ---
SPREADSHEET_NAME = "Contacts"
COLUMN_NAME_FOR_EMAIL = "Имя"
COLUMN_NAME_FOR_STATUS = "Номер телефона"

# --- НАСТРОЙКИ ПОЧТЫ ---
SMTP_SERVER = "smtp.gmail.com"
PORT = 465
SENDER_EMAIL = "chatgptbalance@gmail.com"
PASSWORD = "hmkz cumc odlh qqby"
RECEIVER_EMAIL = "katya.efremova.0404@mail.ru"

# --- ПОДКЛЮЧЕНИЕ К GOOGLE SHEETS ---
scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
credentials = Credentials.from_service_account_file(
    "precise-rune-463409-s6-2579aef7d5ac.json", scopes=scopes
)

client = gspread.authorize(credentials)
sheet = client.open(SPREADSHEET_NAME).sheet1

# --- ЧТЕНИЕ И ОБРАБОТКА ---
rows = sheet.get_all_values()
headers = rows[0]
data = rows[1:]

print("Заголовки колонок:", headers)

# Индексы нужных колонок
email_index = headers.index(COLUMN_NAME_FOR_EMAIL)
status_index = headers.index(COLUMN_NAME_FOR_STATUS)

# Формируем тело письма из всех строк
if not data:
    email_body = "Нет данных в таблице."
else:
    email_body = "Все строки из таблицы:\n\n"
    for row in data:
        email = row[email_index] if len(row) > email_index else "(нет email)"
        value = row[status_index] if len(row) > status_index else "(нет значения)"
        email_body += f"Email: {email}, Value: {value}\n"

# --- ОТПРАВКА ПИСЬМА ---
message = EmailMessage()
message.set_content(email_body)
message["Subject"] = "Отчет по таблице 'vv'"
message["From"] = SENDER_EMAIL
message["To"] = RECEIVER_EMAIL

context = ssl.create_default_context()
with smtplib.SMTP_SSL(SMTP_SERVER, PORT, context=context) as server:
    server.login(SENDER_EMAIL, PASSWORD)
    server.send_message(message)

print("Письмо отправлено ✅")
