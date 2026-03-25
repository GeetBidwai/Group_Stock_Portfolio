from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("auth_module", "0002_alter_user_options_alter_user_groups"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="mobile_number",
            field=models.CharField(blank=True, db_index=True, max_length=32),
        ),
    ]
