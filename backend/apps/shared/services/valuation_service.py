class ValuationService:
    def compute_intrinsic_value(self, eps: float | None, pe: float | None) -> float | None:
        if eps is None or pe is None:
            return None
        return round(eps * max(pe * 0.9, 1), 2)

    def compute_discount_percentage(self, current_price: float | None, intrinsic_value: float | None) -> float | None:
        if not current_price or intrinsic_value is None:
            return None
        return round(((intrinsic_value - current_price) / current_price) * 100, 2)

    def opportunity_signal(self, discount_percentage: float | None) -> str:
        if discount_percentage is None:
            return "insufficient_data"
        if discount_percentage >= 15:
            return "strong_upside"
        if discount_percentage >= 5:
            return "moderate_upside"
        if discount_percentage <= -10:
            return "possibly_overvalued"
        return "fairly_priced"
