import sys
import gspread
from google.oauth2.service_account import Credentials
import smtplib
import ssl
from email.message import EmailMessage
import os

# Берем переменные из окружения
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
PASSWORD = os.environ.get("EMAIL_PASSWORD")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")

# === ДЕБАГ ПЕЧАТЬ (безопасно) ===
print("\n=== ПРОВЕРКА СЕКРЕТОВ ===")
print(f"SENDER_EMAIL: {SENDER_EMAIL}")
print(f"EMAIL_PASSWORD: {'*' * len(PASSWORD) if PASSWORD else '[ПУСТО]'}")
print(f"RECEIVER_EMAIL: {RECEIVER_EMAIL}")


# --- НАСТРОЙКИ GOOGLE ТАБЛИЦЫ ---
SPREADSHEET_NAME = "Contacts"
COLUMN_NAME_FOR_EMAIL = "Имя"
COLUMN_NAME_FOR_STATUS = "Номер телефона"

print("\n=== ПЕРЕМЕННЫЕ GOOGLE ТАБЛИЦЫ ===")
print(f"SPREADSHEET_NAME: {SPREADSHEET_NAME}")
print(f"COLUMN_NAME_FOR_EMAIL: {COLUMN_NAME_FOR_EMAIL}")
print(f"COLUMN_NAME_FOR_STATUS: {COLUMN_NAME_FOR_STATUS}")

# --- НАСТРОЙКИ ПОЧТЫ ---
SMTP_SERVER = "smtp.gmail.com"
PORT = 465
SENDER_EMAIL = "chatgptbalance@gmail.com"
PASSWORD = "hmkz cumc odlh qqby"  # В реальном коде лучше не выводить
RECEIVER_EMAIL = "katya.efremova.0404@mail.ru"

print("\n=== ПЕРЕМЕННЫЕ ПОЧТЫ ===")
print(f"SMTP_SERVER: {SMTP_SERVER}")
print(f"PORT: {PORT}")
print(f"SENDER_EMAIL: {SENDER_EMAIL}")
print(f"PASSWORD: {'*'*len(PASSWORD)}")  # Маскируем пароль
print(f"RECEIVER_EMAIL: {RECEIVER_EMAIL}")

# --- ПОДКЛЮЧЕНИЕ К GOOGLE SHEETS ---
if len(sys.argv) < 2:
    print("\n❌ Укажите путь к файлу учетных данных в качестве аргумента.")
    sys.exit(1)

creds_path = sys.argv[1]
print(f"\nПуть к файлу учетных данных: {creds_path}")

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
print(f"\nScopes: {scopes}")

try:
    credentials = Credentials.from_service_account_file(creds_path, scopes=scopes)
    client = gspread.authorize(credentials)
    sheet = client.open(SPREADSHEET_NAME).sheet1
    print("\n✅ Успешное подключение к Google Sheets")
except Exception as e:
    print(f"\n❌ Ошибка подключения: {e}")
    sys.exit(1)

# --- ЧТЕНИЕ И ОБРАБОТКА ---
rows = sheet.get_all_values()
headers = rows[0]
data = rows[1:]

print("\n=== ДАННЫЕ ИЗ ТАБЛИЦЫ ===")
print("Заголовки:", headers)
print(f"Найдено строк данных: {len(data)}")

try:
    email_index = headers.index(COLUMN_NAME_FOR_EMAIL)
    status_index = headers.index(COLUMN_NAME_FOR_STATUS)
    print(f"\nИндекс колонки '{COLUMN_NAME_FOR_EMAIL}': {email_index}")
    print(f"Индекс колонки '{COLUMN_NAME_FOR_STATUS}': {status_index}")
except ValueError as e:
    print(f"\n❌ Ошибка: {e}. Проверьте названия колонок.")
    sys.exit(1)

# Формируем тело письма с нумерацией строк
email_body = "Отчет по таблице:\n\n"
for i, row in enumerate(data, 1):
    email = row[email_index] if len(row) > email_index else "N/A"
    value = row[status_index] if len(row) > status_index else "N/A"
    email_body += f"{i}. Имя: {email}, Телефон: {value}\n"
    print(f"Обработана строка {i}: Имя='{email}', Телефон='{value}'")

print("\n=== СОДЕРЖИМОЕ ПИСЬМА ===")
print(email_body)

# --- ОТПРАВКА ПИСЬМА ---
try:
    message = EmailMessage()
    message.set_content(email_body)
    message["Subject"] = f"Отчет по таблице {SPREADSHEET_NAME}"
    message["From"] = SENDER_EMAIL
    message["To"] = RECEIVER_EMAIL

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, PORT, context=context) as server:
        server.login(SENDER_EMAIL, PASSWORD)
        server.send_message(message)
    print("\n✅ Письмо успешно отправлено")
except Exception as e:
    print(f"\n❌ Ошибка отправки письма: {e}")
