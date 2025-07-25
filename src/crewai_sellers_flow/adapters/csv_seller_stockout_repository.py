import csv
from pathlib import Path
from typing import Iterable

from crewai_sellers_flow.domain.seller_stockout import SellerStockOut
from crewai_sellers_flow.ports.seller_stockout_repository import (
    SellerStockOutRepository,
)


class CsvSellerStockOutRepository(SellerStockOutRepository):
    """Adapter para o repositório de stockout dos sellers."""
    
    def __init__(self, root_path: str | None = None) -> None:
        self.root_path = Path(root_path or "/home/diego/git/crewai-sellers-flow")
        self.csv_path = self.root_path / "downloads" / "STOCKOUT.csv"
        self.sellers: list[SellerStockOut] = []

    def read(self) -> list[SellerStockOut]:
        if not self.csv_path.exists():
            return []

        if not self.sellers:
            self.sellers = self._read()

        return self.sellers

    def _read(self) -> list[SellerStockOut]:
        sellers: list[SellerStockOut] = []
        with self.csv_path.open("r", encoding="utf-8") as fp:
            reader = csv.reader(fp, delimiter=';')
            # Skip header
            try:
                next(reader)
            except StopIteration:
                return []

            for row in reader:
                if not row or len(row) < 4:
                    continue
                # Some headers include backslashes; data rows appear clean
                try:
                    if row[3].strip() == "#N/D":
                        continue
                    seller = SellerStockOut(
                        id=int(row[0].strip()),
                        name=row[1].strip(),
                        stockout=int(row[2].strip().replace("#N/D", "0")) if row[2].strip() != "" else 0,
                        top_product=row[3].strip(),
                    )
                except ValueError:
                    # If stockout is not an int (e.g., '#N/D'), coerce to 0
                    try:
                        seller = SellerStockOut(
                            id=int(row[0].strip()),
                            name=row[1].strip(),
                            stockout=0,
                            top_product=row[3].strip(),
                        )
                    except Exception:
                        continue
                sellers.append(seller)

        return sellers


