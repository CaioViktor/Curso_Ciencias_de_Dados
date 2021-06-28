import scrapy


class QuotesSpider(scrapy.Spider):
    name = "books_cultura"
    start_urls = [
        'https://www3.livrariacultura.com.br/livros'
    ]
        
    def parse(self, response):
        nav_menu = response.xpath('/html/body/section[5]/div/div/aside/div[2]/div[1]/div/div/div[3]')
        categories = nav_menu.css('h4>a::attr("href")').getall()
        for category in categories:
            yield scrapy.Request(url = category, callback = self.parse_category)

    def parse_category(self,response):
        category = response.css(".titulo-sessao::text").get()
        books = response.css(".prateleiraProduto__foto")
        for book in books:
            link_book = book.css('a::attr("href")').get()
            yield scrapy.Request(url = link_book, callback = self.parse_book, cb_kwargs={'category': category})
        # Crawler pages
        pattern = r"\/buscapagina.*="
        next_page = 2
        scripts = response.css('.vitrine.resultItemsWrapper')
        script_text = scripts.css("script::text")[0]
        base_url = 'http://www3.livrariacultura.com.br/' + script_text.re_first(pattern) 
        next_url = base_url + str(next_page)
        yield scrapy.Request(url = next_url, callback = self.parse_next_page, cb_kwargs={'category': category,'base_url':base_url,'next_page':next_page})

    def parse_next_page(self,response,category,base_url,next_page):
        next_page += 1
        books = response.css(".prateleiraProduto__foto")
        if len(books) > 0 and next_page <= 10:
            for book in books:
                link_book = book.css('a::attr("href")').get()
                yield scrapy.Request(url = link_book, callback = self.parse_book, cb_kwargs={'category': category})
            next_url = base_url + str(next_page)
            yield scrapy.Request(url = next_url, callback = self.parse_next_page, cb_kwargs={'category': category,'base_url':base_url,'next_page':next_page})

    def parse_book(self,response,category):
        if response.css(".skuBestPrice::text").get():
            details = response.xpath('/html/body/section[5]/div/div/div/div')
            headers = details.css("th::text").getall()
            values = details.css("td::text").getall()
            book_info = {}
            for i,header in enumerate(headers):
                book_info[header] = values[i]

            preco = response.css(".skuBestPrice::text").get().replace("R$","").replace(".","").replace(",",".").strip()
            book_info['preço'] = float(preco)
            nome = response.css(".title_product>div::text").get()
            book_info['nome'] = nome
            book_info['categoria'] = category
            yield book_info