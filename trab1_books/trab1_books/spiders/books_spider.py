import scrapy


class QuotesSpider(scrapy.Spider):
    name = "books_cultura"
    counter_pages = 0
    start_urls = [
        'https://www3.livrariacultura.com.br/livros'
    ]
        
    def parse(self, response):
        nav_menu = response.xpath('/html/body/section[5]/div/div/aside/div[2]/div[1]/div/div/div[3]')
        categories = nav_menu.css('h4>a::attr("href")').getall()
        for category in categories:
            counter_pages = 0
            yield scrapy.Request(url = category, callback = self.parse_category)

    def parse_category(self,response):
        books = response.css(".prateleiraProduto__foto")
        category = response.css(".titulo-sessao::text").get()
        for book in books:
            link_book = book.css('a::attr("href")').get()
            yield scrapy.Request(url = link_book, callback = self.parse_book, cb_kwargs={'category': category})
        # counter_pages += 1

    def parse_book(self,response,category):
        if response.css(".skuBestPrice::text").get():
            details = response.xpath('/html/body/section[5]/div/div/div/div')
            headers = details.css("th::text").getall()
            values = details.css("td::text").getall()
            book_info = {}
            for i,header in enumerate(headers):
                book_info[header] = values[i]

            preco = response.css(".skuBestPrice::text").get().replace("R$","").replace(",",".").strip()
            book_info['preço'] = preco
            nome = response.css(".title_product>div::text").get()
            book_info['nome'] = nome
            book_info['categoria'] = category
            yield book_info