from abc import ABC, abstractmethod


class LLMClient(ABC):
    @abstractmethod
    def generate(self, *args: object) -> object:
        pass
