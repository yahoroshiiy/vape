from django.db import migrations, models
import django.db.models.deletion
class Migration(migrations.Migration):
    initial=True
    dependencies=[]
    operations=[
        migrations.CreateModel(name="Category",fields=[
            ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
            ("name",models.CharField(max_length=80)),("slug",models.SlugField(unique=True))]),
        migrations.CreateModel(name="Store",fields=[
            ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
            ("name",models.CharField(max_length=120)),("address",models.CharField(max_length=220)),
            ("hours",models.CharField(default="10:00 — 22:00",max_length=120)),
            ("phone",models.CharField(blank=True,max_length=40)),("distance",models.CharField(blank=True,max_length=40))]),
        migrations.CreateModel(name="Product",fields=[
            ("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),
            ("name",models.CharField(max_length=180)),("subtitle",models.CharField(blank=True,max_length=220)),
            ("price",models.PositiveIntegerField()),("image_url",models.URLField(blank=True)),
            ("description",models.TextField(blank=True)),("specs",models.TextField(blank=True,help_text="Каждая характеристика с новой строки")),
            ("in_stock",models.BooleanField(default=True)),("featured",models.BooleanField(default=False)),
            ("category",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name="products",to="shop.category"))]),
    ]
