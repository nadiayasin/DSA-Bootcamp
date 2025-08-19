import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


df = pd.read_csv('railway.csv')
st.set_page_config(page_title="Maven Rail Challenge Dashboard", layout="wide")
st.title("Railway Data Analysis Dashboard ")
#st.write(df.columns)
 # تنظيف النصوص
df['Reason for Delay'] = df['Reason for Delay'].astype(str).str.strip().str.lower()
df['Reason for Delay'] = df['Reason for Delay'].str.title()
# تحويل الأعمدة
df['Departure Time'] = pd.to_datetime(df['Departure Time'], errors='coerce')
df['Arrival Time'] = pd.to_datetime(df['Arrival Time'], errors='coerce')
df['Actual Arrival Time'] = pd.to_datetime(df['Actual Arrival Time'], errors='coerce')
df['Delay_minutes'] = (df['Actual Arrival Time'] - df['Arrival Time']).dt.total_seconds() / 60

   # حساب مدة التأخير
df['Delay_minutes'] = (df['Actual Arrival Time'] - df['Arrival Time']).dt.total_seconds() / 60

# استخراج ساعة المغادرة (لـ Heatmap)
df['Departure Hour'] = df['Departure Time'].dt.hour

# فلاتر
st.sidebar.header("Filters")
station = st.sidebar.selectbox("Departure Station", ["All"] + list(df['Departure Station'].dropna().unique()))
reason = st.sidebar.selectbox("Reason for Delay", ["All"] + list(df['Reason for Delay'].dropna().unique()))

data = df.copy()
if station != "All":
    data = data[data['Departure Station'] == station]
if reason != "All":
    data = data[data['Reason for Delay'] == reason]

# KPIs
st.subheader("📊 Performance Overview")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Journeys", len(data))
col2.metric("Average Delay (min)", f"{data['Delay_minutes'].mean():.2f}")
col3.metric("Total Revenue (£)", f"{data['Price'].sum():,.0f}")
on_time = (data['Delay_minutes'] <= 5).mean() * 100
col4.metric("On-time %", f"{on_time:.1f}%")

# أسباب التأخير
st.subheader("Delay Reasons")
delay_counts = data['Reason for Delay'].value_counts().head(10)
fig, ax = plt.subplots()
sns.barplot(y=delay_counts.index, x=delay_counts.values, ax=ax)
ax.set_title("Top Delay Reasons")
st.pyplot(fig)

# Boxplot للتأخيرات حسب السبب
st.subheader("Delay Distribution by Reason")
if 'Delay_minutes' in data.columns and 'Reason for Delay' in data.columns:
    fig_box, ax_box = plt.subplots(figsize=(12,6))
    sns.boxplot(data=data, x='Reason for Delay', y='Delay_minutes', ax=ax_box)
    ax_box.set_title("Delay Duration Distribution by Reason")
    ax_box.set_ylabel("Delay (minutes)")
    ax_box.set_xlabel("Reason for Delay")
    ax_box.tick_params(axis='x', rotation=45)
    st.pyplot(fig_box)

# المحطات الأكثر تأخيرًا
st.subheader("Stations with Most Delays")
if 'Delay_minutes' in data.columns:
    station_delays = data.groupby('Departure Station')['Delay_minutes'].mean().sort_values(ascending=False).head(10)
    fig2, ax2 = plt.subplots()
    sns.barplot(x=station_delays.values, y=station_delays.index, ax=ax2)
    ax2.set_title("Avg Delay per Station")
    st.pyplot(fig2)

# الإيرادات حسب فئة التذكرة
st.subheader("Revenue by Ticket Class")
revenue_ticket = data.groupby('Ticket Class')['Price'].sum().sort_values(ascending=False)
fig3, ax3 = plt.subplots()
sns.barplot(x=revenue_ticket.values, y=revenue_ticket.index, ax=ax3)
ax3.set_title("Revenue by Ticket Class")
st.pyplot(fig3)

# الطرق الأكثر شيوعًا
st.subheader("Top Routes")
routes = data.groupby(['Departure Station','Arrival Destination']).size().reset_index(name='Trips')
top_routes = routes.sort_values('Trips', ascending=False).head(10)
fig4, ax4 = plt.subplots()
sns.barplot(x=top_routes['Trips'], y=top_routes['Departure Station'] + " → " + top_routes['Arrival Destination'], ax=ax4)
ax4.set_title("Most Common Routes")
st.pyplot(fig4)

# Heatmap للأوقات الأكثر ازدحامًا
st.subheader("⏰ Busiest Hours Heatmap")
if 'Departure Hour' in data.columns and 'Departure Station' in data.columns:
    pivot = data.pivot_table(index='Departure Hour', columns='Departure Station', values='Transaction ID', aggfunc='count').fillna(0)
    fig5, ax5 = plt.subplots(figsize=(12,6))
    sns.heatmap(pivot, cmap="YlGnBu", ax=ax5)
    ax5.set_title("Journeys per Hour and Station")
    st.pyplot(fig5)
