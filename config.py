import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent

# override=False: переменные, уже заданные в окружении (CI, оболочка),
# не затираются файлом .env. Так локальный .env и CI живут вместе.
load_dotenv(ROOT_DIR / ".env", override=False)


def require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        raise RuntimeError(
            f"Не задана переменная окружения {name}. "
            "Скопируйте .env.example в .env и заполните значения "
            "или экспортируйте переменную в окружении."
        )
    return value


ADMIN_EMAIL = require_env("ADMIN_EMAIL")
ADMIN_PASSWORD = require_env("ADMIN_PASSWORD")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

DB_HOST = require_env("DB_HOST")
DB_PORT = require_env("DB_PORT")
DB_NAME = require_env("DB_NAME")
DB_USER = require_env("DB_USER")
DB_PASSWORD = require_env("DB_PASSWORD")

# quote_plus экранирует @, :, / в пароле, иначе SQLAlchemy разрежет URL не там.
DATABASE_URL = (
    f"postgresql+psycopg2://{quote_plus(DB_USER)}:{quote_plus(DB_PASSWORD)}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
