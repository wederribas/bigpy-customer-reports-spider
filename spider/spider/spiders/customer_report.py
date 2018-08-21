# -*- coding: utf-8 -*-

import scrapy
from scrapy.loader import ItemLoader
from scrapy.exceptions import CloseSpider
from spider.items import Report


class CustomerReports(scrapy.Spider):

    """Spider that retrieves raw customer reports about companies.

    This spider reaches the consumidor.gov.br website to crawl the data
    from the customer raw reports page. The specific page containing
    this information is composed by a hidden form that is submitted to
    retrieve the reports. For this reason, this spider reaches the
    initial page and then trigger the form submission to obtain the
    data. The website returns 10 values per call.

    Attributes
    ----------
    name : str
        the spider name used by Scrapy to start the spider
    allowed_domains : list
        contains the list of domains that the spider is allowed to crawl
    start_urls : list
        URLs where the spider should start the crawl from

    Methods
    -------
    parse(self, response)
        The default Scrapy method to parse the crawled data. In this
        case, gets the main page data and triggers the hidden form.
    parse_response(self, response)
        A callback for `parse` method that handles the crawled form.
        This method will select the required nodes and loads the scrapy
        items that were defined in the Report items object.
    """

    name = 'reports'
    allowed_domains = ['consumidor.gov.br']
    start_urls = [
        'https://www.consumidor.gov.br/pages/indicador/relatos/abrir'
    ]

    def parse(self, response):
        """Trigger the hidden form POST to get the customer report.

        The goal is to get the first million reports. Each request
        is limited by the endpoint to retrieve ten requests at a time.
        """

        total_reports = 1000000
        reports_per_request = 10

        for first_result in range(0, total_reports, reports_per_request):
            yield scrapy.FormRequest(
                url="https://consumidor.gov.br/pages/indicador/relatos/consultar",
                callback=self.parse_response,
                formdata={"indicePrimeiroResultado": str(first_result),
                          "palavrasChave": ""},
            )

    def parse_response(self, response):
        """Parses the response data, crawling the required fields and loading
        the Item to populate the final data set."""

        index = 0
        report_card_path = '//div[contains(@class,"cartao-relato")]'

        if response.xpath(report_card_path).extract_first() is None:
            raise CloseSpider(reason='No more items left to crawl')

        for crawled_report in response.xpath(report_card_path):
            try:
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
                    '/span[descendant::i[contains(@class,"glyphicon")]]'
                    '/text()').extract()
                user_date_location = [
                    item for item in user_date_location if item != ' ']

                # Date and location are stored in the same element.
                date, location = user_date_location[index].split(',')
                city, state = location.split(' - ')

                loader.add_value('date', date)
                loader.add_value('city', city)
                loader.add_value('state', state)

                index += 1

                yield loader.load_item()

            except IndexError:
                # Whenever an Index Error is raised, it means that the current
                # report is missing some of the required data. In this case,
                # ignore it by jumping to the next report.
                continue
