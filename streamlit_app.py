# Import python packages
import streamlit as st
# from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests


# Write directly to the app
st.title(f"Customize Your Smoothie :poop:")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """)

name_on_order = st.text_input("Name on the Smootie:")
st.write("The name on your smooty is", name_on_order)

cnx = st._connection("snowflake")
session = cnx.session() #get_active_session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
filtering_df = session.table("smoothies.public.fruit_options")

# st.dataframe(data=my_dataframe, use_container_width=True)

options = st.multiselect(
    "Choose up to 5 ingredients",
    # ["Green", "Yellow", "Red", "Blue"],
    my_dataframe,
    max_selections=5
)

if options:
    # st.write( options)
    # st.text(options)

    ingredients_string =''

    for fruit_chosen in options:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen + ' Nutrition Information')
        
        filtered_df = filtering_df.filter((col('fruit_chosen') == fruit_chosen) & col('SEARCH_ON').isNotNull()).select(col('SEARCH_ON'))

        # Collect the results
        serach_on_fruit_nm = filtered_df.collect()
      
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + serach_on_fruit_nm)
        # st.text(smoothiefroot_response.json())
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    # st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                values ('""" + ingredients_string + """','"""+name_on_order+"""')"""
    
    # st.write(my_insert_stmt)
    # st.stop()
    time_to_insert=st.button("Submit Order!")
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")


