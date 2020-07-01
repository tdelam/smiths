from django.test import TestCase, Client
from django.core import urlresolvers
from django.contrib.auth import SESSION_KEY

from bigpond_store.catalog.models import Category, Product
from bigpond_store.catalog.forms import ProductAddToCartForm

from decimal import Decimal

import httplib

class NewUserTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # make sure they are not logged in before running new user tests
        logged_in = self.client.session.has_key(SESSION_KEY)
        self.assertFalse(logged_in)

    def test_delete_all(self):
        """
        Test deletion of products
        """
        for p in Product.objects.all():
            p.delete()
        self.assertEqual(Product.objects.all().count(), 0)

    def test_products_exist(self):
        """
        Test that products do exist
        """
        self.assertTrue(Product.objects.all().count() > 0)
        
    def test_view_homepage(self):
        home_url = urlresolvers.reverse('catalog_home')
        resp = self.client.get(home_url)
        self.failUnless(resp)
        self.assertEqual(resp.status_code, httplib.OK)
    
    def test_view_category(self):
        """
        Test category view loads
        """
        category = Category.active.all()[0]
        category_url = category.get_absolute_url()
        url_entry = urlresolvers.resolve(category_url)
        template_name = url_entry[2]['template_name']
        resp = self.client.get(category_url)
        self.failUnless(resp)
        self.assertEqual(resp.status_code, httplib.OK)
        self.assertTemplateUsed(resp, template_name)
        self.assertContains(resp, category.name)
        self.assertContains(resp, category.description)
    
    def test_view_product(self):
        """
        Test Product View loads
        """
        product = Product.active.all()[0]
        product_url = product.get_absolute_url()
        url_entry = urlresolvers.resolve(product_url)
        template_name = url_entry[2]['template_name']
        resp = self.client.get(product_url)
        self.failUnless(resp)
        self.assertEqual(resp.status_code, httplib.OK)
        self.assertTemplateUsed(resp, template_name)
        self.assertContains(resp, product.name)
        self.assertContains(resp, product.description_html)
        cart_form = resp.context[0]['form']
        self.failUnless(cart_form)
        self.failUnless(isinstance(cart_form, ProductAddToCartForm))

    def get_template_name_for_url(self, url):
        """
        Get template name kwarg for URL
        """
        url_entry = urlresolvers.resolve(url)
        return url_entry[2]['template_name']

class CatalogViewsTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, httplib.OK)
    
    def test_category(self):
        category_1 = Category.objects.create(
            name = 'Django Testing',
            slug = 'django-testing',
            description = 'Demo category for testing',
            meta_description = 'Meta data for the HTML'
        )
        resp = self.client.get('/category/django-testing/')
        self.assertEqual(resp.status_code, httplib.OK)
        self.assertTrue('category' in resp.context)
    
    def test_product(self):
        resp = self.client.get('/product/test-product/')
        self.assertEqual(resp.status_code, httplib.OK)

class ProductTestCase(TestCase):
    def setUp(self):
        self.product = Product.active.all()[0]
        self.product.price = Decimal('199.99')
        self.product.save()
        self.client = Client
        
    def test_sale_price(self):
        self.product.old_price = Decimal('220.00')
        self.product.save()
        self.failIfEqual(self.product.sale_price, None)
        self.assertEqual(self.product.sale_price, self.product.price)
    
    def test_no_sale_price(self):
        self.product.old_price = Decimal('0.00')
        self.product.save()
        self.failUnlessEqual(self.product.sale_price, None)