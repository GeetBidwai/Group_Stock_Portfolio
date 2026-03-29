from django.conf import settings
from django.db import models

from apps.portfolio_module.models import PortfolioStock, PortfolioType


class QualityStock(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quality_stocks")
    portfolio = models.ForeignKey(PortfolioType, on_delete=models.CASCADE, related_name="quality_stocks")
    stock = models.ForeignKey(PortfolioStock, on_delete=models.CASCADE, related_name="quality_reports")
    ai_rating = models.FloatField()
    buy_signal = models.CharField(max_length=10)
    report_json = models.JSONField()
    graphs_data = models.JSONField(null=True, blank=True)
    generated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-generated_at", "-id"]
        unique_together = ("portfolio", "stock")

    def __str__(self) -> str:
        return f"{self.user_id}:{self.portfolio_id}:{self.stock_id}"
