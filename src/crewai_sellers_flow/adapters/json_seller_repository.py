import os
import json
import re
from datetime import datetime, timedelta, date
from typing import List, Dict, Any
from collections import defaultdict
import pandas as pd
from decimal import Decimal, ROUND_UP
from crewai_sellers_flow.domain.seller_report import SellerReport, ReasonCancel, CourrierCancel

from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.client_credential import ClientCredential
from crewai_sellers_flow.ports.seller_repository import SellerRepository

class DownloadError(Exception):
    pass

class JsonSellerRepository(SellerRepository):

    def __init__(self):
        self.site_url = os.getenv("SHAREPOINT_SITE_URL")
        self.client_id = os.getenv("SHAREPOINT_CLIENT_ID")
        self.client_secret = os.getenv("SHAREPOINT_CLIENT_SEC")
        self.folder_path = os.getenv("SHAREPOINT_PATH")
        self.ctx = None

    def _connect_sharepoint(self):
        """
        Estabelece conexão com o SharePoint.
        
        Returns:
            bool: True se a conexão foi bem sucedida, False caso contrário
        """
        credentials = ClientCredential(self.client_id, self.client_secret)
        self.ctx = ClientContext(self.site_url).with_credentials(credentials)

    def get_files_in_date_range(self, sufix: str, start_date: datetime, end_date: datetime) -> List[str]:
        """
        Retorna lista de arquivos JSON no diretório que estão dentro do intervalo de datas.
        """
        files = []

        current_date = start_date
        while current_date <= end_date:
            file_name = f"{current_date.strftime('%Y_%m_%d')}{sufix}.json"
            file_path = self._download_file(file_name)
            files.append(file_path)
            current_date += timedelta(days=1)

        return sorted(files)

    def _download_file(self, file_name: str) -> str:
        """
        Faz download de um arquivo do SharePoint.
        
        Args:
            file_url (str): URL relativa do arquivo no SharePoint
            local_path (str): Caminho local onde o arquivo será salvo
            library_name (str, optional): Nome da biblioteca de documentos. Defaults to None.
            
        Returns:
            bool: True se o download foi bem sucedido, False caso contrário
        """
        try:
            if not self.ctx:
                self._connect_sharepoint()

            temp_file = f"/tmp/{file_name}"

            file_url = f"{self.folder_path}/{file_name}"

            file = self.ctx.web.get_file_by_server_relative_url(file_url)

            os.makedirs(os.path.dirname(temp_file), exist_ok=True)

            with open(temp_file, "wb") as local_file:
                file.download(local_file).execute_query()

            print(f"Arquivo baixado com sucesso: {temp_file}")
            return temp_file
        except Exception as e:
            print(f"Erro ao fazer download do arquivo: {str(e)}")
            raise DownloadError(f"Erro ao fazer download do arquivo: {str(e)}")

    def _read_files_order(self, files: list[str]) -> list[dict]:
        data = []
        for file in files:
            with open(file, 'r', encoding='utf-8') as file:
                data.extend(json.load(file))
        return data

    def _aggregate_data_by_poc_id(self, data_list: List[Dict[str, Any]]) -> list[dict]:
        """
        Agrega dados por dim_poc[ID], somando os campos numéricos.
        """
        aggregated = defaultdict(lambda: {
            'ID': None,
            'pedidos_gerados': 0,
            'cancelado_entregador': 0,
            'cancelado_pdv': 0,
            'cancelado_usuario': 0,
            'pedidos_rejeitados': 0,
            'pedidos_expirados': 0,
            'fill_rate': 0,
            'motocas': [],
            'motivos': []
        })

        for record in data_list:
            poc_id = record.get('dim_poc[ID]')
            if poc_id is None:
                print(f"POC {poc_id} não existe")
                continue

            # Se é o primeiro registro para este POC, copia os campos de dimensão
            if aggregated[poc_id]['ID'] is None:
                aggregated[poc_id]['ID'] = poc_id

            # Soma os campos numéricos
            numeric_fields = {
                "[Pedidos_Gerados_PDV]": "pedidos_gerados",
                "[Cancelado_Entregador_PDV]": "cancelado_entregador",
                "[Cancelado_PDV_PDV]": "cancelado_pdv",
                "[Cancelado_Usuário_PDV]": "cancelado_usuario",
                "[Pedidos_Rejeitados_PDV]": "pedidos_rejeitados",
                "[Pedidos_Expirados_PDV]": "pedidos_expirados"
            }

            for field, key in numeric_fields.items():
                value = record.get(field, 0)
                if isinstance(value, (int, float)):
                    aggregated[poc_id][key] += value
            pedidos_gerados = aggregated[poc_id]['pedidos_gerados']
            cancelado_entregador = aggregated[poc_id]['cancelado_entregador']
            cancelado_pdv = aggregated[poc_id]['cancelado_pdv']
            cancelado_usuario = aggregated[poc_id]['cancelado_usuario']
            pedidos_rejeitados = aggregated[poc_id]['pedidos_rejeitados']
            pedidos_expirados = aggregated[poc_id]['pedidos_expirados']      
            cancelados = cancelado_entregador + cancelado_pdv + cancelado_usuario
            rate = (
                Decimal(
                    pedidos_gerados - (cancelados + pedidos_expirados + pedidos_rejeitados)
                ) / Decimal(pedidos_gerados) * 100
            )
            aggregated[poc_id]["fill_rate"] = float(rate.quantize(Decimal('0.1'), rounding=ROUND_UP))

        return [value for value in aggregated.values()]

    def _read_files_reasons(self, files: list[str]) -> pd.DataFrame:
        data = []
        for file in files:
            with open(file, 'r', encoding='utf-8') as file:
                data.extend(json.load(file))   

        # Agrupar por ID, Tipo, Motivo, Data  e Hora
        grouped_data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(int)))))

        for record in data:
            id_record = record.get("[ID]")
            tipo = record.get("[Tipo]")
            motivo = record.get("[Motivo]")
            # data = datetime.strptime(record.get("[Data]"), '%Y/%m/%d').date()
            data = record.get("[Data]")
            hora = record.get("[Hora]")
            quantity = record.get("[Quantity]", 0)

            grouped_data[id_record][tipo][motivo][data][hora] += quantity

        # Converter para um formato mais legível
        results = []
        for id_record in grouped_data:
            for tipo in grouped_data[id_record]:
                for motivo in grouped_data[id_record][tipo]:
                    for data in grouped_data[id_record][tipo][motivo]:
                        for hora in grouped_data[id_record][tipo][motivo][data]:
                            results.append({
                                "ID": id_record,
                                "tipo": tipo,
                                "motivo": motivo,
                                "data": data,
                                "hora": hora,
                                "quantidade": grouped_data[id_record][tipo][motivo][data][hora]
                            })

        # Criar DataFrame para melhor visualização
        df = pd.DataFrame(results)

        # Ordenar por ID, Tipo, Motivo e Hora
        df = df.sort_values(['ID', 'tipo', 'motivo', 'data', 'hora'])
        return df

    def _read_files_courrier(self, files: list[str]) -> pd.DataFrame:
        data = []
        for file in files:
            with open(file, 'r', encoding='utf-8') as file:
                data.extend(json.load(file))   

        # Agrupar por ID, delivery_man
        grouped_data = defaultdict(lambda: defaultdict(int))

        for record in data:
            id_record = record.get("dim_poc[ID]")
            delivery_man = record.get("fact_fill_rate_pdvs[deliveryman_email]", "N/A")
            quantity = record.get("[Canc_motoca]", 0)

            grouped_data[id_record][delivery_man] += quantity

        # Converter para um formato mais legível
        results = []
        for id_record in grouped_data:
            for delivery_man in grouped_data[id_record]:
                results.append({
                    "ID": id_record,
                    "email": delivery_man,
                    "quantidade": grouped_data[id_record][delivery_man]
                })

        # Criar DataFrame para melhor visualização
        df = pd.DataFrame(results)

        # Ordenar por ID, delivery_man
        df = df.sort_values(['ID', 'email'])
        return df    

    def _update_orders_with_reasons(self, orders: list[dict], reasons: pd.DataFrame) -> list[dict]:
        """
        Atualiza as ordens com os motivos de cancelamento.
        """
        for order in orders:
            order_id = order.get("ID")

            if order_id and not reasons.empty:
                order_reasons = reasons[reasons['ID'] == order_id]
                if not order_reasons.empty:
                    # Agrupa por tipo e soma as quantidades
                    tipo_quantidade = order_reasons.groupby('tipo')['quantidade'].sum().reset_index()
                    # Pega o tipo com maior quantidade
                    tipo_maior = tipo_quantidade.loc[tipo_quantidade['quantidade'].idxmax(), 'tipo']

                    # Filtra apenas os registros do tipo com maior quantidade
                    tipo = order_reasons[order_reasons['tipo'] == tipo_maior]
                    motivo_quantidade = tipo.groupby(['tipo', 'motivo'])['quantidade'].sum().reset_index()
                    motivo_maior = motivo_quantidade.loc[motivo_quantidade['quantidade'].idxmax(), 'motivo']

                    motivo = tipo[tipo['motivo'] == motivo_maior]
                    data_hora = motivo.groupby(['tipo', 'motivo', 'data', 'hora'])['quantidade'].sum().reset_index()
                    # data_hora = data_hora[data_hora['quantidade'] >= 2]
                    data_hora = data_hora.sort_values('quantidade', ascending=False)
                    reasons_list = data_hora.to_dict('records')
                    # if len(reasons_list) and int(reasons_list[0]['quantidade']) < 2:
                    #     reasons_list = []
                    # top_reasons = grouped_reasons.nlargest(2, 'quantidade')
                    # reasons_list = top_reasons.to_dict('records')
                    # if len(reasons_list) > 1:
                    #     nlargest = 2
                    #     while reasons_list[0]['tipo'] != reasons_list[nlargest-1]['tipo']:
                    #         nlargest += 1
                    #         top_reasons = grouped_reasons.nlargest(nlargest, 'quantidade')
                    #         reasons_list = top_reasons.to_dict('records')
                    #     reasons_list = [reasons_list[0], reasons_list[nlargest-1]]
                    order['motivos'] = reasons_list
                else:
                    order['motivos'] = []
            else:
                order['motivos'] = []

        return orders

    def _update_orders_with_courrier(self, orders: list[dict], courriers: pd.DataFrame) -> list[dict]:
        """
        Atualiza as ordens com os motivos de cancelamento.
        """
        for order in orders:
            order_id = order.get("ID")
            cancelado_entregador = order.get("cancelado_entregador")
            cancelado_pdv = order.get("cancelado_pdv")
            cancelado_usuario = order.get("cancelado_usuario")
            pedidos_expirados = order.get("pedidos_expirados")
            pedidos_rejeitados = order.get("pedidos_rejeitados")
            if (
                cancelado_entregador > cancelado_pdv
                and cancelado_entregador > cancelado_usuario
                and cancelado_entregador > pedidos_expirados
                and cancelado_entregador > pedidos_rejeitados
            ):
                if order_id and not courriers.empty:
                    order_courriers = courriers[courriers['ID'] == order_id]
                    if not order_courriers.empty:
                        grouped_courriers = order_courriers.groupby(['email'])['quantidade'].sum().reset_index()
                        top_courriers = grouped_courriers.nlargest(2, 'quantidade')
                        courriers_list = top_courriers.to_dict('records')
                        order['motocas'] = courriers_list

        return orders

    def output_sellers(self, sellers: list[dict]) -> list[SellerReport]:
        sellers_report = []
        for seller in sellers:
            seller_report = SellerReport(
                seller_id=seller["ID"],
                orders_managed=seller["pedidos_gerados"],
                canceled_by_seller=seller["cancelado_pdv"],
                canceled_by_consumer=seller["cancelado_usuario"],
                canceled_on_delivery=seller["cancelado_entregador"],
                expired=seller["pedidos_expirados"],
                rejected=seller["pedidos_rejeitados"],
                reasons_cancel=[
                    ReasonCancel(
                        type=reason["tipo"],
                        reason=reason["motivo"],
                        date=datetime.strptime(reason["data"], '%Y/%m/%d').date(),
                        hour=int(reason["hora"]),
                        quantity=reason["quantidade"],
                    )
                    for reason in seller["motivos"]
                ],
                # courriers_cancel=[
                #     CourrierCancel(
                #         email=courrier["email"], quantity=courrier["quantidade"]
                #     )
                #     for courrier in seller["motocas"]
                # ],
            )
            sellers_report.append(seller_report)
        return sellers_report

    def get_sellers(self, start_date: datetime, end_date: datetime) -> list[SellerReport]:
        """
        Obtém os vendedores.
        """ 
        files_order   = self.get_files_in_date_range('_fill_rate_data', start_date, end_date)
        files_reasons = self.get_files_in_date_range('_reasons_fill_rate_data', start_date, end_date)
        # files_courrier  = self.get_files_in_date_range('_fill_rate_motoca', start_date, end_date)

        orders = self._read_files_order(files_order)
        reasons = self._read_files_reasons(files_reasons)
        # courrier = self._read_files_courrier(files_courrier)

        orders = self._aggregate_data_by_poc_id(orders)
        # Ordena as ordens pelo ID para garantir consistência
        orders = sorted(orders, key=lambda x: x.get('ID', ''))
        # print(orders)
        # Atualiza as ordens com os motivos de cancelamento
        orders = self._update_orders_with_reasons(orders, reasons)
        # orders = self._update_orders_with_courrier(orders, courrier)

        sellers = self.output_sellers(orders)
        for seller in sellers:
            seller.fill_rate = seller._fill_rate()
            seller.status = seller._status()
            seller.message = seller.message_to_seller()

        return sellers
