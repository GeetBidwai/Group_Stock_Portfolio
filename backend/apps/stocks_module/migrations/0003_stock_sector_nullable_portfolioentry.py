from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("stocks_module", "0002_seed_catalog"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="stock",
            name="sector",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="stocks", to="stocks_module.sector"),
        ),
        migrations.CreateModel(
            name="PortfolioEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("added_at", models.DateTimeField(auto_now_add=True)),
                ("sector", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="portfolio_entries", to="stocks_module.sector")),
                ("stock", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="portfolio_entries", to="stocks_module.stock")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="stock_portfolio_entries", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["sector__name", "stock__symbol"],
                "unique_together": {("user", "stock")},
            },
        ),
    ]
