import os
from abc import abstractmethod

from google import genai
from google.genai import Client, types

from performance_tracker.latex.factories.latex_factory_base import LaTeXFactoryBase


class LLMFactory(LaTeXFactoryBase):
    _client: Client = None

    def __init__(self) -> None:
        self._client = genai.Client(
            api_key=os.environ.get("LLM_CLIENT_KEY"),
            http_options=types.HttpOptions(api_version="v1"),
        )

    @abstractmethod
    def make_request(self, online: bool = False) -> str:
        pass
