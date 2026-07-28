from dataclasses import dataclass

@dataclass
class Position:
    series_id: str
    net_quantity: int
    avg_cost: float
    current_price: float
    unrealised_pnl: float
    realised_pnl: float

