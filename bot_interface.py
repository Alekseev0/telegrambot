import os
from telegram.ext import Updater, CommandHandler
from constants import TOKEN
from operations_with_currency import make_currency_list, exchange_currency, currency_graph_builder
import re


def all_commands(update, context):
    """Start command shows all available commands"""
    context.bot.send_message(chat_id=update.effective_chat.id, text="Commands\n"
                                                                    "/list - list of currencies and exchange rates\n"
                                                                    "/lst - same as /list\n"
                                                                    "\n"
                                                                    "/exchange - exchange USD to another currency\n"
                                                                    "example: $(amount) to (currency);\n"
                                                                    "(amount) USD to (currency);\n"
                                                                    "$10 to CAD;\n"
                                                                    "10 USD to CAD\n"
                                                                    "\n"
                                                                    "/history - exchange rate history of two currencies\n"
                                                                    "example: USD/(currency) for 7 days;\n"
                                                                    "USD/CAD for 7 days\n")


def currency_list(update, context):
    """List of all currencies"""
    context.bot.send_message(chat_id=update.effective_chat.id, text='Currency rates\n' + make_currency_list())


def exchange(update, context):
    """Exchange one currency to another"""
    message = update.message['text'].replace('/exchange ', '')

    symbol_pattern = re.compile('[$][0-9]+\s[t][o]\s[A-Z]{3}')  # Pattern to search: $10 to EUR
    first_result = symbol_pattern.findall(message)
    usd_pattern = re.compile('[0-9]+\sUSD\s[t][o]\s[A-Z]{3}')   # Pattern to search: 10 USD to EUR
    second_result = usd_pattern.findall(message)

    results = (first_result + second_result)
    if not results or message != results[0]:
        context.bot.send_message(chat_id=update.effective_chat.id, text='The entered data is wrong. Try again')
    else:
        results = results[0]
        currency = ''.join(re.sub('[a-z0-9$]', '', results).split())
        amount = ''.join(re.sub('[a-zA-Z$]', '', results))
        amount = int(amount)
        context.bot.send_message(chat_id=update.effective_chat.id, text=exchange_currency(currency, amount))


def history_rates(update, context):
    message = update.message['text'].replace('/history ', '')

    pattern = re.compile('[A-Z]{3}\/[A-Z]{3} for 7 days')   # Pattern to search: USD/CAD for 7 days
    result = pattern.match(message)
    if not result or message != result[0]:
        context.bot.send_message(chat_id=update.effective_chat.id, text='The entered data in wrong. Try again')
    else:
        result = result[0]
        currency = ''.join(re.sub('[a-z/0-9]', '', result).split())
        currency_graph_builder(currency, update.update_id)

        with open(f'{update.update_id}.png', 'rb') as image:
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=image)
        os.remove(f'{update.update_id}.png')


def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', all_commands))
    dispatcher.add_handler(CommandHandler(['list', 'lst'], currency_list))
    dispatcher.add_handler(CommandHandler('exchange', exchange))
    dispatcher.add_handler(CommandHandler('history', history_rates))

    updater.start_polling()

if __name__ == '__main__':
    main()
