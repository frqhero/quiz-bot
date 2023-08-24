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
)
import redis

from read_question import get_questions_and_answers


def start(update: Update, context: CallbackContext) -> None:
    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счёт']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Привет! Я бот для викторин!',
        reply_markup=reply_markup,
    )


def echo(update: Update, context: CallbackContext) -> None:
    if update.message.text == 'Новый вопрос':
        questions_and_answers = context.bot.questions_and_answers
        random_question = random.choice(list(questions_and_answers.keys()))
        context.bot.redis_connect.set(update.message.chat_id, random_question)
        update.message.reply_text(random_question)
    else:
        question = context.bot.redis_connect.get(update.message.chat_id)
        if not question:
            update.message.reply_text(update.message.text)
        original_answer = context.bot.questions_and_answers[question]
        answer = original_answer.replace('Ответ:\n', '')
        if '(' in answer:
            answer = re.sub(r'\([^)]*\)', '', answer)
        period = answer.find('.')
        if period != -1:
            answer = answer[:period].strip()
        answer = answer.replace('\n', ' ')
        answer = answer.replace('  ', ' ')
        user_answer = update.message.text
        if answer.lower() == user_answer.lower():
            update.message.reply_text(
                'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
            )
        else:
            update.message.reply_text('Неправильно… Попробуешь ещё раз?')


def main():
    load_dotenv()

    telegram_token = os.getenv('TELEGRAM_TOKEN')
    redis_password = os.getenv('REDIS_PASSWORD')

    updater = Updater(telegram_token)
    bot = updater.bot
    bot.questions_and_answers = get_questions_and_answers()
    bot.redis_connect = redis.Redis(
        host='redis-14788.c264.ap-south-1-1.ec2.cloud.redislabs.com',
        port=14788,
        password=redis_password,
        decode_responses=True,
    )

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, echo)
    )

    updater.start_polling()
    updater.idle()
    1


if __name__ == '__main__':
    main()
