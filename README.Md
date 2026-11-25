QuickBite Assessment - Data Cleaning and Analysis

 1. Understanding the Dataset

First, I went through the given Excel file to understand the data and the relationship between the sheets.

The dataset contains six sheets: orders, customers, restaurants, areas, delivery_partners and feedback.

I considered orders as the main table and connected the remaining tables using their respective IDs. My requirement was to have one row for each order in the final dataset.

I used the restaurant's area and city for the analysis instead of the customer's location because I wanted to understand how restaurants perform in different areas.

While checking the order dates, I found three different date formats:

- 2026-01-05 22:24
- 05/01/2026 22:24
- 05 Jan 2026 10:24 PM

At first, I was confused about whether the second format was DD/MM/YYYY or MM/DD/YYYY. After checking some dates where the first value was greater than 12, I decided to follow DD/MM/YYYY.


 2. Data Cleaning - Task 1

I started by checking the missing values, duplicate records, data types and inconsistent values in each sheet using Pandas.


 Duplicate Records

I cleaned the inconsistent values before removing duplicates because some records had the same information but were stored in different formats.

I used the drop_duplicates() function to remove them.

I removed 67 duplicate records from orders, 14 from customers, 2 from restaurants, 1 from areas, 1 from delivery partners and 18 from feedback.

A total of 103 duplicate records were removed from all six sheets.


 Problems I Found and Fixed

Order Status

I noticed that order status values were stored in different formats, such as delivered, DELIVERED, Completed and Canceled. I changed these values into two common categories: Delivered and Cancelled.

Payment Mode

Payment modes were stored in different formats, such as upi, Upi, COD, Credit Card, Debit Card and Paytm Wallet.

I was not sure whether Credit Card and Debit Card should be kept separately. Since the given analysis did not require that difference, I grouped both under Card.

The final payment categories are UPI, Card, Cash, Wallet, GPay, PhonePe and Amazon Pay.

Order Amount

Some order amounts were stored as text, such as Rs.501.00, INR 437.17 and 1,441.01.

I removed the currency prefixes and commas and converted the values into numbers for revenue calculations.

Delivery Minutes

Delivery minutes were stored in different formats, such as 26 mins, 18 min and 28m.

I removed the units and converted the values into numbers.

City Names

I found different names for the same city, such as BLR, Hyd, Madras and hyderabad. I standardized these values into four common city names.

Cuisine Names

Cuisine names were stored in different formats, such as Biriyani, N. Indian, South-Indian and Italian - Pizza.

I standardized these values into seven cuisine categories to avoid unnecessary groups during analysis.

Vehicle Types

I found different names for similar vehicles, such as Motor Bike, Scooty, Activa, EV, e-scooter and Cycle.

I grouped these values into four categories: Bike, Scooter, EV Scooter and Bicycle.

ID Standardization

One issue I noticed was that some IDs were in lowercase, such as r110, p536 and c0039.

Even though the IDs represented the same records, they did not match during merging. So I converted all the IDs to uppercase.

Phone Numbers

Phone numbers were stored in five different formats, including +91, 91 prefixes, spaces and hyphens.

I removed unnecessary characters and retained the last 10 digits.

Name Standardization

Some names were completely uppercase, such as CRUST AND CHEESE. I converted these names into title case.

I also noticed that converting names to title case changed HSR Layout into Hsr Layout. I handled this separately to maintain the correct name.


Handling Missing Values

After removing duplicates, I found 17 missing customer IDs, 16 missing order amounts and 13 missing restaurant IDs.

I decided to remove these 46 orders because I did not have enough information to fill in the correct values. Assuming values for these columns could affect the final results.

I saved the removed orders separately in the Removed Orders sheet of the Quality Review file for reference.

I also removed 19 feedback records that belonged to the removed orders.


3. Combining the Data - Task 2

After completing the cleaning process, I merged all six sheets using the orders table as the main table.

I used left joins to retain valid orders even if some additional details were missing.

Before merging, I checked for duplicate IDs in the lookup tables. I also compared the number of rows before and after merging to make sure that the merge did not create extra records.


Final Dataset Summary

The original orders sheet contained 1,567 records. After removing 67 duplicate orders and 46 orders with missing mandatory values, the final combined dataset contains 1,454 orders and 19 columns.

Out of these 1,454 orders, 1,350 orders were delivered and 104 orders were cancelled.

I noticed that cancelled orders did not have delivery partner details or delivery minutes. I kept those records because the orders were cancelled and were not delivered.

There were also 44 delivered orders without delivery minutes. I included these orders in revenue calculations but excluded them from delivery time and late delivery percentage calculations.


 4. Data Analysis - Task 3

For all three analyses, I considered only delivered orders.

An order is considered late if its delivery time is greater than 45 minutes.


4.1 Area Performance

I grouped the delivered orders based on city and area.

For each area, I calculated the total revenue, late delivery percentage, revenue rank and delivery quality rank.

Revenue was calculated by adding the order amounts.

For late delivery percentage, I divided the number of late deliveries by the number of delivered orders with available delivery minutes and multiplied the result by 100.

The area with the highest revenue received revenue rank 1, and the area with the lowest late delivery percentage received delivery quality rank 1.


Revenue Performance

Anna Nagar generated the highest revenue of Rs. 78,141.67, followed by Madhapur with Rs. 72,320.08 and Velachery with Rs. 56,439.15.


 Delivery Performance

Kukatpally had the best delivery performance with a late delivery percentage of 3.53%.

Andheri West had the highest late delivery percentage of 44.44%.

Whitefield and Marathahalli are not included in the results because they had no delivered orders.


 My Observation

One thing I noticed was that an area with high revenue does not always have good delivery performance.

For example, HSR Layout ranked fourth in revenue, but 23.62% of its deliveries with available delivery times were late.

So I understood that revenue and delivery performance need to be checked separately.


4.2 Top Cuisine by Day

I extracted the weekday from the order date and grouped the delivered orders based on day and cuisine.

I counted the orders for each cuisine and selected the cuisine with the highest order count for each day.

I also calculated the percentage of orders contributed by that cuisine on the particular day.


 Analysis Results

On Monday, South Indian was the most ordered cuisine with 49 out of 178 orders, contributing 27.53% of the total orders.

On Tuesday, South Indian was again the most ordered cuisine with 40 out of 172 orders, contributing 23.26%.

On Wednesday, Chinese was the most ordered cuisine with 56 out of 205 orders, contributing 27.32%.

On Thursday, South Indian had the highest order count with 41 out of 188 orders, contributing 21.81%.

On Friday, Biryani was the most ordered cuisine with 52 out of 197 orders, contributing 26.40%.

On Saturday, Pizza had the highest order count with 59 out of 215 orders, contributing 27.44%.

On Sunday, North Indian was the most ordered cuisine with 43 out of 195 orders, contributing 22.05%.


 My Observation

South Indian cuisine was the most ordered cuisine on Monday, Tuesday and Thursday.

Biryani was the most ordered cuisine on Friday, and Pizza was the most ordered cuisine on Saturday.

From this, I could see that customer preferences vary depending on the day of the week.


 4.3 Vehicle Performance

I grouped the delivered orders based on vehicle type and calculated the average delivery time and late delivery percentage.

I excluded orders that did not have delivery minutes.


 Analysis Results

Bike had an average delivery time of 32.76 minutes and a late delivery percentage of 9.46%.

EV Scooter had an average delivery time of 34.03 minutes and a late delivery percentage of 12.71%.

Scooter had an average delivery time of 36.66 minutes and a late delivery percentage of 15.46%.

Bicycle had an average delivery time of 45.45 minutes and a late delivery percentage of 49.54%.


 My Observation

Bike performed better than the other vehicle types in this dataset. It had the lowest average delivery time and late delivery percentage.

Bicycle had the highest average delivery time, and almost half of its deliveries were late.

Based on these results, Bike seems to be a better option for timely deliveries. However, other factors like delivery distance and traffic may also affect the delivery time.


 5. Technologies Used

- Python
- Pandas
- OpenPyXL
- Microsoft Excel

 6. How to Run the Project

 Step 1: Install the Required Libraries


pip install pandas openpyxl


Step 2: Run the Data Cleaning Script

python scripts/cleaning.py


Step 3: Run the Data Analysis Script


python scripts/analysis.py


The cleaning script should be executed first because the analysis script uses the combined dataset generated by the cleaning script.

The cleaned files are stored in the cleaned_data/ folder, and the analysis results are stored in the analysis/ folder.


 7. Additional Quality Review

Apart from the required output files, I created an additional Excel file named Quick_Bite_Quality_Review.xlsx.

This file contains the dataset summary, missing value details, removed orders and foreign key checks.

I created this file to keep track of the records removed during cleaning and to verify the data before proceeding with the analysis.


8. Assumptions and Limitations

I removed orders with missing customer IDs, restaurant IDs or order amounts instead of assuming values.

I considered DD/MM/YYYY as the format for slash-separated dates based on the available date patterns.

Credit Card and Debit Card were grouped under Card, so the individual card type information is lost.

I used the restaurant's location instead of the customer's location for area-wise analysis.

Orders without delivery minutes were excluded from delivery performance calculations because their actual delivery time was unknown.

The dataset contains only six months of data, from January to June 2026. So the results may not represent the entire year's performance.