# NOIR VAPE — Django + Telegram

Production-friendly demo. На Vercel сайт не требует PostgreSQL для демонстрационного каталога: если база недоступна/не мигрирована, Django использует встроенный демо-каталог. Локально админка и `seed` работают с SQLite/PostgreSQL.

## Локально
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed
python manage.py runserver
```

## Telegram
```powershell
cd bot
pip install -r requirements.txt
copy .env.example .env
# впиши НОВЫЙ токен в .env
python main.py
```

Бот читает `/api/catalog/` и `/api/stores/` с Django-сайта. Дистанционная продажа никотинсодержащей продукции не реализована.
