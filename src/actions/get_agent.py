from fake_useragent import UserAgent


class GetAgent:
    @staticmethod
    def get() -> str:
        return UserAgent().random
