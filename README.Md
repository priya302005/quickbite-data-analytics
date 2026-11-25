# QuickBite Assessment - Data Cleaning and Analysis

## 1. Understanding the Dataset

First, I went through the given Excel file to understand the data and the relationship between the sheets.

The dataset contains six sheets:

- orders
- customers
- restaurants
- areas
- delivery_partners
- feedback

I considered orders as the main table and connected the remaining tables using their respective IDs. My requirement was to have one row for each order in the final dataset.

I used the restaurant's area and city for the analysis instead of the customer's location because I wanted to understand how restaurants perform in different areas.

While checking the order dates, I found three different date formats:

- 2026-01-05 22:24
- 05/01/2026 22:24
- 05 Jan 2026 10:24 PM

At first, I was confused about whether the second format was DD/MM/YYYY or MM/DD/YYYY. After checking some dates where the first value was greater than 12, I decided to follow DD/MM/YYYY.

## 2. Data Cleaning - Task 1

I started by checking the missing values, duplicate records, data types and inconsistent values in each sheet using Pandas.

### Duplicate Records

I cleaned the inconsistent values before removing duplicates because some records had the same information but were stored in different formats.

I used the `drop_duplicates()` function to remove them.

| Sheet             | Duplicates Removed |
| ----------------- | -----------------: |
| Orders            | 67                 |
| Customers         | 14                 |
| Restaurants       | 2                  |
| Areas             | 1                  |
| Delivery Partners | 1                  |
| Feedback          | 18                 |
| Total             | 103                |

### Problems I Found and Fixed

| Problem          | Examples                                           | Solution                                                      |
| ---------------- | -------------------------------------------------- | ------------------------------------------------------------- |
| Order Status     | delivered, DELIVERED, Completed, Canceled          | Changed to Delivered and Cancelled                            |
| Payment Mode     | upi, Upi, COD, Credit Card, Debit Card             | Standardized payment modes                                    |
| Order Amount     | Rs.501.00, INR 437.17, 1,441.01                    | Removed currency prefixes and commas and converted to numbers |
| Delivery Minutes | 26 mins, 18 min, 28m                               | Removed units and converted to numbers                        |
| City Names       | BLR, Hyd, Madras, hyderabad                        | Standardized into four cities                                 |
| Cuisine Names    | Biriyani, N. Indian, South-Indian, Italian - Pizza | Standardized into seven cuisines                              |
| Vehicle Type     | Motor Bike, Scooty, Activa, EV, Cycle              | Grouped into four vehicle types                               |
| IDs              | r110, p536, c0039                                  | Converted to uppercase                                        |
| Phone Numbers    | +91, 91 prefix, spaces and hyphens                 | Retained the last 10 digits                                   |
| Names            | CRUST AND CHEESE                                   | Converted to title case                                       |

One issue I noticed was that some IDs were in lowercase. Even though the IDs represented the same records, they did not match during merging. So I converted all the IDs to uppercase.

I also noticed that converting names to title case changed HSR Layout into Hsr Layout. I handled this separately.

For payment modes, I was not sure whether Credit Card and Debit Card should be kept separately. Since the given analysis did not require that difference, I grouped both under Card.

The final payment categories are:

- UPI
- Card
- Cash
- Wallet
- GPay
- PhonePe
- Amazon Pay

The final vehicle categories are:

- Bike
- Scooter
- EV Scooter
- Bicycle

### Handling Missing Values

After removing duplicates, I found missing values in the following mandatory columns.

| Column        | Missing Values |
| ------------- | -------------: |
| Customer ID   | 17             |
| Order Amount  | 16             |
| Restaurant ID | 13             |
| Total         | 46             |

I decided to remove these 46 orders because I did not have enough information to fill in the correct values. Assuming values for these columns could affect the final results.

I saved the removed orders separately in the Quality Review file for reference.

I also removed 19 feedback records that belonged to the removed orders.

## 3. Combining the Data - Task 2

After completing the cleaning process, I merged all six sheets using the orders table as the main table.

I used left joins to retain valid orders even if some additional details were missing.

Before merging, I checked for duplicate IDs in the lookup tables. I also compared the number of rows before and after merging to make sure that the merge did not create extra records.

### Final Dataset Summary

| Description                          | Count |
| ------------------------------------ | ----: |
| Raw Orders                           | 1,567 |
| Duplicate Orders Removed             | 67    |
| Orders Removed Due to Missing Values | 46    |
| Final Orders                         | 1,454 |
| Total Columns                        | 19    |
| Delivered Orders                     | 1,350 |
| Cancelled Orders                     | 104   |

I noticed that cancelled orders did not have delivery partner details or delivery minutes. I kept those records because the orders were cancelled and were not delivered.

There were also 44 delivered orders without delivery minutes. I included these orders in revenue calculations but excluded them from delivery time and late delivery percentage calculations.

## 4. Data Analysis - Task 3

For all three analyses, I considered only delivered orders.

An order is considered late if its delivery time is greater than 45 minutes.

### 4.1 Area Performance

I grouped the delivered orders based on city and area.

For each area, I calculated:

- Total revenue
- Late delivery percentage
- Revenue rank
- Delivery quality rank

Revenue was calculated by adding the order amounts.

For late delivery percentage, I divided the number of late deliveries by the number of delivered orders with available delivery minutes.

The area with the highest revenue received revenue rank 1, and the area with the lowest late delivery percentage received delivery quality rank 1.

#### Top Three Areas by Revenue

| Area       | Revenue (INR) |
| ---------- | ------------: |
| Anna Nagar | 78,141.67     |
| Madhapur   | 72,320.08     |
| Velachery  | 56,439.15     |

#### Delivery Performance

| Area                 | Late Delivery Percentage |
| -------------------- | -----------------------: |
| Kukatpally (Best)    | 3.53%                    |
| Andheri West (Worst) | 44.44%                   |

Whitefield and Marathahalli are not included in the results because they had no delivered orders.

#### My Observation

One thing I noticed was that an area with high revenue does not always have good delivery performance.

For example, HSR Layout ranked fourth in revenue, but 23.62% of its deliveries with recorded delivery times were late.

So I understood that revenue and delivery performance need to be checked separately.

### 4.2 Top Cuisine by Day

I extracted the weekday from the order date and grouped the delivered orders based on day and cuisine.

I counted the orders for each cuisine and selected the cuisine with the highest order count for each day.

I also calculated the percentage of orders contributed by that cuisine on the particular day.

| Day       | Top Cuisine  | Cuisine Orders | Total Orders | Share  |
| --------- | ------------ | -------------: | -----------: | -----: |
| Monday    | South Indian | 49             | 178          | 27.53% |
| Tuesday   | South Indian | 40             | 172          | 23.26% |
| Wednesday | Chinese      | 56             | 205          | 27.32% |
| Thursday  | South Indian | 41             | 188          | 21.81% |
| Friday    | Biryani      | 52             | 197          | 26.40% |
| Saturday  | Pizza        | 59             | 215          | 27.44% |
| Sunday    | North Indian | 43             | 195          | 22.05% |

#### My Observation

South Indian cuisine was the most ordered cuisine on Monday, Tuesday and Thursday.

Biryani was the most ordered cuisine on Friday, and Pizza was the most ordered cuisine on Saturday.

From this, I could see that customer preferences vary depending on the day of the week.

### 4.3 Vehicle Performance

I grouped the delivered orders based on vehicle type and calculated the average delivery time and late delivery percentage.

I excluded orders that did not have delivery minutes.

| Vehicle Type | Average Delivery Time (mins) | Late Delivery (%) |
| ------------ | ---------------------------- | ----------------- |
| Bike         | 32.76                        | 9.46%             |
| EV Scooter   | 34.03                        | 12.71%            |
| Scooter      | 36.66                        | 15.46%            |
| Bicycle      | 45.45                        | 49.54%            |

#### My Observation

Bike performed better than the other vehicle types in this dataset. It had the lowest average delivery time and late delivery percentage.

Bicycle had the highest delivery time, and almost half of its deliveries were late.

Based on these results, Bike seems to be a better option for timely deliveries. However, other factors like delivery distance and traffic may also affect the delivery time.

## 5. Technologies Used

- Python
- Pandas
- OpenPyXL
- Microsoft Excel

## 6. How to Run the Project

### Step 1: Install the Required Libraries

```bash
pip install pandas openpyxl
```

### Step 2: Run the Data Cleaning Script

```bash
python scripts/cleaning.py
```

### Step 3: Run the Data Analysis Script

```bash
python scripts/analysis.py
```

The cleaning script should be executed first because the analysis script uses the combined dataset generated by the cleaning script.

The cleaned files are stored in the `cleaned_data/` folder, and the analysis results are stored in the `analysis/` folder.

## 7. Additional Quality Review

Apart from the required output files, I created an additional Excel file named Quick_Bite_Quality_Review.xlsx.

This file contains:

- Dataset Summary
- Missing Values
- Removed Orders
- Foreign Key Checks

I created this file to keep track of the records removed during cleaning and to verify the data before proceeding with the analysis.

## 8. Assumptions and Limitations

- I removed orders with missing customer IDs, restaurant IDs or order amounts instead of assuming values.
- I considered DD/MM/YYYY as the format for slash-separated dates.
- Credit Card and Debit Card were grouped under Card, so the individual card type information is lost.
- I used the restaurant's location instead of the customer's location for area-wise analysis.
- Orders without delivery minutes were excluded from delivery performance calculations.
- The dataset contains only six months of data, from January to June 2026. So the results may not represent the entire year's performance.
