from typing import TYPE_CHECKING

from kivy.cache import Cache
from kivy.logger import Logger

from ..Model.anime_screen import AnimeScreenModel
from ..View.AnimeScreen.anime_screen import AnimeScreenView

if TYPE_CHECKING:
    from fastanime.libs.anilist.types import AnilistBaseMediaDataSchema

Cache.register("data.anime", limit=20, timeout=600)


class AnimeScreenController:
    """The controller for the anime screen"""

    def __init__(self, model: AnimeScreenModel):
        self.model = model
        self.view = AnimeScreenView(controller=self, model=self.model)

    def get_view(self) -> AnimeScreenView:
        return self.view

    def fetch_streams(self, anilist_Data, is_dub=False, episode="1"):
        if self.view.is_dub:
            is_dub = self.view.is_dub.active
            if anime_data := self.model.get_anime_data_from_provider(
                anilist_Data, is_dub
            ):
                self.view.current_anime_data = anime_data
        if current_servers := self.model.get_episode_streams(episode, is_dub):
            Logger.debug(f"current servers {current_servers}")
            self.view.current_servers = current_servers
        else:
            Logger.warning(f"No servers found for {anilist_Data['title']['romaji']}")
        # TODO: add auto start
        #
        # self.view.current_link = self.view.current_links[0]["gogoanime"][0]

    def update_anime_view(
        self, anilist_data: "AnilistBaseMediaDataSchema", caller_screen_name
    ):
        self.fetch_streams(anilist_data)
        self.view.current_anilist_data = anilist_data
        self.view.current_title = (
            anilist_data["title"]["english"] or anilist_data["title"]["romaji"]
        )
        self.view.caller_screen_name = caller_screen_name


__all__ = ["AnimeScreenController"]
