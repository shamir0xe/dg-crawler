class ModifyUrlPerPage:
    @staticmethod
    def modify(url: str, page: int) -> str:
        while url[-1] == "/":
            url = url[:-1]
        return url + f"/?page={page}"
