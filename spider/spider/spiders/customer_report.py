# -*- coding: utf-8 -*-

import scrapy
from scrapy.loader import ItemLoader
from spider.items import Report


class CustomerReports(scrapy.Spider):

    """Spider that retrieves raw customer reports about companies.

    This spider reaches the consumidor.gov.br website to crawl the data from
    the customer raw reports page. The specific page containing this information
    is composed by a hidden form that is submitted to retrieve the reports.
    For this reason, this spider reaches the initial page and then trigger the
    form submission to obtain the data. The website returns 10 values per call.

    The default Scrapy `parse` method will perform the form submission.

    The `parse_response` method is a callback for `parse` and will crawl the
    required data from the website response, loading the scrapy items.
    """

    name = 'reports'
    start_urls = [
        'https://www.consumidor.gov.br/pages/indicador/relatos/abrir'
    ]

    def parse(self, response):
        """Trigger the hidden form POST to get the customer report."""

        return scrapy.FormRequest(
            url="https://consumidor.gov.br/pages/indicador/relatos/consultar",
            callback=self.parse_response,
            formdata={"indicePrimeiroResultado": "0", "palavrasChave": ""},
        )

    def parse_response(self, response):
        """Parses the response data, crawling the required fields and loading
        the Item to populate the final data set."""

        index = 0
        report_card_path = '//div[contains(@class,"cartao-relato")]'

        for crawled_report in response.xpath(report_card_path):
            # Loader responsible to process input and populate an item
            loader = ItemLoader(item=Report(), response=response)

            loader.add_value(
                'company_name',
                crawled_report.xpath(
                    '//*[@class="relatos-nome-empresa"]/a/text()').extract_first()
            )

            users_report = crawled_report.xpath(
                '//div[strong="Relato"]/p/text()').extract()
            loader.add_value('user_report', users_report[index])

            company_response = crawled_report.xpath(
                '//div[strong="Resposta"]/p/text()').extract()
            loader.add_value(
                'company_response',
                company_response[index]
            )

            loader.add_value(
                'status',
                crawled_report.xpath(
                    '//h4[@class="relatos-status"]/text()').extract_first()
            )

            users_feedback = crawled_report.xpath(
                '//div[strong="Avaliação"]/p[2]/text()').extract()
            loader.add_value('user_feedback', users_feedback[index])

            users_rating = crawled_report.xpath(
                '//div[strong="Avaliação"]/p[1]/text()').extract()
            loader.add_value('user_rating', users_rating[index])

            user_date_location = crawled_report.xpath(
                '//div[strong="Relato"]'
                '/span[descendant::i[@class="glyphicon glyphicon-calendar"]]'
                '/text()').extract()
            user_date_location = [
                item for item in user_date_location if item != ' ']

            # Date and location are stored in the same element. Need to split.
            date, location = user_date_location[index].split(',')
            loader.add_value('date', date)
            loader.add_value('location', location)

            index += 1

            yield loader.load_item()
