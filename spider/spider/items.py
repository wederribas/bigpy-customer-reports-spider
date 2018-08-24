# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
from scrapy.loader.processors import MapCompose


def strip_string(value):
    """Remove all blank spaces from the ends of a given value."""
    return value.strip()


def parse_date(date):
    """Parse date string to date epoch in millisecons."""
    date_obj = datetime.strptime(date, "%d/%m/%Y")
    return date_obj.timestamp() * 1000


def parse_to_int(string):
    """Remove all non-digit chars from string and parse it to integer."""
    parsed_string = list(filter(lambda x: x.isdigit(), string))
    return int(parsed_string[0])


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
    user_rating = scrapy.Field(input_processor=MapCompose(parse_to_int))
    date = scrapy.Field(input_processor=MapCompose(parse_date))
    city = scrapy.Field(input_processor=MapCompose(strip_string))
    state = scrapy.Field(input_processor=MapCompose(strip_string))
