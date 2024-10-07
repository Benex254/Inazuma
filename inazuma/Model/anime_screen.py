from fastanime.anilist import AniList
from fastanime.AnimeProvider import AnimeProvider
from fastanime.libs.anilist.types import AnilistBaseMediaDataSchema
from fastanime.Utility.utils import anime_title_percentage_match
from kivy.cache import Cache
from kivy.logger import Logger

from .base_model import BaseScreenModel

Cache.register("streams.anime", limit=10)

anime_provider = AnimeProvider("allanime", "true")


class AnimeScreenModel(BaseScreenModel):
    """the Anime screen model"""

    data = {}
    anime_id = 0
    current_anime_data = None
    current_anilist_anime_id = "0"
    current_provider_anime_id = "0"
    current_title = ""
    anilist_data: "AnilistBaseMediaDataSchema | None" = None

    def get_anime_data_from_provider(
        self, anilist_data: "AnilistBaseMediaDataSchema", is_dub, id=None
    ):
        try:
            if (self.anilist_data or {"id": -1})["id"] == anilist_data[
                "id"
            ] and self.current_anime_data:
                return self.current_anime_data
            translation_type = "dub" if is_dub else "sub"
            search_results = anime_provider.search_for_anime(
                anilist_data["title"]["romaji"] or anilist_data["title"]["english"],
                translation_type,
            )

            if search_results:
                _search_results = search_results["results"]
                result = max(
                    _search_results,
                    key=lambda x: anime_title_percentage_match(
                        x["title"], anilist_data
                    ),
                )
                self.current_anilist_anime_id = anilist_data["id"]
                self.current_provider_anime_id = result["id"]
                self.current_anime_data = anime_provider.get_anime(result["id"])
                if self.current_anime_data:
                    Logger.debug(f"Got data of {self.current_anime_data['title']}")
                return self.current_anime_data
            return {}
        except Exception as e:
            Logger.info("anime_screen error: %s" % e)
            return {}

    def get_episode_streams(self, episode, is_dub):
        translation_type = "dub" if is_dub else "sub"

        try:
            if self.current_anime_data:
                streams = anime_provider.get_episode_streams(
                    self.current_provider_anime_id, episode, translation_type
                )
                if not streams:
                    return []
                return [episode_stream for episode_stream in streams]

            return []
        except Exception as e:
            Logger.error("anime_screen error: %s" % e)
            return []

        # should return {type:{provider:streamlink}}

    def get_anime_data(self, id: int):
        return AniList.get_anime(id)


__all__ = ["AnimeScreenModel"]
