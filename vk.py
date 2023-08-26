import os
import random

import vk_api as vk
from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

from util import get_questions_and_answers, get_redis_connect, clean_answer


keyboard = VkKeyboard(one_time=True)
keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
keyboard.add_line()
keyboard.add_button('Мой счёт', color=VkKeyboardColor.PRIMARY)


def start(vk_api, event):
    vk_api.messages.send(
        user_id=event.user_id,
        message='Привет! Я бот для викторин!',
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard(),
    )


def handle_new_question_request(
    event, vk_api, questions_and_answers, redis_connect, question_asked
):
    question_asked.append(True)
    random_question = random.choice(list(questions_and_answers.keys()))
    redis_connect.set(event.user_id, random_question)
    vk_api.messages.send(
        user_id=event.user_id,
        message=random_question,
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard(),
    )


def handle_solution_attempt(
    event, vk_api, questions_and_answers, redis_connect
):
    question = redis_connect.get(event.user_id)
    answer = clean_answer(questions_and_answers[question])
    user_answer = event.text
    if answer.lower() == user_answer.lower():
        vk_api.messages.send(
            user_id=event.user_id,
            message='Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»',
            random_id=random.randint(1, 1000),
            keyboard=keyboard.get_keyboard(),
        )
    else:
        vk_api.messages.send(
            user_id=event.user_id,
            message='Неправильно… Попробуешь ещё раз?',
            random_id=random.randint(1, 1000),
            keyboard=keyboard.get_keyboard(),
        )


def main():
    load_dotenv()

    questions_and_answers = get_questions_and_answers()
    redis_connect = get_redis_connect()

    vk_token = os.getenv('VK_TOKEN')
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    question_asked = []
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == 'Новый вопрос':
                handle_new_question_request(
                    event,
                    vk_api,
                    questions_and_answers,
                    redis_connect,
                    question_asked,
                )
            elif event.text == 'Сдаться':
                pass
            elif not question_asked:
                start(vk_api, event)
            else:
                handle_solution_attempt(
                    event, vk_api, questions_and_answers, redis_connect
                )


if __name__ == '__main__':
    main()
