import pandas as pd
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Connect to Snowflake and fetch fruit options
try:
    cnx = st.connection("snowflake")
    session = cnx.session()
    my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

    # Convert Snowpark DataFrame to Pandas DataFrame
    pd_df = my_dataframe.to_pandas()
except Exception as e:
    st.error(f"Error fetching data from Snowflake: {e}")
    st.stop()

# Allow user to select ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen + ' Nutrition Information')

        # Use the correct search term from the DataFrame
        search_term = pd_df[pd_df['FRUIT_NAME'] == fruit_chosen]['SEARCH_ON'].values[0]

        try:
            fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_term}")
            fruityvice_response.raise_for_status()  # Check for request errors
            fruityvice_data = fruityvice_response.json()

            # Convert JSON response to DataFrame for display
            if fruityvice_data:
                fv_df = pd.json_normalize(fruityvice_data)
                st.dataframe(fv_df, use_container_width=True)
            else:
                st.warning(f"No nutritional information available for {fruit_chosen}.")
        except requests.RequestException as req_e:
            st.error(f"Error fetching nutritional information: {req_e}")

    order_filled = False  # Define this variable as False

    my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders (ingredients, NAME_ON_ORDER, ORDER_FILLED)
    VALUES ('{ingredients_string}', '{name_on_order}', {order_filled})
    """
    
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
else:
    st.warning("Please select at least one fruit.")
