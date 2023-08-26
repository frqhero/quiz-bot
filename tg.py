import os
import random
import re

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    ConversationHandler,
)
import redis

from util import get_questions_and_answers, get_redis_connect


def clean_answer(original_answer):
    answer = original_answer.replace('Ответ:\n', '')
    if '(' in answer:
        answer = re.sub(r'\([^)]*\)', '', answer)
    period_position = answer.find('.')
    if period_position != -1:
        answer = answer[:period_position].strip()
    answer = answer.replace('\n', ' ')
    answer = answer.replace('  ', ' ')
    return answer


def start(update: Update, context: CallbackContext) -> str:
    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счёт']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Привет! Я бот для викторин!',
        reply_markup=reply_markup,
    )
    return 'SELECTING_FEATURE'


def handle_new_question_request(
    update: Update, context: CallbackContext
) -> str:
    questions_and_answers = context.bot.questions_and_answers
    random_question = random.choice(list(questions_and_answers.keys()))
    context.bot.redis_connect.set(update.message.chat_id, random_question)
    update.message.reply_text(random_question)

    return 'ANSWERING_QUESTION'


def handle_solution_attempt(update: Update, context: CallbackContext) -> str:
    question = context.bot.redis_connect.get(update.message.chat_id)
    answer = clean_answer(context.bot.questions_and_answers[question])
    user_answer = update.message.text
    if answer.lower() == user_answer.lower():
        update.message.reply_text(
            'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
        )
        return 'SELECTING_FEATURE'
    else:
        update.message.reply_text('Неправильно… Попробуешь ещё раз?')


def give_up(update: Update, context: CallbackContext) -> str:
    question = context.bot.redis_connect.get(update.message.chat_id)
    answer = clean_answer(context.bot.questions_and_answers[question])
    update.message.reply_text(answer)
    handle_new_question_request(update, context)


def main():
    load_dotenv()

    telegram_token = os.getenv('TELEGRAM_TOKEN')

    updater = Updater(telegram_token)
    bot = updater.bot
    bot.questions_and_answers = get_questions_and_answers()
    bot.redis_connect = get_redis_connect()

    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            'SELECTING_FEATURE': [
                MessageHandler(
                    Filters.regex('^Новый вопрос$'),
                    handle_new_question_request,
                ),
            ],
            'ANSWERING_QUESTION': [
                MessageHandler(
                    Filters.regex('^Новый вопрос$'),
                    handle_new_question_request,
                ),
                MessageHandler(Filters.regex('^Сдаться$'), give_up),
                MessageHandler(
                    Filters.text & ~Filters.command, handle_solution_attempt
                )
            ],
        },
        fallbacks=[],
    )
    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
