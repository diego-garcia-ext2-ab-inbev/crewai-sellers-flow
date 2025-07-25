from crewai_sellers_flow.tools.custom_tool import JSONTool
from crewai_tools import JSONSearchTool
from crewai_sellers_flow.adapters.json_seller_repository import JsonSellerRepository
import json
import traceback
from datetime import datetime
from crewai_sellers_flow.adapters.braze_crm_plataform import BrazeCRMPlatform
from crewai_sellers_flow.config import config
from crewai_sellers_flow.adapters.whatsapp_lka_sharepoint import WhatsappLKASharepoint
from crewai_sellers_flow.adapters.api_z_message import ApiZMessage
import base64
import concurrent.futures
import time
from typing import List, Dict, Any
from crewai_sellers_flow.domain.seller_report import SellerReport, SellerStatus
from crewai_sellers_flow.domain.sellers_new_target import SELLERS_NEW_TARGET
from crewai_sellers_flow.adapters.csv_seller_stockout_repository import CsvSellerStockOutRepository

# General JSON content search
# This approach is suitable when the JSON path is either known beforehand or can be dynamically identified.

def convert_to_base64(file_path: str):
    with open(file_path, "rb") as file:
        file_data = file.read()
        base64_string = base64.b64encode(file_data).decode('utf-8')
    return base64_string


def process_seller(
    seller: SellerReport,
    sharepoint: WhatsappLKASharepoint,
    api_z_message: ApiZMessage,
    base64_images: Dict[str, str],
) -> Dict[str, Any]:
    """
    Processa um seller individualmente e retorna o resultado.
    """
    result = {
        "seller_id": seller.seller_id,
        "success": False,
        "error": None,
        "responses": []
    }

    try:
        lka = sharepoint.get_lka(seller.seller_id)

        if seller.status != SellerStatus.CONGRATS:
            if len(seller.reasons_cancel) == 0:
                result["error"] = "No reasons to cancel"
                return result

            type = seller.reasons_cancel[0].type

            # Mapeia o tipo para a imagem correspondente
            type_to_image = {
                "USER_CANCEL": "base64_consumidor",
                "PDV_EXPIRED": "base64_expirado", 
                "COURIER_CANCEL": "base64_motoca",
                "PDV_REJECTED": "base64_rejeitado",
                "PDV_CANCEL": "base64_loja"
            }

            if type not in type_to_image:
                result["error"] = f"Unknown type: {type}"
                return result
            base64_image = base64_images[type_to_image[type]]
        else:
            base64_image = base64_images["base64_parabens"]

        seller.message = seller.message_to_seller_to_whatsapp()

        # Envia a imagem
        image_response = api_z_message.send_image(
            lka.phone_seller,
            f"data:image/png;base64,{base64_image}",
            lka.instance,
            lka.token
        )
        result["responses"].append(image_response)

        # Envia a mensagem
        message_response = api_z_message.send_message(
            lka.phone_seller,
            seller.message,
            lka.instance,
            lka.token
        )
        result["responses"].append(message_response)

        result["success"] = True
        print(f"✅ Mensagem enviada para o vendedor {seller.seller_id}")

    except Exception as e:
        result["error"] = str(e)
        print(f"❌ Erro ao processar vendedor {seller.seller_id}: {e}")

    return result


if __name__ == "__main__":
    # tool = JSONTool()
    # print(tool.run())

    # # tool = JSONSearchTool(json_path='2025_06_11_03_26_fill_rate_data.json')
    # resultado = FillRateCrew().crew().kickoff()
    # print(resultado)

    base64_parabens = convert_to_base64("downloads/Parabéns.png") 
    base64_consumidor = convert_to_base64("downloads/Consumidor.png")
    base64_expirado = convert_to_base64("downloads/Expirado.png")
    base64_loja = convert_to_base64("downloads/Loja.png")
    base64_motoca = convert_to_base64("downloads/Motoca.png")
    base64_rejeitado = convert_to_base64("downloads/Rejeitado.png")

    repository = JsonSellerRepository()
    start_date = datetime(2025, 10, 13)
    end_date = datetime(2025, 10, 19)
    sellers = repository.get_sellers(start_date, end_date)
    stockout = CsvSellerStockOutRepository()
    stockout_sellers = stockout.read()
    for seller in sellers:
        seller.stockout_top_product = next((s.top_product for s in stockout_sellers if s.id == seller.seller_id), None)
        seller.message = seller.message_to_seller_to_whatsapp()

    # sellers = [
    #     seller
    #     for seller in sellers
    #     if seller.stockout_top_product
    #     and seller.have_message_to_seller()
    # ]

    sharepoint = WhatsappLKASharepoint()
    sharepoint.setup()
    # total_sellers = len(sellers)
    # total_lka_not_found = 0
    # for seller in sellers:
    #     try:
    #         if seller.have_message_to_seller():
    #             # api_z_message.send_message(lka.phone_seller, seller.message_to_seller_to_whatsapp(), lka.instance, lka.token)
    #             seller.message = seller.message_to_seller_to_whatsapp()
    #             lka = sharepoint.get_lka(seller.seller_id)
    #     except Exception as e:
    #         total_lka_not_found += 1
    #         print(f"Erro ao enviar mensagem para o vendedor {seller.seller_id}: {e}")
    #         # print(f"Traceback completo:")
    #         # print(traceback.format_exc())

    json_strings = [seller.model_dump_json(indent=4) for seller in sellers]
    combined_json = f"[{','.join(json_strings)}]"
    with open("resultado.json", 'w', encoding='utf-8') as f:
        f.write(combined_json)

    # print(f"Total de vendedores: {total_sellers}")
    # print(f"Total de LKA não encontrados: {total_lka_not_found}")

    api_z_message = ApiZMessage()

    # Prepara as imagens base64 em um dicionário para facilitar o acesso
    base64_images = {
        "base64_parabens": base64_parabens,
        "base64_consumidor": base64_consumidor,
        "base64_expirado": base64_expirado,
        "base64_motoca": base64_motoca,
        "base64_rejeitado": base64_rejeitado,
        "base64_loja": base64_loja
    }

    # Filtra sellers que precisam de mensagem
    sellers_to_process = [
        seller
        for seller in sellers
        if (seller.seller_id < 82354 or seller.seller_id == 85452)
        and seller.seller_id not in SELLERS_NEW_TARGET
        if seller.have_message_to_seller()
    ]

    print(f"🚀 Iniciando processamento paralelo de {len(sellers_to_process)} vendedores...")
    start_time = time.time()

    # Processamento paralelo
    results = []
    max_workers = 15  # Ajuste conforme necessário (recomendo 5-15 para APIs externas)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submete todas as tarefas
        future_to_seller = {
            executor.submit(process_seller, seller, sharepoint, api_z_message, base64_images): seller 
            for seller in sellers_to_process
        }

        # Coleta os resultados conforme são concluídos
        for future in concurrent.futures.as_completed(future_to_seller):
            seller = future_to_seller[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"❌ Erro inesperado ao processar vendedor {seller.seller_id}: {e}")
                results.append({
                    "seller_id": seller.seller_id,
                    "success": False,
                    "error": str(e),
                    "responses": []
                })

    end_time = time.time()
    processing_time = end_time - start_time

    # Estatísticas
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful

    print(f"\n📊 Estatísticas do processamento:")
    print(f"   ⏱️  Tempo total: {processing_time:.2f} segundos")
    print(f"   ✅ Sucessos: {successful}")
    print(f"   ❌ Falhas: {failed}")
    print(f"   📈 Taxa de sucesso: {(successful/len(results)*100):.1f}%")
    print(f"   🚀 Velocidade: {len(results)/processing_time:.1f} vendedores/segundo")

    # Salva apenas as respostas bem-sucedidas
    successful_responses = []
    for result in results:
        if result["success"]:
            successful_responses.extend(result["responses"])

    # Salva os resultados completos para análise
    with open("z_api_response.json", 'w', encoding='utf-8') as f:
        f.write(json.dumps(results, indent=4))

    # Salva apenas as respostas bem-sucedidas
    with open("z_api_successful_responses.json", 'w', encoding='utf-8') as f:
        f.write(json.dumps(successful_responses, indent=4))
