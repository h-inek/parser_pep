from pathlib import Path

BASE_DIR = Path(__file__).parent
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
MAIN_DOC_URL = 'https://docs.python.org/3/'
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'
PEP_URL = 'https://peps.python.org/'

PRETTY_OUTPUT = 'pretty'
FILE_OUTPUT = 'file'
DEFAULT_OUTPUT = None

DIRS_DOWNLOADS = 'downloads'
DIRS_LOGS = 'logs'
DIRS_RESULTS = 'results'

EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
