import argparse
import os
import random

import redis
import vk_api as vk
from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

from util import get_questions_and_answers, clean_answer


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
    event, vk_api, questions_and_answers, redis_connect
):
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


def give_up(event, vk_api, questions_and_answers, redis_connect) -> str:
    question = redis_connect.get(event.user_id)
    answer = clean_answer(questions_and_answers[question])
    vk_api.messages.send(
        user_id=event.user_id,
        message=answer,
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard(),
    )
    handle_new_question_request(event, vk_api, questions_and_answers, redis_connect)


def main():
    load_dotenv()

    questions_and_answers = get_questions_and_answers()
    redis_password = os.getenv('REDIS_PASSWORD')
    redis_connect = redis.Redis(
        host='redis-14788.c264.ap-south-1-1.ec2.cloud.redislabs.com',
        port=14788,
        password=redis_password,
        decode_responses=True,
    )

    vk_token = os.getenv('VK_TOKEN')
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == 'Новый вопрос':
                handle_new_question_request(
                    event,
                    vk_api,
                    questions_and_answers,
                    redis_connect,
                )
            elif event.text == 'Сдаться':
                give_up(event, vk_api, questions_and_answers, redis_connect)
            else:
                handle_solution_attempt(
                    event, vk_api, questions_and_answers, redis_connect
                )


if __name__ == '__main__':
    main()
