# Запуск API-тестов

Фреймворк гоняет pytest против уже запущенного HTTP API и сверяет часть ответов с PostgreSQL. Тесты сами создают пользователей и items и убирают их в teardown.

## Что понадобится

- Python 3.10 или новее
- Запущенное API (по умолчанию `http://localhost:8000`)
- PostgreSQL с той же базой, которую использует API
- Учётка суперпользователя, которым API уже умеет логиниться

Тесты не поднимают сервер и не накатывают миграции. Стенд должен быть жив до `pytest`.

## Стенд

Из каталога API:

```bash
docker compose up -d
curl http://localhost:8000/api/v1/utils/health-check/
```

Ответ `true` — можно запускать тесты.

## Установка

Из корня репозитория:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

В bash то же самое, активация другая:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

`requirements.txt` фиксирует версии, с которыми прогон воспроизводим. `pydantic` стоит `2.14.0`: версий `2.3.15` и `2.13.15` на PyPI нет, линейка 2.3 закончилась на `2.3.0`.

## Настройка стенда

Секреты и адрес базы не лежат в коде. Их читает `config.py` через [python-dotenv](https://github.com/theskumar/python-dotenv).

```powershell
copy .env.example .env
```

Заполни `.env`:

| Переменная | Зачем |
| --- | --- |
| `BASE_URL` | Корень API. Если переменной нет, берётся `http://localhost:8000` |
| `ADMIN_EMAIL`, `ADMIN_PASSWORD` | Логин суперпользователя. Им тесты удаляют созданных пользователей |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Подключение SQLAlchemy для проверок в базе |

`.env` в git не коммитится. Файл `.env.example` коммитится и содержит только плейсхолдеры.

Порядок значений такой: переменная, уже заданная в оболочке или CI, важнее строчки в `.env` (`load_dotenv(..., override=False)`). В CI файл можно не класть, достаточно экспортировать те же имена.

Пароль в URL базы кодируется через `urllib.parse.quote_plus`, чтобы символы `@` и `:` в пароле не ломали строку подключения.

Пароль одноразового пользователя из фикстуры `regular_user` в `.env` не выносится: тест сам придумывает его через `secrets.token_hex` и забывает вместе с пользователем. В окружение попадают только секреты стенда, которые тесты не создают.

## Запуск

Из корня репозитория:

```powershell
pytest
```

Полезные сужения:

```powershell
pytest tests/test_items.py
pytest tests/test_roles.py -k delete
pytest -n auto
```

`-n auto` включает pytest-xdist. Пользователи и items создаются с уникальным email и title, фикстуры имеют scope `function`, поэтому тесты не делят учётки между собой.

Сценарии без SQLAlchemy:

```powershell
pytest tests/test_auth.py tests/test_roles.py
```

В PostgreSQL ходят `tests/test_users.py` и `test_update_item_and_verify_in_db`. Остальные тесты в `tests/test_items.py` говорят только с API.

## Что делают тесты

- `tests/test_auth.py` — регистрация, логин, валидация тела signup.
- `tests/test_users.py` — `GET /users/me` сверяет `id` и `email` ответа с созданным пользователем и со строкой в БД; каскадное удаление пользователя вместе с его items.
- `tests/test_items.py` — создание сверяет `title`, `description` и `owner_id`; обновление читает строку из БД; удаление требует `DELETE 200`, затем отдельный `GET 404`.
- `tests/test_roles.py` — матрица admin / regular / guest на список пользователей и на удаление. Чужой item обновить нельзя.

Схема ответа проверяется моделями pydantic в `schemas.py`. Совпадение схемы не заменяет сверку полей: модель проверяет форму, assert проверяет, что API вернул именно те данные, которые тест отправил.

## Как устроена очистка

Созданный пользователь или item сразу регистрируется в фикстуре `user_cleanup` или `item_cleanup`. Код после `yield` в этих фикстурах выполняется после теста, в том числе после упавшего assert.

- Пользователей удаляет админ. Обычный пользователь на `DELETE /users/{id}` получает 403, поэтому фикстура `regular_user` сама себя стереть не может.
- Items удаляются токеном владельца и раньше пользователей. Порядок задаёт зависимость: `item_cleanup` просит `user_cleanup`, pytest поднимает зависимости первыми и сносит фикстуры с конца.
- В teardown допустимы `200` (удалили сейчас) и `404` (тест уже удалил запись сам, повтор безопасен). Другой HTTP-код или исключение не прерывают цикл: остальные id всё равно удаляются. В конце teardown падает один раз и перечисляет каждый неудачный ресурс.
- В теле теста удаления договор другой. `DELETE` только что созданного item должен вернуть `200`. Следующий `GET` этого id должен вернуть `404`. `404` на самом `DELETE` успехом не считается.

Админская учётка в teardown не удаляется: это учётка стенда, не данные теста.

## Структура

```
config.py            чтение .env и сборка DATABASE_URL
conftest.py          клиент, роли, реестры очистки, сессия БД
schemas.py           pydantic-модели ответов
models.py            таблицы user и item для SQLAlchemy
services/            обёртки над URL пользователей и items
utils/api_client.py  requests.Session
utils/cleanup.py     цикл teardown: ошибка одного id не останавливает остальные
tests/               сценарии
```

## Прогон коммита

Лог снят с чистого дерева коммита `23329530c4c84fcc1522dfe90b90440bcc2da255` (`fix(tests): не прерывать очистку на ошибке одного ресурса`), ветка `practice/gorohov.maksimdmitrievich`. Скриншот сюда не кладётся: в выводе есть SHA, команда и окружение.

```text
commit: 23329530c4c84fcc1522dfe90b90440bcc2da255
subject: fix(tests): не прерывать очистку на ошибке одного ресурса
branch: practice/gorohov.maksimdmitrievich
status:
command: pytest -vv
cwd: C:\Users\maksi\PycharmProjects\fastapi-api-testing-framework
os: Microsoft Windows NT 10.0.26300.0
python: 3.11.15 (main, Jun  2 2026, 22:29:49) [MSC v.1944 64 bit (AMD64)]
pytest: pytest 8.0.0
packages:
Faker==20.1.0 httpx==0.28.1 pydantic==2.14.0 pytest==8.0.0 pytest-xdist==3.5.0 python-dotenv==1.2.4 requests==2.31.0 ruff==0.17.0 SQLAlchemy==2.1.4 tenacity==9.1.4
BASE_URL=http://localhost:8000
============================= test session starts =============================
platform win32 -- Python 3.11.15, pytest-8.0.0, pluggy-1.6.0 -- C:\Users\maksi\AppData\Local\Temp\fastapi-req-check\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\maksi\PycharmProjects\fastapi-api-testing-framework
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1, Faker-20.1.0, xdist-3.5.0
collecting ... collected 28 items

tests/test_auth.py::test_signup_success PASSED                           [  3%]
tests/test_auth.py::test_login_success PASSED                            [  7%]
tests/test_auth.py::test_signup_validation[invalid_email] PASSED         [ 10%]
tests/test_auth.py::test_signup_validation[empty_email] PASSED           [ 14%]
tests/test_auth.py::test_signup_validation[invalid_password] PASSED      [ 17%]
tests/test_auth.py::test_signup_validation[empty_password] PASSED        [ 21%]
tests/test_cleanup.py::test_cleanup_keeps_going_after_http_error PASSED  [ 25%]
tests/test_cleanup.py::test_cleanup_reports_each_failed_status[500] PASSED [ 28%]
tests/test_cleanup.py::test_cleanup_reports_each_failed_status[403] PASSED [ 32%]
tests/test_cleanup.py::test_cleanup_continues_after_exception PASSED     [ 35%]
tests/test_cleanup.py::test_cleanup_accepts_200_and_404 PASSED           [ 39%]
tests/test_items.py::test_create_item_success PASSED                     [ 42%]
tests/test_items.py::test_create_item_negative_validation[-422-string_too_short] PASSED [ 46%]
tests/test_items.py::test_create_item_negative_validation[AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA-422-string_too_long] PASSED [ 50%]
tests/test_items.py::test_create_item_validation PASSED                  [ 53%]
tests/test_items.py::test_update_item_and_verify_in_db PASSED            [ 57%]
tests/test_items.py::test_delete_item PASSED                             [ 60%]
tests/test_roles.py::test_get_all_users_access[admin] PASSED             [ 64%]
tests/test_roles.py::test_get_all_users_access[regular] PASSED           [ 67%]
tests/test_roles.py::test_get_all_users_access[guest] PASSED             [ 71%]
tests/test_roles.py::test_delete_user[admin] PASSED                      [ 75%]
tests/test_roles.py::test_delete_user[regular] PASSED                    [ 78%]
tests/test_roles.py::test_delete_user[guest] PASSED                      [ 82%]
tests/test_roles.py::test_item_ownership PASSED                          [ 85%]
tests/test_users.py::test_success_signup_user_in_db PASSED               [ 89%]
tests/test_users.py::test_read_user_authorized PASSED                    [ 92%]
tests/test_users.py::test_cascade_verification PASSED                    [ 96%]
tests/test_users.py::test_get_user PASSED                                [100%]

============================= 28 passed in 10.80s =============================
```
