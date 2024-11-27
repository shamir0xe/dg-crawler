class ModifyUrlPerPage:
    @staticmethod
    def modify(url: str, page: int, sort_number: int) -> str:
        while url[-1] != "/":
            url += "/"
        url += f"?page={page}"
        url += f"&sort={sort_number}"
        return url
