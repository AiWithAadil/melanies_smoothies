import requests
import pandas as pd
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Connect to Snowflake and fetch fruit options
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Convert Snowpark DataFrame to Pandas DataFrame
my_dataframe_pd = my_dataframe.to_pandas()

# Use st.experimental_data_editor with Pandas DataFrame
editable_df = st.experimental_data_editor(my_dataframe_pd)

# Allow user to select ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe_pd['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    # Join selected ingredients into a string for the SQL insert statement
    ingredients_string = ' '.join(ingredients_list)

    # Create SQL insert statement
    my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders (ingredients, NAME_ON_ORDER)
    VALUES ('{ingredients_string}', '{name_on_order}')
    """
    
    # Display SQL insert statement
    st.write(my_insert_stmt)
     # Fetch data for the selected fruits from the Fruityvice API
    for fruit in ingredients_list:
            # Make API call for each selected fruit
        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{fruit.lower()}")
            
            # Check if the request was successful
        if fruityvice_response.status_code == 200:
                # Parse JSON data from the response
            response_data = fruityvice_response.json()
                
                # Convert JSON data to a Pandas DataFrame
            fv_df = pd.DataFrame([response_data])
                
                # Display the DataFrame
            st.write(f"Fruityvice DataFrame for {fruit}:", fv_df)
        else:
            st.error(f"API request for {fruit} failed with status code {fruityvice_response.status_code}")
        

    # Button to submit the order
    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        # Execute the SQL insert statement
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
        
        # Stop the Streamlit script execution
        st.stop()
