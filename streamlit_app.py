import requests
import pandas as pd
import streamlit as st
import snowflake.connector
from snowflake.snowpark.functions import col
from requests.exceptions import RequestException, HTTPError, ConnectionError
import time

# Function to fetch data from Fruityvice API with retry logic
def fetch_fruityvice_data(search_on, retries=3, delay=2):
    url = f"https://fruityvice.com/api/fruit/{search_on.lower()}"
    for attempt in range(retries):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses
            return response.json()
        except (HTTPError, ConnectionError) as e:
            if attempt < retries - 1:
                time.sleep(delay)  # Wait before retrying
            else:
                st.error(f"Failed to fetch data for {search_on}: {e}")
                return None
        except RequestException as e:
            st.error(f"An error occurred: {e}")
            return None

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Connect to Snowflake
conn = snowflake.connector.connect(
    user='<your_user>',
    password='<your_password>',
    account='<your_account>',
    warehouse='<your_warehouse>',
    database='<your_database>',
    schema='<your_schema>'
)

# Fetch fruit options from Snowflake
cursor = conn.cursor()
cursor.execute("SELECT FRUIT_NAME, SEARCH_ON FROM smoothies.public.fruit_options")
rows = cursor.fetchall()
pd_df = pd.DataFrame(rows, columns=['FRUIT_NAME', 'SEARCH_ON'])

# Allow user to select ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    fruits_data = {}
    for fruit in ingredients_list:
        fruit_data = fetch_fruityvice_data(fruit)
        if fruit_data:
            fruits_data[fruit] = fruit_data

    # Display fruit data
    for fruit, data in fruits_data.items():
        st.subheader(fruit)
        st.json(data)

    # Create SQL insert statement
    ingredients_string = ', '.join(ingredients_list)
    my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders (ingredients, NAME_ON_ORDER)
    VALUES ('{ingredients_string}', '{name_on_order}')
    """
    
    # Display SQL insert statement
    st.write("Generated SQL Insert Statement:")
    st.code(my_insert_stmt, language='sql')
    
    # Button to submit the order
    if st.button("Submit Order"):
        try:
            cursor.execute(my_insert_stmt)
            conn.commit()
            st.success('Your Smoothie is ordered!', icon="✅")
        except Exception as e:
            st.error(f"An error occurred while submitting the order: {e}")
        
        # Stop the Streamlit script execution
        st.stop()
else:
    st.warning("Please select at least one fruit.")
