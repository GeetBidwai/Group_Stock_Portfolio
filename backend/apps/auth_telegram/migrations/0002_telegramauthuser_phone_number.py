from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("auth_telegram", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="telegramauthuser",
            name="phone_number",
            field=models.CharField(blank=True, db_index=True, max_length=32),
        ),
    ]
