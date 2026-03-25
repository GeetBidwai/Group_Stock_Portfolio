from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("auth_module", "0004_passwordresetotp_failed_attempts"),
    ]

    operations = [
        migrations.CreateModel(
            name="TelegramLinkSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("token", models.CharField(db_index=True, max_length=128, unique=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("linked", "Linked"),
                            ("consumed", "Consumed"),
                            ("expired", "Expired"),
                        ],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("telegram_chat_id", models.CharField(blank=True, max_length=255)),
                ("telegram_username", models.CharField(blank=True, max_length=255)),
                ("telegram_user_id", models.BigIntegerField(blank=True, db_index=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("expires_at", models.DateTimeField()),
                ("linked_at", models.DateTimeField(blank=True, null=True)),
                ("consumed_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={"ordering": ("-created_at",)},
        ),
    ]
