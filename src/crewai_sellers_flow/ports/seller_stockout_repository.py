from abc import ABC, abstractmethod
from typing import Iterable
from crewai_sellers_flow.domain.seller_stockout import SellerStockOut


class SellerStockOutRepository(ABC):
    """Interface para o repositório de stockout dos sellers."""

    @abstractmethod
    def read(self) -> list[SellerStockOut]:
        pass


