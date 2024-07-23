import logging

from bs4 import BeautifulSoup
from requests import RequestException
from exceptions import (
    ParserFindTagException, ResponseErrorException, BeautifulSoupException
)


def get_response(session, url, encoding='utf-8'):
    try:
        response = session.get(url)
        response.encoding = encoding

        return response

    except RequestException:
        raise ResponseErrorException(
            'Возникла ошибка при загрузке страницы',
            url
        )


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=attrs or {})
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg)
        raise ParserFindTagException(error_msg)

    return searched_tag


def get_soup(session, url):
    try:

        return BeautifulSoup(get_response(session, url).text, 'lxml')

    except ValueError:
        raise BeautifulSoupException('Не получилось собрать данные')
