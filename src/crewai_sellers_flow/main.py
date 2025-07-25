from crewai.flow import Flow, listen, start
from crewai_sellers_flow.ports.seller_repository import SellerRepository
from crewai_sellers_flow.ports.crm_platform import CRMPlatform
from crewai_sellers_flow.config import Config
from crewai_sellers_flow.domain.seller_report import SellerReport
from crewai_sellers_flow.adapters.braze_crm_plataform import BrazeCRMPlatform
from crewai_sellers_flow.adapters.json_seller_repository import JsonSellerRepository

class SellerStrikesFlow(Flow):
    config: Config
    seller_repository: SellerRepository
    crm_platform: CRMPlatform
    sellers: list[dict]
    analysis: list[SellerReport]

    def __init__(
        self,
        *,
        seller_repository: SellerRepository | None = None,
        crm_platform: CRMPlatform | None = None,
    ) -> None:
        super().__init__()

        self.config = Config()
        self.seller_repository = seller_repository or JsonSellerRepository()
        self.crm_platform = crm_platform or BrazeCRMPlatform()

    @start()
    def get_fill_rate_data(self):
        self.sellers = self.seller_repository.get_sellers()

    @listen(get_fill_rate_data)
    def analyse_sellers(self):
        pass

    @listen(analyse_sellers)
    def update_crm(self):
        self.crm_platform.update_sellers(self.analysis)
    

def kickoff():
    flow = SellerStrikesFlow(
        crm_platform=MockCRMPlatform()
    )
    flow.kickoff()


def plot():
    flow = SellerStrikesFlow()
    flow.plot()


if __name__ == "__main__":
    kickoff()
