
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
            if 'en-uk' in lang or 'en-us' in lang or 'fr' in lang:
                product  = c_url.split('/')[5].replace(lang, '').replace('-', ' ').title().strip()
            else:
                product  = c_url.split('/')[4].replace('-', ' ').title().strip()
                lang = 'en'
            thumb = response.css('.taller::attr(src)').get()
            if not thumb:
                thumb = response.css('.slides:nth-child(2) img::attr(src)').get()
            model = response.css('.product-name::text').get()
            brand = "Danby"
            source = "danby.com"
            if(product):
                if ' En Us' in product:
                    manual['product'] = product.replace(' En Us', '')
                elif ' Fr' in product:
                    manual['product'] = product.replace(' Fr', '')
                else:
                    manual['product'] = product
            else:
                manual["product"] = 'No Category'
            manual["brand"] = brand
            manual["thumb"] = thumb
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
            else:
                manual["product_lang"] = ''

            yield manual


         