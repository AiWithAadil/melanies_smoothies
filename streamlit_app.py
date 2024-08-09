# Import Python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom smoothie!"""
)

# Input for the name of the smoothie
name_on_order = st.text_input('Name of Smoothie:')
st.write('The name on your smoothie will be:', name_on_order)

# Connect to Snowflake and fetch fruit options
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table('smoothies.public.fruit_options').select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert the Snowflake DataFrame to a Pandas DataFrame
pd_df = my_dataframe.to_pandas()

# Multi-select widget for ingredients
ingredient_list = st.multiselect(
    'Choose up to 5 ingredients:',
    options=pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredient_list:
    ingredients_string = ' '.join(ingredient_list)

    # Display the search value and nutrition information for selected fruits
    for fruit_chosen in ingredient_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for', fruit_chosen, 'is', search_on, '.')

        st.subheader(fruit_chosen + ' Nutrition Information')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + fruit_chosen)
        if fruityvice_response.status_code == 200:
            fv_df = pd.json_normalize(fruityvice_response.json())
            st.dataframe(data=fv_df, use_container_width=True)
        else:
            st.write('Error fetching data for', fruit_chosen)

    # Build and display the SQL Insert Statement
    ingredients_string = ingredients_string.strip().replace("'", "''")
    name_on_order = name_on_order.strip().replace("'", "''")
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """
    st.write(my_insert_stmt)

    # Submit button to insert the order
    if st.button('Submit Order'):
        try:
            session.sql(my_insert_stmt).collect()
            st.success('Your smoothie is ordered!', icon='✅')
        except Exception as e:
            st.error(f'Error: {e}')
