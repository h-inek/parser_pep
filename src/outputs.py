import datetime as dt
import csv
import logging

from prettytable import PrettyTable

from constants import (
    BASE_DIR, DATETIME_FORMAT, DIRS_RESULTS, PRETTY_OUTPUT, DEFAULT_OUTPUT,
    FILE_OUTPUT
)


def default_output(results, *args, **kwargs):
    for row in results:
        print(*row)


def pretty_output(results, *args, **kwargs):
    table = PrettyTable()

    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])

    print(table)


def file_output(results, cli_args,  *args, **kwargs):
    results_dir = BASE_DIR / DIRS_RESULTS
    results_dir.mkdir(exist_ok=True)

    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f'{cli_args.mode}_{now_formatted}.csv'
    file_path = results_dir / file_name

    with open(file_path, 'w', encoding='utf-8') as file:
        writer = csv.writer(file, dialect='unix')
        writer.writerows(results)

    logging.info(f'Файл с результатами был сохранён: {file_path}')


OUTPUT_FUNCTIONS = {
    PRETTY_OUTPUT: pretty_output,
    FILE_OUTPUT: file_output,
    DEFAULT_OUTPUT: default_output,
}


def control_output(results, cli_args):
    OUTPUT_FUNCTIONS.get(cli_args.output)(results, cli_args)
