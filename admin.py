import streamlit as st
import pandas as pd
import numpy as np
import mysql.connector as ms
import os

conn = ms.connect(host="k8ikuh3kl5mx.ap-south-2.psdb.cloud", user="tzllu164x99t",
                  password="pscale_pw_4PwmfgI5lZb-VJIpfnxTtlo1_v7zRJQKwzld83ypc3g", database="kau")

def clean(b):
    for row in range(len(b)):
        b[row] = list(b[row])
        for cell in range(len(b[row])):
            if b[row][cell] == None:
                b[row][cell] = "Nil"


query1 = "SELECT c_id,dp_id,c_location,f_name,l_name FROM customer"
query2 = "SELECT * FROM delivery_person"
query3 = "SELECT * FROM delivery_company"

def adminPage():
    
    with conn.cursor(buffered=True) as cur:
        cur.execute(query1)
        b = cur.fetchall()

    clean(b)

    
    with conn.cursor(buffered=True) as cur:
        cur.execute(query2)
        c = cur.fetchall()

    clean(c)
    
    
    with conn.cursor(buffered=True) as cur:
        cur.execute(query3)
        d = cur.fetchall()

    clean(d)
    
    df1 = pd.DataFrame(
        b,
        columns=('Customer Username', 'Delivery Person ID Assigned', 'Customer Location', 'First Name', 'Last Name'))
    df2 = pd.DataFrame(
        c,
        columns=('Delivery Person ID', 'Delivery Company ID', 'Salary', 'First Name', 'Last Name', 'Date of Join'))
    df3 = pd.DataFrame(
        d,
        columns=( 'Delivery Company Id', 'Founded IN', 'Delivery Company', 'Customer Care Hotline', 'Founder'))


    #? Stream lit starts here
    hide_menu_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """

    st.markdown(hide_menu_style, unsafe_allow_html=True)
    # st.set_page_config(layout="wide")

    st.title("Admin Info Page")

    with st.sidebar:
        st.image("https://www.pngkit.com/png/full/246-2464653_personal-information-comments-2-in-a-circle.png", width=50,)
        ausername = st.text_input('Username',value="")
        apassword = st.text_input('Password', type="password",value="")
        b = st.button('Login')

    if b :
        if (ausername == "admin" and apassword=="1234") :
            st.success("Authorized to access")
            st.header("Customer Information Frames")
            st.dataframe(df1, width=1500)

            st.header("Delivery Person Information Frame")
            st.dataframe(df2, width=1500)

            st.header("Delivery Company Information Frame")
            st.dataframe(df3, width=1500)
        else:
            st.error("Cannot log you in, ERROR: Bad credentials")

    else:
        st.error("Login to the view the information Frame")
