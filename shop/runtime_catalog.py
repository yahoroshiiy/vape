from types import SimpleNamespace
from .catalog_data import DATA, STORES

def fallback_categories():
    out=[]
    pid=1
    for name, slug, items in DATA:
        products=[]
        for i,item in enumerate(items):
            products.append(SimpleNamespace(
                id=pid, name=item["name"], subtitle=item["subtitle"], price=item["price"],
                image_url=item.get("image_url", ""), brand=item.get("brand", ""),
                official_url=item.get("official_url", ""), description=item.get("description", ""),
                specs="\n".join(item.get("specs", [])), featured=i<6, in_stock=True,
                category=SimpleNamespace(name=name, slug=slug)
            ))
            pid += 1
        out.append(SimpleNamespace(name=name, slug=slug, products=products))
    return out

def fallback_products():
    return [p for c in fallback_categories() for p in c.products]

def fallback_stores():
    return [SimpleNamespace(**s) for s in STORES]
