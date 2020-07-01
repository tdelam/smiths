### Smiths Market Web site

I will update this document with a requirements, how-to install, version information, and some fixture docs in the future. This is just
a placeholder for now.

- American Express Test Card: 370000000000002
- Discover Test Card: 6011000000000012
- Visa Test Card: 4007000000027
- Second Visa Test Card: 4012888818888
- JCB: 3088000000000017
- Diners Club/ Carte Blanche: 38000000000006

https://test.authorize.net/
tdelamor1
eemc2feC


## Interesting:

>>> from smiths.search import search
>>> from django.db import connection
>>> connection.queries
[]
>>> search.products('news big')
{'products': [<Product: Big Pond News Release>]}
>>> len(connection.queries)
1
>>> connection.queries
[{'time': '0.001', 'sql': u'SELECT "catalog_product"."id", "catalog_product"."name", "catalog_product"."slug", "catalog_product"."price", "catalog_product"."old_price", "catalog_product"."image", "catalog_product"."is_active", "catalog_product"."is_featured", "catalog_product"."quantity", "catalog_product"."description", "catalog_product"."description_html", "catalog_product"."meta_description", "catalog_product"."created_at", "catalog_product"."updated_at" FROM "catalog_product" WHERE ("catalog_product"."is_active" = True  AND ("catalog_product"."name" LIKE %news% ESCAPE \'\\\'  OR "catalog_product"."description" LIKE %news% ESCAPE \'\\\'  OR "catalog_product"."meta_description" LIKE %news% ESCAPE \'\\\' ) AND ("catalog_product"."name" LIKE %big% ESCAPE \'\\\'  OR "catalog_product"."description" LIKE %big% ESCAPE \'\\\'  OR "catalog_product"."meta_description" LIKE %big% ESCAPE \'\\\' )) ORDER BY "catalog_product"."created_at" DESC LIMIT 21'}]
>>>
