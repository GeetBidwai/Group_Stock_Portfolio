from django.db import models


class Market(models.Model):
    code = models.CharField(max_length=12, unique=True, db_index=True)
    name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Sector(models.Model):
    market = models.ForeignKey(Market, related_name="sectors", on_delete=models.CASCADE)
    code = models.CharField(max_length=48)
    name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("market", "code")

    def __str__(self) -> str:
        return f"{self.market.code}:{self.name}"


class Stock(models.Model):
    sector = models.ForeignKey(Sector, related_name="stocks", on_delete=models.CASCADE, null=True, blank=True)
    symbol = models.CharField(max_length=24, db_index=True)
    name = models.CharField(max_length=255)
    exchange = models.CharField(max_length=24, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["symbol"]
        unique_together = ("sector", "symbol")

    def __str__(self) -> str:
        return f"{self.symbol} - {self.name}"


class PortfolioEntry(models.Model):
    user = models.ForeignKey("auth_module.User", related_name="stock_portfolio_entries", on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, related_name="portfolio_entries", on_delete=models.CASCADE)
    sector = models.ForeignKey(Sector, related_name="portfolio_entries", on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sector__name", "stock__symbol"]
        unique_together = ("user", "stock")

    def __str__(self) -> str:
        return f"{self.user_id}:{self.stock.symbol}"
