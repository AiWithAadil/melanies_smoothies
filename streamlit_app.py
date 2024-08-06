import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col, when_matched

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

session = get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Convert Snowpark DataFrame to Pandas DataFrame
my_dataframe_pd = my_dataframe.to_pandas()

# Use st.experimental_data_editor with Pandas DataFrame
editable_df = st.experimental_data_editor(my_dataframe_pd)

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe_pd['FRUIT_NAME'].tolist()
    , max_selections = 5
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
    st.stop()


