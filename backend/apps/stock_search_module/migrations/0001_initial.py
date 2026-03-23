from django.db import migrations, models
import django.db.models.functions.text


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="StockReference",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("symbol", models.CharField(db_index=True, max_length=32, unique=True)),
                ("name", models.CharField(db_index=True, max_length=255)),
                ("exchange", models.CharField(blank=True, max_length=32)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["symbol"]},
        ),
        migrations.AddIndex(
            model_name="stockreference",
            index=models.Index(fields=["is_active", "symbol"], name="stock_active_symbol_idx"),
        ),
        migrations.AddIndex(
            model_name="stockreference",
            index=models.Index(fields=["is_active", "name"], name="stock_active_name_idx"),
        ),
        migrations.AddIndex(
            model_name="stockreference",
            index=models.Index(django.db.models.functions.text.Lower("symbol"), name="stock_symbol_lower_idx"),
        ),
        migrations.AddIndex(
            model_name="stockreference",
            index=models.Index(django.db.models.functions.text.Lower("name"), name="stock_name_lower_idx"),
        ),
    ]
