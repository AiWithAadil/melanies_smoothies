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
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert Snowpark DataFrame to Pandas DataFrame
pd_df = my_dataframe.to_pandas()

# Allow user to select ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    # Prepare search terms for API calls and create SQL insert statement
    ingredients_string = ' '.join(ingredients_list)
    is_filled = st.checkbox("Mark as Filled")
    order_filled = 'TRUE' if is_filled else 'FALSE'
    
    my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders (ingredients, NAME_ON_ORDER, ORDER_FILLED)
    VALUES ('{ingredients_string}', '{name_on_order}', {order_filled})
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
else:
    st.warning("Please select at least one fruit.")
