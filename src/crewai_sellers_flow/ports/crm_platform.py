from abc import ABC, abstractmethod
from crewai_sellers_flow.domain.seller_report import SellerReport

class CRMPlatform(ABC):
    @abstractmethod
    def update_sellers(self, analysis: list[SellerReport]) -> None:

        """Update the sellers in the CRM platform.
        
        Args:
            analysis: List of sellers to be updated
        """
        pass
