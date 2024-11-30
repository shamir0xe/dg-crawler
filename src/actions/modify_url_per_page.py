class ModifyUrlPerPage:
    @staticmethod
    def modify(category_id: int, page: int, sort_number: int) -> str:
        url = f"https://sirius.digikala.com/v1/category/{category_id}/"
        url += f"?page={page}"
        url += f"&sort={sort_number}"
        return url
