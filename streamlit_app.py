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
# Ensure Snowflake connection details are correctly configured in the Streamlit configuration
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert Snowpark DataFrame to Pandas DataFrame
pd_df = my_dataframe.to_pandas()

# Use st.experimental_data_editor with Pandas DataFrame
editable_df = st.experimental_data_editor(pd_df)

# Allow user to select ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    # Prepare search terms for API calls
    for fruit in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit, 'SEARCH_ON'].iloc[0]
        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on.lower()}")
        
        # Check if the request was successful
        if fruityvice_response.status_code == 200:
            # Parse JSON data from the response
            response_data = fruityvice_response.json()
            
            if isinstance(response_data, dict):  # Ensure the response is a dictionary
                # Convert JSON data to a Pandas DataFrame
                fv_df = pd.DataFrame([response_data])
                
                # Display the DataFrame
                st.write(f"Fruityvice DataFrame for {fruit}:", fv_df)
            else:
                st.error(f"Unexpected data format for {fruit}: {response_data}")
        else:
            st.error(f"API request for {fruit} failed with status code {fruityvice_response.status_code}")

    # Create SQL insert statement
    ingredients_string = ' '.join(ingredients_list)
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
            # Execute the SQL insert statement
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
        except Exception as e:
            st.error(f"An error occurred while submitting the order: {e}")
        
        # Stop the Streamlit script execution
        st.stop()
