import os
import re


def get_questions_and_answers():
    project_directory = os.path.dirname(__file__)
    questions_path = 'quiz-questions/1vs1200.txt'
    full_path = os.path.join(project_directory, questions_path)
    with open(full_path, 'r', encoding='KOI8-R') as file:
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


def clean_answer(original_answer):
    answer = original_answer.replace('Ответ:\n', '')
    if '(' in answer:
        answer = re.sub(r'\([^)]*\)', '', answer)
    period_position = answer.find('.')
    if period_position != -1:
        answer = answer[:period_position].strip()
    answer = answer.replace('\n', ' ').replace('  ', ' ')
    return answer
