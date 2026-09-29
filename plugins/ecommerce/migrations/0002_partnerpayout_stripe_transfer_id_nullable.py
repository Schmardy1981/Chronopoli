from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chronopoli_ecommerce", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="partnerpayout",
            name="stripe_transfer_id",
            field=models.CharField(blank=True, default=None, max_length=100, null=True, unique=True),
        ),
    ]
