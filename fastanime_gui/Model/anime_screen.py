from fastanime.anilist import AniList
from fastanime.AnimeProvider import AnimeProvider
from fastanime.Utility.data import anime_normalizer
from kivy.cache import Cache
from kivy.logger import Logger
from thefuzz import fuzz

from .base_model import BaseScreenModel


def anime_title_percentage_match(
    possible_user_requested_anime_title: str, title: tuple
) -> float:
    """Returns the percentage match between the possible title and user title

    Args:
        possible_user_requested_anime_title (str): an Animdl search result title
        title (str): the anime title the user wants

    Returns:
        int: the percentage match
    """
    if normalized_anime_title := anime_normalizer.get(
        possible_user_requested_anime_title
    ):
        possible_user_requested_anime_title = normalized_anime_title
    print(locals())
    # compares both the romaji and english names and gets highest Score
    percentage_ratio = max(
        fuzz.ratio(title[0].lower(), possible_user_requested_anime_title.lower()),
        fuzz.ratio(title[1].lower(), possible_user_requested_anime_title.lower()),
    )
    print(percentage_ratio)
    return percentage_ratio


Cache.register("streams.anime", limit=10)

anime_provider = AnimeProvider("allanime")


class AnimeScreenModel(BaseScreenModel):
    """the Anime screen model"""

    data = {}
    anime_id = 0
    current_anime_data = None
    current_anime_id = "0"
    current_title = ""

    def get_anime_data_from_provider(self, anime_title: tuple, is_dub, id=None):
        try:
            if self.current_title == anime_title and self.current_anime_data:
                return self.current_anime_data
            translation_type = "dub" if is_dub else "sub"
            search_results = anime_provider.search_for_anime(
                anime_title[0], translation_type
            )

            if search_results:
                _search_results = search_results["results"]
                result = max(
                    _search_results,
                    key=lambda x: anime_title_percentage_match(x["title"], anime_title),
                )
                self.current_anime_id = result["id"]
                self.current_anime_data = anime_provider.get_anime(result["id"])
                self.current_title = anime_title
                return self.current_anime_data
            return {}
        except Exception as e:
            Logger.info("anime_screen error: %s" % e)
            return {}

    def get_episode_streams(self, episode, is_dub):
        translation_type = "dub" if is_dub else "sub"

        try:
            if cached_episode := Cache.get(
                "streams.anime", f"{self.current_title}{episode}{is_dub}"
            ):
                return cached_episode
            if self.current_anime_data:
                streams = anime_provider.get_episode_streams(
                    self.current_anime_id, episode, translation_type
                )

            return []
        except Exception as e:
            Logger.info("anime_screen error: %s" % e)
            return []

        # should return {type:{provider:streamlink}}

    def get_anime_data(self, id: int):
        return AniList.get_anime(id)


__all__ = ["AnimeScreenModel"]
