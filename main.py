# import json
# import os
# from datetime import datetime, time, timedelta
# from pathlib import Path
# from zoneinfo import ZoneInfo
# from dotenv import load_dotenv
# from telegram import Update, ReplyKeyboardMarkup
# from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters
#
# load_dotenv()
#
# BOT_TOKEN = os.environ["BOT_TOKEN"]
# CHAT_ID = os.environ["CHAT_ID"]
# TIMEZONE = ZoneInfo("Europe/Kyiv")
# IDS_FILE = Path("message_ids.json")
# CONFIG_FILE = Path("config.json")
#
# ranezol_cina_sent = False
#
# # Tracks current phase in the daily medication flow.
# # phase_timestamp is when the current timed phase started (for run_once delays).
# current_phase = "INIT"
# phase_timestamp: datetime | None = None
#
#
# def load_config() -> dict:
#     return json.loads(CONFIG_FILE.read_text())
#
#
# def get_germiflora_time() -> time:
#     t = load_config()["germiflora_time"]
#     hour, minute = map(int, t.split(":"))
#     return time(hour, minute, tzinfo=TIMEZONE)
#
#
# def get_germiflora_pranz_time() -> time:
#     t = load_config()["germiflora_pranz_time"]
#     hour, minute = map(int, t.split(":"))
#     return time(hour, minute, tzinfo=TIMEZONE)
#
#
# def load_ids() -> list[int]:
#     if IDS_FILE.exists():
#         return json.loads(IDS_FILE.read_text())
#     return []
#
#
# def save_ids(ids: list[int]) -> None:
#     IDS_FILE.write_text(json.dumps(ids))
#
#
# def save_config(config: dict) -> None:
#     CONFIG_FILE.write_text(json.dumps(config, indent=4))
#
#
# def format_duration(delta: timedelta) -> str:
#     total = int(delta.total_seconds())
#     if total <= 0:
#         return "mai putin de 1 minut"
#     hours, remainder = divmod(total, 3600)
#     minutes = remainder // 60
#     parts = []
#     if hours:
#         parts.append(f"{hours}h")
#     if minutes:
#         parts.append(f"{minutes}min")
#     return " ".join(parts) if parts else "mai putin de 1 minut"
#
#
# def _keyboard(*rows: str) -> ReplyKeyboardMarkup:
#     """Build a keyboard where each arg is a main button row, plus a permanent Timp ramas row."""
#     buttons = [[btn] for btn in rows] + [["Timp ramas"]]
#     return ReplyKeyboardMarkup(buttons, resize_keyboard=True)
#
#
# async def send_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
#     await context.bot.send_message(chat_id=CHAT_ID, text=context.job.data)
#
# async def good_morning(context: ContextTypes.DEFAULT_TYPE) -> None:
#     await context.bot.send_message(chat_id=CHAT_ID, text="Buna dimineata! 🌅")
#
# async def start(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
#     ids = load_ids()
#     ids.append(update.message.message_id)
#     msg = await update.message.reply_text("Let's go", reply_markup=_keyboard("Am mancat micul dejun"))
#     ids.append(msg.message_id)
#     save_ids(ids)
#
# async def ospanox_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
#     msg = await context.bot.send_message(chat_id=CHAT_ID, text="Bea ospanox 1 pastila la masa 💊", reply_markup=_keyboard("Am mancat pranzul"))
#     ids = load_ids()
#     ids.append(msg.message_id)
#     save_ids(ids)
#
# async def ranezol_ulcavis_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
#     global current_phase, phase_timestamp
#     current_phase = "AFTER_RANEZOL_AM"
#     phase_timestamp = datetime.now(tz=TIMEZONE)
#     msg = await context.bot.send_message(chat_id=CHAT_ID, text="Ranezol 1 pastila si Ulcavis 2 pastile 💊")
#     ids = load_ids()
#     ids.append(msg.message_id)
#     save_ids(ids)
#     context.job_queue.run_once(ospanox_reminder, when=1800)
#
# async def germiflora_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
#     global current_phase, phase_timestamp
#     current_phase = "AFTER_GERMIFLORA_AM"
#     phase_timestamp = datetime.now(tz=TIMEZONE)
#     msg = await context.bot.send_message(chat_id=CHAT_ID, text="Bea 1 pastila GermiFlora 💊")
#     ids = load_ids()
#     ids.append(msg.message_id)
#     save_ids(ids)
#     context.job_queue.run_once(ranezol_ulcavis_reminder, when=7200)
#
# async def am_mancat(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
#     global current_phase
#     current_phase = "AFTER_BREAKFAST"
#     ids = load_ids()
#     ids.append(update.message.message_id)
#     msg = await update.message.reply_text("Bea 1 pastila de Metrozol 💊", reply_markup=_keyboard("Am mancat pranzul"))
#     ids.append(msg.message_id)
#     save_ids(ids)
#
# async def am_mancat_cina_handler(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
#     if not ranezol_cina_sent:
#         return
#     ids = load_ids()
#     ids.append(update.message.message_id)
#     msg = await update.message.reply_text("Bea 1 pastila de Metrozol 💊")
#     ids.append(msg.message_id)
#     msg2 = await update.message.reply_text("Gata pe azi! 🎉")
#     ids.append(msg2.message_id)
#     save_ids(ids)
#
# async def ospanox_cina_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
#     msg = await context.bot.send_message(chat_id=CHAT_ID, text="Bea ospanox 1 pastila la masa 💊", reply_markup=_keyboard("Am mancat cina"))
#     ids = load_ids()
#     ids.append(msg.message_id)
#     save_ids(ids)
#
# async def ranezol_cina_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
#     global ranezol_cina_sent, current_phase, phase_timestamp
#     ranezol_cina_sent = True
#     current_phase = "AFTER_RANEZOL_PM"
#     phase_timestamp = datetime.now(tz=TIMEZONE)
#     msg = await context.bot.send_message(chat_id=CHAT_ID, text="Ranezol 1 pastila si Ulcavis 2 pastile 30 minute inainte de cina 💊")
#     ids = load_ids()
#     ids.append(msg.message_id)
#     save_ids(ids)
#     context.job_queue.run_once(ospanox_cina_reminder, when=1800)
#
# async def germiflora_pranz_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
#     global current_phase, phase_timestamp
#     current_phase = "AFTER_GERMIFLORA_PM"
#     phase_timestamp = datetime.now(tz=TIMEZONE)
#     msg = await context.bot.send_message(chat_id=CHAT_ID, text="Bea GermiFlora 1 pastila 💊")
#     ids = load_ids()
#     ids.append(msg.message_id)
#     save_ids(ids)
#     context.job_queue.run_once(ranezol_cina_reminder, when=7200)
#
# async def am_mancat_pranzul(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
#     global current_phase
#     current_phase = "AFTER_PRANZ"
#     ids = load_ids()
#     ids.append(update.message.message_id)
#     msg = await update.message.reply_text("Bea Metrozol 1 pastila 💊")
#     ids.append(msg.message_id)
#     save_ids(ids)
#
# async def timp_ramas(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
#     now = datetime.now(tz=TIMEZONE)
#
#     if current_phase == "AFTER_BREAKFAST":
#         gt = get_germiflora_time()
#         next_dt = now.replace(hour=gt.hour, minute=gt.minute, second=0, microsecond=0)
#         if next_dt <= now:
#             next_dt += timedelta(days=1)
#         text = f"GermiFlora in {format_duration(next_dt - now)}"
#
#     elif current_phase == "AFTER_GERMIFLORA_AM":
#         next_dt = phase_timestamp + timedelta(hours=2)
#         text = f"Ranezol + Ulcavis in {format_duration(next_dt - now)}"
#
#     elif current_phase == "AFTER_RANEZOL_AM":
#         next_dt = phase_timestamp + timedelta(minutes=30)
#         text = f"Ospanox (pranz) in {format_duration(next_dt - now)}"
#
#     elif current_phase == "AFTER_PRANZ":
#         gpt = get_germiflora_pranz_time()
#         next_dt = now.replace(hour=gpt.hour, minute=gpt.minute, second=0, microsecond=0)
#         if next_dt <= now:
#             next_dt += timedelta(days=1)
#         text = f"GermiFlora (pranz) in {format_duration(next_dt - now)}"
#
#     elif current_phase == "AFTER_GERMIFLORA_PM":
#         next_dt = phase_timestamp + timedelta(hours=2)
#         text = f"Ranezol + Ulcavis (cina) in {format_duration(next_dt - now)}"
#
#     elif current_phase == "AFTER_RANEZOL_PM":
#         next_dt = phase_timestamp + timedelta(minutes=30)
#         text = f"Ospanox (cina) in {format_duration(next_dt - now)}"
#
#     else:
#         text = "Nu exista un medicament urmator programat."
#
#     await update.message.reply_text(text)
#
# async def set_germiflora(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     if not context.args:
#         await update.message.reply_text("Foloseste: /setgermiflora HH:MM")
#         return
#     t_str = context.args[0]
#     try:
#         hour, minute = map(int, t_str.split(":"))
#         time(hour, minute)
#     except (ValueError, TypeError):
#         await update.message.reply_text("Format invalid. Exemplu: /setgermiflora 10:30")
#         return
#     config = load_config()
#     config["germiflora_time"] = t_str
#     save_config(config)
#     for job in context.job_queue.get_jobs_by_name("germiflora_reminder"):
#         job.schedule_removal()
#     context.job_queue.run_daily(germiflora_reminder, time=time(hour, minute, tzinfo=TIMEZONE), name="germiflora_reminder")
#     await update.message.reply_text(f"GermiFlora (dimineata) setat la {t_str} ✅")
#
#
# async def set_germiflora_pranz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     if not context.args:
#         await update.message.reply_text("Foloseste: /setgermiflora_pranz HH:MM")
#         return
#     t_str = context.args[0]
#     try:
#         hour, minute = map(int, t_str.split(":"))
#         time(hour, minute)
#     except (ValueError, TypeError):
#         await update.message.reply_text("Format invalid. Exemplu: /setgermiflora_pranz 16:00")
#         return
#     config = load_config()
#     config["germiflora_pranz_time"] = t_str
#     save_config(config)
#     for job in context.job_queue.get_jobs_by_name("germiflora_pranz_reminder"):
#         job.schedule_removal()
#     context.job_queue.run_daily(germiflora_pranz_reminder, time=time(hour, minute, tzinfo=TIMEZONE), name="germiflora_pranz_reminder")
#     await update.message.reply_text(f"GermiFlora (pranz) setat la {t_str} ✅")
#
#
# async def clear_and_restart(context: ContextTypes.DEFAULT_TYPE) -> None:
#     global ranezol_cina_sent, current_phase, phase_timestamp
#     ranezol_cina_sent = False
#     current_phase = "INIT"
#     phase_timestamp = None
#     ids = load_ids()
#     for msg_id in ids:
#         try:
#             await context.bot.delete_message(chat_id=CHAT_ID, message_id=msg_id)
#         except Exception:
#             pass
#     save_ids([])
#     msg = await context.bot.send_message(chat_id=CHAT_ID, text="O zi noua", reply_markup=_keyboard("Am mancat micul dejun"))
#     save_ids([msg.message_id])
#
#
# def main() -> None:
#     app = Application.builder().token(BOT_TOKEN).build()
#
#     app.add_handler(CommandHandler("start", start))
#     app.add_handler(CommandHandler("setgermiflora", set_germiflora))
#     app.add_handler(CommandHandler("setgermiflora_pranz", set_germiflora_pranz))
#     app.add_handler(MessageHandler(filters.Text(["Am mancat micul dejun"]), am_mancat))
#     app.add_handler(MessageHandler(filters.Text(["Am mancat pranzul"]), am_mancat_pranzul))
#     app.add_handler(MessageHandler(filters.Text(["Am mancat cina"]), am_mancat_cina_handler))
#     app.add_handler(MessageHandler(filters.Text(["Timp ramas"]), timp_ramas))
#
#     app.job_queue.run_daily(clear_and_restart, time=time(6, 0, tzinfo=TIMEZONE))
#     app.job_queue.run_daily(good_morning, time=time(6, 30, tzinfo=TIMEZONE))
#     app.job_queue.run_daily(germiflora_reminder, time=get_germiflora_time(), name="germiflora_reminder")
#     app.job_queue.run_daily(germiflora_pranz_reminder, time=get_germiflora_pranz_time(), name="germiflora_pranz_reminder")
#
#     app.run_polling(drop_pending_updates=True)
#
#
# if __name__ == "__main__":
#     main()
