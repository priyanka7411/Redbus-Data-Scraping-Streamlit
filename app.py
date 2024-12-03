import pandas as pd
import streamlit as st
import mysql.connector
from mysql.connector import Error
import plotly.express as px

# Connect to the MySQL database
def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",  # Database host 
            user="root",       # MySQL username
            password="pochi2002*",  # MySQL password
            database="Red_Bus_Scrap"  # Database name
        )
        if connection.is_connected():
            return connection
    except Error as e:
        st.error(f"Error connecting to database: {e}")
        return None
    

# Create a connection
connection = create_connection()

# SQL query to fetch bus data
query = """
SELECT route_name, route_link, busname, bustype, departing_time, duration,
       reaching_time, star_rating, price, seats_available
FROM bus_routes;
"""

if connection:
    # Fetch data from the database
    df_bus = pd.read_sql(query, connection)

    # Close the connection
    connection.close()
else:
    df_bus = pd.DataFrame()

# Create a navigation menu to switch between Home and Select Bus options
page = st.sidebar.radio("Navigate", ["Home", "Select Bus"])

# --- Home Page ---
if page == "Home":
    st.markdown("""
        <div style="text-align: center; padding-top: 50px;">
            <h2 style="font-size: 50px; color: #FF6347; font-weight: bold;">Redbus Data Explorer</h2>
            <p style="font-size: 22px; color: #2E8B57;">Explore bus routes, prices, ratings, and seat availability!</p>
            <p style="font-size: 18px; color: #696969; font-style: italic;">Find your perfect bus with customized filters and visual insights.</p>
        </div>
    """, unsafe_allow_html=True)

    # --- Data Visualization on Home Page ---
    st.markdown("<h4 style='text-align: center;'>📊 Overview of Bus Data</h4>", unsafe_allow_html=True)

    if not df_bus.empty:
        # Visualization: Average Price by Bus Type (Bar Chart)
        avg_price_by_bustype = df_bus.groupby('bustype')['price'].mean().reset_index()
        fig_avg_price = px.bar(avg_price_by_bustype, x="bustype", y="price", 
                               title="Average Price by Bus Type", 
                               labels={"price": "Average Price", "bustype": "Bus Type"},
                               color='bustype')
        st.plotly_chart(fig_avg_price, use_container_width=True)

        # Visualization: Bus Availability by Type (Pie Chart)
        availability_by_bustype = df_bus.groupby('bustype')['seats_available'].sum().reset_index()
        fig_pie_availability = px.pie(availability_by_bustype, values='seats_available', names='bustype', 
                                      title="Bus Availability by Type", hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_pie_availability, use_container_width=True)

    else:
        st.write("No data available to display.")

# --- Select Bus Page ---
elif page == "Select Bus":
    st.sidebar.image("/Users/priyankamalavade/Desktop/redbus_scraping/images/rb.png", width=100)  # Adjust width as needed
    
    st.sidebar.markdown("## 🛠️ **Bus Filters**")

    # Route Filter (searchable dropdown in sidebar)
    route = st.sidebar.selectbox('Select Route', df_bus['route_name'].unique(), help="Choose the bus route you're interested in.")

    # Bus Type Filter
    bus_type = st.sidebar.selectbox('Select Bus Type', df_bus['bustype'].unique(), help="Choose the type of bus (AC, Non-AC, Sleeper, etc.).")
    
    # Price Range Filter (slider in sidebar)
    price_range = st.sidebar.slider('Price Range', int(df_bus['price'].min()), int(df_bus['price'].max()), 
                            (int(df_bus['price'].min()), int(df_bus['price'].max())), help="Set your price range.")

    # Star Rating Filter (slider in sidebar)
    rating_range = st.sidebar.slider('Star Rating', 1, 5, (1, 5), help="Filter buses by customer rating.")
    
    # Checkbox to filter buses with available seats
    seat_availability = st.sidebar.checkbox('Show only buses with available seats', help="Only show buses with available seats.")

    # Sort results by selected option
    sort_by = st.sidebar.selectbox('Sort By', ['Price: Low to High', 'Price: High to Low', 'Rating: High to Low'], 
                           help="Sort results by price or rating.")

    # Filter the data based on selected filters
    filtered_data = df_bus[
        (df_bus['route_name'] == route) &
        (df_bus['bustype'] == bus_type) &
        (df_bus['price'].between(price_range[0], price_range[1])) &
        (df_bus['star_rating'].between(rating_range[0], rating_range[1]))
    ]
    
    if seat_availability:
        filtered_data = filtered_data[filtered_data['seats_available'] > 0]

    # Apply sorting
    if sort_by == 'Price: Low to High':
        filtered_data = filtered_data.sort_values(by='price', ascending=True)
    elif sort_by == 'Price: High to Low':
        filtered_data = filtered_data.sort_values(by='price', ascending=False)
    else:
        filtered_data = filtered_data.sort_values(by='star_rating', ascending=False)

    # Show results
    st.markdown(f"**Found {len(filtered_data)} buses matching your criteria**")

    if not filtered_data.empty:
        # Display filtered data in a table
        st.dataframe(filtered_data)

        # Download button for filtered data
        csv_data = filtered_data.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download Data as CSV", data=csv_data, file_name="filtered_bus_data.csv", mime="text/csv")

        # --- Data Visualization for filtered data ---
        st.markdown("<h4 style='text-align: center;'>📊 Visual Insights from Filtered Data</h4>", unsafe_allow_html=True)

        # Price Distribution (Histogram)
        fig_hist = px.histogram(filtered_data, x="price", nbins=20, title="Price Distribution")
        st.plotly_chart(fig_hist, use_container_width=True)

        # Bus Type Distribution (Pie Chart)
        bus_type_dist = filtered_data['bustype'].value_counts()
        fig_pie = px.pie(values=bus_type_dist, names=bus_type_dist.index, title="Bus Type Distribution")
        st.plotly_chart(fig_pie, use_container_width=True)

        # Price vs Star Rating (Scatter Plot)
        fig_scatter = px.scatter(filtered_data, x="price", y="star_rating", color="bustype", title="Price vs Star Rating")
        st.plotly_chart(fig_scatter, use_container_width=True)

    else:
        st.write("No buses match your criteria. Please adjust your filters.")
