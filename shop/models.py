from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=80)
    slug = models.SlugField(unique=True)
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
    def __str__(self): return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=180)
    subtitle = models.CharField(max_length=220, blank=True)
    price = models.PositiveIntegerField()
    image_url = models.URLField(blank=True)
    brand = models.CharField(max_length=80, blank=True)
    official_url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    specs = models.TextField(blank=True, help_text="Каждая характеристика с новой строки")
    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    class Meta:
        ordering = ["-featured", "name"]
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
    def __str__(self): return self.name

class Store(models.Model):
    name = models.CharField(max_length=120)
    address = models.CharField(max_length=220)
    hours = models.CharField(max_length=120, default="10:00 — 22:00")
    phone = models.CharField(max_length=40, blank=True)
    distance = models.CharField(max_length=40, blank=True)
    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "Магазины"
    def __str__(self): return self.name
