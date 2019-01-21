from abc import ABC, abstractmethod


class AbstractInputAdapter(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def ingest(self, file, *args, **kwargs):
        pass