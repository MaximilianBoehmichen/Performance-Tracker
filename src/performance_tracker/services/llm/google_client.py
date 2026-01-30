import os

from performance_tracker.services.llm.llm_client import LLMClient


class GoogleClient(LLMClient):
    def __init__(self) -> None:
        super().__init__()

        self.api_key = os.environ.get("GOOGLE_API_KEY")

    def generate(self, text: str, online: bool = False) -> str:
        return ""
