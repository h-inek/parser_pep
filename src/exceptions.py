class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""
    pass


class ResponseErrorException(Exception):
    """Вызывается при ошибке обработки session."""
    def __init__(self, message, url):
        self.message = message
        self.url = url
        super().__init__(self.message)


class BeautifulSoupException(Exception):
    """Вызывается при ошибки создания BeautifulSoup."""
    pass
