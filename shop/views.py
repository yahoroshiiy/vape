import logging
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db import OperationalError, ProgrammingError
from .models import Category, Product, Store
from .runtime_catalog import fallback_categories, fallback_products, fallback_stores

log = logging.getLogger(__name__)

IMAGE_BY_PRODUCT = {
    "OXVA XLIM PRO 2": "/static/shop/products/generated-1.jpg",
    "Geekvape Wenax Q2": "/static/shop/products/generated-2.jpg",
    "Vaporesso XROS Series Pod": "/static/shop/products/generated-3.jpg",
    "VooPoo Drag S2": "/static/shop/products/generated-4.jpg",
    "OXVA Xlim SQ Pro": "/static/shop/products/generated-5.jpg",
    "NOIR Salt 20mg": "/static/shop/products/generated-6.jpg",
}

def normalize_product_images(products):
    for p in products:
        image = IMAGE_BY_PRODUCT.get(getattr(p, "name", ""))
        if image:
            p.image_url = image
    return products


def db_catalog():
    try:
        categories=list(Category.objects.prefetch_related("products").all())
        products=list(Product.objects.select_related("category").filter(in_stock=True))
        allowed=set(IMAGE_BY_PRODUCT)
        products=[p for p in products if p.name in allowed]
        categories=[c for c in categories if any(getattr(p, "category_id", None) == c.id for p in products)]
        if categories and products:
            return categories, normalize_product_images(products), True
    except Exception as exc:
        log.warning("Database unavailable; using demo catalog: %s", exc)
    categories=fallback_categories()
    products=[p for c in categories for p in c.products if p.in_stock]
    return categories, normalize_product_images(products), False

def db_stores():
    try:
        stores=list(Store.objects.all())
        if stores:
            return stores, True
    except Exception as exc:
        log.warning("Database unavailable; using demo stores: %s", exc)
    return fallback_stores(), False

def home(request):
    categories, products, _ = db_catalog()
    stores, _ = db_stores()
    return render(request, "shop/home.html", {
        "featured": [p for p in products if p.featured][:6],
        "categories": categories, "stores": stores[:3],
    })

def catalog(request):
    cats, products, _ = db_catalog()
    cat = request.GET.get("category")
    q = (request.GET.get("q") or "").strip()
    if cat:
        products=[p for p in products if getattr(p.category, "slug", "") == cat]
    if q:
        products=[p for p in products if q.lower() in p.name.lower() or q.lower() in p.brand.lower()]
    return render(request, "shop/catalog.html", {"products": products, "categories": cats, "active": cat, "q": q})

def product(request, pk):
    try:
        item=Product.objects.select_related("category").get(pk=pk, in_stock=True)
        normalize_product_images([item])
    except Exception:
        item=next((p for p in fallback_products() if p.id == int(pk)), None)
        if item is not None:
            normalize_product_images([item])
    if item is None:
        from django.http import Http404
        raise Http404
    return render(request, "shop/product.html", {"product": item})

def stores(request):
    stores, _ = db_stores()
    return render(request, "shop/stores.html", {"stores": stores})

def api_catalog(request):
    categories, products, _ = db_catalog()
    payload=[]
    for c in categories:
        ps=[p for p in products if getattr(p.category, "slug", "") == c.slug]
        payload.append({"name":c.name,"slug":c.slug,"products":[{
            "id":p.id,"name":p.name,"brand":p.brand,"subtitle":p.subtitle,"price":p.price,
            "image_url":p.image_url,"description":p.description,"specs":p.specs.splitlines(),
            "official_url":p.official_url
        } for p in ps]})
    return JsonResponse({"categories":payload})

def api_stores(request):
    stores, _ = db_stores()
    return JsonResponse({"stores":[{"name":s.name,"address":s.address,"hours":s.hours,"phone":s.phone,"distance":s.distance} for s in stores]})
