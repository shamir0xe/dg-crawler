from src.actions.download_dictionaries import DownloadDictionaries
from src.factories.image_filter_factory import ImageFilterFactory
from src.actions.get_driver import GetDriver


class Initialize:
    def __init__(self) -> None:
        DownloadDictionaries().dl()
        GetDriver()
        ImageFilterFactory().create()
