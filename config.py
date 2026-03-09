import os
from dotenv import load_dotenv

load_dotenv()

VK_TOKEN = os.getenv("VK_TOKEN")
VK_API_VERSION = "5.199"

if not VK_TOKEN:
    raise EnvironmentError(
        "VK_TOKEN не найден. Создайте файл .env с VK_TOKEN=<ваш_токен>"
    )
