from pydantic import BaseModel


class Category(BaseModel):
    id: int
    name: str
    url: str
    page_cnt: int

    def __repr__(self) -> str:
        return f"{self.id} || {self.page_cnt} || {self.url}"
