import os
import re

import redis


def get_questions_and_answers():
    with open('quiz-questions/1vs1200.txt', 'r', encoding='KOI8-R') as file:
        file_content = file.read()
    file_content_split = file_content.split('\n\n')
    questions = []
    answers = []
    for paragraph in file_content_split:
        if 'Вопрос' in paragraph:
            questions.append(paragraph)
        elif 'Ответ' in paragraph:
            answers.append(paragraph)
    questions_answers = dict(zip(questions, answers))
    return questions_answers


def get_redis_connect():
    redis_password = os.getenv('REDIS_PASSWORD')
    redis_connect = redis.Redis(
        host='redis-14788.c264.ap-south-1-1.ec2.cloud.redislabs.com',
        port=14788,
        password=redis_password,
        decode_responses=True,
    )
    return redis_connect


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
