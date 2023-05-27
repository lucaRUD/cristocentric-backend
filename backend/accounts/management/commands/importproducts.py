from django.core.management.base import BaseCommand
import requests
from accounts.models import Product

def import_products():
    skus = ['A-MH-JH001', 'A-MT-3413', 'A-WT-6004']
    headers = {'X-API-Key': 'test_197d4ae4-7f06-4c01-8ad8-601cb4e78512'}
    for sku in skus:
        response = requests.get(f'https://api.sandbox.prodigi.com/v4.0/products/{sku}', headers=headers)
        print(response.status_code)
        
        data = response.json()
        product = Product(
            sku=data['product']['sku'],
            description=data['product']['description'],
            colors=data['product']['attributes']['color'],
            sizes=data['product']['attributes']['size'],
            price=99.99,
            image='https://example.com/image.png',
        )
        product.save()


class Command(BaseCommand):
    help = 'Import products from Prodigi API'

    def handle(self, *args, **options):
        import_products()
        self.stdout.write(self.style.SUCCESS('Successfully imported products'))
