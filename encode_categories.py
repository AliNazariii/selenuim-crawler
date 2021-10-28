import pandas as pd
import utils

if __name__ == "__main__":
    DATASET_PATH = "marketplace.csv"
    df = pd.read_csv(DATASET_PATH)

    categories = utils.extract_unique_items(df, "categories")
    df = utils.encode_categorical_values(df, categories)

    ENCODED_DATASET_PATH = "encoded_cat_marketplace.csv"
    df.to_csv(ENCODED_DATASET_PATH, encoding='utf-8', index=False)
