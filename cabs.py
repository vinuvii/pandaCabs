import mysql.connector
import pandas as pd
import warnings
import hashlib
import datetime
from geopy.distance import geodesic

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="panda_cabs"
)


def existing_customer():
    username = input("Type Your Username (ID): ")
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM customer WHERE customer_id = %s", (username,))
    ext_cust = mycursor.fetchone()
    if ext_cust == None:
        print("Username does not exits :( ")
        existing_customer()
    else:
        passw = input("Type Your Password: ")
        mycursor.execute("SELECT password FROM customer WHERE customer_id = %s", (username,))
        hash = mycursor.fetchone()[0]
        if hashlib.sha256(passw.encode('utf-8')).hexdigest() == hash:
            print('Login successful!')
            customer_ride(username)
        else:
            print('Incorrect Password!')
            existing_customer()
    mydb.commit()


def existing_driver():
    username = input("Type Your Username (ID): ")
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM driver WHERE driver_id = %s", (username,))
    ext_driv = mycursor.fetchone()
    if ext_driv == None:
        print("Username does not exits :( ")
        existing_driver()
    else:
        passw = input("Type Your Password: ")
        mycursor.execute("SELECT password FROM driver WHERE driver_id = %s", (username,))
        hash = mycursor.fetchone()[0]
        if hashlib.sha256(passw.encode('utf-8')).hexdigest() == hash:
            print('Login successful!')
            driver_ride(username)
        else:
            print('Incorrect Password!')
            existing_driver()
    mydb.commit()


def add_coupon():
    mycursor = mydb.cursor()
    coupon_code = input("Create A Coupon Code: ")
    mycursor.execute("SELECT * FROM discount_coupon WHERE discount_coupon_code = %s", (coupon_code,))
    ext_coup = mycursor.fetchone()
    if ext_coup == None:
        discount_value = input("Enter the discount amount: ")
        expiration_date = input("Enter the expiration date: ")
    else:
        print("Coupon Code Exists :( ")
        add_coupon()

    num = input("How many of the most frequent customers would you like to see? ")
    print("---Displaying " + num + " Most Frequent Customers---")
    customer_df = pd.read_sql("SELECT customer_id, number_of_rides FROM customer", mydb)
    customer_df = customer_df.sort_values("number_of_rides", ascending=False)
    customer_df = customer_df.head(int(num))
    print(customer_df)

    coupon_custid = input("Customer ID willing to provide the discount to: ")
    mycursor.execute("SELECT EXISTS (SELECT 1 FROM customer WHERE customer_id = %s)", (coupon_custid,))
    exists = mycursor.fetchone()[0]
    if exists:
        mycursor.execute(
            "INSERT INTO discount_coupon (discount_coupon_code, customer_id, discount, expiration_date) VALUES (%s, %s, %s, %s)",
            (coupon_code, coupon_custid, discount_value, expiration_date,))
        last_discount_id = mycursor.lastrowid
        mydb.commit()
        print("--- Sending a SMS to Customer of ID -> " + str(
            coupon_custid) + " ---\n \' Congratulations You Recieved A Coupon Code -> '"
              + str(coupon_code) + "' Redeem The Code When Requesting A Ride Before " + expiration_date + " \'")
        more_coupon()
    else:
        print("User Does Not Exist! Try Again!")
        add_coupon()
    mydb.commit()


def more_coupon():
    more_code = input("Do you wish to create more coupons? (Yes/No): ")
    if more_code == 'Yes' or more_code == 'yes':
        add_coupon()
    elif more_code == 'No' or more_code == 'no':
        user()
    else:
        print("Invalid Entry! Try Again!")
        more_coupon()


def insert_customer():
    customer_id = input("Add A Username (ID): ")
    mycursor = mydb.cursor()
    mycursor.execute("SELECT EXISTS (SELECT 1 FROM customer WHERE customer_id = %s)", (customer_id,))
    exists = mycursor.fetchone()[0]
    if exists:
        print('The username already exists. Try another')
        insert_customer()
    else:
        password = input("Enter Password: ")
        hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        customer_name = input("Enter Your Name: ")
        customer_phoneNumber = input("Enter Your Phone Number: ")
        mycursor = mydb.cursor()
        mycursor.execute("INSERT INTO customer (customer_id, name, phone_number, password) VALUES (%s, %s, %s, %s)",
                         (str(customer_id), str(customer_name), str(customer_phoneNumber), str(hash)))
        mydb.commit()
        customer_ride(customer_id)


def insert_driver():
    driver_id = input("Add A Username (ID): ")
    mycursor = mydb.cursor()
    mycursor.execute("SELECT EXISTS (SELECT 1 FROM driver WHERE driver_id = %s)", (driver_id,))
    exists = mycursor.fetchone()[0]
    mydb.commit()
    if exists:
        print('The username already exists. Try another')
        insert_driver()
    else:
        driver_current_location_cordinates = ""
        password = input("Enter Password: ")
        hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        driver_name = input("Enter Your Name: ")
        driver_phoneNumber = input("Enter Your Phone Number: ")
        driver_number_plate = input("Enter The Vehicle Number Plate: ")
        driver_capacity = input("Enter The Capacity of The Vehicle: ")
        driver_minimum_price_per_km = input("Enter The Minimum Price Per Km: ")
        driver_availability = input("Are you currently available to take a ride?: ").capitalize()
        if driver_availability == 'Yes':
            driver_current_location_cordinates = input("Enter the current location cordinates: ")
        elif driver_availability == 'No':
            driver_current_location_cordinates = "Not Available"
        else:
            print("Invalid Entry! Try Again!")
            insert_driver()
        mycursor = mydb.cursor()
        mycursor.execute(
            "INSERT INTO driver (driver_id, name, phone_number, available, number_plate, capacity, minimum_price_per_km, current_location_cordinates, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ",
            (driver_id, driver_name, driver_phoneNumber, driver_availability, driver_number_plate, driver_capacity,
             driver_minimum_price_per_km, driver_current_location_cordinates, hash,))
        mydb.commit()
        driver_ride(driver_id)


def driver_ride(driv_id):
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM ride WHERE ride_status = %s and driver_id = %s", ("Active", driv_id,))
    act_driver = mycursor.fetchone()
    if act_driver == None:
        print("Currently there's no rides for you :( ")
    else:
        print("---Continuing To A Ride---")
        req_id = act_driver[5]
        mycursor.execute("SELECT * FROM request WHERE request_ID = %s", (req_id,))
        act_req = mycursor.fetchone()
        dropoff_location = act_req[1]
        pickup_location = act_req[3]
        customer_id = act_req[4]
        mycursor.execute("SELECT * FROM customer WHERE customer_id = %s", (customer_id,))
        act_cus = mycursor.fetchone()
        customer_name = act_cus[1]
        phone = act_cus[3]
        print(
            "Following are the trip details: \n Customer Name: %s \n Customer Phone Number: %s \n Pickup Location: %s \n Dropoff Location %s" %
            (customer_name, phone, pickup_location, dropoff_location))
    payment(driv_id)
    mydb.commit()


def redeem_coupons():
    expiration_date = "2000-01-01"
    total_discount = 0
    coupons = ""
    mycursor = mydb.cursor()
    have_coupon = input("Do You Wish To Redeem Coupon (Yes/No)? ")
    if have_coupon == "Yes" or have_coupon == "yes":
        coupons = input("Enter the coupon codes you would like to redeem (seperating by commas if many): ").split(',')
        for x in coupons:

            mycursor.execute("SELECT discount FROM discount_coupon WHERE discount_coupon_code = %s and ride_id IS NULL",
                             (x,))
            amount = mycursor.fetchone()[0]
            mydb.commit()
            mycursor.execute("SELECT expiration_date FROM discount_coupon WHERE discount_coupon_code = %s and ride_id IS NULL",
                (x,))

            expiration_date = mycursor.fetchone()[0]
            expiration_date_obj = datetime.datetime.strptime(str(expiration_date), '%Y-%m-%d')
            current_date = datetime.datetime.now()

            mydb.commit()

            if amount == None or expiration_date_obj < current_date:
                print("Invalid Entry! Or Used/Expired Code Included!")
                redeem_coupons()
            else:
                total_discount += int(str(amount).strip('(').strip(',)'))


    elif have_coupon == "No" or have_coupon == "no":
        print("No discounts granted")
        return tuple([coupons, total_discount])
    else:
        print("Invalid Entry! Try Again!")
        redeem_coupons()

    print("Total Amount of Discount Allowed = " + str(total_discount))
    return tuple([coupons, total_discount])
    mydb.commit()


def customer_ride(cust_id):
    print("---Continuing To Add A Ride Request---")
    pickup_location = input("Enter Your Pickup Location: ")
    dropoff_location = input("Enter Your Dropoff Location: ")
    total_km = round(kmcal(pickup_location, dropoff_location), 2)
    print("Total Distance between Pickup Location and Dropoff Location: " + str(total_km))
    max_pay = input("What's the maximum amount you're willing to pay for the trip?: ")
    mycursor = mydb.cursor()
    mycursor.execute(
        "INSERT INTO request (dropoff_location, maximum_pay, pickup_location, customer_id, total_km) VALUES (%s, %s, %s, %s, %s) ",
        (dropoff_location, max_pay, pickup_location, cust_id, total_km,))
    mydb.commit()

    tuplet = redeem_coupons()
    listcoupon = tuplet[0]
    total_discount = tuplet[1]
    mydb.commit()

    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM driver WHERE available = 'Yes' ORDER BY minimum_price_per_km ASC LIMIT 1")
    min_driver = mycursor.fetchone()
    ride_status = 'Active'
    driver_id = min_driver[0]
    driver_name = min_driver[1]
    driver_phoneNumber = min_driver[2]
    driver_number_plate = min_driver[4]
    driver_availabilty = min_driver[3]
    min_km = min_driver[6]
    mycursor.execute("SELECT MAX(request_id) FROM request")
    first_request = mycursor.fetchone()
    confirm_request_id = first_request[0]
    mycursor.execute("SELECT * FROM request WHERE request_id = %s", (confirm_request_id,))
    firs_uest = mycursor.fetchone()
    km = firs_uest[5]
    total_minimum_pay = km * min_km
    mycursor.execute("SELECT * FROM customer WHERE customer_id = %s", (cust_id,))
    first_cust = mycursor.fetchone()
    customer_name = first_cust[1]
    customer_phoneNumber = first_cust[3]

    final_amount = total_minimum_pay - total_discount
    if final_amount < 0:
        final_amount = 0

    print("Final amount to pay = " + str(final_amount))
    mycursor.execute(
        "INSERT INTO ride (total_minimum_pay, ride_status, total_discount, final_amount, confirm_request_id, driver_id) VALUES (%s, %s, %s, %s, %s, %s)",
        (total_minimum_pay, ride_status, total_discount, final_amount, confirm_request_id, driver_id,))
    ride_id = mycursor.lastrowid
    for coupons in listcoupon:
        valueToUpdateList = []
        valueToUpdateList.append(ride_id)
        valueToUpdateList.append(coupons)
        valueToUpdateTupple = tuple(valueToUpdateList)
        query = "UPDATE discount_coupon SET ride_id = %s WHERE discount_coupon_code = %s"
        mycursor.execute(query, valueToUpdateTupple)

    valueToUpdateList = []
    valueToUpdateList.append(driver_id)
    valueToUpdateTupple = tuple(valueToUpdateList)
    query = "UPDATE driver SET available = 'No' WHERE driver_id = %s"
    mycursor.execute(query, valueToUpdateTupple)

    mycursor.execute("INSERT INTO ride_with (customer_id, driver_id) VALUES (%s, %s)",
                     (cust_id, driver_id,))
    mydb.commit()
    print("--- SMS Details ---\n Driver Name: " + str(driver_name) + " \n Number Plate: " + str(
        driver_number_plate) + " \n Driver Phone Number:" + str(driver_phoneNumber)
          + "\n Customer name: " + str(customer_name) + "\n Customer Phone Number: " + str(
        customer_phoneNumber) + "\n Pickup Location: " + str(pickup_location) + "\n Dropoff Location: "
          + str(dropoff_location) + "\n Amount: " + str(final_amount))
    user()


def user():
    user_role = input("What role are you? ('Driver', 'Customer', 'Admin'): ")
    if user_role == "Customer" or user_role == "customer":
        customer()
    elif user_role == "Driver" or user_role == "driver":
        driver()
    elif user_role == "Admin" or user_role == "admin":
        admin()
    else:
        print("Invalid role entered!")
        user()


def customer():
    qnew_customer = input("New Customer? ('Yes', 'No'): ")
    if qnew_customer == "Yes" or qnew_customer == "yes":
        insert_customer()
    elif qnew_customer == "No" or qnew_customer == "no":
        existing_customer()
    else:
        print("Invalid Entry! Try Again!")
        customer()


def driver():
    qnew_driver = input("New Driver? ('Yes', 'No'): ")
    if qnew_driver == "Yes" or qnew_driver == "yes":
        insert_driver()
    elif qnew_driver == "No" or qnew_driver == "no":
        existing_driver()
    else:
        print("Invalid Entry! Try Again!")
        driver()


def admin():
    admin_need = input(
        "What function to do? ('Add A Discount Coupon', 'Payment Report', 'Discounts Report', 'List of Customers Each Driver Drived With'): ")
    if admin_need == "Add A Discount Coupon" or admin_need == "add a discount coupon":
        add_coupon()
    elif admin_need == "Payment Report" or admin_need == "payment report":
        payment_report()
    elif admin_need == "Discounts Report" or admin_need == "discounts report":
        discounts_report()
    elif admin_need == "List of Customers Each Driver Drived With" or admin_need == "list of customers each driver drived with":
        driver_customer()
    else:
        print('Invalid Function!')
        admin()


def driver_customer():
    mycursor = mydb.cursor()
    customer_df = pd.read_sql(
        "SELECT ride_with.driver_id, GROUP_CONCAT(ride_with.customer_id) AS customer_list FROM ride_with GROUP BY ride_with.driver_id",
        mydb)
    print(customer_df)
    mydb.commit()
    user()


def payment_report():
    mycursor = mydb.cursor()
    customer_df = pd.read_sql(
        "SELECT ride.ride_id, payment.payment_method, payment.payment_date, ride.final_amount FROM payment LEFT JOIN paid_for ON paid_for.payment_id = payment.payment_id LEFT JOIN ride ON ride.ride_id = paid_for.ride_id",
        mydb)
    print(customer_df)
    total = customer_df['final_amount'].sum()
    print("Total Income Recieved:" + str(total))
    mydb.commit()
    user()


def discounts_report():
    mycursor = mydb.cursor()
    mycursor.execute(
        "SELECT customer.customer_id, customer.number_of_rides AS no_of_rides, SUM(discount_coupon.discount) AS total_discount, GROUP_CONCAT(discount_coupon.discount_coupon_code) AS all_discount_coupons FROM customer LEFT JOIN discount_coupon ON customer.customer_id = discount_coupon.customer_id  GROUP BY customer.customer_id")
    results = mycursor.fetchall()
    pd.set_option('display.max_columns', None)
    df = pd.DataFrame(results, columns=["customer_id", "no_of_rides", "total_discount", "all_discount_coupons"])
    df = df.sort_values('no_of_rides', ascending=False)
    print(df)
    total = df['total_discount'].sum()
    print("Total Amount of Discounts Granted:" + str(total))
    mydb.commit()
    user()


def kmcal(pickup_location, dropoff_location):
    distance = geodesic(pickup_location, dropoff_location).km
    return distance


def availability(username):
    driver_availability = input("Are you currently available to take a ride?: ")
    driver_current_location_cordinates = ""
    if driver_availability == 'Yes' or driver_availability == 'yes':
        driver_current_location_cordinates = input("Enter the current location cordinates: ")
        mycursor = mydb.cursor()
        valueToUpdateList = []
        valueToUpdateList.append(driver_availability)
        valueToUpdateList.append(driver_current_location_cordinates)
        valueToUpdateList.append(username)

        valueToUpdateTupple = tuple(valueToUpdateList)
        query = "UPDATE driver SET available = %s, current_location_cordinates = %s WHERE driver_id = %s"
        mycursor.execute(query, valueToUpdateTupple)
        mydb.commit()
        driver_ride(username)
    elif driver_availability == 'No' or driver_availability == 'no':
        driver_current_location_cordinates = "Not Available"
    else:
        print("Invalid Entry! Try Again!")
        availability(username)

    mycursor = mydb.cursor()
    valueToUpdateList = []
    valueToUpdateList.append(driver_availability)
    valueToUpdateList.append(driver_current_location_cordinates)
    valueToUpdateList.append(username)

    valueToUpdateTupple = tuple(valueToUpdateList)
    query = "UPDATE driver SET available = %s, current_location_cordinates = %s WHERE driver_id = %s"
    mycursor.execute(query, valueToUpdateTupple)
    mydb.commit()
    user()


def payment(username):
    username = username
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM ride WHERE driver_id = %s and ride_status = 'Active'", (username,))
    ext_coup = mycursor.fetchall()

    if len(ext_coup) == 0:
        availability(username)
    else:
        pay = input("Was the payment recieved (Yes/No) ? ")
        if pay == 'Yes' or pay == "yes":
            rid_id = ext_coup[0][0]
            req_id = ext_coup[0][5]
            mycursor.execute("SELECT customer_id FROM request WHERE request_id = %s", (req_id,))
            cust_id = mycursor.fetchone()[0]
            mycursor = mydb.cursor()
            mycursor.execute("SELECT number_of_rides FROM customer WHERE customer_id = %s", (cust_id,))
            no_rides = mycursor.fetchone()[0]

            no_rides += 1
            valueToUpdateList = []
            valueToUpdateList.append(no_rides)
            valueToUpdateList.append(cust_id)
            valueToUpdateTupple = tuple(valueToUpdateList)
            query = "UPDATE customer SET number_of_rides = %s WHERE customer_id = %s"
            mycursor.execute(query, valueToUpdateTupple)

            valueeToUpdateList = []
            valueeToUpdateList.append(rid_id)
            valueeToUpdateTupple = tuple(valueeToUpdateList)
            query = "UPDATE ride SET ride_status = 'Completed' WHERE ride_id = %s"
            mycursor.execute(query, valueeToUpdateTupple)

            payment__method(username, rid_id)
        elif pay == 'No' or pay == "no":
            payment(username)
        else:
            print("Invalid Entry!")
            payment(username)

def payment__method(username, rid_id):
    mycursor = mydb.cursor()
    payment_date = datetime.datetime.today()
    payment_method = input("What's the payment method (Card Payment/Cash Payment)? ")
    if payment_method.title() == "Card Payment" or payment_method.title() == "Cash Payment":
        mycursor.execute("INSERT INTO payment (payment_method, payment_date) VALUES (%s, %s)",
                         (payment_method.title(), payment_date,))
        last_payment_id = mycursor.lastrowid
        mycursor.execute("INSERT INTO paid_for (payment_id, ride_id) VALUES (%s, %s)",
                         (last_payment_id, rid_id,))
        availability(username)
    else:
        print("Invalid Entry!")
        payment__method(username, rid_id)
    mydb.commit()
    user()


warnings.filterwarnings('ignore')
user()
