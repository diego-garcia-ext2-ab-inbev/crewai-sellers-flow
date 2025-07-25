from abc import ABC, abstractmethod


class SellerRepository(ABC):
    """Interface para o repositório de relatórios de vendedores."""

    @abstractmethod
    def get_sellers(self) -> list[dict]:
        pass
