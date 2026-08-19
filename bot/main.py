from dotenv import load_dotenv
load_dotenv()

import html
import logging
import os
import sqlite3
from pathlib import Path

import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

SITE_URL = os.getenv("SITE_URL", "http://127.0.0.1:8000").rstrip("/")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
ADMIN_IDS = {
    int(value.strip())
    for value in os.getenv("TELEGRAM_ADMIN_IDS", "").split(",")
    if value.strip().lstrip("-").isdigit()
}
if not TOKEN:
    raise RuntimeError("Set TELEGRAM_BOT_TOKEN in the environment.")
if not ADMIN_IDS:
    raise RuntimeError("Set TELEGRAM_ADMIN_IDS in the environment.")

DB_PATH = Path(__file__).with_name("support.sqlite3")


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS support_messages (
            admin_chat_id INTEGER NOT NULL,
            admin_message_id INTEGER NOT NULL,
            user_chat_id INTEGER NOT NULL,
            PRIMARY KEY (admin_chat_id, admin_message_id)
        )
        """
    )
    conn.commit()
    return conn


def remember_admin_message(admin_chat_id: int, admin_message_id: int, user_chat_id: int):
    conn = db()
    conn.execute(
        "INSERT OR REPLACE INTO support_messages(admin_chat_id, admin_message_id, user_chat_id) VALUES (?, ?, ?)",
        (admin_chat_id, admin_message_id, user_chat_id),
    )
    conn.commit()
    conn.close()


def find_user_by_admin_message(admin_chat_id: int, admin_message_id: int):
    conn = db()
    row = conn.execute(
        "SELECT user_chat_id FROM support_messages WHERE admin_chat_id = ? AND admin_message_id = ?",
        (admin_chat_id, admin_message_id),
    ).fetchone()
    conn.close()
    return row[0] if row else None


def api(path):
    r = requests.get(f"{SITE_URL}{path}", timeout=10)
    r.raise_for_status()
    return r.json()


def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Каталог", callback_data="catalog"),
         InlineKeyboardButton("📍 Магазины", callback_data="stores")],
        [InlineKeyboardButton("💬 Связаться с нами", url="https://t.me/VapeShopDemo_bot")],
        [InlineKeyboardButton("🌐 Открыть сайт", url=f"{SITE_URL}/")],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "<b>NOIR VAPE</b>\n\n"
        "Информационный каталог устройств, расходников и аксессуаров.\n\n"
        "18+ • Дистанционная продажа никотинсодержащей продукции через бота не осуществляется.\n"
        "Наличие и актуальную цену уточняйте в физическом магазине.\n\n"
        "Если нужна помощь — нажмите «Связаться с нами», и администратор ответит вам здесь."
    )
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=menu())


async def catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = api("/api/catalog/")
    rows = []
    for c in data["categories"]:
        rows.append([InlineKeyboardButton(f"▣ {c['name']}", callback_data=f"cat:{c['slug']}")])
    rows.append([InlineKeyboardButton("🌐 Весь каталог на сайте", url=f"{SITE_URL}/catalog/")])
    rows.append([InlineKeyboardButton("💬 Связаться с нами", url="https://t.me/VapeShopDemo_bot")])
    await update.callback_query.edit_message_text(
        "<b>Каталог</b>\nВыберите раздел:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(rows),
    )


async def category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    slug = update.callback_query.data.split(":", 1)[1]
    data = api("/api/catalog/")
    cat = next((x for x in data["categories"] if x["slug"] == slug), None)
    if not cat:
        await update.callback_query.answer("Раздел не найден")
        return
    rows = []
    for p in cat["products"]:
        rows.append([InlineKeyboardButton(
            f"{p['name']} · {p['price']:,} ₽".replace(",", " "),
            callback_data=f"prod:{p['id']}"
        )])
    rows.append([InlineKeyboardButton("← Разделы", callback_data="catalog")])
    await update.callback_query.edit_message_text(
        f"<b>{html.escape(cat['name'])}</b>\n\nВыберите товар:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(rows),
    )


async def product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pid = int(update.callback_query.data.split(":", 1)[1])
    data = api("/api/catalog/")
    item = next((p for c in data["categories"] for p in c["products"] if p["id"] == pid), None)
    if not item:
        await update.callback_query.answer("Товар не найден")
        return
    specs = "\n".join(f"• {html.escape(s)}" for s in item["specs"])
    text = (
        f"<b>{html.escape(item['name'])}</b>\n"
        f"{html.escape(item['subtitle'])}\n\n"
        f"<b>{item['price']:,} ₽</b>\n\n".replace(",", " ")
        + f"{html.escape(item['description'])}\n\n"
        f"<b>Характеристики</b>\n{specs}\n\n"
        "Наличие и актуальную цену уточняйте в физическом магазине."
    )
    buttons = [
        [InlineKeyboardButton("🌐 Открыть этот товар на сайте", url=f"{SITE_URL}/catalog/{pid}/")],
        [InlineKeyboardButton("💬 Задать вопрос администратору", url="https://t.me/VapeShopDemo_bot")],
        [InlineKeyboardButton("📍 Найти магазин", callback_data="stores")],
        [InlineKeyboardButton("← Назад", callback_data="catalog")],
    ]
    await update.callback_query.edit_message_text(
        text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons)
    )


async def stores(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = api("/api/stores/")
    lines = ["<b>Магазины NOIR</b>\n"]
    for s in data["stores"]:
        lines.append(
            f"<b>{html.escape(s['name'])}</b>\n"
            f"📍 {html.escape(s['address'])}\n"
            f"🕐 {html.escape(s['hours'])}\n"
            f"☎️ {html.escape(s['phone'])}\n"
        )
    await update.callback_query.edit_message_text(
        "\n".join(lines), parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🌐 Открыть магазины на сайте", url=f"{SITE_URL}/stores/")],
            [InlineKeyboardButton("💬 Связаться с нами", url="https://t.me/VapeShopDemo_bot")],
            [InlineKeyboardButton("← Меню", callback_data="catalog")],
        ])
    )


async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "catalog":
        await catalog(update, context)
    elif q.data.startswith("cat:"):
        await category(update, context)
    elif q.data.startswith("prod:"):
        await product(update, context)
    elif q.data == "stores":
        await stores(update, context)


async def support_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Forward user messages to the admin and relay admin replies back to users."""
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not message or not chat or not user:
        return

    # Admin replies to a copied user message -> send the reply back to that user.
    if user.id in ADMIN_IDS:
        replied = message.reply_to_message
        if not replied:
            return
        user_chat_id = find_user_by_admin_message(chat.id, replied.message_id)
        if not user_chat_id:
            await message.reply_text("Ответьте именно на сообщение пользователя, которое бот переслал в этот чат.")
            return
        try:
            await context.bot.copy_message(
                chat_id=user_chat_id,
                from_chat_id=chat.id,
                message_id=message.message_id,
            )
            await message.reply_text("✓ Ответ отправлен пользователю.")
        except Exception as exc:
            log.exception("Failed to send admin reply: %s", exc)
            await message.reply_text("Не удалось отправить ответ пользователю.")
        return

    # User support message -> notify admin and keep a durable mapping.
    if chat.type != "private":
        return

    username = f"@{user.username}" if user.username else "без username"
    name = html.escape(user.full_name or "Пользователь")
    header = (
        "<b>💬 Новое сообщение</b>\n"
        f"Имя: {name}\n"
        f"Username: {html.escape(username)}\n"
        f"Telegram ID: <code>{user.id}</code>\n\n"
        "Ответьте реплаем на сообщение ниже — бот отправит ответ пользователю."
    )
    sent_to = 0
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(chat_id=admin_id, text=header, parse_mode="HTML")
            copied = await context.bot.copy_message(
                chat_id=admin_id,
                from_chat_id=chat.id,
                message_id=message.message_id,
            )
            remember_admin_message(admin_id, copied.message_id, chat.id)
            sent_to += 1
        except Exception as exc:
            log.exception("Failed to forward support message to admin %s: %s", admin_id, exc)

    if sent_to:
        await message.reply_text("Сообщение отправлено администратору. Ответ придёт сюда в этот чат.")
    else:
        await message.reply_text("Не удалось передать сообщение администратору. Попробуйте ещё раз позже.")


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callbacks))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, support_message))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
