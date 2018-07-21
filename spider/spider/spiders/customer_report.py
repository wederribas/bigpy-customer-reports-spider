import scrapy


class CustomerReports(scrapy.Spider):
    name = 'reports'
    start_urls = [
        'https://www.consumidor.gov.br/pages/indicador/relatos/abrir'
    ]

    def parse(self, response):
        return scrapy.FormRequest(
            url="https://consumidor.gov.br/pages/indicador/relatos/consultar",
            callback=self.after_fetch,
            formdata={"indicePrimeiroResultado": "0", "palavrasChave": ""},
        )

    def after_fetch(self, response):
        for report in response.css('div.cartao-relato'):
            # Generate index from own element counter
            index = report.css(
                'h5.relatos-contador::text').extract_first()
            index = int(index) - 1

            company_name = report.css(
                'h3.relatos-nome-empresa a::text').extract_first()
            users_report = report.xpath(
                '//div[strong="Relato"]/p/text()').extract()
            user_report = users_report[index]
            report_status = report.css(
                'h4.relatos-status::text').extract_first()

            user_date_location = report.xpath(
                '//div[strong="Relato"]'
                '/span[descendant::i[@class="glyphicon glyphicon-calendar"]]')
            user_date_location = user_date_location.css(
                'span::text').extract()
            user_date_location = [
                item for item in user_date_location if item != ' ']
            date, location = user_date_location[index].split(',')

            yield {
                "companyName": company_name.strip(),
                "userReport": user_report.strip(),
                "status": report_status.strip(),
                "date": date,
                "location": location
            }
