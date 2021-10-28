from selenium.webdriver.common.by import By
from loguru import logger
import numpy as np
import time
import json

GRAPHQL_URI = "https://marketplace.atlassian.com/gateway/api/graphql"


def save_list_to_file(path, items):
    with open(path, "w") as f:
        for item in items:
            f.write(f"{str(item)}\n")


def click(driver, xpath):
    more_results = driver.find_elements(By.XPATH, xpath)[0]
    time.sleep(2)
    more_results.click()
    time.sleep(5)


def inifite_load_more(driver, xpath):
    while True:
        try:
            logger.info("Click on Load More")
            click(driver, xpath)
        except Exception as e:
            break


def collect_page_links(driver, xpath):
    links = []
    link_elements = driver.find_elements(By.XPATH, xpath)
    for link_el in link_elements:
        href = link_el.get_attribute("href")
        links.append(href)
    return links


def get_element_content(driver, xpath):
    return driver.find_elements(By.XPATH, xpath)[0].text


def get_graphql_responses(driver):
    raw_logs = driver.get_log("performance")
    logs = [json.loads(log["message"])["message"] for log in raw_logs]

    def filter_log(log_):
        return (
            # is an actual response
            log_["method"] == "Network.responseReceived"
            # and json
            and "json" in log_["params"]["response"]["mimeType"]
        )

    responses = []
    for log in filter(filter_log, logs):
        response_url = log["params"]["response"]["url"]
        if response_url == GRAPHQL_URI:
            responses.append(driver.execute_cdp_cmd(
                "Network.getResponseBody",
                {"requestId": log["params"]["requestId"]}
            ))
    return responses


def get_pricing_link(link):
    link = link.split("=")
    link[-1] = "pricing"
    link = "=".join(link)
    return link


def get_min_price(response, field):
    if response[field]:
        return response[field]["tieredPricing"]["items"][0]["amount"]


def extract_unique_items(df, feature):
    return list(set(np.concatenate(np.array(list(map(lambda categories: eval(categories), df[feature].values)))).ravel()))

def encode_categorical_values(df, categories):
    for category in categories:
        df[category] = 0
    
    def encode_categories(row):
        index = row.name
        for category in eval(row.categories):
            df.loc[index, category] = 1
    df.apply(encode_categories, axis=1)
    return df