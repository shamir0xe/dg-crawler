class ModifyUrlPerPage:
    @staticmethod
    def modify(url: str, page: int) -> str:
        while url[-1] == "/":
            url = url[:-1]
        i = len(url) - 1
        while i >= 0 and url[i] != "/" and url[i] != "?":
            i -= 1
        if i >= 0 and url[i] == "?":
            url += f"&page={page}"
        else:
            url += f"/?page={page}"
        return url
