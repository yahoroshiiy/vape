from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("shop", "0001_initial")]
    operations = [
        migrations.AddField(
            model_name="product",
            name="brand",
            field=models.CharField(max_length=80, blank=True),
        ),
        migrations.AddField(
            model_name="product",
            name="official_url",
            field=models.URLField(blank=True),
        ),
    ]
