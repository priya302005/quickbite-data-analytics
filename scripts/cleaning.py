import os
import re
import pandas as pd

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

INPUT_FILE = os.path.join(
    BASE_DIR, "data", "QuickBite_Assessment.xlsx"
)

CLEANED_FOLDER = os.path.join(
    BASE_DIR, "cleaned_data"
)

CLEANED_FILE = os.path.join(
    CLEANED_FOLDER, "Quick_Bite_Data_Cleaning.xlsx"
)

COMBINED_FILE = os.path.join(
    CLEANED_FOLDER, "Quick_Bite_Combined_Data.xlsx"
)

QUALITY_FILE = os.path.join(
    CLEANED_FOLDER, "Quick_Bite_Quality_Review.xlsx"
)

LATE_THRESHOLD = 45

SHEET_NAMES = [
    "orders",
    "customers",
    "restaurants",
    "areas",
    "delivery_partners",
    "feedback"
]

MANDATORY_ORDER_COLUMNS = [
    "order_id",
    "customer_id",
    "restaurant_id",
    "order_amount",
    "order_datetime"
]

FINAL_COLUMNS = [
    "order_id",
    "order_date",
    "order_time",
    "order_day",
    "customer_name",
    "restaurant_name",
    "cuisine",
    "area_name",
    "city",
    "partner_name",
    "vehicle_type",
    "order_amount",
    "payment_mode",
    "coupon_code",
    "order_status",
    "delivery_minutes",
    "is_late",
    "rating",
    "comment"
]


def load_data(file_path):

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Input file not found: {file_path}"
        )

    data = {}

    for sheet in SHEET_NAMES:
        data[sheet] = pd.read_excel(
            file_path,
            sheet_name=sheet
        )

    return data


def inspect_data(data):

    for name, df in data.items():

        print("\nDataset:", name)
        print("Shape:", df.shape)

        print("\nMissing Values:")
        print(df.isna().sum())

        print("\nExact Duplicate Rows:")
        print(df.duplicated().sum())


def clean_text(series):

    return (
        series.astype("string")
        .str.strip()
        .replace(r"^\s*$", pd.NA, regex=True)
    )


def clean_id(series):

    return clean_text(series).str.upper()


def clean_phone(series):

    digits = (
        clean_text(series)
        .str.replace(r"\D", "", regex=True)
        .replace("", pd.NA)
    )

    # keep the last 10 digits (drops +91 / 91 country code)
    return digits.str[-10:]


def clean_all_text_columns(df):

    df = df.copy()

    for column in df.select_dtypes(
        include=["object", "string"]
    ).columns:

        df[column] = clean_text(df[column])

    return df


def parse_order_datetime(series):

    values = clean_text(series)

    result = pd.Series(
        pd.NaT,
        index=series.index,
        dtype="datetime64[ns]"
    )

    for index, value in values.items():

        if pd.isna(value):
            continue

        value = str(value).strip()

        try:

            if re.match(
                r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}",
                value
            ):

                parsed = pd.to_datetime(
                    value,
                    yearfirst=True,
                    errors="coerce"
                )

            else:

                parsed = pd.to_datetime(
                    value,
                    dayfirst=True,
                    errors="coerce"
                )

            result.at[index] = parsed

        except (ValueError, TypeError):

            result.at[index] = pd.NaT

    return result


def standardize_orders(orders):

    orders = clean_all_text_columns(orders)

    id_columns = [
        "order_id",
        "customer_id",
        "restaurant_id",
        "partner_id"
    ]

    for column in id_columns:

        orders[column] = clean_id(
            orders[column]
        )

    payment_mapping = {
        "upi": "UPI",
        "card": "Card",
        "cash": "Cash",
        "wallet": "Wallet",
        "cod": "Cash",
        "cash on delivery": "Cash",
        "credit card": "Card",
        "debit card": "Card",
        "gpay": "GPay",
        "phonepe": "PhonePe",
        "amazon pay": "Amazon Pay",
        "paytm wallet": "Wallet"
    }

    orders["payment_mode"] = (
        clean_text(orders["payment_mode"])
        .str.lower()
        .replace(payment_mapping)
    )

    status_mapping = {
        "delivered": "Delivered",
        "completed": "Delivered",
        "cancelled": "Cancelled",
        "canceled": "Cancelled"
    }

    orders["order_status"] = (
        clean_text(orders["order_status"])
        .str.lower()
        .replace(status_mapping)
    )

    orders["coupon_code"] = (
        clean_text(orders["coupon_code"])
        .str.upper()
    )

    amount = clean_text(
        orders["order_amount"]
    )

    amount = (
        amount
        .str.replace(
            r"(?i)^(?:rs\.?|inr|₹)\s*",
            "",
            regex=True
        )
        .str.replace(",", "", regex=False)
        .str.strip()
    )

    orders["order_amount"] = pd.to_numeric(
        amount,
        errors="coerce"
    )

    orders.loc[
        orders["order_amount"] < 0,
        "order_amount"
    ] = pd.NA

    minutes = clean_text(
        orders["delivery_minutes"]
    )

    minutes = (
        minutes
        .str.replace(
            r"(?i)\s*(?:minutes?|mins?|m)\s*$",
            "",
            regex=True
        )
        .str.strip()
    )

    orders["delivery_minutes"] = pd.to_numeric(
        minutes,
        errors="coerce"
    )

    orders.loc[
        orders["delivery_minutes"] < 0,
        "delivery_minutes"
    ] = pd.NA

    orders["order_datetime"] = parse_order_datetime(
        orders["order_datetime"]
    )

    return orders


def standardize_customers(customers):

    customers = clean_all_text_columns(customers)

    for column in ["customer_id", "area_id"]:

        customers[column] = clean_id(
            customers[column]
        )

    customers["customer_name"] = (
        clean_text(customers["customer_name"])
        .str.title()
    )

    customers["phone"] = clean_phone(
        customers["phone"]
    )

    customers["email"] = (
        clean_text(customers["email"])
        .str.lower()
    )

    customers["signup_date"] = (
        parse_order_datetime(
            customers["signup_date"]
        ).dt.normalize()
    )

    return customers


def standardize_restaurants(restaurants):

    restaurants = clean_all_text_columns(
        restaurants
    )

    for column in ["restaurant_id", "area_id"]:

        restaurants[column] = clean_id(
            restaurants[column]
        )

    restaurants["restaurant_name"] = (
        clean_text(restaurants["restaurant_name"])
        .str.title()
    )

    cuisine_mapping = {
        "chinese": "Chinese",
        "biryani": "Biryani",
        "biriyani": "Biryani",
        "burgers": "Burgers",
        "south indian": "South Indian",
        "south-indian": "South Indian",
        "north indian": "North Indian",
        "north-indian": "North Indian",
        "n. indian": "North Indian",
        "pizza": "Pizza",
        "italian - pizza": "Pizza",
        "desserts": "Desserts",
        "dessert": "Desserts"
    }

    restaurants["cuisine"] = (
        clean_text(restaurants["cuisine"])
        .str.lower()
        .replace(cuisine_mapping)
        .str.title()
    )

    restaurants["rating"] = pd.to_numeric(
        restaurants["rating"],
        errors="coerce"
    )

    restaurants.loc[
        ~restaurants["rating"].between(1, 5),
        "rating"
    ] = pd.NA

    restaurants["onboard_date"] = (
        parse_order_datetime(
            restaurants["onboard_date"]
        ).dt.normalize()
    )

    return restaurants


def standardize_areas(areas):

    areas = clean_all_text_columns(areas)

    areas["area_id"] = clean_id(
        areas["area_id"]
    )

    areas["area_name"] = (
        clean_text(areas["area_name"])
        .str.title()
        .replace({"Hsr Layout": "HSR Layout"})
    )

    city_mapping = {
        "bengaluru": "Bengaluru",
        "bangalore": "Bengaluru",
        "blr": "Bengaluru",
        "hyderabad": "Hyderabad",
        "hyd": "Hyderabad",
        "chennai": "Chennai",
        "madras": "Chennai",
        "mumbai": "Mumbai"
    }

    areas["city"] = (
        clean_text(areas["city"])
        .str.lower()
        .replace(city_mapping)
        .str.title()
    )

    areas["zone"] = (
        clean_text(areas["zone"])
        .str.title()
    )

    return areas


def standardize_partners(partners):

    partners = clean_all_text_columns(partners)

    partners["partner_id"] = clean_id(
        partners["partner_id"]
    )

    partners["partner_name"] = (
        clean_text(partners["partner_name"])
        .str.title()
    )

    partners["phone"] = clean_phone(
        partners["phone"]
    )

    vehicle_mapping = {
        "bike": "Bike",
        "motor bike": "Bike",
        "motorbike": "Bike",
        "bicycle": "Bicycle",
        "cycle": "Bicycle",
        "scooter": "Scooter",
        "scooty": "Scooter",
        "activa": "Scooter",
        "ev": "EV Scooter",
        "ev scooter": "EV Scooter",
        "e-scooter": "EV Scooter"
    }

    partners["vehicle_type"] = (
        clean_text(partners["vehicle_type"])
        .str.lower()
        .replace(vehicle_mapping)
    )

    partners["join_date"] = (
        parse_order_datetime(
            partners["join_date"]
        ).dt.normalize()
    )

    return partners


def standardize_feedback(feedback):

    feedback = clean_all_text_columns(feedback)

    for column in ["feedback_id", "order_id"]:

        feedback[column] = clean_id(
            feedback[column]
        )

    feedback["comment"] = clean_text(
        feedback["comment"]
    )

    feedback["rating"] = pd.to_numeric(
        feedback["rating"],
        errors="coerce"
    )

    feedback.loc[
        ~feedback["rating"].between(1, 5),
        "rating"
    ] = pd.NA

    feedback["feedback_date"] = (
        parse_order_datetime(
            feedback["feedback_date"]
        ).dt.normalize()
    )

    return feedback


def clean_data(data):

    cleaned_data = {}
    cleaning_summary = []
    removed_orders = pd.DataFrame()

    cleaning_functions = {
        "orders": standardize_orders,
        "customers": standardize_customers,
        "restaurants": standardize_restaurants,
        "areas": standardize_areas,
        "delivery_partners": standardize_partners,
        "feedback": standardize_feedback
    }

    for name, df in data.items():

        before = len(df)

        df = cleaning_functions[name](
            df.copy()
        )

        df = df.drop_duplicates().reset_index(
            drop=True
        )

        duplicate_count = before - len(df)

        mandatory_removed = 0

        if name == "orders":

            invalid_mask = (
                df[MANDATORY_ORDER_COLUMNS]
                .isna()
                .any(axis=1)
            )

            removed_orders = df.loc[
                invalid_mask
            ].copy()

            removed_orders["removal_reason"] = (
                removed_orders[MANDATORY_ORDER_COLUMNS]
                .isna()
                .apply(
                    lambda row: ", ".join(
                        row.index[row].tolist()
                    ),
                    axis=1
                )
            )

            mandatory_removed = len(removed_orders)

            df = df.loc[
                ~invalid_mask
            ].reset_index(drop=True)

        cleaned_data[name] = df

        cleaning_summary.append({
            "dataset": name,
            "original_rows": before,
            "duplicates_removed": duplicate_count,
            "mandatory_missing_removed": mandatory_removed,
            "cleaned_rows": len(df),
            "remaining_missing_cells": int(
                df.isna().sum().sum()
            )
        })

        print(
            f"\n{name}: Removed {duplicate_count} "
            "duplicate rows"
        )

        print(
            "Rows removed for missing mandatory fields:",
            mandatory_removed
        )

        print("Remaining rows:", len(df))

    return (
        cleaned_data,
        pd.DataFrame(cleaning_summary),
        removed_orders
    )


def remove_orphan_feedback(cleaned_data):

    feedback = cleaned_data["feedback"]

    valid_orders = cleaned_data["orders"]["order_id"]

    orphan_mask = ~feedback["order_id"].isin(valid_orders)

    print(
        "\nFeedback rows removed (order no longer exists):",
        int(orphan_mask.sum())
    )

    cleaned_data["feedback"] = feedback.loc[
        ~orphan_mask
    ].reset_index(drop=True)

    return cleaned_data


def validate_unique_key(df, key, dataset_name):

    if df[key].isna().any():

        raise ValueError(
            f"Missing {key} in {dataset_name}"
        )

    duplicates = df[
        df.duplicated(
            subset=[key],
            keep=False
        )
    ]

    if not duplicates.empty:

        print(
            f"\nDuplicate keys in {dataset_name}:"
        )

        print(duplicates.head(20))

        raise ValueError(
            f"Duplicate {key} in {dataset_name}"
        )

    print(
        f"{dataset_name}: Unique {key} validated"
    )


def inspect_foreign_keys(cleaned_data):

    relationships = [
        ("orders", "customer_id", "customers", "customer_id"),
        ("orders", "restaurant_id", "restaurants", "restaurant_id"),
        ("orders", "partner_id", "delivery_partners", "partner_id"),
        ("customers", "area_id", "areas", "area_id"),
        ("restaurants", "area_id", "areas", "area_id"),
        ("feedback", "order_id", "orders", "order_id")
    ]

    summary = []

    for source, foreign_key, target, primary_key in relationships:

        source_df = cleaned_data[source]
        target_df = cleaned_data[target]

        missing_mask = source_df[
            foreign_key
        ].isna()

        unmatched_mask = (
            source_df[foreign_key].notna()
            & ~source_df[foreign_key].isin(
                target_df[primary_key]
            )
        )

        missing_count = int(missing_mask.sum())
        unmatched_count = int(unmatched_mask.sum())

        summary.append({
            "source_dataset": source,
            "foreign_key": foreign_key,
            "target_dataset": target,
            "missing_keys": missing_count,
            "unmatched_keys": unmatched_count
        })

        print(
            f"{source}.{foreign_key}: "
            f"{missing_count} missing, "
            f"{unmatched_count} unmatched"
        )

    return pd.DataFrame(summary)


def save_cleaned_data(cleaned_data):

    os.makedirs(
        CLEANED_FOLDER,
        exist_ok=True
    )

    with pd.ExcelWriter(
        CLEANED_FILE,
        engine="openpyxl"
    ) as writer:

        for name, df in cleaned_data.items():

            df.to_excel(
                writer,
                sheet_name=name,
                index=False
            )

    print("\nCleaned data saved successfully!")


def combine_data(cleaned_data):

    orders = cleaned_data["orders"].copy()
    customers = cleaned_data["customers"].copy()
    restaurants = cleaned_data["restaurants"].copy()
    areas = cleaned_data["areas"].copy()

    partners = cleaned_data[
        "delivery_partners"
    ].copy()

    feedback = cleaned_data["feedback"].copy()

    validate_unique_key(
        orders, "order_id", "orders"
    )

    validate_unique_key(
        customers, "customer_id", "customers"
    )

    validate_unique_key(
        restaurants, "restaurant_id", "restaurants"
    )

    validate_unique_key(
        areas, "area_id", "areas"
    )

    validate_unique_key(
        partners, "partner_id", "delivery_partners"
    )

    validate_unique_key(
        feedback, "feedback_id", "feedback"
    )

    validate_unique_key(
        feedback, "order_id", "feedback"
    )

    expected_rows = len(orders)

    combined = pd.merge(
        orders,
        customers[
            [
                "customer_id",
                "customer_name"
            ]
        ],
        on="customer_id",
        how="left",
        validate="many_to_one"
    )

    print(
        "Rows after customer merge:",
        len(combined)
    )

    restaurants = restaurants.rename(
        columns={
            "rating": "restaurant_rating",
            "area_id": "restaurant_area_id"
        }
    )

    combined = pd.merge(
        combined,
        restaurants[
            [
                "restaurant_id",
                "restaurant_name",
                "restaurant_area_id",
                "cuisine"
            ]
        ],
        on="restaurant_id",
        how="left",
        validate="many_to_one"
    )

    print(
        "Rows after restaurant merge:",
        len(combined)
    )

    combined = pd.merge(
        combined,
        areas[
            [
                "area_id",
                "area_name",
                "city"
            ]
        ],
        left_on="restaurant_area_id",
        right_on="area_id",
        how="left",
        validate="many_to_one"
    )

    print(
        "Rows after area merge:",
        len(combined)
    )

    combined = pd.merge(
        combined,
        partners[
            [
                "partner_id",
                "partner_name",
                "vehicle_type"
            ]
        ],
        on="partner_id",
        how="left",
        validate="many_to_one"
    )

    print(
        "Rows after delivery partner merge:",
        len(combined)
    )

    feedback = feedback.rename(
        columns={
            "rating": "feedback_rating"
        }
    )

    combined = pd.merge(
        combined,
        feedback[
            [
                "order_id",
                "feedback_rating",
                "comment"
            ]
        ],
        on="order_id",
        how="left",
        validate="one_to_one"
    )

    print(
        "Rows after feedback merge:",
        len(combined)
    )

    if len(combined) != expected_rows:

        raise ValueError(
            "Merge changed the number of orders."
        )

    if combined["order_id"].duplicated().any():

        raise ValueError(
            "Repeated order IDs found after merge."
        )

    combined["order_date"] = (
        combined["order_datetime"].dt.date
    )

    combined["order_time"] = (
        combined["order_datetime"]
        .dt.strftime("%H:%M:%S")
    )

    combined["order_day"] = (
        combined["order_datetime"].dt.day_name()
    )

    combined["is_late"] = pd.Series(
        pd.NA,
        index=combined.index,
        dtype="boolean"
    )

    valid_delivery = (
        combined["order_status"].eq("Delivered")
        & combined["delivery_minutes"].notna()
    )

    combined.loc[
        valid_delivery,
        "is_late"
    ] = (
        combined.loc[
            valid_delivery,
            "delivery_minutes"
        ] > LATE_THRESHOLD
    )

    combined["rating"] = (
        combined["feedback_rating"]
    )

    combined = combined[
        FINAL_COLUMNS
    ].copy()

    if combined.columns.duplicated().any():

        raise ValueError(
            "Duplicate column names in combined data."
        )

    if combined["order_id"].duplicated().any():

        raise ValueError(
            "Duplicate order IDs in combined data."
        )

    if combined.columns.tolist() != FINAL_COLUMNS:

        raise ValueError(
            "Combined dataset columns are incorrect."
        )

    print("\nFinal combined dataset shape:")
    print(combined.shape)

    print("\nFinal columns:")
    print(combined.columns.tolist())

    print("\nInvalid order dates:")
    print(combined["order_date"].isna().sum())

    print("\nMissing values:")
    print(combined.isna().sum())

    print("\nDuplicate order IDs:")
    print(combined["order_id"].duplicated().sum())

    return combined


def save_combined_data(combined):

    combined.to_excel(
        COMBINED_FILE,
        index=False
    )

    print(
        "\nCombined data saved successfully!"
    )


def save_quality_review(
    cleaned_data,
    combined,
    cleaning_summary,
    removed_orders,
    foreign_key_summary
):

    summary = []

    for name, df in cleaned_data.items():

        summary.append({
            "dataset": name,
            "rows": len(df),
            "columns": len(df.columns),
            "missing_cells": int(
                df.isna().sum().sum()
            ),
            "duplicate_rows": int(
                df.duplicated().sum()
            )
        })

    summary.append({
        "dataset": "combined",
        "rows": len(combined),
        "columns": len(combined.columns),
        "missing_cells": int(
            combined.isna().sum().sum()
        ),
        "duplicate_rows": int(
            combined.duplicated().sum()
        )
    })

    summary_df = pd.DataFrame(summary)

    missing_df = pd.DataFrame({
        "column": combined.columns,
        "missing_count": combined.isna().sum().values
    })

    if len(combined) > 0:

        missing_df["missing_percentage"] = (
            missing_df["missing_count"]
            / len(combined)
            * 100
        ).round(2)

    else:

        missing_df["missing_percentage"] = pd.NA

    review_columns = [
        "order_id",
        "customer_name",
        "restaurant_name",
        "area_name",
        "city",
        "partner_name",
        "vehicle_type",
        "order_amount",
        "delivery_minutes",
        "order_status",
        "order_date"
    ]

    review_mask = (
        combined["customer_name"].isna()
        | combined["restaurant_name"].isna()
        | combined["area_name"].isna()
        | combined["city"].isna()
        | combined["order_amount"].isna()
        | combined["order_date"].isna()
        | (
            combined["order_status"].eq("Delivered")
            & (
                combined["delivery_minutes"].isna()
                | combined["vehicle_type"].isna()
            )
        )
    )

    review_orders = combined.loc[
        review_mask,
        review_columns
    ].copy()

    with pd.ExcelWriter(
        QUALITY_FILE,
        engine="openpyxl"
    ) as writer:

        summary_df.to_excel(
            writer,
            sheet_name="Dataset Summary",
            index=False
        )

        cleaning_summary.to_excel(
            writer,
            sheet_name="Cleaning Summary",
            index=False
        )

        missing_df.to_excel(
            writer,
            sheet_name="Missing Values",
            index=False
        )

        foreign_key_summary.to_excel(
            writer,
            sheet_name="Foreign Key Review",
            index=False
        )

        removed_orders.to_excel(
            writer,
            sheet_name="Removed Orders",
            index=False
        )

        review_orders.to_excel(
            writer,
            sheet_name="Orders To Review",
            index=False
        )

    print(
        "\nQuality review saved successfully!"
    )


def main():

    print("\nQUICKBITE DATA CLEANING STARTED")

    data = load_data(INPUT_FILE)

    inspect_data(data)

    (
        cleaned_data,
        cleaning_summary,
        removed_orders
    ) = clean_data(data)

    cleaned_data = remove_orphan_feedback(cleaned_data)

    print("\nFOREIGN KEY VALIDATION")

    foreign_key_summary = inspect_foreign_keys(
        cleaned_data
    )

    combined = combine_data(cleaned_data)

    save_cleaned_data(cleaned_data)

    save_combined_data(combined)

    save_quality_review(
        cleaned_data,
        combined,
        cleaning_summary,
        removed_orders,
        foreign_key_summary
    )

    print("\nCLEANING COMPLETED SUCCESSFULLY")

    print("\nOutput files:")
    print(CLEANED_FILE)
    print(COMBINED_FILE)
    print(QUALITY_FILE)


if __name__ == "__main__":
    main()