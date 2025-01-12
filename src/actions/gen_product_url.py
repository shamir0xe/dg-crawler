class GenProductUrl:
    @staticmethod
    def gen(id: int) -> str:
        return f"https://sirius.digikala.com/v1/product/{id}/"
