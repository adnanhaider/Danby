
from scrapy.spiders import SitemapSpider
from danby.items import Manual

import logging
logger = logging.getLogger(__name__)

class Danby(SitemapSpider):
    name = 'danby'
    sitemap_urls = [
        'https://www.danby.com/en-us/wp-sitemap-posts-product-1.xml',
        'https://www.danby.com/fr/wp-sitemap-posts-product-1.xml',
        'https://www.danby.com/wp-sitemap-posts-product-1.xml'
    ]
    sitemap_rules = [('/products/', 'parse')]

    def parse(self, response):
        pdfs = response.css('.product-download-link')
        for pdf in pdfs:
            manual = Manual()
            pdf_url = pdf.css('::attr(href)').get()
            if not pdf_url:
                continue
            type = pdf.css('.product-download-link-title::text').get()
            c_url = response.request.url
            lang = c_url.split('/')[3]
            brand = "Danby"
            product = response.css('.product-name::text').get()
            if product:
                product = product.replace(brand, '').strip()
            else:
                continue
            if 'en-uk' in lang or 'en-us' in lang or 'fr' in lang:
                parent_product  = c_url.split('/')[5].replace(lang, '').replace('-', ' ').title().strip()
                # parent_product, product = self.get_parent_and_product_names(parent_product, product, c_url)
                parent_product, product = self.get_parent_and_product_names(parent_product, product, c_url)
            else:
                parent_product  = c_url.split('/')[4].replace('-', ' ').title().strip()
                parent_product, product = self.get_parent_and_product_names(parent_product, product, c_url)
                lang = 'en'
            if not parent_product or not product:
                continue
            thumb = response.css('.taller::attr(src)').get()
            if not thumb:
                thumb = response.css('.slides:nth-child(2) img::attr(src)').get()
          
            model = response.css('.product-sku::text').get().strip()
            source = "danby.com"
            if(parent_product):
                if ' En Us' in parent_product:
                    manual['product_parent'] = parent_product.replace(' En Us', '')
                elif ' Fr' in parent_product:
                    manual['product_parent'] = parent_product.replace(' Fr', '')
                else:
                    manual['product_parent'] = parent_product
            else:
                manual["product_parent"] = 'No Category'
            manual["brand"] = brand
            manual["thumb"] = thumb
            manual["product"] = product.replace(parent_product, '').strip()

            if 'Danby' in model:
                manual["model"] = model.replace('Danby ', '')
            else:
                manual["model"] = model
            manual["source"] = source
            manual["file_urls"] = [pdf_url]
            manual["url"] = c_url
            manual["type"] = type.strip()
            if 'en' in lang:
                manual["product_lang"] = 'en'
            elif 'fr' in lang:
                manual["product_lang"] = 'fr'
            else:
                manual["product_lang"] = ''

            yield manual

    def get_parent_and_product_names(self, pp, p, c_url):
        en_parent_products = {
        'Refrigeration' : ['Apartment Size Refrigerators','Apartment Size Refrigerator', 'Compact Refrigerators',"Compact Refrigerator", 'Freezers', "Freezers", 'Health Medical and Clinical Fridges', "Health Medical and Clinical Fridge"],
        'Entertaining' : ['Beverage Centers','Beverage Center', 'Ice Makers', 'Ice Maker', 'Kegerators', 'Kegerator', 'Wine Coolers', 'Wine Cooler'], 
        'Climate Control' : ['Air Purifiers','Air Purifier', 'Dehumidifiers', 'Dehumidifier', 'Ductless Split Systems','Ductless Split System', 'Packaged Terminal Air Conditioners','Packaged Terminal Air Conditioner', 'Portable Air Conditioners','Portable Air Conditioner', 'Window Air Conditioners','Window Air Conditioner'],
        'Niche': ['Home Herb Grower', 'Parcel Mailbox', 'Specialty'],
        'Kitchen': ['Dishwashers','Dishwasher', 'Microwaves','Microwave', 'Ranges','Range', 'Toaster Ovens','Toaster Oven'],
        'Laundry': ['Accessories','Accessorie', 'Dryers','Dryer', 'Washing Machines','Washing Machine']
            }
        fr_parent_products = {
        'Divertissement': ['Divertissement', 'Refroidisseurs de boissons', 'Refroidisseurs de boisson', 'Refroidisseur de boisson', 'Machines à glaçons','Machine à glaçons', 'Machines à glaçon','Machine à glaçon', 'Rafraîchisseurs de fûts de bière', 'Rafraîchisseur de fûts de bière', 'Refroidisseurs à vin', 'Refroidisseur à vin'], 
        'Confort Au Foyer': ['Confort au foyer', 'Purificateurs d’air','Purificateur d’air', 'Systèmes De Séparation Sans Conduit', 'Système De Séparation Sans Conduit', 'Déshumidificateurs', 'Déshumidificateur', 'Climatiseurs portatifs', 'Climatiseur portatif','Climatiseurs de fenêtre', 'Climatiseur de fenêtre'], 
        'Cuisine': ['Cuisine','Lave-vaiselle', 'Fours à micro-ondes', 'Four à micro-ondes', 'Four à micro-onde', 'Cuisinières', 'Cuisinières', 'Fours Grille-pains', 'Four Grille-pains', 'Four Grille-pain'], 
        'Buanderie': ['Buanderie', 'Accessoires', 'Accessoire', 'Machines à laver le linge' , 'Machine à laver le linge', 'Sécheuses', 'Sécheuse'], 
        'Refrigeration': ['Réfrigération', 'Réfrigérateurs pour petites surfaces', 'Réfrigérateurs pour petites surface', 'Réfrigérateur pour petite surface', 'Réfrigérateur pour petites surface', 'Réfrigération Compact', 'Congélateurs', 'Congélateur', 'Danby Santé', 'Danby Santé'], 
        'Niche': ['Niche', 'Home Herb Grower', 'Colis Postal', 'Spécialité']}
        parent_product = ''
        product = ''
        foundPP = False
        if '/fr/' in c_url:
            for key_arr in list(fr_parent_products.keys()):
                if key_arr.lower().strip() == pp.lower().strip():
                    foundPP = True
                    parent_product = list(fr_parent_products.keys())[0]
                    for product_title in fr_parent_products[key_arr]:
                        if self.matchProducts(p,product_title):
                            product = product_title
            if not foundPP:
                for key_arr in list(fr_parent_products.keys()):
                    for product_title in fr_parent_products[key_arr]:
                        if pp.lower() == product_title.lower():
                            parent_product = list(fr_parent_products.keys())[0]
                            product = product_title
        else:
            for key_arr in list(en_parent_products.keys()):
                if key_arr.lower().strip() == pp.lower().strip():
                    foundPP = True
                    parent_product = key_arr
                    for product_title in en_parent_products[key_arr]:
                        if self.matchProducts(p,product_title):
                            product = product_title
            if not foundPP:
                for key_arr in list(en_parent_products.keys()):
                    for product_title in en_parent_products[key_arr]:
                        if pp.lower() == product_title.lower():
                            parent_product = key_arr
                            product = product_title

        return parent_product, product
    
    def matchProducts(self, p, product_title):
        parts_of_pro_title = product_title.strip().split(' ')
        count = 0
        for part in parts_of_pro_title:
            if part in p:
                count = count + 1
        if count == len(parts_of_pro_title):
            return True
        else:
            return False