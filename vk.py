import os
import random

import vk_api as vk
from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

from util import get_questions_and_answers, get_redis_connect


def handle_new_question_request(questions_and_answers):
    random_question = random.choice(list(questions_and_answers.keys()))
    
    # questions_and_answers = context.bot.questions_and_answers
    # random_question = random.choice(list(questions_and_answers.keys()))
    # context.bot.redis_connect.set(update.message.chat_id, random_question)
    # update.message.reply_text(random_question)

    return 'ANSWERING_QUESTION'


def echo(event, vk_api):
    vk = vk_session.get_api()
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Белая кнопка', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('Зелёная кнопка', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()  # Переход на вторую строку
    keyboard.add_button('Красная кнопка', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Синяя кнопка', color=VkKeyboardColor.PRIMARY)

    vk_api.messages.send(
        user_id=event.user_id,
        message=event.text,
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard(),
    )


if __name__ == '__main__':
    load_dotenv()

    questions_and_answers = get_questions_and_answers()
    redis_connect = get_redis_connect()

    vk_token = os.getenv('VK_TOKEN')
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == 'Новый вопрос':
                handle_new_question_request(
                    questions_and_answers, redis_connect
                )
            if event.text == 'Сдаться':
                """"""
            echo(event, vk_api)
