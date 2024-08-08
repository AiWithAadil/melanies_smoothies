import requests
import pandas as pd
import streamlit as st
from snowflake.snowpark.functions import col, when_matched

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Convert Snowpark DataFrame to Pandas DataFrame
my_dataframe_pd = my_dataframe.to_pandas()

# Use st.experimental_data_editor with Pandas DataFrame
editable_df = st.experimental_data_editor(my_dataframe_pd)

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe_pd['FRUIT_NAME'].tolist(),
    max_selections = 5
)

if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)

    my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders (ingredients, NAME_ON_ORDER)
    VALUES ('{ingredients_string}', '{name_on_order}')
    """

    st.write(my_insert_stmt)
    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")

        # Make the API call
fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon")

# Check if the request was successful
if fruityvice_response.status_code == 200:
    
    # Convert JSON data to a Pandas DataFrame
    fv_df = pd.DataFrame(response_data)
    
    # Display the DataFrame
    st.write("Fruityvice DataFrame:", fv_df)
else:
    st.error(f"API request failed with status code {fruityvice_response.status_code}")
    st.stop()



