import requests
from bs4 import BeautifulSoup
import csv

# Create a file to write to, add headers row
products_file = csv.writer(open('bestbuy-products.csv', 'w'))
products_file.writerow(['Product name', 'Detail page link', 'Image URL', 'Model No', 'SKU', 'Price'])

page1 = 'https://www.bestbuy.com/site/searchpage.jsp?_dyncharset=UTF-8&browsedCategory=pcmcat369900050002&id=pcat17071&iht=n&intl=nosplash&ks=960&list=y&sc=Global&st=categoryid%24pcmcat369900050002&type=page&usc=All%20Categories'
page2 = 'https://www.bestbuy.com/site/searchpage.jsp?_dyncharset=UTF-8&browsedCategory=pcmcat369900050002&id=pcat17071&iht=n&intl=nosplash&ks=960&list=y&sc=Global&st=categoryid%24pcmcat369900050002&type=page&usc=All%20Categories'

# This is page 2 link
page_list = [page1, page2, ]

for url in page_list:
    agent = {"User-Agent": 'Mozilla/5.0'}
    response = requests.get(url, headers=agent)

    soup = BeautifulSoup(response.content, 'html.parser')

    name_list = []
    product_detail_page_url_list = []
    image_url_list = []
    model_name_list = []
    sku_value_list = []
    price_list = []

    main_results = soup.find('div', class_="list-wrapper top-border")

    # Loop through every product and fetch respective info.
    for product in main_results:
        # Product name
        detail_page_url = product.find_all('h4', class_="sku-header")
        for name in detail_page_url:
            product_name = name.find('a').text
            name_list.append(product_name)
            product_detail_url = name.a['href']
            product_detail_page_url = "https://www.bestbuy.com{0}".format(product_detail_url)
            product_detail_page_url_list.append(product_detail_page_url)

        # Product image link
        shop_list_item = product.find_all('div', class_="shop-sku-list-item")
        for image in shop_list_item:
            img = image.find('img', class_="product-image")
            img_alt = img['alt']    # Not required
            image_url_list.append(img['src'])

        # variation info
        variation_info = product.find_all('div', class_="variation-info")
        for info in variation_info:
            model = info.find('span', class_="sku-value")
            sku_value = info.find('div', class_="sku-attribute-title").find('span', class_="sku-value")
            sku_next_span = sku_value.findNext('span').findNext('span').text
            model_name_list.append(model.text)
            sku_value_list.append(sku_next_span)

        # Price
        price_view = product.find_all('div', class_="priceView-hero-price priceView-customer-price")
        for price in price_view:
            actual_price = price.span.string
            price_list.append(actual_price.strip('$'))

    zipped_product_list = zip(name_list, product_detail_page_url_list, image_url_list,
                              model_name_list, sku_value_list, price_list)

    for name, detail_link, image, model, sku, price in zipped_product_list:
        products_file.writerow([name, detail_link, image, model, sku, price])
        print("Product name: {0}, Detail link: {1}, image URL: {2}, Model No: {3}, SKU: {4}, Price: {5}".format(
            name, detail_link, image, model, sku, price))

print("File Generated.")
