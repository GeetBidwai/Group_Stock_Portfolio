from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("stock_search_module", "0002_stockreference_sector"),
    ]

    operations = [
        migrations.AddField(
            model_name="stockreference",
            name="risk_category",
            field=models.CharField(blank=True, db_index=True, max_length=32, null=True),
        ),
    ]
