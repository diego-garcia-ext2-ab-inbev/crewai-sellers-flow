from pydantic import BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal, ROUND_UP
from enum import Enum
from crewai_sellers_flow.domain.message_template import CRITICAL, NORMAL, CONGRATS, ALERT, HEADER

class ReasonCancel(BaseModel):
    type: str
    reason: str
    date: date
    hour: int
    quantity: int


class CourrierCancel(BaseModel):
    email: str
    quantity: int

class SellerStatus(Enum):
    CRITICAL = "CRITICAL"
    ALERT = "ALERT"
    NORMAL = "NORMAL"
    CONGRATS = "CONGRATS"

class Offender(Enum):
    SELLER = "SELLER"
    CONSUMER = "CONSUMER"
    DELIVERY = "DELIVERY"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class SellerReport(BaseModel):
    seller_id: int
    orders_managed: int
    canceled_by_seller: int
    canceled_by_consumer: int
    canceled_on_delivery: int
    expired: int
    rejected: int
    fill_rate: Optional[float] = None
    status: Optional[SellerStatus] = None
    message: Optional[str] = None
    stockout_top_product: Optional[str] = None
    reasons_cancel: list[ReasonCancel]

    def total_canceled(self) -> int:
        return (
            self.canceled_by_seller
            + self.canceled_by_consumer
            + self.canceled_on_delivery
            + self.expired
            + self.rejected
        )

    def _fill_rate(self) -> float:
        canceled = self.total_canceled()
        if self.orders_managed == 0:
            return 0
        rate = (
            Decimal(self.orders_managed - canceled) / Decimal(self.orders_managed) * 100
        )
        return float(rate.quantize(Decimal("0.1"), rounding=ROUND_UP))

    def rate_canceled_on_delivery(self) -> float:
        rate = Decimal(self.canceled_on_delivery) / Decimal(self.orders_managed) * 100
        return float(rate.quantize(Decimal('0.1'), rounding=ROUND_UP))

    def _status(self) -> SellerStatus:
        """Calcula o status do vendedor com base na taxa de preenchimento.
        
        Returns:
            SellerStatus: O status do vendedor
        Rules:
            Congrats >> taxa de cancelamento <6%
            Normal >> taxa de cancelamento >=6% e <=8%
            Alerta >> taxa de cancelamento >8% e <10%
            Crítico >> taxa de cancelamento >=10%
        """
        if self.orders_managed == 0:
            return SellerStatus.NORMAL

        fill_rate = self._fill_rate()
        if fill_rate > 94:
            return SellerStatus.CONGRATS
        elif 92 <= fill_rate <= 94:
            return SellerStatus.NORMAL
        elif 90 < fill_rate < 92:
            return SellerStatus.ALERT
        return SellerStatus.CRITICAL

    def offender(self) -> Offender | None:
        """Identifica o maior ofensor entre os tipos de cancelamento.
        
        Returns:
            Offender: O tipo de ofensor com maior número de cancelamentos
        """
        if self._status() == SellerStatus.CONGRATS:
            return None

        offenders = {
            Offender.SELLER: self.canceled_by_seller,
            Offender.CONSUMER: self.canceled_by_consumer,   
            Offender.DELIVERY: self.canceled_on_delivery,
            Offender.REJECTED: self.rejected,
            Offender.EXPIRED: self.expired,
        }

        return max(offenders.items(), key=lambda x: x[1])[0]

    def message_to_seller_to_whatsapp(self) -> str:
        reasons = self.reasons_cancel
        if len(reasons) > 0:
            if template := self._get_template(reasons[0]):
                template = f"{HEADER.get(self.status.value, '')}\n\n{template}\n\n"
                template = template.format(
                    FILL_RATE_CANCELED_ON_DELIVERY=f"{self.rate_canceled_on_delivery():.2f}%",
                    FILL_RATE_INDEX=f"{self.fill_rate:.2f}%",
                    STOCKOUT_TOP_PRODUCT=(
                        f"\n\nO produto de maior impacto nos seus cancelamentos essa semana foi: {self.stockout_top_product}"
                        if self.stockout_top_product
                        else ""
                    ),
                )
                reasons = [reason for reason in self.reasons_cancel if reason.quantity >= 2]
                if len(reasons) > 0 and self.status != SellerStatus.CONGRATS:
                    cancel = f"{self._get_day_of_week(reasons[0].date)} às {reasons[0].hour:02d}h"
                    for item in range(1, len(reasons)):
                        if reasons[0].quantity == reasons[item].quantity:
                            cancel += f" e {self._get_day_of_week(reasons[item].date)} às {reasons[item].hour:02d}h"
                    template += f"*Atenção {cancel}.*\nCancelamento é FALTA GRAVE.\n\n"
                template += "Equipe Zé Delivery"
                return template
        return ""

    def _get_day_of_week(self, date: date) -> str:
        day = date.strftime("%A")
        day_mapping = {
            "Monday": "à Segunda-feira",
            "Tuesday": "à Terça-feira", 
            "Wednesday": "à Quarta-feira",
            "Thursday": "à Quinta-feira",
            "Friday": "à Sexta-feira",
            "Saturday": "ao Sábado",
            "Sunday": "ao Domingo"
        }
        return day_mapping.get(day, day)

    def _get_template(self, reason: ReasonCancel) -> str:
        template = ""
        if self.status == SellerStatus.CRITICAL:
            template = CRITICAL
        elif self.status == SellerStatus.ALERT:
            template = ALERT
        elif self.status == SellerStatus.CONGRATS:
            template = CONGRATS
        elif self.status == SellerStatus.NORMAL:
            template = NORMAL

        if isinstance(template, dict):
            template = template.get(reason.type, "")
            if isinstance(template, dict):
                template = template.get(reason.reason, "")
        return template

    def get_reason(self) -> str | None:
        """Retorna o motivo de cancelamento do vendedor.
        
        Returns:
            str | None: O motivo de cancelamento do vendedor ou None se o vendedor está com status de Congrats
        """
        if self._status() != SellerStatus.CONGRATS:
            return self.reasons_cancel[0].reason if len(self.reasons_cancel) > 0 else None
        return None

    def have_message_to_seller(self) -> bool:
        """Verifica se o vendedor tem uma mensagem para enviar.
        O vendedor deve estar com status de Congrats ou ter algum motivo de cancelamento que 
        possui uma mensagem.

        Returns:
            bool: True se o vendedor tem uma mensagem para enviar, False caso contrário
        """
        if self._status() == SellerStatus.CONGRATS:
            return True
        reasons = self.reasons_cancel
        if len(reasons) > 0:
            if self._get_template(reasons[0]) != "":
                return True
        return False

    def message_to_seller(self) -> str | None:
        """Retorna a mensagem para o vendedor.
        Para retornar uma mensagem, o vendedor deve:
        - Não estar com status de Congrats.
        - Ter mais de 2 cancelamentos no mesmo dia e hora.
        Concatena na mensagem todos os motivos que possuem mais de 2 cancelamentos no mesmo dia e hora.
        
        Returns:
            str | None: A mensagem para o vendedor ou None se o vendedor não tem uma mensagem para enviar
        """
        if self._status() != SellerStatus.CONGRATS:
            reasons = self.reasons_cancel
            if len(reasons) > 0:
                reasons = [reason for reason in self.reasons_cancel if reason.quantity >= 2]
                if len(reasons) > 0:
                    cancel = f"{self._get_day_of_week(reasons[0].date)} as {reasons[0].hour:02d}h"
                    for item in range(1, len(reasons)):
                        if reasons[0].quantity == reasons[item].quantity:
                            cancel += f" e {self._get_day_of_week(reasons[item].date)} as {reasons[item].hour:02d}h"
                    return f"Atenção {cancel}. Cancelamento é FALTA GRAVE."
        return None

class SellerReportNewTarget(SellerReport):
    
    def _status(self) -> SellerStatus:
        """Calcula o status do vendedor com base na taxa de preenchimento.
        
        Returns:
            SellerStatus: O status do vendedor
        """
        if self.orders_managed == 0:
            return SellerStatus.CRITICAL

        fill_rate = self._fill_rate()
        if fill_rate >= 94:
            return SellerStatus.CONGRATS
        return SellerStatus.CRITICAL
