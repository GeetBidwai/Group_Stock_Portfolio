from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("portfolio_module", "0002_sector_portfoliotype_sector"),
    ]

    operations = [
        migrations.CreateModel(
            name="QualityStock",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("ai_rating", models.FloatField()),
                ("buy_signal", models.CharField(max_length=10)),
                ("report_json", models.JSONField()),
                ("graphs_data", models.JSONField(blank=True, null=True)),
                ("generated_at", models.DateTimeField(auto_now=True)),
                ("portfolio", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="quality_stocks", to="portfolio_module.portfoliotype")),
                ("stock", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="quality_reports", to="portfolio_module.portfoliostock")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="quality_stocks", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-generated_at", "-id"],
                "unique_together": {("portfolio", "stock")},
            },
        ),
    ]
