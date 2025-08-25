from pydantic import BaseModel


class SchemaBase(BaseModel):
    class Config:
        from_attributes = True


class PaginationResponse(BaseModel):
    current_page: int
    page_size: int
    total_pages: int
    total_items: int
    results: list
