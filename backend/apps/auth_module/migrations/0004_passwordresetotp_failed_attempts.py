from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("auth_module", "0003_userprofile_mobile_number"),
    ]

    operations = [
        migrations.AddField(
            model_name="passwordresetotp",
            name="failed_attempts",
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
