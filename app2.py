import pandas as pd
#import mysql.connector
import streamlit as st
#import plotly.express as px
import os

# Function to load all bus routes data by concatenating state-wise CSVs
def load_all_bus_data():
    file_path_dict = {
        "Kerala": "./scraped bus details/df.kerala.csv",
        "Andhra Pradesh": "./scraped bus details/df.andhra.csv",
        "Telangana": "./scraped bus details/df.telangana.csv",
        "Goa": "./scraped bus details/df.GOA.csv",
        "Rajasthan": "./scraped bus details/df.rajastan.csv",
        "Bihar": "./scraped bus details/df.bihar.csv",
        "South Bengal": "./scraped bus details/df.south_bengal.csv",
        "Himachal Pradesh": "./scraped bus details/df.himachalpradesh.csv",
        "Assam": "./scraped bus details/df.assam.csv",
        "Uttar Pradesh": "./scraped bus details/df.up.csv",
        "West Bengal": "./scraped bus details/df.wb.csv",
        "Chandigarh": "./scraped bus details/df.chandigarh.csv"
        
    }
    
    # Load and concatenate all datasets into one DataFrame
    df_list = [pd.read_csv(file_path) for file_path in file_path_dict.values()]
    return pd.concat(df_list, ignore_index=True)

# Function to load bus routes based on selected state
def load_bus_routes(state):
    file_path_dict = {
        "Kerala": "./scraped bus details/df.kerala.csv",
        "Andhra Pradesh": "./scraped bus details/df.andhra.csv",
        "Telangana": "./scraped bus details/df.telangana.csv",
        "Goa": "./scraped bus details/df.GOA.csv",
        "Rajasthan": "./scraped bus details/df.rajastan.csv",
        "Bihar": "./scraped bus details/df.bihar.csv",
        "South Bengal": "./scraped bus details/df.south_bengal.csv",
        "Himachal Pradesh": "./scraped bus details/df.himachalpradesh.csv",
        "Assam": "./scraped bus details/df.assam.csv",
        "Uttar Pradesh": "./scraped bus details/df.up.csv",
        "West Bengal": "./scraped bus details/df.wb.csv",
        "Chandigarh": "./scraped bus details/df.chandigarh.csv"
    }
    
    # Load the CSV file based on state
    df = pd.read_csv(file_path_dict[state])
    # Return the list of routes
    return df['Route_name'].tolist()

# Function to connect to MySQL and filter based on bus type, fare, rating, etc.
def type_and_fare(bus_type, fare_range, rate_range, route_name, departure_time, seat_availability, sort_by):
    conn = mysql.connector.connect(host="localhost", user="root", password="pochi2002*", database="Red_Bus_Scrap")
    my_cursor = conn.cursor()

    # Define bus type condition based on selected type
    bus_type_option = {
        "sleeper": "bustype LIKE '%Sleeper%'",
        "semi-sleeper": "bustype LIKE '%Semi Sleeper%'",
        "A/C": "bustype LIKE '%A/C%'",
        "NON A/C": "bustype LIKE '%NON A/C%'",
        "seater": "bustype LIKE '%Seater%'",
        "others": "bustype NOT LIKE '%Sleeper%' AND bustype NOT LIKE '%Semi-Sleeper%' AND bustype NOT LIKE '%Seater%' AND bustype NOT LIKE '%A/C%' AND bustype NOT LIKE '%NON A/C%'"
    }

    # Define rating range
    rate_min, rate_max = 0, 5
    if rate_range == 5:
        rate_min, rate_max = 4.2, 5
    elif rate_range == 4:
        rate_min, rate_max = 3.0, 4.2
    elif rate_range == 3:
        rate_min, rate_max = 2.0, 3.0
    elif rate_range == 2:
        rate_min, rate_max = 1.0, 2.0
    elif rate_range == 1:
        rate_min, rate_max = 0, 1.0

    # SQL query for filtering
    sqlquery = f"""
        SELECT * FROM  bus_routes
        WHERE price <= {fare_range}
        AND route_name = '{route_name}'
        AND {bus_type_option[bus_type]}
        AND departing_time >= '{departure_time}'
        AND star_rating BETWEEN {rate_min} and {rate_max}
        ORDER BY price, departing_time DESC
    """

    my_cursor.execute(sqlquery)
    out = my_cursor.fetchall()
    conn.close()

    # Return filtered data as a DataFrame
    df_result = pd.DataFrame(out, columns=[
        "ID", "Route_name", "Route_link", "Bus_name", "Bus_type", "Departing_time", "Total_duration", "End_time", "Ratings", "Price", "Seats_Available"
    ])
    return df_result


# Sidebar and Main Menu


# Navigation between Home and Filtering Page
page = st.sidebar.radio("Select a Page", ["Home", "Filter Buses"])

# --- Home Page ---
if page == "Home":
    # Load all bus data
    #df_bus = load_all_bus_data()
    

    # Header with custom background and styling
    st.markdown("""
        <div>
            <h2 style="font-size: 50px; color: #FF6347; font-weight: bold">Redbus Data Explorer</h2>
            <p style="font-size: 22px; color: #2E8B57;">Explore bus routes, prices, ratings, and seat availability!</p>
            <p style="font-size: 18px; color: #696969; font-style: italic;">Find your perfect bus with customized filters and visual insights.</p>
            <p style="font-size: 18px; color: #2F4F4F; text-align: left; font-style: normal;">
                <strong>Project Overview:</strong><br>
                This project is designed to scrape and analyze bus route data from Redbus, enabling users to filter buses based on criteria such as bus type, fare range, ratings, and seat availability. The platform allows for interactive exploration of bus options across multiple states, with visualizations to support data-driven decision-making.<br><br>
                <strong>Key Technologies:</strong><br>
                Python (Pandas, Plotly), Streamlit, MySQL, Web Scraping (Selenium), Data Visualization, SQL Database.
            </p>
        </div>
    """, unsafe_allow_html=True)
    

    st.markdown("<h4 style='text-align: center;'>Overview of Bus Data</h4>", unsafe_allow_html=True)

#visualization
    folder_path = './scraped_all_required_bus_details'

# Load all CSV files from the folder
    dataframes = []
    for file in os.listdir(folder_path):
        if file.endswith('.csv'):
            file_path = os.path.join(folder_path, file)
            df = pd.read_csv(file_path)
            dataframes.append(df)

# Combine all the dataframes into one
    df_combined = pd.concat(dataframes, ignore_index=True)



#Bar chart==Count of bus routes by route name(compare discrete categories or groups of data)
    if 'Route_name' in df_combined.columns:
        fig = px.bar(df_combined, x='Route_name', title="Count of Bus Routes by Route Name")
        st.plotly_chart(fig)
#pie chart(represent the proportion of categories in a dataset )
    if 'Bus_type' in df_combined:
        fig = px.pie(df_combined, names='Bus_type', title="Distribution of Bus Types")
        st.plotly_chart(fig)
#Seat availability distribution(histogram)(visualize the distribution of a continuous variable)
    if 'Seats_Available' in df_combined:
        fig = px.histogram(df_combined, x='Seats_Available', nbins=50, title="Seat Availability Distribution")
        st.plotly_chart(fig)
#Price Distribution(Histogram)
    if 'Price' in df_combined.columns:
       fig = px.histogram(df_combined, x='Price', nbins=50, title="Price Distribution of Bus Tickets")
       st.plotly_chart(fig)



# --- Filtering Page ---
if page == "Filter Buses":
    st.sidebar.markdown("## 🛠️ **Bus Filters**")
    st.sidebar.image("./images/rb.png", width=100)

    # Select state
    state = st.sidebar.selectbox("Select State", [
        "Kerala", "Andhra Pradesh", "Telangana", "Goa", "Rajasthan", "Bihar", "South Bengal", 
        "Himachal Pradesh", "Assam", "Uttar Pradesh", "West Bengal", "Chandigarh"
    ])

    # Load the routes for the selected state
    routes = load_bus_routes(state)

    # Select bus route
    route_name = st.sidebar.selectbox("Select Bus Route", routes)

    # Select filters
    bus_type = st.sidebar.radio("Select Bus Type", ("sleeper", "semi-sleeper", "A/C", "NON A/C", "seater", "others"))
    fare_range = st.sidebar.slider("Fare Range", min_value=100, max_value=5000, value=1000)
    rate_range = st.sidebar.slider("Rating Range", 1, 5, 4)
    departure_time = st.sidebar.text_input("Enter departure time in HH:MM format", "00:00")
    seat_availability = st.sidebar.radio("Seat Availability", ("Available Only", "Show All"))
    sort_by = st.sidebar.radio("Sort By", ("price", "departure time", "ratings"))
    
    # Load filtered data only when the filter button is clicked
    #if st.sidebar.button("Filter Buses"):
        # Load filtered data based on the selected filters
    df_filtered = type_and_fare(bus_type, fare_range, rate_range, route_name, departure_time, seat_availability, sort_by)
    st.markdown(f"**Found {len(df_filtered)} buses matching your criteria**")

        # Display filtered data
    st.dataframe(df_filtered)

        # Convert the filtered dataframe to CSV and create a download button
    csv_data = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(label="Download Data as CSV", data=csv_data, file_name="filtered_bus_data.csv", mime="text/csv")

        # --- Visualizations based on filtered data ---
    if not df_filtered.empty:
            # 1. Average Price by Bus Type (Bar Chart)
        avg_price_by_bustype = df_filtered.groupby('Bus_type')['Price'].mean().reset_index()

# Create the bar chart
        fig_avg_price = px.bar(avg_price_by_bustype, x="Bus_type", y="Price", 
                        title="Average Price by Bus Type", 
                       labels={"Price": "Average Price", "Bus_type": "Bus Type"},
                       color='Bus_type')

# Adjust bar width by modifying the 'bargap' (controls the gap between bars)
        fig_avg_price.update_layout(bargap=0.1)  # Reduce this value to decrease the bar width

# Show the figure
        st.plotly_chart(fig_avg_price, use_container_width=True)

            # 2. Bus Availability by Type (Pie Chart)
        availability_by_bustype = df_filtered.groupby('Bus_type')['Seats_Available'].sum().reset_index()
        fig_pie_availability = px.pie(availability_by_bustype, values='Seats_Available', names='Bus_type', 
                                          title="Bus Availability by Type", hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_pie_availability, use_container_width=True)

            # 3. Rating Distribution (Scatter Plot)
        fig_rating_dist = px.scatter(df_filtered, x='Ratings', y='Price', 
                                         title="Ratings vs Price Distribution", 
                                         labels={"Ratings": "Ratings", "Price": "Price"},
                                         color='Bus_type',  # Color by Bus Type for distinction
                                         hover_data=['Bus_name', 'Seats_Available'])  # Additional details on hover
        st.plotly_chart(fig_rating_dist, use_container_width=True)

    else:
            st.write("No buses match your filter criteria.")
