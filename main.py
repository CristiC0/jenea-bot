import json
from datetime import time
from pathlib import Path
from zoneinfo import ZoneInfo
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters

BOT_TOKEN = "8638651292:AAFQKaRHgDunijziT7_EXxmrwQXfrCJk1yM"
CHAT_ID = "1120695231"
TIMEZONE = ZoneInfo("Europe/Kyiv")
IDS_FILE = Path("message_ids.json")
CONFIG_FILE = Path("config.json")


def load_config() -> dict:
    return json.loads(CONFIG_FILE.read_text())


def get_germiflora_time() -> time:
    t = load_config()["germiflora_time"]
    hour, minute = map(int, t.split(":"))
    return time(hour, minute, tzinfo=TIMEZONE)


def get_germiflora_pranz_time() -> time:
    t = load_config()["germiflora_pranz_time"]
    hour, minute = map(int, t.split(":"))
    return time(hour, minute, tzinfo=TIMEZONE)


def load_ids() -> list[int]:
    if IDS_FILE.exists():
        return json.loads(IDS_FILE.read_text())
    return []


def save_ids(ids: list[int]) -> None:
    IDS_FILE.write_text(json.dumps(ids))


async def send_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=CHAT_ID, text=context.job.data)

async def start(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    ids = load_ids()
    ids.append(update.message.message_id)
    keyboard = ReplyKeyboardMarkup([["Am mancat micul dejun"]], resize_keyboard=True)
    msg = await update.message.reply_text("Let's go", reply_markup=keyboard)
    ids.append(msg.message_id)
    save_ids(ids)

async def ospanox_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = ReplyKeyboardMarkup([["Am mancat pranzul"]], resize_keyboard=True)
    msg = await context.bot.send_message(chat_id=CHAT_ID, text="Bea ospanox 1 pastila la masa 💊", reply_markup=keyboard)
    ids = load_ids()
    ids.append(msg.message_id)
    save_ids(ids)

async def ranezol_ulcavis_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = await context.bot.send_message(chat_id=CHAT_ID, text="Ranezol 1 pastila si Ulcavis 2 pastile 💊")
    ids = load_ids()
    ids.append(msg.message_id)
    save_ids(ids)
    context.job_queue.run_once(ospanox_reminder, when=1800)

async def germiflora_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = await context.bot.send_message(chat_id=CHAT_ID, text="Bea 1 pastila GermiFlora 💊")
    ids = load_ids()
    ids.append(msg.message_id)
    save_ids(ids)
    context.job_queue.run_once(ranezol_ulcavis_reminder, when=7200)

async def am_mancat(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    ids = load_ids()
    ids.append(update.message.message_id)
    keyboard = ReplyKeyboardMarkup([["Am mancat pranzul"]], resize_keyboard=True)
    msg = await update.message.reply_text("Bea 1 pastila de Metrozol 💊", reply_markup=keyboard)
    ids.append(msg.message_id)
    save_ids(ids)

async def am_mancat_cina_handler(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    ids = load_ids()
    ids.append(update.message.message_id)
    msg = await update.message.reply_text("Bea 1 pastila de Metrozol 💊")
    ids.append(msg.message_id)
    msg2 = await update.message.reply_text("Gata pe azi! 🎉")
    ids.append(msg2.message_id)
    save_ids(ids)

async def ospanox_cina_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = ReplyKeyboardMarkup([["Am mancat cina"]], resize_keyboard=True)
    msg = await context.bot.send_message(chat_id=CHAT_ID, text="Bea ospanox 1 pastila la masa 💊", reply_markup=keyboard)
    ids = load_ids()
    ids.append(msg.message_id)
    save_ids(ids)

async def ranezol_cina_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = await context.bot.send_message(chat_id=CHAT_ID, text="Ranezol 1 pastila si Ulcavis 2 pastile 30 minute inainte de cina 💊")
    ids = load_ids()
    ids.append(msg.message_id)
    save_ids(ids)
    context.job_queue.run_once(ospanox_cina_reminder, when=1800)

async def germiflora_pranz_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = await context.bot.send_message(chat_id=CHAT_ID, text="Bea GermiFlora 1 pastila 💊")
    ids = load_ids()
    ids.append(msg.message_id)
    save_ids(ids)
    context.job_queue.run_once(ranezol_cina_reminder, when=7200)

async def am_mancat_pranzul(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    ids = load_ids()
    ids.append(update.message.message_id)
    msg = await update.message.reply_text("Bea Metrozol 1 pastila 💊")
    ids.append(msg.message_id)
    save_ids(ids)

async def clear_and_restart(context: ContextTypes.DEFAULT_TYPE) -> None:
    ids = load_ids()
    for msg_id in ids:
        try:
            await context.bot.delete_message(chat_id=CHAT_ID, message_id=msg_id)
        except Exception:
            pass
    save_ids([])
    keyboard = ReplyKeyboardMarkup([["Am mancat micul dejun"]], resize_keyboard=True)
    msg = await context.bot.send_message(chat_id=CHAT_ID, text="O zi noua", reply_markup=keyboard)
    save_ids([msg.message_id])


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Text(["Am mancat micul dejun"]), am_mancat))
    app.add_handler(MessageHandler(filters.Text(["Am mancat pranzul"]), am_mancat_pranzul))
    app.add_handler(MessageHandler(filters.Text(["Am mancat cina"]), am_mancat_cina_handler))

    app.job_queue.run_daily(clear_and_restart, time=time(6, 0, tzinfo=TIMEZONE))
    app.job_queue.run_daily(germiflora_reminder, time=get_germiflora_time())
    app.job_queue.run_daily(germiflora_pranz_reminder, time=get_germiflora_pranz_time())

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
