from src.factories.image_filter_factory import ImageFilterFactory
from src.actions.get_driver import GetDriver


class Initialize:
    def __init__(self) -> None:
        GetDriver()
        ImageFilterFactory().create()
