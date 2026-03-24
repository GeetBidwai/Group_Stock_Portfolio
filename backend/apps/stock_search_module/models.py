from django.db import models
from django.db.models.functions import Lower


class StockReference(models.Model):
    symbol = models.CharField(max_length=32, unique=True, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    sector = models.CharField(max_length=255, blank=True, db_index=True)
    risk_category = models.CharField(max_length=32, null=True, blank=True, db_index=True)
    exchange = models.CharField(max_length=32, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["symbol"]
        indexes = [
            models.Index(fields=["is_active", "symbol"], name="stock_active_symbol_idx"),
            models.Index(fields=["is_active", "name"], name="stock_active_name_idx"),
            models.Index(Lower("symbol"), name="stock_symbol_lower_idx"),
            models.Index(Lower("name"), name="stock_name_lower_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.symbol} - {self.name}"
