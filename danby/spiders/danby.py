
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
        
        dictionary = {}
        divs = response.css('.container ul.nav  .menu-item.menu-item-has-children')
        for div in divs:
            arr = []
            name = div.css('.menu-item-text::text').get()

            for sub_menu_item in div.css('.sub-menu .menu-item-text'):
                product = sub_menu_item.css('::text').get()
                arr.append(product)
            dictionary[name] = arr
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
                parent_product, product = self.get_parent_and_product_names(parent_product, product, dictionary)
            else:
                parent_product  = c_url.split('/')[4].replace('-', ' ').title().strip()
                parent_product, product = self.get_parent_and_product_names(parent_product, product, dictionary)
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

    def get_parent_and_product_names(self, pp, p, dictionary):
        parent_product = ''
        product = ''
        foundPP = False
        for key_arr in list(dictionary.keys()):
            if key_arr.lower().strip() == pp.lower().strip():
                foundPP = True
                parent_product = key_arr
                for product_title in dictionary[key_arr]:
                    if self.matchProducts(p,product_title):
                        product = product_title
        
        return parent_product, product
    
    def matchProducts(self, p, product_title):
        parts_of_pro_title = product_title.strip().split(' ')
        count = 0
        for part in parts_of_pro_title:
            # if part in p:
            if self.matchSingularOrPluralOfPart(part, p):
                count = count + 1
        if count == len(parts_of_pro_title):
            return True
        else:
            return False
    def matchSingularOrPluralOfPart(self, part, p):
        part = part.lower()
        p = p.lower()
        if(part[:-1] in p or part[:-2] in p or p[:-1] in part or p[:-2] in part or part in p):
            return True
        return False