class CatUrlBuilder:
    @staticmethod
    def build(cat_code: str) -> str:
        return f"https://api.digikala.com/v1/categories/{cat_code}/search/"
