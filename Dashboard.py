import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# ---------------------------
# Database Connection
# ---------------------------
engine = create_engine('postgresql://postgres:sugana@localhost:5432/Phonepe_Project')

# ---------------------------
# Load Data from PostgreSQL
# ---------------------------
agg_trans = pd.read_sql("SELECT * FROM aggregated_transaction", engine)
agg_user = pd.read_sql("SELECT * FROM aggregated_user", engine)
agg_ins = pd.read_sql("SELECT * FROM aggregated_insurance", engine)
map_trans = pd.read_sql("SELECT * FROM map_transaction", engine)
map_ins = pd.read_sql("SELECT * FROM map_insurance", engine)
map_user = pd.read_sql("SELECT * FROM map_user", engine)
map_conins = pd.read_sql("SELECT * FROM map_conty_insurance", engine)
top_trans = pd.read_sql("SELECT * FROM top_transaction", engine)
top_user = pd.read_sql("SELECT * FROM top_user", engine)
top_ins = pd.read_sql("SELECT * FROM top_insurance", engine)


# ---------------------------
# Streamlit Layout
# ---------------------------

st.set_page_config(
    page_title="PhonePe Dashboard",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed")

st.title("📱:violet[PhonePe Transactions Dashboard]")


# Merge all data

merge_map = ["state", "year","district","quarter"]

mdf1 = pd.merge(map_user,map_trans,on=merge_map,how="outer")
mdf2 = pd.merge(mdf1,map_conins,on=merge_map,how="outer")
df = pd.merge(mdf2,map_ins,on=merge_map,how="outer")

# 1️⃣ Create a lookup table of unique district coordinates (from years after 2020)
coords_lookup = (
    df[df['year'] > 2020]                         # take only rows where lat/lon exist
    .dropna(subset=['latitude', 'longitude'])     # make sure they're not NaN
    .groupby('district')[['latitude', 'longitude']]
    .first()                                      # one coordinate per district
    .reset_index()
)

# 2️⃣ Merge lookup back into full dataset
df = df.merge(coords_lookup, on='district', how='left', suffixes=('', '_ref'))

# 3️⃣ Fill missing lat/lon using the reference
df['latitude'] = df['latitude'].fillna(df['latitude_ref'])
df['longitude'] = df['longitude'].fillna(df['longitude_ref'])

# 4️⃣ Remove helper columns
df = df.drop(columns=['latitude_ref', 'longitude_ref'])


# Covert to Numeric
df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
df['transaction_count'] = pd.to_numeric(df['transaction_count'], errors='coerce')
df['transaction_amount'] = pd.to_numeric(df['transaction_amount'], errors='coerce')
df['app_opens'] = pd.to_numeric(df['app_opens'], errors='coerce')
df['registered_users'] = pd.to_numeric(df['registered_users'], errors='coerce')
df.dropna(subset=['latitude', 'longitude', 'transaction_count','app_opens','registered_users','transaction_amount'], inplace=True)


# Sidebar Filters
with st.sidebar:
    st.header("🔍:violet[**Filter Data**]")
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


def metric(df):
    st.header("📊:violet[**Overview**]")
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
    j.metric('💰**Total Premium Value**', f"₹ {round(premium_amt / 1e7):.0f} Cr", border=True)
    avg_premium_amt = f"₹ {round(premium_amt / premium_count):.0f}" if premium_count != 0 else "N/A"  #To AVoid Error
    k.metric('💰**Avg.Premium Value**', avg_premium_amt, border=True)
    l.metric('🛡️**Total Premium Counts**', f"{round(premium_count / 1e5)} L", border=True)

    
    st.markdown('---')

# ---------------------------
# Tabs: Metrics | Charts | Raw Data | Maps
# ---------------------------
tab1, tab2, tab3,tab4 = st.tabs(["📈:violet[**Metrics**]", "📊:violet[**Visualization**]", "📄:violet[**Data**]","📄:violet[**Observations**]"])

# ---------------------------
# Tab 1: Metrics
# ---------------------------
with tab1:
    metric(filtered_df)
#Map    
    st.header(":violet[**🗺️Map (Transactions,Insurance,Users,App Opens)**]")
    fig = px.scatter_mapbox(
    filtered_df,
    lat="latitude",
    lon="longitude",
    size="transaction_amount",
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
    zoom=3.8,
    height=900)
    fig.update_layout(
    mapbox_style="open-street-map",
    margin={"r":0, "t":0, "l":0, "b":0})
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# Tab 2: Charts
# ---------------------------
with tab2:
    st.title(':violet[_**Business Case Studys**_]')
    st.markdown('***')
# ---------------------------
    with st.expander("**1. Decoding Transaction Dynamics on PhonePe**"):

# ✅ Query 1: Total Transaction Amount by State
        q1 = """SELECT state, SUM(transaction_amount) AS total_amount FROM aggregated_transaction GROUP BY state ORDER BY total_amount DESC"""
        df1 = pd.read_sql(q1, engine)
        fig1 = px.bar(df1, x='state', y='total_amount', title='Total Transaction Amount by State',
        hover_data={'total_amount': ':.2f'}, text_auto=True)
        st.plotly_chart(fig1)

# ✅ Query 2: Year-over-Year Decline in Transaction Amount
        q2 = '''WITH yearly_txn AS (SELECT state, year, SUM(transaction_amount) AS present_year_totalamt
                FROM aggregated_transaction GROUP BY state, year),
                WITH_lag AS (SELECT *, LAG(present_year_totalamt) OVER (PARTITION BY state ORDER BY year) AS previous_year_totalamt
                FROM yearly_txn)
                SELECT state, year, present_year_totalamt, previous_year_totalamt,
                ((present_year_totalamt-previous_year_totalamt)/NULLIF(previous_year_totalamt, 0))*100 AS percentage FROM with_lag
                WHERE present_year_totalamt < previous_year_totalamt
                ORDER BY percentage'''
        df2 = pd.read_sql(q2, engine)
        fig2 = px.bar(df2, x='state', y='percentage', color='percentage',title='States with Decline in Transaction Amount (YoY)',
                hover_data={'year': ':.0f','present_year_totalamt': ':.2f', 'previous_year_totalamt': ':.2f', 'percentage': ':.2f'},text_auto=True)
        st.plotly_chart(fig2)

# ✅ Query 3: Transaction Breakdown by Payment Type
        q3 = """SELECT type_payments, SUM(transaction_count) AS total_count, SUM(transaction_amount) AS total_amount FROM aggregated_transaction GROUP BY type_payments"""
        df3 = pd.read_sql(q3, engine)
        fig3 = px.pie(df3, names='type_payments', values='total_amount',title='Transactions by Payment Type', hover_data=['total_count'], hole=0.3)
        st.plotly_chart(fig3)

# ✅ Query 4: Average Transaction Amount by State
        q4 = """SELECT state, AVG(transaction_amount) AS avg_amount FROM aggregated_transaction GROUP BY state"""
        df4 = pd.read_sql(q4, engine)
        fig4 = px.bar(df4, x='state', y='avg_amount',title='Average Transaction Amount by State',hover_data={'avg_amount': ':.2f'}, text_auto=True)
        st.plotly_chart(fig4)

# ✅ Query 5: National Transaction Trend by Quarter
        q5 = """SELECT year, quarter, SUM(transaction_amount) AS total_amount FROM aggregated_transaction GROUP BY year, quarter ORDER BY year, quarter"""
        df5 = pd.read_sql(q5, engine)
        fig5 = px.line(df5, x='quarter', y='total_amount', color='year', markers=True,title='National Transaction Trend by Quarter',hover_data={'total_amount': ':.2f'})
        st.plotly_chart(fig5)

# ---------------------------
    with st.expander("**2. Device Dominance and User Engagement Analysis**"):
# ---------------------------

# Query 6
        # ✅ Query 6: Registered Users by Device Brand
        q6 = """SELECT brand, SUM(count) AS total_users FROM aggregated_user GROUP BY brand ORDER BY total_users DESC"""
        df6 = pd.read_sql(q6, engine)
        fig6 = px.bar(df6, x='brand', y='total_users', title='Total Registered Users by Device Brand',
              hover_data={'total_users': ':.0f'}, text_auto=True)
        st.plotly_chart(fig6)


# ✅ Query 8: Device Brand Usage by State
        q8 = """SELECT state, brand, SUM(count) AS user_count FROM aggregated_user WHERE brand !='None' GROUP BY state, brand ORDER BY SUM(count)DESC LIMIT 15"""
        df8 = pd.read_sql(q8, engine)
        fig8 = px.bar(df8, x='state', y='user_count', color='brand', barmode='group',
              title='Device Brand Usage by State', hover_data=['user_count'], text_auto=True)
        st.plotly_chart(fig8)

# ✅ Query 9: Top 5 Brands by App Opens
        q9 = """SELECT state,SUM(appopens) AS opens FROM aggregated_user WHERE brand != 'None'  GROUP BY state,appopens ORDER BY opens DESC LIMIT 8"""
        df9 = pd.read_sql(q9, engine)
        fig9 = px.pie(df9, names='state', values='opens', title='Top 5 States by App Opens',
              hover_data=['opens'], hole=0.3)
        st.plotly_chart(fig9)

# ✅ Query 10: App Opens to User Ratio by Brand
        q10 = """SELECT brand, SUM(appopens)*1.0/SUM(count) AS open_to_user_ratio FROM aggregated_user GROUP BY brand ORDER BY open_to_user_ratio DESC"""
        df10 = pd.read_sql(q10, engine)
        fig10 = px.bar(df10, x='brand', y='open_to_user_ratio',
               title='App Opens to User Ratio by Brand', hover_data=['open_to_user_ratio'], text_auto=True)
        st.plotly_chart(fig10)

# ✅ Query 10.1: User Growth Percentage from 2023 to 2024
        q10_1 = '''SELECT state,
    SUM(CASE WHEN CAST(year as INTEGER) = 2023 THEN registeredusers ELSE 0 END) AS y2023,
    SUM(CASE WHEN CAST(year as INTEGER) = 2024 THEN registeredusers ELSE 0 END) AS y2024,
    (SUM(CASE WHEN CAST(year as INTEGER) = 2024 THEN registeredusers ELSE 0 END) - 
     SUM(CASE WHEN CAST(year as INTEGER) = 2023 THEN registeredusers ELSE 0 END)) AS growth,
    ((SUM(CASE WHEN CAST(year as INTEGER) = 2024 THEN registeredusers ELSE 0 END) - 
      SUM(CASE WHEN CAST(year as INTEGER) = 2023 THEN registeredusers ELSE 0 END)) / 
     NULLIF(SUM(CASE WHEN CAST(year as INTEGER) = 2023 THEN registeredusers ELSE 0 END), 0)) * 100 AS growth_percentage FROM aggregated_user
        GROUP BY state
        ORDER BY growth_percentage DESC'''
        df10_1 = pd.read_sql(q10_1, engine)
        fig10_1 = px.bar(df10_1, x='state', y='growth_percentage',title='User Growth Percentage 2023 - 2024', hover_data=['y2023', 'y2024', 'growth_percentage'], text_auto=True)
        st.plotly_chart(fig10_1)

    with st.expander("**3. Insurance Penetration and Growth Potential Analysis**"):
        # ✅ Query 11: Insurance Transaction Amount by State
        q11 = '''select year,state,sum(amount) as total_ins_amt,rank()over(order by sum(amount) desc) from top_insurance Group by state,year
                order by rank asc LIMIT 5'''
        df11 = pd.read_sql(q11, engine)
        fig11 = px.bar(df11, x='rank', y='total_ins_amt', color='state',
               title='Rank wise Insurance Txn States', text_auto=True)
        st.plotly_chart(fig11)

# ✅ Query 12: Yearly Insurance Growth Trend
        q12 = """SELECT year, SUM(amount) AS total_amount FROM aggregated_insurance GROUP BY year ORDER BY year"""
        df12 = pd.read_sql(q12, engine)
        fig12 = px.line(df12, x='year', y='total_amount', markers=True,
                title='Yearly Insurance Growth Trend', hover_data=['total_amount'], text='total_amount')
        st.plotly_chart(fig12)

# ✅ Query 13: Policy Count vs Insurance Amount
        q13 = """SELECT state, SUM(count) AS policy_count, SUM(amount) AS total_amount FROM aggregated_insurance GROUP BY state ORDER BY policy_count DESC LIMIT 5"""
        df13 = pd.read_sql(q13, engine)
        fig13 = px.pie(df13, names='state', values='total_amount', color='policy_count', hole=0.3,
               title='Policy Count vs Insurance Amount', hover_data=['policy_count', 'total_amount'])
        st.plotly_chart(fig13)

# ✅ Query 14: Insurance Market Share by State
        q14 = """SELECT state, SUM(amount) AS total_amount FROM aggregated_insurance GROUP BY state"""
        df14 = pd.read_sql(q14, engine)
        fig14 = px.pie(df14, names='state', values='total_amount', title='Insurance Market Share by State', hole=0.2,
               hover_data=['total_amount'])
        st.plotly_chart(fig14)

# ✅ Query 15: Top 5 States by Insurance Policy Count
        q15 = """SELECT state, SUM(count) AS total_policies FROM aggregated_insurance GROUP BY state ORDER BY total_policies DESC LIMIT 5"""
        df15 = pd.read_sql(q15, engine)
        fig15 = px.bar(df15, x='state', y='total_policies', title='Top 5 States by Insurance Policy Count',
               hover_data=['total_policies'], text_auto=True)
        st.plotly_chart(fig15)

    with st.expander("**4. Transaction Analysis for Market Expansion**"):

# ✅ Query 16: Transaction Amount by State
        q16 = """SELECT state, SUM(transaction_amount) AS total_amount FROM map_transaction GROUP BY state ORDER BY total_amount DESC"""
        df16 = pd.read_sql(q16, engine)
        fig16 = px.bar(df16, x='state', y='total_amount', title='Transaction Amount by State',
               hover_data=['total_amount'], text_auto=True)
        st.plotly_chart(fig16)

# ✅ Query 17: Transaction Trend Over Time
        q17 = """SELECT year, quarter, SUM(transaction_amount) AS total_amount FROM map_transaction GROUP BY year, quarter ORDER BY year, quarter"""
        df17 = pd.read_sql(q17, engine)
        fig17 = px.line(df17, x='quarter', y='total_amount', color='year', markers=True,
                title='Transaction Trend Over Time', hover_data=['total_amount'], text='total_amount')
        st.plotly_chart(fig17)

# ✅ Query 18: Top 10 Districts by Transaction Amount
        q18 = """SELECT district, SUM(transaction_amount) AS total_amount FROM map_transaction GROUP BY district ORDER BY total_amount DESC LIMIT 10"""
        df18 = pd.read_sql(q18, engine)
        fig18 = px.bar(df18, x='district', y='total_amount', title='Top 10 Districts by Transaction Amount',
               hover_data=['total_amount'], text_auto=True)
        st.plotly_chart(fig18)

# ✅ Query 19: Average Transaction Amount per State
        q19 = """SELECT state, AVG(transaction_amount) AS avg_amount FROM map_transaction GROUP BY state"""
        df19 = pd.read_sql(q19, engine)
        fig19 = px.bar(df19, x='state', y='avg_amount', title='Average Transaction Amount per State',
               hover_data=['avg_amount'], text_auto=True)
        st.plotly_chart(fig19)

# ✅ Query 20: Transaction Count Yearly Trend
        q20 = """SELECT year, SUM(transaction_count) AS total_txns FROM map_transaction GROUP BY year ORDER BY year"""
        df20 = pd.read_sql(q20, engine)
        fig20 = px.line(df20, x='year', y='total_txns', markers=True,
                title='Transaction Count Yearly Trend', hover_data=['total_txns'], text='total_txns')
        st.plotly_chart(fig20)
    with st.expander("**5. User Engagement and Growth Strategy**"):
        # ✅ Query 21: Registered Users by State
        q21 = """SELECT state, SUM(registered_users) AS total_users FROM map_user GROUP BY state ORDER BY total_users DESC"""
        df21 = pd.read_sql(q21, engine)
        fig21 = px.bar(df21, x='state', y='total_users', title='Registered Users by State',
               hover_data=['total_users'], text_auto=True)
        st.plotly_chart(fig21)

# ✅ Query 22: Top 10 Districts by Registered Users
        q22 = """SELECT district, SUM(registered_users) AS total_users FROM map_user GROUP BY district ORDER BY total_users DESC LIMIT 10"""
        df22 = pd.read_sql(q22, engine)
        fig22 = px.bar(df22, x='district', y='total_users', title='Top 10 Districts by Registered Users',
               hover_data=['total_users'], text_auto=True)
        st.plotly_chart(fig22)

# ✅ Query 23: Quarterly Registered Users Over Time
        q23 = """SELECT year, quarter, SUM(registered_users) AS users FROM map_user GROUP BY year, quarter ORDER BY year, quarter"""
        df23 = pd.read_sql(q23, engine)
        fig23 = px.line(df23, x='quarter', y='users', color='year', markers=True,
                title='Quarterly Registered Users Over Time', hover_data=['users'], text='users')
        st.plotly_chart(fig23)

# ✅ Query 24: User Growth by State Over Years
        q24 = """SELECT year, state, SUM(registered_users) AS total_users FROM map_user GROUP BY year, state"""
        df24 = pd.read_sql(q24, engine)
        fig24 = px.bar(df24, x='state', y='total_users', color='year', barmode='group',
               title='User Growth by State Over Years', hover_data=['total_users'], text_auto=True)
        st.plotly_chart(fig24)

# ✅ Query 25: Top Districts per Year by User Registrations
        q25 = """SELECT year, district, SUM(registered_users) AS total_users FROM map_user GROUP BY year, district ORDER BY total_users DESC LIMIT 10"""
        df25 = pd.read_sql(q25, engine)
        fig25 = px.bar(df25, x='district', y='total_users', color='year',
               title='Top Districts per Year by User Registrations', hover_data=['total_users'], text_auto=True)
        st.plotly_chart(fig25)

        

    with st.expander("**6. Insurance Engagement Analysis**"):

# ✅ Query 26: Insurance Amount by State
        df26 = pd.read_sql("SELECT state, SUM(amount) AS total_amount FROM top_insurance GROUP BY state ORDER BY total_amount DESC", engine)
        fig26 = px.bar(df26, x='state', y='total_amount', title='Insurance Amount by State',
               hover_data=['total_amount'], text_auto=True)
        st.plotly_chart(fig26)

# ✅ Query 27: Top 10 Districts by Insurance Amount
        df27 = pd.read_sql("SELECT district, SUM(amount) AS total_amount FROM top_insurance GROUP BY district ORDER BY total_amount DESC LIMIT 10", engine)
        fig27 = px.bar(df27, x='district', y='total_amount', title='Top 10 Districts by Insurance Amount',
               hover_data=['total_amount'], text_auto=True)
        st.plotly_chart(fig27)

# ✅ Query 28: Top 10 Pincodes by Insurance Amount
        df28 = pd.read_sql("SELECT pincode, SUM(amount) AS total_amount FROM top_insurance WHERE pincode !='0' GROUP BY pincode ORDER BY total_amount DESC LIMIT 10", engine)
        fig28 = px.pie(df28, values='total_amount', names='pincode', title='Top 10 Pincodes by Insurance Amount',
               hover_data=['total_amount'])
        st.plotly_chart(fig28)

# ✅ Query 29: Insurance Transactions Over Time
        df29 = pd.read_sql("SELECT year, quarter, SUM(amount) AS total_amount FROM top_insurance GROUP BY year, quarter ORDER BY quarter asc", engine)
        fig29 = px.line(df29, x='quarter', y='total_amount', color='year', markers=True,
                title='Insurance Transactions Over Time', hover_data=['total_amount'], text='total_amount')
        st.plotly_chart(fig29)

# ✅ Query 30: Top Districts by Insurance per Year
        df30 = pd.read_sql("SELECT year, district, SUM(amount) AS total_amount FROM top_insurance GROUP BY year, district ORDER BY total_amount DESC LIMIT 10", engine)
        fig30 = px.bar(df30, x='district', y='total_amount', color='year',
               title='Top Districts by Insurance per Year', hover_data=['total_amount'], text_auto=True)
        st.plotly_chart(fig30)

    with st.expander(" **7. Transaction Analysis Across States and Districts**"):        

# ✅ Query 31: Total Transactions by State
        df31 = pd.read_sql("SELECT state, SUM(transaction_amount) AS total_amount FROM map_transaction GROUP BY state ORDER BY total_amount DESC", engine)
        fig31 = px.bar(df31, x='state', y='total_amount', title='Total Transactions by State',
               hover_data=['total_amount'], text_auto=True)
        st.plotly_chart(fig31, key='fig31')

# ✅ Query 32: Top 10 Districts by Transaction Amount
        df32 = pd.read_sql("SELECT district, SUM(transaction_amount) AS total_amount FROM map_transaction GROUP BY district ORDER BY total_amount DESC LIMIT 10", engine)
        fig32 = px.bar(df32, x='district', y='total_amount', title='Top 10 Districts by Transaction Amount',
               hover_data=['total_amount'], text_auto=True)
        st.plotly_chart(fig32, key='fig32')

# ✅ Query 33: Top 10 Pincodes by Transaction Amount
        df33 = pd.read_sql("SELECT pincode, SUM(amount) AS total_amount FROM top_transaction WHERE pincode!= '0' GROUP BY pincode ORDER BY total_amount DESC LIMIT 10", engine)
        fig33 = px.pie(df33, names='pincode', values='total_amount', title='Top 10 Pincodes by Transaction Amount',
               hover_data=['total_amount'])
        st.plotly_chart(fig33, key='fig33')

# ✅ Query 34: Yearly Transaction Amount (Nationwide)
        df34 = pd.read_sql("SELECT year, SUM(transaction_amount) AS total_amount FROM map_transaction GROUP BY year", engine)
        fig34 = px.bar(df34, x='year', y='total_amount', title='Yearly Transaction Amount (Nationwide)',
               hover_data=['total_amount'], text_auto=True)
        st.plotly_chart(fig34, key='fig34')

# ✅ Query 35: Top Districts by Yearly Transactions
        df35 = pd.read_sql("SELECT district, year, SUM(transaction_amount) AS total FROM map_transaction GROUP BY district, year ORDER BY total DESC LIMIT 10", engine)
        fig35 = px.bar(df35, x='district', y='total', color='year', title='Top Districts by Yearly Transactions',
               hover_data=['total'], text_auto=True)
        st.plotly_chart(fig35, key='fig35')

    with st.expander("**8. User Registration Analysis**"):  

# ✅ Query 36: User Registrations by State
        df36 = pd.read_sql("SELECT state, SUM(registered_users) AS total_users FROM map_user GROUP BY state ORDER BY total_users DESC", engine)
        fig36 = px.bar(df36, x='state', y='total_users', title='User Registrations by State',
               hover_data=['total_users'], text_auto=True)
        st.plotly_chart(fig36, key='fig36')

# ✅ Query 37: Top 10 Districts by User Registrations
        df37 = pd.read_sql("SELECT district, SUM(registered_users) AS total_users FROM map_user GROUP BY district ORDER BY total_users DESC LIMIT 10", engine)
        fig37 = px.bar(df37, x='district', y='total_users', title='Top 10 Districts by User Registrations',
               hover_data=['total_users'], text_auto=True)
        st.plotly_chart(fig37, key='fig37')

# ✅ Query 38: Top 10 Pincodes by User Registrations
        df38 = pd.read_sql("SELECT pincode, SUM(registeredusers) AS total_users FROM top_user WHERE pincode!='0' GROUP BY pincode ORDER BY total_users DESC LIMIT 10", engine)
        fig38 = px.pie(df38, names='pincode', values='total_users', title='Top 10 Pincodes by User Registrations',
               hover_data=['total_users'])
        st.plotly_chart(fig38, key='fig38')

# ✅ Query 39: Quarterly User Registration Trends
        df39 = pd.read_sql("SELECT year, quarter, SUM(registered_users) AS users FROM map_user GROUP BY year, quarter ORDER BY year, quarter", engine)
        fig39 = px.line(df39, x='quarter', y='users', color='year', markers=True,
                title='Quarterly User Registration Trends', hover_data=['users'], text='users')
        st.plotly_chart(fig39, key='fig39')

# ✅ Query 40: User Growth by State and Year
        df40 = pd.read_sql("SELECT state, year, SUM(registered_users) AS users FROM map_user GROUP BY state, year ORDER BY users DESC", engine)
        fig40 = px.bar(df40, x='state', y='users', color='year', title='User Growth by State and Year',
               hover_data=['users'], text_auto=True)
        st.plotly_chart(fig40, key='fig40')

    with st.expander("**9. Insurance Transactions Analysis**"):  

# ✅ Query 41: Insurance Transactions by State
        df41 = pd.read_sql("SELECT state, SUM(amount) AS total_amount FROM top_insurance GROUP BY state ORDER BY total_amount DESC", engine)
        fig41 = px.bar(df41, x='state', y='total_amount', title='Insurance Transactions by State',
               hover_data=['total_amount'], text_auto=True)
        st.plotly_chart(fig41, key='fig41')

# ✅ Query 42: Top 10 Districts in Insurance Transactions
        df42 = pd.read_sql("SELECT district, SUM(amount) AS total_amount FROM top_insurance GROUP BY district ORDER BY total_amount DESC LIMIT 10", engine)
        fig42 = px.bar(df42, x='district', y='total_amount', title='Top 10 Districts in Insurance Transactions',
               hover_data=['total_amount'], text_auto=True)
        st.plotly_chart(fig42, key='fig42')

# ✅ Query 43: Top 10 Pincodes in Insurance Transactions
        df43 = pd.read_sql("SELECT pincode, SUM(amount) AS total_amount FROM top_insurance WHERE pincode != '0' GROUP BY pincode ORDER BY total_amount DESC LIMIT 10", engine)
        fig43 = px.pie(df43, names='pincode', values='total_amount', title='Top 10 Pincodes in Insurance Transactions',
               hover_data=['total_amount'])
        st.plotly_chart(fig43, key='fig43')

# ✅ Query 44: Insurance Trends Over Time
        df44 = pd.read_sql("SELECT year, quarter, SUM(amount) AS total_amount FROM top_insurance GROUP BY year, quarter ORDER BY quarter", engine)
        fig44 = px.line(df44, x='quarter', y='total_amount', color='year', markers=True,
                title='Insurance Trends Over Time', hover_data=['total_amount'], text='total_amount')
        st.plotly_chart(fig44, key='fig44')

# ✅ Query 45: Top Districts in Insurance by Year
        df45 = pd.read_sql("SELECT year, district, SUM(amount) AS total FROM top_insurance GROUP BY year, district ORDER BY total DESC LIMIT 10", engine)
        fig45 = px.bar(df45, x='district', y='total', color='year', title='Top Districts in Insurance by Year',
               hover_data=['total'], text_auto=True)
        st.plotly_chart(fig45, key='fig45')

        st.markdown('***')
# Add project insights and recommendations as a multi-line Python comment for use within a program


with tab3:
      
        st.title("📄 :violet[_**Raw Data**_]")

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
        st.title(":violet[**INSIGHT & RECOMMENDS**]")
        st.markdown('----')
        col1, col2 = st.columns(2)

        with col1:
            st.header("💡**Insights**")
            st.write("""
1. Transaction Trends:
   * High-performing states - Maharashtra, Karnataka, and Tamil Nadu.
   * Transactions have grown steadily year-over-year.
   * Some temporary declines found(Manipur,Chandigar on 2023).

2. Payment Type Patterns:
   * Top payments by Peer-to-Peer (P2P) and Merchant transactions.
   * UPI is the primary method used.

3. Device & User Behavior:
   * Most users access the app through Samsung, Xiaomi, and Vivo devices.
   * Some brands have higher app-open ratios, indicating strong engagement.

4. Insurance Penetration:
   * Urban states dominate insurance adoption.
   * Insurance counts remain lower than total transactions.

5 User Engagement:
   * Consistent growth in app opens and registered users.
   * Some emerging districts show high potential for expansion.

6. Geographic Trends:
   * Metro cities lead in digital activity.
   * Rural and North-Eastern regions still show relatively low adoption.""")

        with col2:
            st.header("✅**Recommendations**")
            st.write("""
1. Market Expansion:
   * Prioritize low-performance regions (e.g.,Andhaman, Lakshadweep, NE states).
   * Use successful district strategies to replicate growth elsewhere.

2. Product Strategy:
   * Promote insurance and financial tools in underserved markets.
   * Optimize app performance for mid-range and budget smartphones.

3. Technology Enhancements:
   * Improve UI for mobile and map resolution for better experience.
   * Make User - Friendly for beginners to pay bills


4. Policy Suggestions:
   * Create Campaighns regards Insurance policy & Give awarness in rural areas.
   * Tie-up with insurance partners.
   * Partner with local governments to drive UPI awareness and training.""")

        st.markdown('----')

st.balloons()
