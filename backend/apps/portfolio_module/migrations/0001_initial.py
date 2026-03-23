from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PortfolioType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="portfolio_types", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["name"], "unique_together": {("user", "name")}},
        ),
        migrations.CreateModel(
            name="PortfolioStock",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("symbol", models.CharField(max_length=24)),
                ("company_name", models.CharField(blank=True, max_length=255)),
                ("quantity", models.PositiveIntegerField(default=1)),
                ("average_buy_price", models.FloatField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("portfolio_type", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="stocks", to="portfolio_module.portfoliotype")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="portfolio_stocks", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["symbol"], "unique_together": {("user", "portfolio_type", "symbol")}},
        ),
    ]
