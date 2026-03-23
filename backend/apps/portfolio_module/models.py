from django.conf import settings
from django.db import models


#  NEW: Sector Model
class Sector(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name


#  UPDATED: PortfolioType
class PortfolioType(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="portfolio_types",
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)

    #  NEW FIELD
    sector = models.ForeignKey(
        Sector,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="portfolios"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "name")
        ordering = ["name"]

    def __str__(self):
        return self.name


#  SAME: PortfolioStock (no change)
class PortfolioStock(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="portfolio_stocks",
        on_delete=models.CASCADE
    )
    portfolio_type = models.ForeignKey(
        PortfolioType,
        related_name="stocks",
        on_delete=models.CASCADE
    )
    symbol = models.CharField(max_length=24)
    company_name = models.CharField(max_length=255, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    average_buy_price = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "portfolio_type", "symbol")
        ordering = ["symbol"]

    def __str__(self):
        return self.symbol