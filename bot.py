import logging
import os
from functools import wraps

import requests
from telegram import Bot, Update, ParseMode
from telegram.ext import CallbackContext, Updater, CommandHandler, MessageHandler, Filters

import db
from utils import str_to_num, get_exchange_rates, ExchApiNotResponding


logging.basicConfig(
        level=logging.INFO, 
        format="%(asctime)s - [%(levelname)-5.5s] - %(message)s",
        handlers=[
            logging.FileHandler(".log"),
            logging.StreamHandler(),
        ]
)
logger = logging.getLogger(__name__)


def error_callback(update: Update, context: CallbackContext) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="Error, you probably sent wrong number or something"
    )


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Бухгалтер, милый твой бухгалтер..")


def help(update: Update, context: CallbackContext) -> None:
    msg = """
`/add {number}` \- to add expense in the size of `{number}`,
`/days` \- to get expenses by days,
`/total` \- to get total expenses\,
`/total_rub` \- to get total expenses in both currencies\.
    """
    update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN_V2)


def add_expense(update: Update, context: CallbackContext) -> None:
    logger.info(f"add_expense command, args={context.args}")
    arg = context.args[0]
    chat_id = update.message.chat_id
    try:
        amount = str_to_num(arg)
    except ValueError:
        return
    db.insert(str(amount))
    if amount >= 0:
        msg = f"Added {amount}"
    else:
        msg = f"Subtracted {-amount}"
    update.message.reply_text(msg)


def get_expenses_by_days(update: Update, context: CallbackContext) -> None:
    logger.info(f"get_expenses_by_days command")
    result = db.get_sum_by_days()
    min_date, max_date = db.get_date_range()
    try:
        rates = get_exchange_rates(start_date=min_date, end_date=max_date)
    except ExchApiNotResponding:
        msg = ""
        for date, amount in result.items():
            msg += f"{date}: {amount}\n"
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
        return
    msg = ""
    for date, amount in result.items():
        rate = rates.get(date)
        msg += f"{date}: {amount:7.2f} TRY, {(amount * rate):7.2f} RUB\n"
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


def get_total(update: Update, context: CallbackContext) -> None:
    logger.info(f"get_total command")
    amount = db.get_all_sum()
    msg = f"TOTAL: {amount}"
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


def get_total_rub(update: Update, context: CallbackContext) -> None:
    logger.info(f"get_total_rub command")
    result = db.get_sum_by_days()
    min_date, max_date = db.get_date_range()
    try:
        rates = get_exchange_rates(start_date=min_date, end_date=max_date)
    except ExchApiNotResponding:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="api.exchangeratesapi.io not responding"
        )
        return
    amount_tr = 0
    amount_rub = 0
    for date, amount in result.items():
        rate = rates.get(date)
        amount_tr += amount
        amount_rub += (amount * rate)
    msg = f"TOTAL: {amount_tr:.2f} TRY, {amount_rub:.2f} RUB"
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


def main() -> None:
    token = os.environ.get("TG_TOKEN")
    updater = Updater(token)
    
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("add", add_expense, pass_args=True))
    dispatcher.add_handler(CommandHandler("days", get_expenses_by_days))
    dispatcher.add_handler(CommandHandler("total", get_total))
    dispatcher.add_handler(CommandHandler("total_rub", get_total_rub))
    dispatcher.add_error_handler(error_callback)

    updater.start_polling()
    logger.info("started bot")
    updater.idle()


if __name__ == "__main__":
    if not db.exists():
        db.init()
    main()

