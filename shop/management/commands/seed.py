from django.core.management.base import BaseCommand
from shop.models import Category, Product, Store
from shop.catalog_data import DATA, STORES

class Command(BaseCommand):
    help = "Создаёт демонстрационный каталог устройств и аксессуаров."

    def handle(self, *args, **kwargs):
        for cat_name, slug, items in DATA:
            c, _ = Category.objects.get_or_create(slug=slug, defaults={"name": cat_name})
            for i, item in enumerate(items):
                Product.objects.update_or_create(
                    name=item["name"],
                    defaults={
                        "category": c, "brand": item["brand"], "subtitle": item["subtitle"],
                        "price": item["price"], "official_url": item["official_url"],
                        "description": item["description"], "specs": "\n".join(item["specs"]),
                        "in_stock": True, "featured": i < 6, "image_url": item.get("image_url", ""),
                    },
                )
        for s in STORES:
            Store.objects.update_or_create(name=s["name"], defaults=s)
        self.stdout.write(self.style.SUCCESS("Demo catalog created."))
