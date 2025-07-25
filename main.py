from crewai_sellers_flow.tools.custom_tool import JSONTool
from crewai_tools import JSONSearchTool
from crewai_sellers_flow.adapters.json_seller_repository import JsonSellerRepository
import json
from datetime import datetime
from crewai_sellers_flow.adapters.braze_crm_plataform import BrazeCRMPlatform
from crewai_sellers_flow.config import config
from crewai_sellers_flow.domain.sellers_new_target import SELLERS_NEW_TARGET

# General JSON content search
# This approach is suitable when the JSON path is either known beforehand or can be dynamically identified.

if __name__ == "__main__":
    # tool = JSONTool()
    # print(tool.run())

    # # tool = JSONSearchTool(json_path='2025_06_11_03_26_fill_rate_data.json')
    # resultado = FillRateCrew().crew().kickoff()
    # print(resultado)

    repository = JsonSellerRepository()
    start_date = datetime(2025, 10, 6)
    end_date = datetime(2025, 10, 12)
    sellers = repository.get_sellers(start_date, end_date)
    sellers = [
        seller
        for seller in sellers
        if seller.seller_id >= 82354
        and seller.seller_id != 85452
        and seller.seller_id not in SELLERS_NEW_TARGET
        and seller.have_message_to_seller()
    ]
    json_strings = [seller.model_dump_json(indent=4) for seller in sellers]
    combined_json = f"[{','.join(json_strings)}]"
    # sellers = json.dumps(sellers, indent=4, ensure_ascii=False)
    with open("resultado.json", 'w', encoding='utf-8') as f:
        f.write(combined_json)

    braze_crm_platform = BrazeCRMPlatform(config.BRAZE_API_KEY)
    braze_crm_platform.update_sellers(sellers)
    print("Sellers updated successfully")
