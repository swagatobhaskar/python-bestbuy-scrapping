import requests
from bs4 import BeautifulSoup
import csv

# Create a file to write to
products_file = csv.writer(open('bestbuy-products.csv', 'w'))
# add the CSV headers row
products_file.writerow(['Product name', 'Detail page link', 'Image URL', 'Model No', 'SKU', 'Price'])

# The links to parse from
page1 = 'https://www.bestbuy.com/site/searchpage.jsp?_dyncharset=UTF-8&browsedCategory=pcmcat369900050002&id=pcat17071&iht=n&intl=nosplash&ks=960&list=y&sc=Global&st=categoryid%24pcmcat369900050002&type=page&usc=All%20Categories'
page2 = 'https://www.bestbuy.com/site/searchpage.jsp?_dyncharset=UTF-8&browsedCategory=pcmcat369900050002&id=pcat17071&iht=n&intl=nosplash&ks=960&list=y&sc=Global&st=categoryid%24pcmcat369900050002&type=page&usc=All%20Categories'

# List containing URLs to loop through
page_list = [page1, page2, ]

# Loop through URLs
for url in page_list:
    
    # Specify browser agent
    agent = {"User-Agent": 'Mozilla/5.0'}
    # Send the agent information as payload through GET method
    response = requests.get(url, headers=agent)

    soup = BeautifulSoup(response.content, 'html.parser')

    # Define lists to hold specific info for all products in respective lists
    name_list = []     # list of all product names
    product_detail_page_url_list = []   # list of all product details page links
    image_url_list = []     # list of all image urls
    model_name_list = []    # list of all product model names
    sku_value_list = []     # list of all product sku values
    price_list = []     # list of every prices

    # Get the primary container within which every element lives
    main_results = soup.find('div', class_="list-wrapper top-border")

    # Loop through every product and fetch respective info.
    for product in main_results:
        # Product name
        detail_page_url = product.find_all('h4', class_="sku-header")
        
        for name in detail_page_url:
            # get the product name text
            product_name = name.find('a').text
            # append the name text to the respective list
            name_list.append(product_name)
            # the product detail page link is used as hyperlink so, get the href attribute
            # to get the URL and append it to the respective list
            product_detail_url = name.a['href']
            product_detail_page_url = "https://www.bestbuy.com{0}".format(product_detail_url)
            product_detail_page_url_list.append(product_detail_page_url)

        # Product image link
        shop_list_item = product.find_all('div', class_="shop-sku-list-item")
        
        for image in shop_list_item:
            img = image.find('img', class_="product-image")
            img_alt = img['alt']    # Not required
            # append the product image URL to the respective list
            image_url_list.append(img['src'])

        # get the model and sku values
        variation_info = product.find_all('div', class_="variation-info")
        
        for info in variation_info:
            model = info.find('span', class_="sku-value")
            sku_value = info.find('div', class_="sku-attribute-title").find('span', class_="sku-value")
            # there are two <span> tags under the same parent tag without any class or id
            # using `findNext()` to get the required <span>
            sku_next_span = sku_value.findNext('span').findNext('span').text
            
            # append model and sku to respective lists
            model_name_list.append(model.text)
            sku_value_list.append(sku_next_span)

        # get the price
        price_view = product.find_all('div', class_="priceView-hero-price priceView-customer-price")
        
        for price in price_view:
            actual_price = price.span.string
            # append the price to respective list by stripping the prefix '$'
            price_list.append(actual_price.strip('$'))

    # use zip() method to put every list item into a single iterable list
    zipped_product_list = zip(name_list, product_detail_page_url_list, image_url_list,
                              model_name_list, sku_value_list, price_list)

    # loop through the 'zipped' list and write each row to the CSV
    for name, detail_link, image, model, sku, price in zipped_product_list:
        products_file.writerow([name, detail_link, image, model, sku, price])
        
        # for console display only
        print("Product name: {0}, Detail link: {1}, image URL: {2}, Model No: {3}, SKU: {4}, Price: {5}".format(
            name, detail_link, image, model, sku, price))

print("File Generated.")
