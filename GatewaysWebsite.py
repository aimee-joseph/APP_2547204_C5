import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from wordcloud import WordCloud
import os
os.environ["SHAPE_RESTORE_SHX"] = "YES"


st.set_page_config(page_title = "Gateways Website", layout = "wide")
st.title("Welcome to the Gateways Webpage!")

df = pd.read_csv("FestDataset.csv")
data = df

tab1, tab2, tab3 = st.tabs(["Participation Analysis", "Feedback Analysis", "Insights"])

with tab1:
    st.header("Analysis of participation trends")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Event-wise Participation")
        fig, ax = plt.subplots()
        data["Event Type"].value_counts().plot(kind = "bar", ax = ax)
        st.pyplot(fig)

    with col2:
        st.subheader("College-wise Participation")
        fig, ax = plt.subplots()
        data["College"].value_counts().plot(kind = "bar", ax = ax)
        st.pyplot(fig)

    st.subheader("State-wise Participation Map")
    state_counts = data["State"].value_counts().reset_index()
    state_counts.columns = ["State", "count"]
    india_map = gpd.read_file("./India_State_Boundary.shp")
    india_map["State_Name"] = india_map["State_Name"].str.upper()
    state_counts["State"] = state_counts["State"].str.upper()
    merged = india_map.merge(state_counts, left_on = "State_Name", right_on = "State", how = "left")
    merged["count"] = merged["count"].fillna(0)
    fig, ax = plt.subplots(figsize = (8, 8))
    merged.plot(column="count", cmap = "OrRd", legend = True, ax = ax)
    ax.set_title("State-wise Participation in India")
    ax.axis("off")
    st.pyplot(fig)
    
with tab2:
    st.title("Feedback Analysis")

    selected_event_text = st.selectbox("Select Event Type for Feedback Analysis", ["All"] + list(df["Event Type"].unique()))
    if selected_event_text == "All":
        event_feedback = df["Feedback on Fest"]
    else:
        event_feedback = df[df["Event Type"] == selected_event_text]["Feedback on Fest"]
    text = " ".join(event_feedback)
    st.subheader(f"Word Cloud - {selected_event_text}")
    wordcloud = WordCloud(width = 800, height = 400, background_color = "white").generate(text)
    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation = "bilinear")
    ax.axis("off")
    st.pyplot(fig)

    st.subheader("Rating Distribution")
    fig, ax = plt.subplots()
    rating_counts = data["Rating"].value_counts()
    fig, ax = plt.subplots()
    rating_counts.plot(kind = "pie", autopct = '%1.1f%%', ax = ax)
    ax.set_ylabel("")
    ax.set_title("Ratings Breakdown")
    st.pyplot(fig)

    st.subheader("Average Rating per College")
    avg_rating_college = data.groupby("College")["Rating"].mean().sort_values(ascending = False)
    fig, ax = plt.subplots()
    avg_rating_college.plot(kind = "bar", ax = ax)
    ax.set_ylabel("Average Rating")
    st.pyplot(fig)
    

with tab3:
    st.title("Insights")

    st.subheader("Filter Data")

    col1, col2 = st.columns(2)

    selected_event = col1.selectbox("Filter by Event", ["All"] + list(data["Event Type"].unique()))
    selected_college = col2.selectbox("Filter by College", ["All"] + list(data["College"].unique()))

    filtered_data = data.copy()
    if selected_event != "All":
        filtered_data = filtered_data[filtered_data["Event Type"] == selected_event]
    if selected_college != "All":
        filtered_data = filtered_data[filtered_data["College"] == selected_college]

    st.subheader("Overall Insights")

    col1, col2, col3, col4 = st.columns(4)

    avg_rating = filtered_data["Rating"].mean()
    col1.metric("Total Participants", len(filtered_data))
    col2.metric("Total Events", filtered_data["Event Type"].nunique())
    col3.metric("Avg Rating", round(avg_rating, 2), delta=round(avg_rating - 3, 2))
    col4.metric("Top Event", filtered_data["Event Type"].value_counts().idxmax())
    st.divider()

    st.subheader("Event Performance Insights")
    avg_rating_event = filtered_data.groupby("Event Type")["Rating"].mean().sort_values(ascending=False)
    top_event = avg_rating_event.idxmax()
    low_event = avg_rating_event.idxmin()
    st.success(f"Top Rated Event: {top_event}")
    if avg_rating_event.min() < 3:
        st.warning(f"Lowest Rated Event Needs Improvement: {low_event}")
    else:
        st.info(f"Lowest Rated Event: {low_event}")
    st.divider()

    st.subheader("College Performance")
    avg_rating_college = filtered_data.groupby("College")["Rating"].mean().sort_values(ascending=False)
    top_college = avg_rating_college.idxmax()
    if avg_rating_college.max() >= 4:
        st.success(f"Best College (Excellent Performance): {top_college}")
    else:
        st.info(f"Best College: {top_college}")
    st.divider()

    st.subheader("Geographical Insight")
    top_state = filtered_data["State"].value_counts().idxmax()
    count = filtered_data["State"].value_counts().max()
    st.info(f"{top_state} has the highest participation with {count} participants")
    st.divider()

    st.subheader("Participation vs Rating")
    event_participation = filtered_data["Event Type"].value_counts()
    event_rating = filtered_data.groupby("Event Type")["Rating"].mean()

    comparison = pd.DataFrame({"Participation": event_participation, "Avg Rating": event_rating})

    st.dataframe(comparison)
    high_part_low_rating = comparison[
        (comparison["Participation"] > comparison["Participation"].mean()) &
        (comparison["Avg Rating"] < comparison["Avg Rating"].mean())
    ]

    if not high_part_low_rating.empty:
        st.warning("Some popular events have below-average ratings. These need improvement.")
    else:
        st.success("Popular events are also well-rated!")
    
    with st.expander("See Detailed Data"):
        st.dataframe(filtered_data)