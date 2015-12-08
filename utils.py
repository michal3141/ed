import re

def _sanitize_question(question):
    """
    :param question: question to be sanitized e.g. 'what is terrorism'
    :return: sanitized question e.g. 'what-is-terrorism'
    """
    return re.sub(r'(\W)\1+', r'\1', question.replace(' ', '-').replace('?', '').replace(',', '').replace('/', '-') \
        .replace("'", '').replace('.', '').replace(':', '').replace('(', '').replace(')', '') \
        .replace('"', ''))

def _sanitize_username(username):
    """
    :param username: username to be sanitized e.g. 'Austin Conlon'
    :return: sanitized username e.g. 'Austin-Conlon'
    """
    return re.sub(r'(\W)\1+', r'\1', username.replace(' ', '-').replace('.', ''))