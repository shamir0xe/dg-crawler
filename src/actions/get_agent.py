from fake_useragent import UserAgent


class GetAgent:
    @staticmethod
    def get() -> str:
        return UserAgent(
            os=["ios"],
            browsers=["safari"],
            platforms=["mobile"],
            fallback=("AppleWebKit/537.36 (KHTML, like Gecko) "),
        ).random
