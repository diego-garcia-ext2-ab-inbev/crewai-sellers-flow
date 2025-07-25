from abc import ABC, abstractmethod
from pydantic import BaseModel

class WhatsappLKARepository(ABC):
    """Interface para o repositório de LKA dos sellers."""

    class Output(BaseModel):
        instance: str
        token: str

    @abstractmethod
    def get_lka(self, seller_id: str) -> Output:
        pass
