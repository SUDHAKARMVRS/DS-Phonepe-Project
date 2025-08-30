# PhonePe Dashboard Application
import pandas as pd                     # For data manipulation
from sqlalchemy import create_engine    # For PostgreSQL connection
import plotly.express as px             # For interactive visualizations
import streamlit as st                  # For web app creation


# Database Connection

engine = create_engine('postgresql://postgres:sugana@localhost:5432/Phonepe_Project')

# Caching the data to improve performance
@st.cache_data

# Function to load all datasets from PostgreSQL
def load_data():
    agg_trans = pd.read_sql("SELECT * FROM aggregated_transaction", engine)
    agg_user = pd.read_sql("SELECT * FROM aggregated_user", engine)
    agg_ins = pd.read_sql("SELECT * FROM aggregated_insurance", engine)
    map_trans = pd.read_sql("SELECT * FROM map_transaction", engine)
    map_ins = pd.read_sql("SELECT * FROM map_insurance", engine)
    map_user = pd.read_sql("SELECT * FROM map_user", engine)
    map_conins = pd.read_sql("SELECT * FROM map_country_insurance", engine)
    top_trans = pd.read_sql("SELECT * FROM top_transaction", engine)
    top_user = pd.read_sql("SELECT * FROM top_user", engine)
    top_ins = pd.read_sql("SELECT * FROM top_insurance", engine)
    return agg_trans, agg_user, agg_ins, map_trans, map_ins, map_user, map_conins, top_trans, top_user, top_ins

# Load datasets
agg_trans, agg_user, agg_ins, map_trans, map_ins, map_user, map_conins, top_trans, top_user, top_ins = load_data() 


# Streamlit Layout

st.set_page_config(
    page_title="PhonePe Dashboard",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed")

st.title("📱:violet[PhonePe Transactions Dashboard]")


# Merge Datasets for Map Visualization

merge_map = ["state", "year","district","quarter"]

mdf1 = pd.merge(map_user,map_trans,on=merge_map,how="outer")
mdf2 = pd.merge(mdf1,map_ins,on=merge_map,how="outer")

# Get Coordinates for Districts
coords_lookup = (
    map_conins[map_conins['year'] > 2020]         # take only rows where lat/lon exist
    .dropna(subset=['latitude', 'longitude'])     # make sure they're not NaN
    .groupby('district')[['latitude', 'longitude']]
    .first()                                # one coordinate per district
    .reset_index()
)
# Merge with main dataframe
df = pd.merge(coords_lookup,mdf2,on='district',how="inner")


# Covert to Numeric
df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
df['transaction_count'] = pd.to_numeric(df['transaction_count'], errors='coerce')
df['transaction_amount'] = pd.to_numeric(df['transaction_amount'], errors='coerce')
df['app_opens'] = pd.to_numeric(df['app_opens'], errors='coerce')
df['registered_users'] = pd.to_numeric(df['registered_users'], errors='coerce')
df['insurance_count'] = pd.to_numeric(df['insurance_count'], errors='coerce')
df['insurance_amount'] = pd.to_numeric(df['insurance_amount'], errors='coerce') 

# Drop rows with missing critical values
df.dropna(subset=['latitude', 'longitude', 'transaction_count','app_opens','registered_users','transaction_amount'], inplace=True)


# Sidebar Filters
with st.sidebar:
    st.header("🔍:violet[**SEARCH**]")
    selected_state = st.multiselect("Select State", df['state'].unique(), default=df['state'].unique())
    selected_district = st.multiselect("Select District", df['district'].unique(), default=df['district'].unique())
    selected_quarter = st.multiselect("Select Quarter", df['quarter'].unique(), default=df['quarter'].unique())
    selected_year = st.multiselect("Select Year", df['year'].unique(), default=df['year'].unique())

# Filter DataFrame
filtered_df = df[
    (df['state'].isin(selected_state)) &
    (df['district'].isin(selected_district)) &
    (df['year'].isin(selected_year)) &
    (df['quarter'].isin(selected_quarter))
]
 
# for large datasets, caching can improve performance
@st.cache_data    

# Function to display metrics
def metric(df):
    st.title("📊:blue[**Overview**]")
    st.markdown('---')
    a,b,c = st.columns(3)
    g,h,i = st.columns(3)
    j,k,l = st.columns(3)
    d,e= st.columns(2)
    a.metric('🗺️ **States & Union Territories**', df['state'].nunique(), border=True)
    b.metric('📍**Districts**', df['district'].nunique(), border=True)
    c.metric('🕒 **Quarters**', df['quarter'].nunique(), border=True)
    d.metric('🧑‍💻 **Registered Users**', f"{df['registered_users'].sum() / 1e7:.0f} Cr", border=True)
    e.metric('📲**Total AppOpens**', f"{df['app_opens'].sum() / 1e7:.0f} Cr", border=True)
    g.metric('💰 **Total Transaction Amount**', f"₹ {round(df['transaction_amount'].sum() / 1e9):.0f} Bn", border=True)
    trans_sum = df['transaction_amount'].sum()
    trans_count = df['transaction_count'].sum()
    avg_txn_amt = f"₹ {round(trans_sum / trans_count):.0f}" if trans_count != 0 else "N/A" # To AVoid Error
    h.metric('💰 **Avg.Transaction Amount**', avg_txn_amt, border=True)
    i.metric('🔢 **Total Transaction Counts**', f"{round(trans_count / 1e7)} Cr", border=True)
    premium_amt = df['insurance_amount'].sum()
    premium_count = df['insurance_count'].sum()
    avg_premium_amt = f"₹ {round(premium_amt / premium_count):.0f}" if premium_count != 0 else "N/A"  #To AVoid Error
    j.metric('💰**Total Premium Value**', f"₹ {round(premium_amt / 1e7):.0f} Cr", border=True)
    k.metric('💰**Avg.Premium Value**', avg_premium_amt, border=True)
    l.metric('🛡️**Total Premium Counts**', f"{round(premium_count / 1e5)} L", border=True)

    
    st.markdown('---')

# Tabs: Metrics & Map | Charts | Raw Data | Insights

tab1, tab2, tab3,tab4 = st.tabs(["📈:violet[**METRICS**]", "📊:violet[**VISUALIZATION**]", "📄:violet[**DATA**]","📄:violet[**OBSERVATIONS**]"])


# Tab 1: Metrics and Map

with tab1:
    metric(filtered_df)

# India Map Creation
    st.title(":blue[**🗺️Map**]")
    st.markdown('---')
    fig = px.scatter_map(
    filtered_df,
    lat="latitude",
    lon="longitude",
    size="transaction_count",
    color="state",
    hover_name="district",
    hover_data={
        "year": True,
        "quarter":True,
        "state": True,
        "latitude": False,
        "longitude":False,
        "transaction_amount": True,
        "insurance_amount": True,
        "registered_users": True,
        "app_opens": True
    },
    size_max=30,
    color_continuous_scale="Plasma",
    zoom=4,
    height=900)
    fig.update_layout(
    mapbox_style="open-street-map",
    margin={"r":0, "t":0, "l":0, "b":0})
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('---')

# Tab 2: Charts

with tab2:
    st.title(':blue[**Business Case Studys**]')
    st.markdown('----')

    with st.expander("**1. Decoding Transaction Dynamics on PhonePe**"):

# Query 1: Total Transaction Amount by State
        q1 = """SELECT state, SUM(transaction_amount) AS total_amount FROM aggregated_transaction GROUP BY state ORDER BY total_amount DESC"""
        df1 = pd.read_sql(q1,engine)
        fig1 = px.bar(df1,x='state',y='total_amount',title='1.Total Transaction Amount by State',
        hover_data={'total_amount': ':.2f'}, text_auto=True)
        st.plotly_chart(fig1)

# Query 2: Year-over-Year Decline in Transaction Amount
        q2 = '''WITH yearly_txn AS (SELECT state, year, SUM(transaction_amount) AS present_year_totalamt
                FROM aggregated_transaction GROUP BY state, year),
                with_lag AS (SELECT *, LAG(present_year_totalamt) OVER (PARTITION BY state ORDER BY year) AS previous_year_totalamt
                FROM yearly_txn)
                SELECT state, year, present_year_totalamt, previous_year_totalamt,
                ((present_year_totalamt-previous_year_totalamt)/NULLIF(previous_year_totalamt, 0))*100 AS percentage FROM with_lag
                WHERE present_year_totalamt < previous_year_totalamt
                ORDER BY percentage'''
        df2 = pd.read_sql(q2,engine)
        fig2 = px.bar(df2,x='state',y='percentage',color='percentage',title='2.States with Decline in Transaction Amount (YoY)',
                hover_data={'year': ':.0f','present_year_totalamt': ':.2f', 'previous_year_totalamt': ':.2f', 'percentage': ':.2f'},text_auto=True)
        st.plotly_chart(fig2)

# Query 3: Transaction Breakdown by Payment Type
        q3 = """SELECT type_payments,SUM(transaction_count) AS total_count,SUM(transaction_amount) AS total_amount FROM aggregated_transaction GROUP BY type_payments"""
        df3 = pd.read_sql(q3,engine)
        fig3 = px.pie(df3,names='type_payments',values='total_amount',title='3.Transactions by Payment Type', hover_data=['total_count'], hole=0.3)
        st.plotly_chart(fig3)

# Query 4: Average Transaction Amount by State
        q4 = """SELECT state,AVG(transaction_amount) AS avg_amount FROM aggregated_transaction GROUP BY state ORDER BY avg_amount DESC"""
        df4 = pd.read_sql(q4,engine)
        fig4 = px.bar(df4, x='state',y='avg_amount',title='4.Average Transaction Amount by State',hover_data={'avg_amount': ':.2f'}, text_auto=True)
        st.plotly_chart(fig4)

# Query 5: National Transaction Trend by Quarter
        q5 = """SELECT year, quarter,SUM(transaction_amount) AS total_amount FROM aggregated_transaction GROUP BY year, quarter ORDER BY year, quarter"""
        df5 = pd.read_sql(q5,engine)
        fig5 = px.line(df5,x='quarter',y='total_amount',color='year',markers=True,title='5.National Transaction Trend by Quarter',hover_data={'total_amount': ':.2f'})
        st.plotly_chart(fig5)

    with st.expander("**2. Device Dominance and User Engagement Analysis**"):


# Query 6: Registered Users by Device Brand
        q6 = """SELECT brand,SUM(count) AS total_users FROM aggregated_user GROUP BY brand ORDER BY total_users DESC"""
        df6 = pd.read_sql(q6, engine)
        fig6 = px.bar(df6, x='brand',y='total_users',title='6.Total Registered Users by Device Brand',
              hover_data={'total_users': ':.0f'},text_auto=True)
        st.plotly_chart(fig6)



# Query 7: Top 5 Brands by App Opens
        q7 = """SELECT state,SUM(appopens) AS opens FROM aggregated_user WHERE brand != 'None'  GROUP BY state ORDER BY state DESC LIMIT 5"""
        df7 = pd.read_sql(q7,engine)
        fig7 = px.pie(df7,names='state',values='opens',title='7.Top 5 States by App Opens',
              hover_data=['opens'],hole=0.3)
        st.plotly_chart(fig7)

# Query 8: App Opens to User Ratio by Brand
        q8 = """SELECT brand,SUM(appopens)/SUM(count) AS open_to_user_ratio FROM aggregated_user GROUP BY brand ORDER BY open_to_user_ratio DESC"""
        df8 = pd.read_sql(q8,engine)
        fig8 = px.bar(df8, x='brand',y='open_to_user_ratio',color = 'brand',
               title='8.App Opens to User Ratio by Brand',hover_data=['open_to_user_ratio'], text_auto=True)
        st.plotly_chart(fig8)

# Query 9: User Growth Percentage from 2023 to 2024
        q9 = '''SELECT state,
        SUM(CASE WHEN CAST(year as INTEGER) = 2023 THEN registeredusers ELSE 0 END) AS y2023,
        SUM(CASE WHEN CAST(year as INTEGER) = 2024 THEN registeredusers ELSE 0 END) AS y2024,
        (SUM(CASE WHEN CAST(year as INTEGER) = 2024 THEN registeredusers ELSE 0 END) - 
        SUM(CASE WHEN CAST(year as INTEGER) = 2023 THEN registeredusers ELSE 0 END)) AS growth,
        ((SUM(CASE WHEN CAST(year as INTEGER) = 2024 THEN registeredusers ELSE 0 END) - 
        SUM(CASE WHEN CAST(year as INTEGER) = 2023 THEN registeredusers ELSE 0 END)) / 
        NULLIF(SUM(CASE WHEN CAST(year as INTEGER) = 2023 THEN registeredusers ELSE 0 END), 0)) * 100 AS growth_percentage FROM aggregated_user
        GROUP BY state
        ORDER BY growth_percentage DESC'''
        df9 = pd.read_sql(q9,engine)
        fig9= px.bar(df9,x='state',y='growth_percentage',title='9.User Growth Percentage 2023 - 2024', hover_data=['y2023', 'y2024', 'growth_percentage'], text_auto=True)
        st.plotly_chart(fig9)

    with st.expander("**3. Insurance Penetration and Growth Potential Analysis**"):
        
# Query 10: Insurance Transaction Amount by State
        q10 = '''select year,state,sum(amount) as total_ins_amt,rank()over(order by sum(amount) desc) from top_insurance Group by state,year
                order by rank asc LIMIT 10'''
        df10 = pd.read_sql(q10,engine)
        fig10 = px.bar(df10,x='rank',y='total_ins_amt',color='state',
               title='10.Rank wise Insurance Txn',text_auto=True)
        st.plotly_chart(fig10)

# Query 11: Yearly Insurance Growth Trend
        q11 = """SELECT year, SUM(amount) AS total_amount FROM aggregated_insurance GROUP BY year ORDER BY year"""
        df11 = pd.read_sql(q11,engine)
        fig11 = px.line(df11,x='year',y='total_amount',markers=True,
                title='11.Yearly Insurance Growth Trend',hover_data=['total_amount'],text='total_amount')
        st.plotly_chart(fig11)


# Query 12: Insurance Market Share by State
        q12 = """SELECT state,SUM(amount) AS total_amount FROM aggregated_insurance GROUP BY state"""
        df12 = pd.read_sql(q12, engine)
        fig12 = px.pie(df12, names='state',values='total_amount',title='12.Insurance Market Share by State',hole=0.2,
               hover_data=['total_amount'])
        st.plotly_chart(fig12)

# Query 13: Top 5 States by Insurance Policy Count
        q13 = """SELECT state,SUM(count) AS total_policies FROM aggregated_insurance GROUP BY state ORDER BY total_policies DESC LIMIT 5"""
        df13 = pd.read_sql(q13, engine)
        fig13 = px.bar(df13,x='state',y='total_policies',title='13.Top 5 States by Insurance Policy Count',
               hover_data=['total_policies'],text_auto=True)
        st.plotly_chart(fig13)

    with st.expander("**4. Transaction Analysis for Market Expansion**"):

# Query 14: Avg Transaction Amount by State
        q14 = """SELECT state, AVG(transaction_amount) AS avg_amount FROM map_transaction GROUP BY state ORDER BY avg_amount ASC LIMIT 5"""
        df14 = pd.read_sql(q14,engine)
        fig14 = px.bar(df14, x='state',y='avg_amount',title='14.Avg Transaction Amount by State(Bottom 5)',
               hover_data=['avg_amount'],text_auto=True)
        st.plotly_chart(fig14)

# Query 15: Transaction Trend Over Time
        q15 = """SELECT year, quarter,SUM(transaction_amount) AS total_amount FROM map_transaction GROUP BY year, quarter ORDER BY year, quarter"""
        df15 = pd.read_sql(q15, engine)
        fig15 = px.line(df15,x='quarter',y='total_amount',color='year',markers=True,
                title='15.Transaction Trend Over Time', hover_data=['total_amount'], text='total_amount')
        st.plotly_chart(fig15)

# Query 16: Top 10 Districts by Transaction Amount
        q16 = """SELECT district,SUM(transaction_amount) AS total_amount FROM map_transaction GROUP BY district ORDER BY total_amount DESC LIMIT 10"""
        df16 = pd.read_sql(q16,engine)
        fig16 = px.bar(df16,x='district',y='total_amount',title='16.Top 10 Districts by Transaction Amount',
               hover_data=['total_amount'],text_auto=True)
        st.plotly_chart(fig16)

# Query 17: Average Transaction Amount per State
        q17 = """SELECT state,AVG(transaction_amount) AS avg_amount FROM map_transaction GROUP BY state ORDER BY avg_amount DESC """
        df17 = pd.read_sql(q17,engine)
        fig17 = px.bar(df17,x='state',y='avg_amount',title='17.Average Transaction Amount per State',
               hover_data=['avg_amount'],text_auto=True)
        st.plotly_chart(fig17)

# Query 18: Transaction Count Yearly Trend
        q18 = """SELECT year,SUM(transaction_count) AS total_txns FROM map_transaction GROUP BY year ORDER BY year"""
        df18 = pd.read_sql(q18,engine)
        fig18 = px.line(df18,x='year',y='total_txns',markers=True,
                title='18.Transaction Count Yearly Trend',hover_data=['total_txns'],text='total_txns')
        st.plotly_chart(fig18)

    with st.expander("**5. User Engagement and Growth Strategy**"):

# Query 19: Registered Users by State
        q19 = """SELECT state,SUM(registered_users) AS total_users FROM map_user GROUP BY state ORDER BY total_users DESC"""
        df19 = pd.read_sql(q19, engine)
        fig19 = px.bar(df19,x='state',y='total_users',title='19.Registered Users by State',
               hover_data=['total_users'],text_auto=True)
        st.plotly_chart(fig19)

# Query 20: Top 10 Districts by Registered Users
        q20 = """SELECT district,SUM(registered_users) AS total_users FROM map_user GROUP BY district ORDER BY total_users DESC LIMIT 10"""
        df20 = pd.read_sql(q20,engine)
        fig20 = px.bar(df20,x='district',y='total_users',title='20.Top 10 Districts by Registered Users',
               hover_data=['total_users'],text_auto=True)
        st.plotly_chart(fig20)

# Query 21: Quarterly Registered Users Over Time
        q21 = """SELECT year,quarter,SUM(registered_users) AS users FROM map_user GROUP BY year, quarter ORDER BY year, quarter"""
        df21 = pd.read_sql(q21, engine)
        fig21 = px.line(df21,x='quarter',y='users',color='year',markers=True,
                title='21.Quarterly Registered Users Over Time',hover_data=['users'],text='users')
        st.plotly_chart(fig21)

# Query 22: User Growth by State Over Years
        q22 = '''SELECT state, 
       SUM(CASE WHEN CAST(year as INTEGER) = 2023 THEN registeredusers ELSE 0 END) AS y2023,
       SUM(CASE WHEN CAST(year as INTEGER) = 2024 THEN registeredusers ELSE 0 END) AS y2024,
       (SUM(CASE WHEN CAST(year as INTEGER) = 2024 THEN registeredusers ELSE 0 END) - SUM(CASE WHEN CAST(year as INTEGER) = 2023 THEN registeredusers ELSE 0 END)) AS growth,
       (SUM(CASE WHEN CAST(year as INTEGER) = 2024 THEN registeredusers ELSE 0 END) - SUM(CASE WHEN CAST(year as INTEGER) = 2023 THEN registeredusers ELSE 0 END))/(SUM(CASE WHEN CAST(year as INTEGER) = 2024 THEN registeredusers ELSE 0 END))*100 as growth_percentage
        FROM aggregated_user GROUP BY state ORDER BY growth_percentage desc limit 5;'''
        df22 = pd.read_sql(q22,engine)
        fig22 = px.bar(df22,x='state',y='growth_percentage',color ='growth_percentage', title='22.User Growth Percentage 2023 - 2024', hover_data=['y2023', 'y2024', 'growth_percentage'], text_auto=True)
        st.plotly_chart(fig22)


# Query 23: Top Districts per Year by User Registrations
        q23 = """SELECT district,SUM(registered_users) AS total_users FROM map_user GROUP BY district ORDER BY total_users DESC LIMIT 10"""
        df23 = pd.read_sql(q23,engine)
        fig23 = px.bar(df23,x='district',y='total_users',color='district',
               title='23.Top Districts per Year by User Registrations',hover_data=['total_users'],text_auto=True)
        st.plotly_chart(fig23)


    with st.expander("**6. Insurance Engagement Analysis**"):

# Query 24: Insurance Amount by State
        q24 = "SELECT state,SUM(amount) AS total_amount FROM top_insurance GROUP BY state ORDER BY total_amount DESC"
        df24 = pd.read_sql(q24,engine)
        fig24 = px.bar(df24,x='state',y='total_amount',title='24.Insurance Amount by State',
               hover_data=['total_amount'],text_auto=True)
        st.plotly_chart(fig24)

# Query 25: Top 10 Districts by Insurance Amount
        q25= "SELECT district,SUM(amount) AS total_amount FROM top_insurance GROUP BY district ORDER BY total_amount DESC LIMIT 10"
        df25 = pd.read_sql(q25,engine)
        fig25 = px.bar(df25,x='district',y='total_amount',title='25.Top 10 Districts by Insurance Amount',
               hover_data=['total_amount'],text_auto=True)
        st.plotly_chart(fig25)

# Query 26: Top 10 Pincodes by Insurance Amount
        q26 = "SELECT pincode,SUM(amount) AS total_amount FROM top_insurance WHERE pincode !='0' GROUP BY pincode ORDER BY total_amount DESC LIMIT 10"
        df26 = pd.read_sql(q26,engine)
        fig26 = px.pie(df26,values='total_amount',names='pincode',title='26.Top 10 Pincodes by Insurance Amount',
               hover_data=['total_amount'])
        st.plotly_chart(fig26)

# Query 27: Insurance Transactions Over Time
        q27 = "SELECT year,quarter,SUM(amount) AS total_amount FROM top_insurance GROUP BY year, quarter ORDER BY quarter asc"
        df27 = pd.read_sql(q27,engine)
        fig27 = px.line(df27,x='quarter',y='total_amount',color='year',markers=True,
                title='27.Insurance Transactions Over Time',hover_data=['total_amount'],text='total_amount')
        st.plotly_chart(fig27)

# Query 28: Top Districts by Insurance per Year
        q28 = "SELECT year,district,SUM(amount) AS total_amount FROM top_insurance GROUP BY year, district ORDER BY total_amount DESC LIMIT 10"
        df28 = pd.read_sql(q28,engine)
        fig28 = px.bar(df28, x='district',y='total_amount',color='year',
               title='28.Top Districts by Insurance per Year',hover_data=['total_amount'],text_auto=True)
        st.plotly_chart(fig28)

    with st.expander("**7.Transaction Analysis Across States and Districts**"):        

# Query 29: Total Transactions by State
        q29 = "SELECT quarter,SUM(transaction_amount) AS total_amount FROM map_transaction GROUP BY quarter ORDER BY total_amount DESC"
        df29 = pd.read_sql(q29,engine)
        fig29 = px.bar(df29,x='quarter',y='total_amount',title='29.Total Transactions by Quarter Wise',
               hover_data=['total_amount'],text_auto=True)
        st.plotly_chart(fig29)

# Query 30: Top 10 Districts by Transaction Amount
        q30 = "SELECT district, SUM(transaction_amount) AS total_amount FROM map_transaction GROUP BY district ORDER BY total_amount DESC LIMIT 10"
        df30 = pd.read_sql(q30,engine)
        fig30 = px.bar(df30,x='district',y='total_amount',title='30.Top 10 Districts by Transaction Amount',
               hover_data=['total_amount'],text_auto=True)
        st.plotly_chart(fig30,key='fig30')

# Query 31: Top 10 Pincodes by Transaction Amount
        q31 = "SELECT pincode, SUM(amount) AS total_amount FROM top_transaction WHERE pincode!= '0' GROUP BY pincode ORDER BY total_amount DESC LIMIT 10"
        df31 = pd.read_sql(q31,engine)
        fig31 = px.pie(df31,names='pincode',values='total_amount',title='31.Top 10 Pincodes by Transaction Amount',
               hover_data=['total_amount'])
        st.plotly_chart(fig31)

# Query 32: Yearly Transaction Amount (Nationwide)
        q32 = "SELECT year,SUM(transaction_amount) AS total_amount FROM map_transaction GROUP BY year"
        df32 = pd.read_sql(q32,engine)
        fig32 = px.bar(df32,x='year',y='total_amount',title='32.Yearly Transaction Amount (Nationwide)',
               hover_data=['total_amount'],text_auto=True)
        st.plotly_chart(fig32)

# Query 33: Top Districts by Yearly Transactions
        q33 = '''SELECT district, year, SUM(transaction_amount) AS total FROM map_transaction
                GROUP BY district, year ORDER BY total DESC LIMIT 10'''
        df33 = pd.read_sql(q33,engine)
        fig33 = px.bar(df33,x='district',y='total',color='year',title='33.Top Districts by Yearly Transactions',
               hover_data=['total'],text_auto=True)
        st.plotly_chart(fig33)

    with st.expander("**8. User Registration Analysis**"):  

# Query 34: Top 10 Pincodes by User Registrations
        q34 = "SELECT pincode, SUM(registeredusers) AS total_users FROM top_user GROUP BY pincode HAVING pincode>0 ORDER BY total_users DESC LIMIT 10"
        df34 = pd.read_sql(q34, engine)
        fig34 = px.pie(df34,names='pincode',values='total_users',title='34.Top 10 Pincodes by User Registrations',
               hover_data=['total_users'])
        st.plotly_chart(fig34)

# Query 35: Quarterly User Registration Trends
        q35 = "SELECT year,quarter,SUM(registered_users) AS users FROM map_user GROUP BY year, quarter ORDER BY year, quarter"
        df35 = pd.read_sql(q35,engine)
        fig35 = px.line(df35,x='quarter',y='users',color='year',markers=True,
                title='35.Quarterly User Registration Trends',hover_data=['users'],text='users')
        st.plotly_chart(fig35)


# Query 36: User Growth by Year
        q36 = "SELECT year,SUM(registered_users) AS users FROM map_user GROUP BY year ORDER BY year DESC"
        df36 = pd.read_sql(q36, engine)
        fig36 = px.bar(df36, x='year',y='users',color='year',title='36.User Growth by Year',
               hover_data=['users'],text_auto=True)
        st.plotly_chart(fig36)

        st.markdown('***')

# Load Datasets
with tab3:
      
        st.title("📄:blue[**Raw Data**]")

        st.markdown('---')


        with st.expander("**Aggregated Transactions**"):
            st.dataframe(agg_trans)

        with st.expander("**Aggregated Users**"):
            st.dataframe(agg_user)

        with st.expander("**Aggregated Insurance**"):
            st.dataframe(agg_ins)

        with st.expander("**Map Combined**"):
            st.dataframe(df)

        with st.expander("**Top Insurance**"):
            st.dataframe(top_ins)

        with st.expander("**Top Transactions**"):
            st.dataframe(top_trans)

        with st.expander("**Top Users**"):
            st.dataframe(top_user)

        st.markdown('---')
 

with tab4:
        st.title(":blue[**INSIGHT & RECOMMENDS**]")
        st.markdown('----')
        col1, col2 = st.columns(2)

        with col1:
            st.header("💡**Insights**")
            st.write("""
1. Transaction Trends:
   * High-performing states - Maharashtra, Karnataka, and Telangana.
   * Transactions have grown steadily year-over-year.
   * Some temporary declines found(Manipur,Chandigar on 2023).
                     
2. Payment Type Patterns:
   * Top payments by Peer-to-Peer (P2P) and Merchant transactions.
   * UPI is the primary method used.
   * Metro cities lead in digital activity.
                     

3. Device & User Behavior:
   * Most users access the app through Samsung, Xiaomi, and Vivo devices.
   * Some brands have higher app-open ratios but less no. of users.

4. Insurance Penetration:
   * Urban states dominate insurance adoption.
   * Insurance counts remain lower than total transaction. counts.
   * Yearly growth in insurance transactions is promising.

5 User Engagement:
   * Consistent growth in app opens and registered users.
   * Some emerging districts show high potential for expansion.""")
            
        with col2:
            st.header("✅**Recommendations**")
            st.write("""
1. Market Expansion :
   * Prioritize low-performance regions (e.g.,Andhaman, Lakshadweep).
   * Use successful district strategies to replicate growth elsewhere.
                     
2. Product Strategy:
   * Promote insurance and financial tools in underserved markets.
   * Optimize app performance for mid-range and budget smartphones.

3. Technology Enhancements:
   * Improve UI for mobile and map resolution for better experience.
   * Tie up with mobile partners to distribute app suited devices with low price.                     
   * Make User - Friendly for beginners to pay bills

4. Policy Suggestions:
   * Create Campaighns regards Insurance policy & Give awarness in rural areas.
   * Tie-up with insurance partners.
   * Partner with local governments to drive UPI awareness and training.""")

        st.markdown('----')

st.balloons()
