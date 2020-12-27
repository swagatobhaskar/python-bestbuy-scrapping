from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pathlib import Path
import json

# Import URLs from this local module
from bestbuy_products_details_urls import bestbuy_urls

# add first 3 URLs in this list
url_list = [bestbuy_urls[link] for link in range(3)]    # using list comprehension

for url in url_list:

    # Initial setup for each URL

    # geckodriver path
    PATH = "C:/Program Files (x86)/geckodriver.exe"
    # Firefox profile setup
    firefox_profile = webdriver.FirefoxProfile()
    # Tweak # Firefox profile setting to disable location popup
    firefox_profile.set_preference("geo.enabled", False)
    # Initialize the webdriver with Firefox
    driver = webdriver.Firefox(firefox_profile, executable_path=PATH)

    # Run the url through webdriver
    driver.get(url)

    # get the SKU number from the URL
    sku = url[-7:]

    # COUNTRY SELECTION LOGIC
    # the first page asks to select a country
    if driver.title == "Best Buy International: Select your Country - Best Buy":
        lang_menu = driver.find_element_by_class_name("country-selection")
        eng_button = lang_menu.find_element_by_class_name("us-link").click()

    # driver.implicitly_wait(10)
    WebDriverWait(driver, 10)

    # CONTAINER CONTAINING ALL DROP-DOWNS
    # in some links, this container has different name; therefore adding try/except
    try:
        dropdowns_container = driver.find_element(By.CSS_SELECTOR, ".row.v-border.v-border-top.v-m-bottom-m")
    except NoSuchElementException:
        print("Different class for drop-downs container")
        dropdowns_container = driver.find_element(By.CSS_SELECTOR, ".v-border.v-border-top.v-m-bottom-m")

    # Initialize master dictionary that holds the entire JSON with first key 'sku'
    product_details_master_JSON = {'sku': sku}

    # START OF OVERVIEW DROP-DOWN
    overview_features_bold_list = []
    overview_features_desc_list = []
    overview_whats_included_list = []

    overviewDict = {}
    overview_features = []

    # Get the overview drop-down and the show-hide button
    overview_dropdown = dropdowns_container.find_element_by_class_name("shop-overview-accordion")
    overview_button = overview_dropdown.find_element(By.CSS_SELECTOR, ".c-show-hide-trigger.c-accordion-trigger ")

    # try except block to encounter Element could not be scrolled into view exception
    # but it's still occurring sometimes!
    try:
        element_present = EC.presence_of_element_located((By.CSS_SELECTOR, ".c-show-hide-trigger.c-accordion-trigger "))
        delay = 10
        WebDriverWait(driver, delay).until(element_present)
        overview_button.click()

    except ElementNotInteractableException:
        print(f"Encountered: could not be scrolled into view exception for SKU: {sku}")
        break

    overview_accordion_content = overview_dropdown.find_element_by_id("overview-accordion-content")
    overview_accordion_content_wrapper = overview_accordion_content.find_element_by_class_name(
        "overview-accordion-content-wrapper")

    # Overview -- Description
    long_description = overview_accordion_content_wrapper.find_element_by_class_name("shop-product-description")
    # Description heading is not necessary since dict key is set as 'description'
    desc_heading = long_description.find_element(By.CSS_SELECTOR, ".heading-5.v-fw-regular.description-heading").text
    # Get the long description text
    overview_desc_long_text = long_description.find_element_by_class_name("html-fragment").text

    # Overview -- Features
    features = overview_accordion_content_wrapper.find_element_by_class_name("shop-product-features")
    feature_headings = features.find_elements(By.CSS_SELECTOR, ".heading-5.v-fw-regular.feature-heading")
    features_list = features.find_element(By.CSS_SELECTOR, ".features-list.all-features")
    list_row = features_list.find_elements_by_class_name("list-row")

    for f_list in list_row:
        # The .feature-title.body-copy.v-fw-medium class is not present in some scenarios; adding try except
        try:
            feature_in_bold = f_list.find_element(By.CSS_SELECTOR, ".feature-title.body-copy.v-fw-medium").text
            overview_features_bold_list.append(feature_in_bold)
            feature_description = f_list.find_element_by_tag_name("p").text
            overview_features_desc_list.append(feature_description)
        except NoSuchElementException:
            # This is not in bold, so assigning to feature description is suitable
            body_copy_description = f_list.find_element_by_class_name("body-copy").text
            # Since in this scenario there's no bold text, appending none to bold_list
            overview_features_bold_list.append(None)
            overview_features_desc_list.append(body_copy_description)

    # Overview -- What's Included
    overview_whats_included_list = []

    # add try except to check whether what's included is present or not. If present, get
    # the container items as iterables
    try:
        whats_included = overview_accordion_content_wrapper.find_element_by_class_name("shop-whats-included")
        # header is not needed
        whats_included_header = whats_included.find_element(By.CSS_SELECTOR, ".heading-5.v-fw-regular").text

        whats_included_list_container = whats_included.find_element(By.CSS_SELECTOR, ".list-container.list-lv")
        list_item = whats_included_list_container.find_elements(By.CSS_SELECTOR, ".bold.v-fw-medium.body-copy")

        for item in list_item:
            overview_whats_included_list.append(item.text)
    except NoSuchElementException:
        print("What's included is not present.")

    # New JSON Addition
    overviewDict['desc_text'] = overview_desc_long_text
    overviewFeaturesDict = {}
    for key, value in zip(overview_features_bold_list, overview_features_desc_list):
        overviewFeaturesDict = {'Bold': key, 'text': value}
        overview_features.append(overviewFeaturesDict)

    overviewDict['features'] = overview_features
    overviewDict['whats_included'] = overview_whats_included_list
    product_details_master_JSON['overview'] = overviewDict

    # START OF SPECIFICATIONS DROP-DOWN
    specificationsDict = {}

    # Get the specifications drop-down and the show-hide button and click it
    specifications_dropdown = dropdowns_container.find_element_by_class_name("shop-specifications")
    specs_button = specifications_dropdown.find_element(
        By.CSS_SELECTOR, ".c-show-hide-trigger.c-accordion-trigger ").click()

    # Get the container of entire specifications
    spec_categories = specifications_dropdown.find_element_by_class_name("spec-categories ")
    # get individual specifications as iterables
    category_wrapper_rows = spec_categories.find_elements(By.CSS_SELECTOR, ".category-wrapper.row")

    # Iterate through each category_wrapper_row and get section title and the container of <li> tags
    for rows in category_wrapper_rows:
        section_title = rows.find_element(By.CSS_SELECTOR, ".section-title.heading-5.v-fw-regular ").text

        # convert the section_title variable value to a list and remove the first element
        # as, each section title will hold dicts inside
        section_title_list = list([section_title])
        del section_title_list[0]

        # Get the container of specifications and each li tags inside
        specs_tables = rows.find_element(By.CSS_SELECTOR, ".specs-table.col-xs-9")
        li_tags = specs_tables.find_elements_by_tag_name("li")

        for li in li_tags:
            # for each li tag, get the title and description or value
            row_title = li.find_element_by_class_name("row-title").text
            row_value = li.find_element(By.CSS_SELECTOR, ".row-value.col-xs-6.v-fw-regular").text

            # JSON addition
            rowDict = {"row_title": row_title, "row_value": row_value}
            section_title_list.append(rowDict)
            specificationsDict[section_title] = section_title_list
    product_details_master_JSON['specifications'] = specificationsDict

    # START OF REVIEWS DROP-DOWN
    reviewDict = {}
    reviews_list = []

    # Get the reviews drop-down, the show-hide button and the entire container of all reviews and additional buttons
    reviews_dropdown = dropdowns_container.find_element_by_class_name("user-generated-content-ratings-and-reviews")
    reviews_button = reviews_dropdown.find_element(By.CSS_SELECTOR, ".c-show-hide-trigger.c-accordion-trigger ").click()
    reviews_accordion = reviews_dropdown.find_element_by_id("reviews-accordion")

    # if reviews exist, try clicking on the See More Reviews button
    try:
        all_reviews_button_container = reviews_accordion.find_element_by_class_name("see-all-reviews-button-container")
        see_more_reviews_button = all_reviews_button_container.find_element(
            By.CSS_SELECTOR, ".btn.btn-outline.v-medium.see-more-reviews").click()
    except NoSuchElementException:
        print("The Show More button is not present here.")

    # if review exists get the individual review text containers within try/except
    try:
        reviews_section = reviews_accordion.find_element(By.CSS_SELECTOR, ".row.ugc-reviews.clearfix")
        reviews_card_list = reviews_section.find_element_by_class_name("reviews-list")
        reviews_items = reviews_card_list.find_elements_by_class_name("review-item")

        # Loop through individual review containers
        for review in reviews_items:
            # Get the name of the reviewer
            reviewer_alias = review.find_element(By.CSS_SELECTOR, ".ugc-author.v-fw-medium.body-copy-lg").text

            # Get the container containing review title and body and then get the title and body
            review_container = review.find_element(By.CSS_SELECTOR, ".review-item-content.col-xs-12.col-md-8.col-lg-9")
            review_heading = review_container.find_element_by_tag_name("h4").text
            line_clamp_section = review_container.find_element(By.CSS_SELECTOR, ".ugc-components.line-clamp")
            review_text = line_clamp_section.find_element_by_tag_name("p").text

            # JSON addition
            commentBodyDict = {"sub_heading": review_heading, "review_text": review_text}
            reviewDict['alias'] = reviewer_alias
            reviewDict['comment_body'] = commentBodyDict

            # You need to append a copy, otherwise you are just adding references to the
            # same dictionary over and over again
            reviews_list.append(reviewDict.copy())
        product_details_master_JSON['reviews'] = reviews_list

    except NoSuchElementException:
        print("No reviews here")
        product_details_master_JSON['reviews'] = reviews_list

    # Close the WebDriver
    driver.close()

    # for console display only
    master_json = json.dumps(product_details_master_JSON, indent=4)

    # create the file and write the JSON to it
    json_file_save_path = 'C:/Users/<username>/<path>/<path>/'
    json_filename = f"{sku}_details_master_JSON.json"
    savedFile = Path(json_file_save_path, json_filename)

    with open(savedFile, 'w') as json_file:
        json.dump(product_details_master_JSON, json_file, indent=4)

    # console display only
    print(master_json)

    # add the parsed urls to a file
    parsed_urls_file = "parsed_urls.txt"
    parsedURLsFile = Path(json_file_save_path, parsed_urls_file)

    with open(parsedURLsFile, 'a') as list_file:
        list_file.write('\n' + url)

    # Jumps to the next url in url_list list
