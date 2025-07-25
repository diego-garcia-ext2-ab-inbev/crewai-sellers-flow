import requests
from datetime import datetime
from crewai_sellers_flow.ports.crm_platform import CRMPlatform
from crewai_sellers_flow.domain.seller_report import SellerReport

class BrazeCRMPlatform(CRMPlatform):
    def __init__(self, api_key: str, base_url: str = "https://rest.iad-05.braze.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

    def update_sellers(self, analysis: list[SellerReport]) -> None:
        BATCH_SIZE = 50  
        
        for i in range(0, len(analysis), BATCH_SIZE):
            batch = analysis[i:i + BATCH_SIZE]
            attributes = []
            
            for report in batch:
                if report.have_message_to_seller():
                    attribute = {
                        "external_id": str(report.seller_id),
                        "FILL_RATE_OFENDOR": report.offender().value if report.offender() else None,
                        "FILL_RATE_INDEX": str(report.fill_rate),
                        "FILL_RATE_STATUS": report.status.value,
                        "FILL_RATE_MESSAGE": report.message,
                        "FILL_RATE_REASON": report.get_reason(),
                        "FILL_RATE_CANCELED_ON_DELIVERY": str(report.rate_canceled_on_delivery()),
                        "FILL_RATE_LAST_MESSAGE": datetime.now().strftime("%Y-%m-%d"),
                        "_update_existing_only": True
                    }
                    attributes.append(attribute)

            payload = {
                "attributes": attributes
            }

            response = requests.post(
                f"{self.base_url}/users/track",
                headers=self.headers,
                json=payload
            )

            response_data = response.json()
            if response_data.get("message") != "success":
                raise Exception(f"Erro ao atualizar dados na Braze: {response.text}")
            
            print(f"Lote {i//BATCH_SIZE + 1} processado com sucesso. Atributos processados: {response_data.get('attributes_processed', 0)}") 
