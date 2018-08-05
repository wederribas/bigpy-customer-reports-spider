# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader.processors import MapCompose


def strip_string(value):
    """Remove all blank spaces from the ends of a given value."""
    return value.strip()


class Report(scrapy.Item):

    """Instantiate the customer reports items fields, with its processors.

    Each field is an instance of scrapy.Field. Some fields will receive a
    input processor in order to peform parsing operations over this field
    before loading them into the item.

    """

    company_name = scrapy.Field(input_processor=MapCompose(strip_string))
    user_report = scrapy.Field(input_processor=MapCompose(strip_string))
    company_response = scrapy.Field(input_processor=MapCompose(strip_string))
    status = scrapy.Field(input_processor=MapCompose(strip_string))
    user_feedback = scrapy.Field(input_processor=MapCompose(strip_string))
    user_rating = scrapy.Field(input_processor=MapCompose(strip_string))
    date = scrapy.Field()
    location = scrapy.Field()
