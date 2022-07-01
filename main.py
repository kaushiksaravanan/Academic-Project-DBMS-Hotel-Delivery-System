import streamlit as st
import mysql.connector as ms
from pymongo.mongo_client import MongoClient
import random
import os

from admin import adminPage

client = MongoClient(   "mongodb+srv://admin:admin@cluster0.max1z.mongodb.net/?retryWrites=true&w=majority")
db = client['Dbms']

conn = ms.connect(host="localhost", user="root",
                  password=os.environ.get("SQLPASSWORD", " "), database="vscode01")
cur = conn.cursor()

username = None

def get(food_name):
    food_name = food_name.lower()
    foods = db.Food
    quer = {"food_name": food_name}
    url = foods.find_one(quer)

    if url is not None:
        return url['url']
    else:
        return 0

def username_unique(username):
    unq = True
    query = f"SELECT f_name FROM customer WHERE c_id = '{username}'"
    cur = conn.cursor(buffered=True)
    cur.execute(query)
    row = cur.fetchone()
    cur.close()
    if row is None:
        print("Unique")
        unq = True
    else:
        unq = False
    return unq

def authenticate(username, password):
    authenticated = True
    query = f"SELECT pwd FROM customer WHERE c_id = '{username}'"
    cur = conn.cursor(buffered=True)
    cur.execute(query)

    pwd = None
    for [pwd] in cur:
        print(pwd)
    if pwd is None:
        print("Username doesn't exist")
        authenticated = False
    else:
        if pwd == password:
            authenticated = True
        else:
            authenticated = False

    return authenticated

def savedetails(username, F_name, L_name, Location, password):
    query = f"INSERT INTO customer (C_id, f_name, l_name, c_location, pwd) VALUES ('{username}','{F_name}','{L_name}','{Location}','{password}')"
    try:    
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False

def get_hotels():
    query = "SELECT h_id, h_name FROM hotel"
    a = conn.cursor(buffered=True)
    with a:
        a.execute(query)
        retrieved = a.fetchall()
    return retrieved

def get_food(hotelId):
    query = f"SELECT f_name, f_id, f_price FROM food A WHERE f_id IN (SELECT f_id FROM serves B WHERE B.h_id = '{hotelId}')"
    a = conn.cursor(buffered=True)
    foodInfo = None
    with a:
        a.execute(query)
        foodInfo = a.fetchall()
    print(len(foodInfo), hotelId)
    if len(foodInfo) != 0:
        return foodInfo
    else:
        return [('Parota', "C", 40)]

def selectedDP():
    # Randomly selects a delivery person who will be delivering the food.
    query = "SELECT dp_id, f_name, l_name FROM delivery_person"
    with conn.cursor(buffered=True) as a:
        a.execute(query)
        b = a.fetchall()

    return b[random.randint(0, len(b) - 1)]

def place_order(order, Total, hotelId):
    #update in table
    orderPlaced = True, None
    # Randomly selects a delivery person for the order
    delPerId, del_FName, del_Lname = selectedDP()
    query1 = f"INSERT INTO orders(h_id, dp_id, o_total_price) VALUES('{hotelId}', '{delPerId}', {Total})"
    query2 = f"UPDATE customer  SET dp_id = '{delPerId}' WHERE c_id = '{username}'"  # Settings the delivery person who will delivery the customer his/her current delivery.
    # Users = db.Users

    try:
        with conn.cursor() as a:
            a.execute(query1)
            a.execute(query2)
            conn.commit()
        orderPlaced = (True, del_FName + " " + del_Lname)
    except Exception as e:
        print(e)
        orderPlaced = False, None

    return orderPlaced

def show_food(hotelId, hotel, Location):
    foods = get_food(hotelId)
    food_ = [i[0] for i in foods]
    food_i = [i[1] for i in foods]
    price = [i[2] for i in foods]
    food_ = st.columns(len(food_))
    k = 0
    Total = 0
    order = {}
    for i in food_:
        with i:
            st.header(foods[k][0])
            # st.checkbox(foods[k][0],key=food_i[k])
            str_temp = 'Price ₹'+str(price[k])
            st.write(str_temp)
            no = st.number_input('Quantity', 0, 100,
                                 key=(k*food_i))  # type: ignore
            Total += (no*price[k])
            order[food_i[k]] = no
            st.image(get(foods[k][0]))
            k += 1
    str_total = '# Total '+str(int(Total))
    st.write(str_total)
    str_location = '## Your delivery address - '+Location
    st.write(str_location)
    st.write("Order once placed can't be refunded")
    y = st.button('Place Order')

    # FOr backend order is a dict of order,quantity
    if y:
        res = place_order(order, Total, hotelId)
        if res[0] == True:
            st.success(f'Order placed 🤩. Delivery Agent: {res[1]}')
            st.balloons()
        else:
            st.error('Order Failed 😔')
    else:
        st.write('Avaialabe payment method Cash on delivery')

def create(username):
    list_hotels = get_hotels()
    hotel_names = list(map(lambda x: x[1], list_hotels))
    st.write('# Choose Hotel')
    selHotel = st.radio('Currently open hotels', hotel_names)  # Select a hotel
    selHotelId = list_hotels[hotel_names.index(selHotel)][0]

    query = f"SELECT c_location FROM customer WHERE c_id = '{username}'"
    clocation = None
    curr = conn.cursor(buffered=True)
    with curr:
        curr.execute(query)
        record = curr.fetchone()
        clocation = record[0]

    show_food(selHotelId, selHotel, clocation)

def login(username):
    if len(username) > 0:
        login_cfrm = 'Logged in as '+username
        st.success(login_cfrm)
        # get user's location' as parameted to create
        create(username)

def foodDelivery():
    username = st.text_input('Username',value="")
    password = st.text_input('Password', type="password", value="")
    b = st.button('Login')
    pwd = ''
    if authenticate(username, password):
        login(username)
    elif b:
        st.error('Wrong credentials')
    # with st.sidebar:
    else:
        if st.checkbox('REGISTER'):
            with st.form(key='LOGIN'):
                username = st.text_input('Type Username')
                F_name = st.text_input('First name')
                L_name = st.text_input('Last name')
                Location = st.text_input('Location')
                Password = st.text_input('Password', type="password")
                y = st.form_submit_button('Register')
                if not username_unique(username) and y:
                    print('1')
                    st.error('Username already exists')
                elif y:
                    print(2)
                    st.info('Username avaliable')
                    if savedetails(username, F_name, L_name, Location, Password):
                        st.success('Successfully registed')
                    else:
                        st.error("Can't complete registration contact dev team")

def main():
    global username
    st.set_page_config(layout="wide", page_title="Food Delivery")
    with st.sidebar:
        st.title("Food Delivery Application")
        selected = st.selectbox('Page:', ['Food Ordering', 'Admin'])
        
    if selected == 'Admin':
        adminPage()
    else:
        foodDelivery()
if __name__ == '__main__':
    main()
