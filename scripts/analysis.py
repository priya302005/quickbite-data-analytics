import os
import pandas as pd

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

INPUT_FILE = os.path.join(
    BASE_DIR, "cleaned_data", "Quick_Bite_Combined_Data.xlsx"
)

OUTPUT_FOLDER = os.path.join(BASE_DIR, "analysis")

OUTPUT_FILE = os.path.join(
    OUTPUT_FOLDER, "Quick_Bite_Analysis.xlsx"
)

WEEKDAY_ORDER = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

LATE_THRESHOLD = 45


def load_data():

    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(
            f"Combined data file not found: {INPUT_FILE}"
        )

    df = pd.read_excel(INPUT_FILE)

    print("\nCombined dataset loaded successfully!")
    print("Shape:", df.shape)

    return df


def validate_data(df):

    required_columns = [
        "order_id",
        "order_day",
        "restaurant_name",
        "cuisine",
        "area_name",
        "city",
        "vehicle_type",
        "order_amount",
        "order_status",
        "delivery_minutes"
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    df = df.copy()

    df["order_id"] = (
        df["order_id"]
        .astype("string")
        .str.strip()
        .str.upper()
        .replace("", pd.NA)
    )

    if df["order_id"].isna().any():
        raise ValueError("Missing order IDs found.")

    if df["order_id"].duplicated().any():
        raise ValueError("Duplicate order IDs found.")

    df["order_amount"] = pd.to_numeric(
        df["order_amount"],
        errors="coerce"
    )

    df["delivery_minutes"] = pd.to_numeric(
        df["delivery_minutes"],
        errors="coerce"
    )

    text_columns = [
        "order_status",
        "order_day",
        "restaurant_name",
        "cuisine",
        "area_name",
        "city",
        "vehicle_type"
    ]

    for column in text_columns:
        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
            .replace("", pd.NA)
        )

    df["order_status"] = (
        df["order_status"].str.lower()
    )

    df["order_status"] = df["order_status"].replace({
        "delivered": "Delivered",
        "completed": "Delivered",
        "cancelled": "Cancelled",
        "canceled": "Cancelled"
    })

    df["order_day"] = df["order_day"].str.title()

    df.loc[
        df["delivery_minutes"] < 0,
        "delivery_minutes"
    ] = pd.NA

    print("\nData validation completed!")

    return df


def area_performance(df):

    print("\nAnalyzing Area Performance...")

    delivered = df[
        df["order_status"] == "Delivered"
    ].copy()

    delivered = delivered.dropna(
        subset=["city", "area_name"]
    )

    revenue_data = (
        delivered.groupby(["city", "area_name"])
        .agg(
            delivered_orders=("order_id", "count"),
            revenue=(
                "order_amount",
                lambda x: x.sum(min_count=1)
            )
        )
        .reset_index()
    )

    valid_delivery = delivered[
        delivered["delivery_minutes"].notna()
    ].copy()

    valid_delivery["late_flag"] = (
        valid_delivery["delivery_minutes"] > LATE_THRESHOLD
    ).astype(int)

    delivery_data = (
        valid_delivery.groupby(["city", "area_name"])
        .agg(
            measured_deliveries=("order_id", "count"),
            average_delivery_minutes=(
                "delivery_minutes", "mean"
            ),
            late_deliveries=("late_flag", "sum")
        )
        .reset_index()
    )

    result = revenue_data.merge(
        delivery_data,
        on=["city", "area_name"],
        how="left",
        validate="one_to_one"
    )

    result["measured_deliveries"] = (
        result["measured_deliveries"]
        .fillna(0)
        .astype(int)
    )

    result["late_deliveries"] = (
        result["late_deliveries"]
        .fillna(0)
        .astype(int)
    )

    result["late_delivery_percentage"] = (
        result["late_deliveries"]
        .div(
            result["measured_deliveries"].replace(
                0, float("nan")
            )
        )
        .mul(100)
    )

    result["revenue_rank"] = (
        result["revenue"]
        .rank(method="min", ascending=False)
        .astype("Int64")
    )

    result["delivery_quality_rank"] = (
        result["late_delivery_percentage"]
        .rank(method="min", ascending=True)
        .astype("Int64")
    )

    result["revenue"] = (
        result["revenue"].round(2)
    )

    result["average_delivery_minutes"] = (
        result["average_delivery_minutes"].round(2)
    )

    result["late_delivery_percentage"] = (
        result["late_delivery_percentage"].round(2)
    )

    result = result.sort_values(
        by=["revenue_rank", "delivery_quality_rank"],
        na_position="last"
    ).reset_index(drop=True)

    print("\nArea Performance Results:")
    print(result.to_string(index=False))

    return result


def top_cuisine_by_day(df):

    print("\nAnalyzing Top Cuisine by Day...")

    delivered = df[
        df["order_status"] == "Delivered"
    ].copy()

    cuisine_data = delivered[
        delivered["cuisine"].notna()
        & delivered["order_day"].isin(WEEKDAY_ORDER)
    ].copy()

    cuisine_counts = (
        cuisine_data.groupby(["order_day", "cuisine"])
        .agg(
            order_count=("order_id", "count")
        )
        .reset_index()
    )

    daily_totals = (
        cuisine_data.groupby("order_day")
        .agg(
            total_daily_orders=("order_id", "count")
        )
        .reset_index()
    )

    cuisine_counts = cuisine_counts.merge(
        daily_totals,
        on="order_day",
        how="left",
        validate="many_to_one"
    )

    cuisine_counts["order_share_percentage"] = (
        cuisine_counts["order_count"]
        / cuisine_counts["total_daily_orders"]
        * 100
    ).round(2)

    cuisine_counts = cuisine_counts.sort_values(
        by=["order_day", "order_count", "cuisine"],
        ascending=[True, False, True]
    )

    top_cuisine = (
        cuisine_counts
        .drop_duplicates(
            subset=["order_day"],
            keep="first"
        )
        .copy()
    )

    top_cuisine["order_day"] = pd.Categorical(
        top_cuisine["order_day"],
        categories=WEEKDAY_ORDER,
        ordered=True
    )

    top_cuisine = top_cuisine.sort_values(
        "order_day"
    ).reset_index(drop=True)

    top_cuisine = top_cuisine[
        [
            "order_day",
            "cuisine",
            "order_count",
            "total_daily_orders",
            "order_share_percentage"
        ]
    ]

    print("\nTop Cuisine by Day Results:")
    print(top_cuisine.to_string(index=False))

    return top_cuisine


def vehicle_performance(df):

    print("\nAnalyzing Vehicle Performance...")

    delivered = df[
        df["order_status"] == "Delivered"
    ].copy()

    delivered = delivered.dropna(
        subset=["vehicle_type"]
    )

    total_orders = (
        delivered.groupby("vehicle_type")
        .agg(
            delivered_orders=("order_id", "count")
        )
        .reset_index()
    )

    valid_delivery = delivered[
        delivered["delivery_minutes"].notna()
    ].copy()

    valid_delivery["late_flag"] = (
        valid_delivery["delivery_minutes"] > LATE_THRESHOLD
    ).astype(int)

    performance = (
        valid_delivery.groupby("vehicle_type")
        .agg(
            measured_deliveries=("order_id", "count"),
            average_delivery_minutes=(
                "delivery_minutes", "mean"
            ),
            late_deliveries=("late_flag", "sum")
        )
        .reset_index()
    )

    result = total_orders.merge(
        performance,
        on="vehicle_type",
        how="left",
        validate="one_to_one"
    )

    result["measured_deliveries"] = (
        result["measured_deliveries"]
        .fillna(0)
        .astype(int)
    )

    result["late_deliveries"] = (
        result["late_deliveries"]
        .fillna(0)
        .astype(int)
    )

    result["late_delivery_percentage"] = (
        result["late_deliveries"]
        .div(
            result["measured_deliveries"].replace(
                0, float("nan")
            )
        )
        .mul(100)
    )

    result["average_delivery_minutes"] = (
        result["average_delivery_minutes"].round(2)
    )

    result["late_delivery_percentage"] = (
        result["late_delivery_percentage"].round(2)
    )

    result = result.sort_values(
        by=[
            "late_delivery_percentage",
            "average_delivery_minutes"
        ],
        ascending=[True, True],
        na_position="last"
    ).reset_index(drop=True)

    print("\nVehicle Performance Results:")
    print(result.to_string(index=False))

    return result


def save_analysis(
    area_result,
    cuisine_result,
    vehicle_result
):

    os.makedirs(
        OUTPUT_FOLDER,
        exist_ok=True
    )

    with pd.ExcelWriter(
        OUTPUT_FILE,
        engine="openpyxl"
    ) as writer:

        area_result.to_excel(
            writer,
            sheet_name="Area Performance",
            index=False
        )

        cuisine_result.to_excel(
            writer,
            sheet_name="Top Cuisine by Day",
            index=False
        )

        vehicle_result.to_excel(
            writer,
            sheet_name="Vehicle Performance",
            index=False
        )

    print("\nAnalysis Excel file saved successfully!")
    print("Output:", OUTPUT_FILE)


def main():

    print("\nQUICKBITE DATA ANALYSIS STARTED")

    df = load_data()

    df = validate_data(df)

    delivered = df[
        df["order_status"] == "Delivered"
    ].copy()

    print("\nTotal orders:", len(df))
    print("Delivered orders:", len(delivered))

    print(
        "Cancelled orders:",
        df["order_status"].eq("Cancelled").sum()
    )

    print(
        "Delivered orders with missing areas:",
        (
            delivered["area_name"].isna()
            | delivered["city"].isna()
        ).sum()
    )

    print(
        "Delivered orders with missing cuisine:",
        delivered["cuisine"].isna().sum()
    )

    print(
        "Delivered orders with missing vehicle type:",
        delivered["vehicle_type"].isna().sum()
    )

    print(
        "Delivered orders with missing delivery time:",
        delivered["delivery_minutes"].isna().sum()
    )

    area_result = area_performance(delivered)

    cuisine_result = top_cuisine_by_day(delivered)

    vehicle_result = vehicle_performance(delivered)

    save_analysis(
        area_result,
        cuisine_result,
        vehicle_result
    )

    print("\nDATA ANALYSIS COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    main()