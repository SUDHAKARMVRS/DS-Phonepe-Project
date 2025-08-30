# ✅ Query 1: Total Transaction Amount by State
        q1 = """SELECT state, SUM(transaction_amount) AS total_amount FROM aggregated_transaction 
        GROUP BY state 
        ORDER BY total_amount DESC"""


# ✅ Query 2: Year-over-Year Decline in Transaction Amount
        q2 = '''WITH yearly_txn AS (SELECT state, year, SUM(transaction_amount) AS present_year_totalamt
                FROM aggregated_transaction GROUP BY state, year),
                with_lag AS (SELECT *, LAG(present_year_totalamt) OVER (PARTITION BY state ORDER BY year) AS previous_year_totalamt
                FROM yearly_txn)
                SELECT state, year, present_year_totalamt, previous_year_totalamt,
                ((present_year_totalamt-previous_year_totalamt)/NULLIF(previous_year_totalamt, 0))*100 AS percentage FROM with_lag
                WHERE present_year_totalamt < previous_year_totalamt
                ORDER BY percentage'''


# ✅ Query 3: Transaction Breakdown by Payment Type
        q3 = """SELECT type_payments,SUM(transaction_count) AS total_count,SUM(transaction_amount) AS total_amount FROM aggregated_transaction 
        GROUP BY type_payments"""


# ✅ Query 4: Average Transaction Amount by State
        q4 = """SELECT state,AVG(transaction_amount) AS avg_amount FROM aggregated_transaction 
        GROUP BY state 
        ORDER BY avg_amount DESC"""


# ✅ Query 5: National Transaction Trend by Quarter
        q5 = """SELECT year, quarter,SUM(transaction_amount) AS total_amount FROM aggregated_transaction 
        GROUP BY year, quarter 
        ORDER BY year, quarter"""



("**2. Device Dominance and User Engagement Analysis**"):


# Query 6
        # ✅ Query 6: Registered Users by Device Brand
        q6 = """SELECT brand,SUM(count) AS total_users FROM aggregated_user 
        GROUP BY brand 
        ORDER BY total_users DESC"""




# ✅ Query 7: Top 5 Brands by App Opens
        q7 = """SELECT state,SUM(appopens) AS opens FROM aggregated_user 
        WHERE brand != 'None'  
        GROUP BY state,appopens 
        ORDER BY opens DESC 
        LIMIT 5"""


# ✅ Query 8: App Opens to User Ratio by Brand
        q8 = """SELECT brand,SUM(appopens)/SUM(count) AS open_to_user_ratio FROM aggregated_user 
        GROUP BY brand 
        ORDER BY open_to_user_ratio DESC"""


# ✅ Query 9: User Growth Percentage from 2023 to 2024
        q9 = '''SELECT state,
        SUM(CASE WHEN year = 2023 THEN registeredusers ELSE 0 END) AS y2023,
        SUM(CASE WHEN year = 2024 THEN registeredusers ELSE 0 END) AS y2024,
        (SUM(CASE WHEN year = 2024 THEN registeredusers ELSE 0 END) - 
        SUM(CASE WHEN year = 2023 THEN registeredusers ELSE 0 END)) AS growth,
        ((SUM(CASE WHEN year = 2024 THEN registeredusers ELSE 0 END) - 
        SUM(CASE WHEN year = 2023 THEN registeredusers ELSE 0 END)) / 
        NULLIF(SUM(CASE WHEN year = 2023 THEN registeredusers ELSE 0 END), 0)) * 100 AS growth_percentage FROM aggregated_user
        GROUP BY state
        ORDER BY growth_percentage DESC'''


("**3. Insurance Penetration and Growth Potential Analysis**"):

        # ✅ Query 10: Insurance Transaction Amount by State
        q10 = '''select year,state,sum(amount) as total_ins_amt,rank()over(order by sum(amount) desc) from top_insurance 
        Group by state,year
        Order by rank asc LIMIT 10'''


# ✅ Query 11: Yearly Insurance Growth Trend
        q11 = """SELECT year, SUM(amount) AS total_amount FROM aggregated_insurance 
        GROUP BY year 
        ORDER BY year"""



# ✅ Query 12: Insurance Market Share by State
        q12 = """SELECT state,SUM(amount) AS total_amount FROM aggregated_insurance 
        GROUP BY state"""


# ✅ Query 13: Top 5 States by Insurance Policy Count
        q13 = """SELECT state,SUM(count) AS total_policies FROM aggregated_insurance 
        GROUP BY state 
        ORDER BY total_policies DESC 
        LIMIT 5"""

("**4. Transaction Analysis for Market Expansion**"):

# ✅ Query 14: Avg Transaction Amount by State
        q14 = """SELECT state, AVG(transaction_amount) AS avg_amount FROM map_transaction 
        GROUP BY state 
        ORDER BY avg_amount ASC 
        LIMIT 5"""


# ✅ Query 15: Transaction Trend Over Time
        q15 = """SELECT year, quarter,SUM(transaction_amount) AS total_amount FROM map_transaction 
        GROUP BY year, quarter 
        ORDER BY year, quarter"""


# ✅ Query 16: Top 10 Districts by Transaction Amount
        q16 = """SELECT district,SUM(transaction_amount) AS total_amount FROM map_transaction 
        GROUP BY district 
        ORDER BY total_amount DESC 
        LIMIT 10"""


# ✅ Query 17: Average Transaction Amount per State
        q17 = """SELECT state,AVG(transaction_amount) AS avg_amount FROM map_transaction 
        GROUP BY state 
        ORDER BY avg_amount DESC """

# ✅ Query 18: Transaction Count Yearly Trend
        q18 = """SELECT year,SUM(transaction_count) AS total_txns FROM map_transaction 
        GROUP BY year 
        ORDER BY year"""


 ("**5. User Engagement and Growth Strategy**"):

# ✅ Query 19: Registered Users by State
        q19 = """SELECT state,SUM(registered_users) AS total_users FROM map_user 
        GROUP BY state 
        ORDER BY total_users DESC"""


# ✅ Query 20: Top 10 Districts by Registered Users
        q20 = """SELECT district,SUM(registered_users) AS total_users FROM map_user 
        GROUP BY district 
        ORDER BY total_users DESC 
        LIMIT 10"""


# ✅ Query 21: Quarterly Registered Users Over Time
        q21 = """SELECT year,quarter,SUM(registered_users) AS users FROM map_user 
        GROUP BY year, quarter 
        ORDER BY year, quarter"""


# ✅ Query 22: User Growth by State Over Years
        q22 = '''SELECT state, 
       SUM(CASE WHEN year = 2023 THEN registeredusers ELSE 0 END) AS y2023,
       SUM(CASE WHEN year = 2024 THEN registeredusers ELSE 0 END) AS y2024,
       (SUM(CASE WHEN year = 2024 THEN registeredusers ELSE 0 END) - SUM(CASE WHEN year = 2023 THEN registeredusers ELSE 0 END)) AS growth,
       (SUM(CASE WHEN year = 2024 THEN registeredusers ELSE 0 END) - SUM(CASE WHEN year = 2023 THEN registeredusers ELSE 0 END))/(SUM(CASE WHEN CAST(year as INTEGER) = 2024 THEN registeredusers ELSE 0 END))*100 as growth_percentage
        FROM aggregated_user GROUP BY state ORDER BY growth_percentage desc limit 5;'''



# ✅ Query 23: Top Districts per Year by User Registrations
        q23 = """SELECT district,SUM(registered_users) AS total_users FROM map_user 
        GROUP BY district 
        ORDER BY total_users DESC 
        LIMIT 10"""



("**6. Insurance Engagement Analysis**"):

# ✅ Query 24: Insurance Amount by State
        q24 = "SELECT state,SUM(amount) AS total_amount FROM top_insurance 
        GROUP BY state 
        ORDER BY total_amount DESC"


# ✅ Query 25: Top 10 Districts by Insurance Amount
        q25= "SELECT district,SUM(amount) AS total_amount FROM top_insurance 
        GROUP BY district 
        ORDER BY total_amount DESC 
        LIMIT 10"


# ✅ Query 26: Top 10 Pincodes by Insurance Amount
        q26 = "SELECT pincode,SUM(amount) AS total_amount FROM top_insurance 
        WHERE pincode !='0' 
        GROUP BY pincode 
        ORDER BY total_amount DESC 
        LIMIT 10"


# ✅ Query 27: Insurance Transactions Over Time
        q27 = "SELECT year,quarter,SUM(amount) AS total_amount FROM top_insurance 
        GROUP BY year, quarter 
        ORDER BY quarter asc"


# ✅ Query 28: Top Districts by Insurance per Year
        q28 = "SELECT year,district,SUM(amount) AS total_amount FROM top_insurance 
        GROUP BY year, district 
        ORDER BY total_amount DESC 
        LIMIT 10"


("**7.Transaction Analysis Across States and Districts**"):        

# ✅ Query 29: Total Transactions by State
        q29 = "SELECT quarter,SUM(transaction_amount) AS total_amount FROM map_transaction 
        GROUP BY quarter 
        ORDER BY total_amount DESC"

# ✅ Query 30: Top 10 Districts by Transaction Amount
        q30 = "SELECT district, SUM(transaction_amount) AS total_amount FROM map_transaction 
        GROUP BY district 
        ORDER BY total_amount DESC 
        LIMIT 10"


# ✅ Query 31: Top 10 Pincodes by Transaction Amount
        q31 = "SELECT pincode, SUM(amount) AS total_amount FROM top_transaction 
        WHERE pincode!= '0' 
        GROUP BY pincode 
        ORDER BY total_amount DESC 
        LIMIT 10"


# ✅ Query 32: Yearly Transaction Amount (Nationwide)
        q32 = "SELECT year,SUM(transaction_amount) AS total_amount FROM map_transaction 
        GROUP BY year"


# ✅ Query 33: Top Districts by Yearly Transactions
        q33 = '''SELECT district, year, SUM(transaction_amount) AS total FROM map_transaction
                GROUP BY district, year 
                ORDER BY total DESC 
                LIMIT 10'''


"**8. User Registration Analysis**"  

# ✅ Query 34: Top 10 Pincodes by User Registrations
        q34 = "SELECT pincode, SUM(registeredusers) AS total_users FROM top_user 
        GROUP BY pincode 
        HAVING pincode>0 
        ORDER BY total_users DESC LIMIT 10"


# ✅ Query 35: Quarterly User Registration Trends
        q35 = "SELECT year,quarter,SUM(registered_users) AS users FROM map_user 
        GROUP BY year, quarter 
        ORDER BY year, quarter"



# ✅ Query 36: User Growth by Year
        q36 = "SELECT year,SUM(registered_users) AS users FROM map_user 
        GROUP BY year 
        ORDER BY year DESC"
