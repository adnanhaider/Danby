import logging
import scrapy
import os
from scrapy import Spider
from danby.items import Manual

logger = logging.getLogger(__name__)


class Danby(Spider):
    name = "danby.com"
    start_urls = [
        "https://www.danby.com/en-us/",
        # "https://www.danby.com/en-uk/",
        # "https://www.danby.com/fr/"
    ]

    def parse(self, response):
        products_list = response.css('.products-list .product')

        for product in products_list:
            url = product.css('a::attr(href)').get()
            parent_product = product.css('.product-name-inner *::text').get()
            dictionary = { 'parent' : parent_product }
            yield scrapy.Request(url=url, callback=self.get_products, meta={'dic': dictionary})

    def get_products(self, response):        
        dictionary = response.meta.get('dic')
        print(response.request.url, '=============')
        urls = response.css('div.product-inner a::attr(href)').getall()
        print(urls, '----------------------------1111')
        
        for url in urls:
            print(url, '----------------------------0000000')

            yield scrapy.Request(url=url, callback=self.do_parse, meta={'dic': dictionary})



    def do_parse(self, response):
        dictionary = response.meta.get('dic')
        print(response.request.url, '-------------')
        return
        manual = Manual()
        uls = response.css('.manual-item ul')
        if len(uls) > 1:
            pdfs = uls[0].css('li a')
        else:
            pdfs = uls.css('li a')

        c_url = response.request.url
        lang = c_url.split('/')[3]

        if len(pdfs) == 0:
            return

        for pdf in pdfs:
            type = pdf.css('::text').get()

            doc_type = self.get_type(type)

            pdf = pdf.css('::attr(href)').get()
            if 'zip' == pdf.split('.')[-1]:
                continue
            if ' ' in pdf:
                pdf.replace(' ', '%20')
            for key, val in dictionary.items():
                if key == c_url:
                    thumb = val[0]
                    model = val[1]

            manual["product"] = 'No Category'
            manual["brand"] = 'Amazfit'
            manual["thumb"] = thumb
            if 'Amazfit' in model:
                manual["model"] = model.replace('Amazfit ', '')
            else:
                manual["model"] = model
            manual["source"] = self.name
            manual["file_urls"] = [pdf]
            manual["url"] = c_url
            manual["type"] = doc_type
            if 'en' in lang:
                manual["product_lang"] = lang
            else:
                manual["product_lang"] = ''
            yield manual

    def get_type(self, type):
        type = type.lower()
        if 'datasheet' in type:
            return "Datasheet"

        elif 'utility' in type and 'user' in type and 'guide' in type:
            return 'Utility User Guide'

        elif 'user' in type and 'guide' in type:
            return "User Guide"

        elif 'product' in type and 'introduction' in type:
            return "Product Introduction"

        elif 'quick' in type and 'installation' in type:
            return "Quick Installation Guide"

        elif 'guide' in type and 'installation' in type:
            return "Installation Guide"

        elif 'ce' in type and 'doc' in type:
            return 'CE DOC'
        elif 'qsg' in type:
            return 'Quickstart Guide'

        elif 'guide' in type:
            if '_' in type:
                type_pieces = type.split('_')
                for _type in type_pieces:
                    if 'guide' in _type:
                        return _type.title()
            else:
                return type.title()

        return "User Guide"
