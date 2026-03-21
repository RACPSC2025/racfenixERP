import os
import django
import csv
import random
import uuid

# Setup django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.base')
django.setup()

from apps.products.models import Category, Product

def parse_price(price_str):
    try:
        # e.g., "₹32,999"
        clean = ''.join(c for c in price_str if c.isdigit() or c == '.')
        return float(clean) if clean else 0.0
    except Exception:
        return 0.0

def load_data():
    file_path = os.path.join('datasets', 'Air Conditioners.csv')
    
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        count = 0
        for row in reader:
            if count >= 30: # Just load a small inventory
                break
            
            cat_name = row.get('sub_category', 'General').strip()
            cat, created = Category.objects.get_or_create(name=cat_name[:100])
            
            name = row.get('name', '')[:200]
            if not name:
                continue
                
            image_url = row.get('image', '')[:1000]
            price = parse_price(row.get('discount_price', ''))
            
            # If default price is 0, use actual price or 100
            if price == 0:
                price = parse_price(row.get('actual_price', ''))
            if price == 0:
                price = random.randint(100, 500)
                
            cost = price * 0.7 # Simulate cost
            
            sku = str(uuid.uuid4())[:12].upper()
            
            # Avoid duplicate SKUs or Names
            if Product.objects.filter(name=name).exists():
                count += 1
                continue
                
            Product.objects.create(
                name=name,
                category=cat,
                price=price,
                cost=cost,
                stock=random.randint(10, 100),
                image_url=image_url,
                sku=sku
            )
            count += 1
            
        print(f"✅ Se cargaron {count} productos exitosamente.")

if __name__ == '__main__':
    load_data()
