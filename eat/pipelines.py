# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class EatPipeline(object):
    def process_item(self, item, spider):
        return item


from scrapy.exporters import JsonItemExporter


class Utf8JsonItemExporter(JsonItemExporter):

    def __init__(self, file, **kwargs):
        super(Utf8JsonItemExporter, self).__init__(
            file, ensure_ascii=False, **kwargs)