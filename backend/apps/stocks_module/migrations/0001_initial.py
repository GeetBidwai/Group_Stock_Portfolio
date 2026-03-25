from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Market",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(db_index=True, max_length=12, unique=True)),
                ("name", models.CharField(max_length=120)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Sector",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=48)),
                ("name", models.CharField(max_length=120)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("market", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="sectors", to="stocks_module.market")),
            ],
            options={"ordering": ["name"], "unique_together": {("market", "code")}},
        ),
        migrations.CreateModel(
            name="Stock",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("symbol", models.CharField(db_index=True, max_length=24)),
                ("name", models.CharField(max_length=255)),
                ("exchange", models.CharField(blank=True, max_length=24)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("sector", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="stocks", to="stocks_module.sector")),
            ],
            options={"ordering": ["symbol"], "unique_together": {("sector", "symbol")}},
        ),
    ]

