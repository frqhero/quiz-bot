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
