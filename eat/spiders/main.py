import scrapy
from ..items import EatItem
import json


class Main(scrapy.Spider):
    name = 'main'
    allowed_domains = ['eda.ru']
    start_urls = ['https://eda.ru/recepty']

    def parse(self, response):
        # categories = response.xpath('//input[@id="categoryItemsSuggest"]/following-sibling::ul/li')
        # categories = list(map(lambda i: {i.xpath('@data-select-suggest-value').extract_first(): i.xpath('text()').extract_first().strip()}, categories))
        # categories = list(filter(None, [{k: v for k, v in category.items() if k != 'all'} for category in categories]))
        # response.meta['all_categories'] = categories
        #
        # subcategories = response.xpath('//input[@id="subCategoryItemsSuggest"]/following-sibling::ul/li')
        # subcategories = list(map(lambda i: {i.xpath('@data-select-suggest-value').extract_first(): i.xpath('text()').extract_first().strip()}, subcategories))
        # subcategories = list(filter(None, [{k: v for k, v in category.items() if k != 'all'} for category in subcategories]))
        # response.meta['all_subcategories'] = subcategories
        #
        # urls = [self.start_urls[0] + '/' + list(sub.keys())[0] for sub in subcategories]
        #
        # for url in urls:
        #     yield scrapy.Request(
        #         url=url,
        #         meta=response.meta,
        #         callback=self.parse_sub,
        #     )
        categories = response.xpath('//a[contains(@id, "link-recipecatalog-filterTag")]/span[@class="name"]/text()').extract()
        urls = response.xpath('//a[contains(@id, "link-recipecatalog-filterTag")]/@href').extract()
        urls = list(map(lambda i: 'https:' + i, urls))
        categories = list(map(lambda i: i.replace('\xa0', ' '), categories))

        for url, category in zip(urls, categories):
            yield scrapy.Request(
                url=url,
                callback=self.mobile_parse_category,
                meta={'category': category}
            )

    def mobile_parse_category(self, response):

        subcategories = list(map(lambda i: i.strip(), response.xpath('//h4[contains(text(), "Популярные рецепты")]/following-sibling::a/text()').extract()))
        urls = response.xpath('//h4[contains(text(), "Популярные рецепты")]/following-sibling::a/@href').extract()
        for url, subcategory in zip(urls, subcategories):
            response.meta['subcategory'] = subcategory
            yield scrapy.Request(
                url='https://eda.ru' + url,
                callback=self.mobile_parse_subcategory,
                meta=response.meta
            )

    def mobile_parse_subcategory(self, response):
        for url in response.xpath('//h3/a/@href').extract():
            yield scrapy.Request(
                url='https://eda.ru' + url,
                meta=response.meta,
                callback=self.mobile_parse_recept
            )

        next_page = response.xpath('//span[text()="Загрузить еще"]')

        if next_page:
            page = 2
            response.meta['page'] = page
            response.meta['a'] = response.url.split('/')[-1]
            yield scrapy.FormRequest(
                url='https://eda.ru' + '/RecipesCatalog/GetNextRecipes/' + response.url.split('/')[-1],
                formdata={'page': str(page)},
                body='page=%s' % str(page),
                callback=self.mobile_parse_subcategory_api,
                meta=response.meta
            )

    def mobile_parse_subcategory_api(self, response):
        page = response.meta['page']
        resp = json.loads(response.text)
        more = resp.get('HasMore')
        html = resp.get('Html')

        html = scrapy.Selector(text=html)
        for url in html.xpath('//div[@class="recipe-item g-middle-wrap "]/a/@href').extract():
            yield scrapy.Request(
                url='https://eda.ru' + url,
                callback=self.mobile_parse_recept,
                meta=response.meta
            )
        if more:
            next_page = int(page) + 1
            response.meta['page'] = next_page
            yield scrapy.FormRequest(
                url='https://eda.ru' + '/RecipesCatalog/GetNextRecipes/' + response.meta['a'],
                formdata={'page': str(next_page)},
                body='page=%s' % str(next_page),
                callback=self.mobile_parse_subcategory_api,
                meta=response.meta,
                dont_filter=True
            )

    def mobile_parse_recept(self, response):
        item = EatItem()
        item['name'] = response.xpath('//h1/text()').extract_first(default='').replace('\xa0', ' ')
        item['category'] = response.meta['category']
        item['subcategory'] = response.meta['subcategory']
        item['calories'] = response.xpath('//span[text()="Калорийность"]/following-sibling::span/text()').extract_first(default='').replace(' ккал', '')
        item['proteins'] = response.xpath('//span[text()="Белки"]/following-sibling::span/text()').extract_first(default='').replace(' грамм', '')
        item['fats'] = response.xpath('//span[text()="Жиры"]/following-sibling::span/text()').extract_first(default='').replace(' грамм', '')
        item['carbohydrates'] = response.xpath('//span[text()="Углеводы"]/following-sibling::span/text()').extract_first(default='').replace(' грамм', '')
        ingredients = response.xpath('//ul[@class="ingredients-list"]/li/@data-ingredient-object').extract()
        item['ingredients'] = list(map(lambda i: {'name': i.split('name": "')[1].split('",')[0], 'amount': i.split('amount": "')[1].split('"')[0]}, ingredients))
        co = response.xpath('//div[@class="b-select__trigger"]/text()').extract_first(default='').split()
        item['portionsCount'] = co[0] if co else ''
        item['cookingTime'] = response.xpath('//div[@class="cooking-time"]/text()').extract_first(default='')
        item['link'] = response.url
        item['tags'] = response.xpath('//div[@class="b-breadcrumbs"]/a/text()').extract()
        images = response.xpath('//div[@class="b-photo-gall__trigger s-photo-gall__trigger"]/@data-gall-photos-urls').extract_first(default='').split(',')
        item['imagesLinks'] = list(map(lambda i: 'https:' + i[1:-1], images))
        yield item

    def parse_sub(self, response):
        category = response.xpath('//div[@class="group-header__pad"]//ul[@class="breadcrumbs"]//a/text()').extract()[1]
        response.meta['category'] = category
        urls = response.xpath('//div[@class="js-updated-page__content js-load-more-content"]//div[@class="tile-list__horizontal-tile horizontal-tile js-portions-count-parent js-bookmark__obj"]//div[@class="horizontal-tile__item-link js-click-link "]/@data-href').extract()
        for url in urls:
            yield scrapy.Request(
                url=response.urljoin(url),
                meta=response.meta,
                callback=self.parse_recept
            )

        next_page = response.xpath('//div[text()="Показать еще" and @style=""]/@href').extract_first()
        if next_page:
            if next_page.split('/')[-1].split('?')[0] == 'pirogi' and int(next_page.split('=')[1]) >= 132:
                pass
            if next_page.split('/')[-1].split('?')[0] == 'gorjachie-zakuski' and int(next_page.split('=')[1]) >= 136:
                pass
            else:
                yield scrapy.Request(
                    url=next_page,
                    meta=response.meta,
                    callback=self.parse_sub
                )

    def parse_recept(self, response):
        item = EatItem()
        item['name'] = response.xpath('//h1/text()').extract_first(default='').strip().replace('\xa0', ' ')
        item['category'] = response.meta['category']
        subcategory = str(response.request.headers.get('Referer', None)).split('/')[-1].replace("'", '').split('?')[0]
        subcategory = list(filter(None, [sub.get(subcategory) for sub in response.meta['all_subcategories']]))[0]
        item['subcategory'] = subcategory
        item['calories'] = response.xpath('//p[text()="Калорийность"]/following-sibling::p/text()').extract_first(default='')
        item['proteins'] = response.xpath('//p[text()="Белки"]/following-sibling::p/text()').extract_first(default='')
        item['fats'] = response.xpath('//p[text()="Жиры"]/following-sibling::p/text()').extract_first(default='')
        item['carbohydrates'] = response.xpath('//p[text()="Углеводы"]/following-sibling::p/text()').extract_first(default='')
        ingredients = response.xpath('//div[@class="ingredients-list__content"]').extract_first(default='')
        ingredients = scrapy.Selector(text=ingredients)
        ingredients = ingredients.xpath('//p/@data-ingredient-object').extract()
        ingredients = list(map(lambda i: {'name': i.split('name": "')[1].split('",')[0], 'amount': i.split('amount": "')[1].split('"')[0]}, ingredients))
        item['ingredients'] = ingredients
        item['portionsCount'] = response.xpath('//input[@class="portions-control__count g-h6 js-portions-count js-tooltip"]/@value').extract_first(default='')
        item['cookingTime'] = response.xpath('//span[@class="info-text"]/text()').extract_first(default='')
        item['link'] = response.url
        item['tags'] = response.xpath('//div[@class="recipe__title"]/ul[@class="breadcrumbs"]/li/a/text()').extract()
        images = response.xpath('//div[@class="photo-list-preview js-preview-item js-show-gallery trigger-gallery"]/img/@src').extract()
        item['imagesLinks'] = list(map(lambda i: 'https://' + i.split('/', 5)[-1], images))
        yield item
