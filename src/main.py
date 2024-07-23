import requests_cache
import re
import logging
import csv
from collections import defaultdict

from urllib.parse import urljoin
from tqdm import tqdm

from constants import (
    BASE_DIR, MAIN_DOC_URL, PEP_URL, EXPECTED_STATUS, DIRS_DOWNLOADS,
    DIRS_RESULTS
)
from configs import configure_argument_parser, configure_logging
from outputs import control_output
from utils import find_tag, get_soup
from exceptions import (
    ParserFindTagException, BeautifulSoupException, ResponseErrorException
)


def whats_new(session):
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')

    soup = get_soup(session, whats_new_url)

    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})

    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})

    sections_by_python = div_with_ul.find_all(
        'li',
        attrs={'class': 'toctree-l1'}
    )

    for section in tqdm(sections_by_python):
        version_a_tag = section.find('a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)

        soup = get_soup(session, version_link)

        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append((version_link, h1.text, dl_text))

    return results


def latest_versions(session):
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    pattern = r'(?P<version>\d\.\d+) \((?P<status>.*)\)'

    soup = get_soup(session, MAIN_DOC_URL)

    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise ParserFindTagException('Ничего не нашлось')

    for a_tag in a_tags:
        try:
            text_match = re.search(pattern, a_tag.text)
            version, status = text_match.groups()
        except AttributeError:
            version, status = a_tag, ''

        link = a_tag['href']
        results.append((link, version, status))

    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')

    soup = get_soup(session, downloads_url)

    table = find_tag(soup, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(table, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')})
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]

    downloads_dir = BASE_DIR / DIRS_DOWNLOADS
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    response = session.get(archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)

    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    count_status = defaultdict(int)

    soup = get_soup(session, PEP_URL)

    links = soup.find('section', attrs={'id': 'numerical-index'})
    pep_links = [
        a['href'] for a in links.find_all(
            'a',
            href=True,
            attrs={'class': 'pep reference internal'}
        ) if a.text.isdigit()
    ]
    status_in_main = [a.text[1:] for a in links.find_all('abbr')]

    downloads_dir = BASE_DIR / DIRS_RESULTS
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / 'pep_status_counts.csv'

    for index, link in enumerate(pep_links):
        pep_url = urljoin(PEP_URL, link)

        pep_soup = get_soup(session, pep_url)

        status_tag = pep_soup.find(
            string='Status'
        ).find_parent().find_next_sibling().text

        if status_tag not in EXPECTED_STATUS[status_in_main[index]]:
            logging.info(
                f'\nНесовпадающий статус: {pep_url}\n'
                f'Статус в карточке: {status_tag}\n'
                f'Ожидаемый статус: {EXPECTED_STATUS[status_in_main[index]]}'
            )

        count_status[status_tag] += 1

        count_status['Total'] += 1

    with open(archive_path, 'w', newline='') as csvfile:
        fieldnames = ['Status', 'Quantity']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for status, count in count_status.items():
            writer.writerow({'Status': status, 'Quantity': count})


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()

    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode

    try:
        results = MODE_TO_FUNCTION[parser_mode](session)
        control_output(results, args)
    except (
            ValueError, AttributeError, BeautifulSoupException,
            ResponseErrorException
    ) as error:
        logging.error(
            f'Получена ошибка при выполнении: {error}', stack_info=True
        )

    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
