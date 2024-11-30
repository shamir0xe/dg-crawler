from pydantic import BaseModel


class Category(BaseModel):
    id: int
    name: str
    page_cnt: int
    fa_name: str
    url: str

    def __repr__(self) -> str:
        return f"{self.id} || {self.page_cnt} || {self.name}"
