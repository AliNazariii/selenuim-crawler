from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver import Chrome
from loguru import logger
import pandas as pd
import os.path
import utils
import json
import time


def get_links(driver, path):
    if os.path.isfile(path):
        logger.info("Load links from file")
        with open(path, "r") as f:
            return f.read().split("\n")
    else:
        logger.info("Crawl apps links")

        driver.get("https://marketplace.atlassian.com/search/")
        time.sleep(5)

        utils.click(
            driver, "//button[contains(@class,'accept-cookies')]"
        )
        utils.inifite_load_more(
            driver, "//button[contains(@class,'css-doguem')]"
        )

        logger.info("Collect links")
        links = utils.collect_page_links(
            driver, "//div[contains(@class, 'LargeHitStyled')]/a"
        )

        logger.info("Save links")
        utils.save_list_to_file(path, links)

        return links


def crawl_app_details(driver, link, index):
    logger.info(f"({index + 1}) Crawling {link}")
    link = utils.get_pricing_link(link)
    driver.get(link)
    time.sleep(5)

    responses = utils.get_graphql_responses(driver)

    overview_response = json.loads(
        responses[0]["body"]
    )["data"]["marketplaceApp"]
    items = {
        "app_id": overview_response["appId"],
        "name": overview_response["name"],
        "categories": list(map(lambda category: category["name"], overview_response["categories"])),
        "created_at": overview_response["createdAt"],
        "download_count": overview_response["distribution"]["downloadCount"],
        "installation_count": overview_response["distribution"]["installationCount"],
        "is_preinstalled_in_cloud": overview_response["distribution"]["isPreinstalledInCloud"],
        "is_preinstalled_in_server_DC": overview_response["distribution"]["isPreinstalledInServerDC"],
        "partner": overview_response["partner"]["name"],
        "review_count": overview_response["reviewSummary"]["count"],
        "review_rating": overview_response["reviewSummary"]["rating"],
        "summary": overview_response["summary"],
        "marketing_labels": overview_response["marketingLabels"],
        "product_hosting_options": overview_response["productHostingOptions"],
        "url": link
    }

    if len(responses) > 1:
        pricing_response = json.loads(responses[1]["body"])["data"]
        items["is_free"] = False

        items["min_annual_pricing_plan"] = utils.get_min_price(
            pricing_response, "annualPricingPlan"
        )
        items["min_monthly_pricing_plan"] = utils.get_min_price(
            pricing_response, "monthlyPricingPlan"
        )
    else:
        items["is_free"] = True
        items["min_annual_pricing_plan"] = None
        items["min_monthly_pricing_plan"] = None

    return items


if __name__ == "__main__":
    DRIVER_PATH = "./chromedriver"
    capabilities = DesiredCapabilities.CHROME
    capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}
    driver = Chrome(
        desired_capabilities=capabilities,
        executable_path=DRIVER_PATH
    )

    LINKS_PATH = "apps_links.txt"
    links = get_links(driver, LINKS_PATH)

    DF_PATH = "marketplace.csv"
    dataset = []
    for index, link in enumerate(links):
        items = crawl_app_details(driver, link, index)
        dataset.append(list(items.values()))

    df = pd.DataFrame(dataset, columns=list(items.keys()))
    df.to_csv(DF_PATH, encoding='utf-8', index=False)

    driver.quit()
