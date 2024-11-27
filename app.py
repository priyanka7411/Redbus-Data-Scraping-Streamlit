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
            password="pochi2002*",  #  MySQL password
            database="Red_Bus_Scrap"  # database name
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
            <h2 style="font-size: 60px; color: #FF6347; font-weight: bold;">Redbus Data Scraping and Filtering with Streamlit Application</h2>
            <p style="font-size: 24px; color: #2E8B57;">Explore bus routes, prices, ratings, and seat availability in just a few clicks!</p>
            <p style="font-size: 18px; color: #696969; font-style: italic;">Find your perfect bus with customized filters.</p>
        </div>
        
        <div style="text-align: center; margin-top: 50px;">
            <h2 style="color: #32CD32; font-size: 36px;">How It Works</h2>
            <p style="font-size: 20px; color: #708090;">1. Filter buses by route, price, and rating.</p>
            <p style="font-size: 20px; color: #708090;">2. View detailed bus information, including price, availability, and timings.</p>
            <p style="font-size: 20px; color: #708090;">3. Visualize data with easy-to-understand charts.</p>
        </div>
    """, unsafe_allow_html=True)

    # --- Data Visualization on Home Page ---
    st.markdown("<h4 style='text-align: center;'>📊 Bus Data Overview</h4>", unsafe_allow_html=True)

    if not df_bus.empty:
        # Average Price by Bus Type (Bar Chart)
        avg_price_by_bustype = df_bus.groupby('bustype')['price'].mean().reset_index()
        fig_avg_price = px.bar(avg_price_by_bustype, x="bustype", y="price", 
                               title="Average Price by Bus Type", 
                               labels={"price": "Average Price", "bustype": "Bus Type"})
        st.plotly_chart(fig_avg_price)

        # Bus Availability by Type (Pie Chart)
        availability_by_bustype = df_bus.groupby('bustype')['seats_available'].sum().reset_index()
        fig_pie_availability = px.pie(availability_by_bustype, values='seats_available', names='bustype', 
                                      title="Bus Availability by Type")
        st.plotly_chart(fig_pie_availability)

    else:
        st.write("No data available to display.")


# --- Select Bus Page ---
elif page == "Select Bus":
    # Display the Redbus logo at the top of the sidebar
    st.sidebar.image("/Users/priyankamalavade/Desktop/redbus_scraping/images/rb.png", width=50)  # Adjust the width as needed
    
    st.sidebar.markdown("## 🛠️ Bus Filters")

    # Route Filter (searchable dropdown in sidebar)
    route = st.sidebar.selectbox('Select Route', df_bus['route_name'].unique(), help="Choose the bus route you are interested in.")

    # Single Selection for Bus Type (in sidebar)
    bus_type = st.sidebar.selectbox('Select Bus Type', df_bus['bustype'].unique(), help="Select the type of bus (AC, Non-AC, Sleeper, etc.).")
    
    # Price Range Filter (in sidebar)
    price_range = st.sidebar.slider('Select Price Range', int(df_bus['price'].min()), int(df_bus['price'].max()), 
                            (int(df_bus['price'].min()), int(df_bus['price'].max())), help="Set the price range for your search.")

    # Star Rating Filter (in sidebar)
    rating_range = st.sidebar.slider('Select Star Rating Range', 1, 5, (1, 5), help="Filter buses based on customer ratings.")
    
    # Sort by Feature (in sidebar)
    sort_by = st.sidebar.selectbox('Sort Results By', ['Price: Low to High', 'Price: High to Low', 'Rating: High to Low'], 
                           help="Choose how you want to sort the results.")

    # Additional Filter: Seat Availability (in sidebar)
    seat_availability = st.sidebar.checkbox('Show only buses with available seats', help="Filter buses with seat availability.")

    # Apply Filters
    filtered_data = df_bus[
        (df_bus['route_name'] == route) &
        (df_bus['bustype'] == bus_type) &  # Single bus type selection
        (df_bus['price'].between(price_range[0], price_range[1])) &
        (df_bus['star_rating'].between(rating_range[0], rating_range[1]))
    ]
    
    if seat_availability:
        filtered_data = filtered_data[filtered_data['seats_available'] > 0]

    # Sort the filtered data based on the sort_by option
    if sort_by == 'Price: Low to High':
        filtered_data = filtered_data.sort_values(by='price', ascending=True)
    elif sort_by == 'Price: High to Low':
        filtered_data = filtered_data.sort_values(by='price', ascending=False)
    else:  # 'Rating: High to Low'
        filtered_data = filtered_data.sort_values(by='star_rating', ascending=False)

    # Show the number of results found
    st.markdown(f"**Found {len(filtered_data)} buses** based on your filters.", unsafe_allow_html=True)

    # Section for bus data display
    if not filtered_data.empty:
        st.write("Here are the buses matching your criteria:")
        st.dataframe(filtered_data)

        # Download Filtered Data as CSV
        csv_data = filtered_data.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download Data as CSV", data=csv_data, file_name="filtered_bus_data.csv", mime="text/csv")

        # --- Data Visualization Section ---
        st.markdown("<h4 style='text-align: center;'>📊 Data Visualization</h4>", unsafe_allow_html=True)

        # Price Distribution (Histogram)
        fig_hist = px.histogram(filtered_data, x="price", nbins=20, title="Price Distribution of Buses")
        st.plotly_chart(fig_hist)

        # Bus Type Distribution (Pie Chart)
        bus_type_dist = filtered_data['bustype'].value_counts()
        fig_pie = px.pie(values=bus_type_dist, names=bus_type_dist.index, title="Bus Type Distribution")
        st.plotly_chart(fig_pie)

        # Price vs Star Rating (Scatter Plot)
        fig_scatter = px.scatter(filtered_data, x="price", y="star_rating", color="bustype", title="Price vs Star Rating")
        st.plotly_chart(fig_scatter)
        
    else:
        st.write("No buses match your criteria. Please adjust your filters and try again.")
