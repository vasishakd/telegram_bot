import dataclasses

from pydantic import BaseModel, model_validator

from clients.base import JsonBaseClient
from config import Config


class SeriesBase(BaseModel):
    title: str
    series_id: int
    url: str
    year: str
    image_url: str | None

    @model_validator(mode='before')
    @classmethod
    def handle_image_url(cls, data: dict) -> dict:
        data['image_url'] = data['image']['url']['original']

        return data


class Series(SeriesBase):
    latest_chapter: int
    completed: bool


class SearchSeriesItem(BaseModel):
    record: SeriesBase


class SearchSeriesResponse(BaseModel):
    results: list[SearchSeriesItem]


@dataclasses.dataclass
class MangaUpdatesClient(JsonBaseClient):
    base_url: str = Config.MANGA_UPDATES_URL

    async def get_series(self, series_id: str) -> Series:
        return Series(**await self.get(f'/v1/series/{series_id}'))

    async def search_series(self, search_text: str) -> SearchSeriesResponse:
        return SearchSeriesResponse(**await self.post(f'/v1/series/search', json={'search': search_text}))
