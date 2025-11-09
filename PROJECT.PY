# app.py
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    name = "Tamil"
    return render_template("index.html", name=name)

if __name__ == "__main__":
    app.run(debug=True)


import random
import time
from twilio.rest import Client
import mysql.connector

# --- Twilio setup (replace with your verified details) ---
account_sid = "ACe6d055ca92ae57aa1a687500b190ee18"
auth_token = "c734d5d73c3a8dca4cf59e1e9b6ab43c"
twilio_number = "+15017122661"   # your Twilio phone number

client = Client(account_sid, auth_token)

# --- Database setup ---
mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Tamilselvan26',
    database='Bankaccount'
)
mycursor = mydb.cursor()
# --- Ensure 'PIN' column exists ---
try:
    mycursor.execute("DESCRIBE customers")
    columns = [col[0] for col in mycursor.fetchall()]
    if 'pin' not in columns:
        mycursor.execute("ALTER TABLE customers ADD COLUMN pin INT")
        mydb.commit()
        print("✅ Added missing column 'pin' to customers table.")
except mysql.connector.errors.ProgrammingError:
# --- Ensure customers table exists ---
  mycursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_no VARCHAR(20),
    name VARCHAR(60),
    dob DATE,
    mobile VARCHAR(15),
    adhar VARCHAR(20),
    pan VARCHAR(20),
    Adress VARCHAR(50),
    pin VARCHAR(6),
    balance FLOAT DEFAULT 0
)
''')

# --- Welcome Screen ---
def welcome_screen():
    print("====================================")
    print("       WELCOME TO OUR BANK")
    print("====================================")
    print("Please select a mode to continue:")
    print("1. ATM Mode")
    print("2. Bank Mode")
    mode = input("Enter your choice (1 or 2): ").strip()
    if mode not in ['1', '2']:
        print("Invalid choice! Defaulting to ATM Mode.")
        mode = '1'
    print()
    return mode

# --- Create Account ---
def create_account():
    print("\n--- Create New Account ---")
    name = input("Enter Name: ")
    dob = input("Enter DOB (YYYY-MM-DD): ")
    mobile = input("Enter Mobile Number (10 digits): ")
    adhar = input("Enter Aadhaar Number: ")
    pan = input("Enter PAN Number: ")
    Adress = input("Enter Address: ")
    pin = input("Set a 4-digit ATM PIN: ")

    #---Starting Deposite---
    deposit=float(input("Enter your Opening Deposit Amount: ")) 

    account_no = str(random.randint(1000000000, 9999999999))

    mycursor.execute('''
        INSERT INTO customers (account_no, name, dob, mobile, adhar, pan, Adress, pin, balance)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (account_no, name, dob, mobile, adhar, pan, Adress, pin, 0))
    mydb.commit()

    # Twilio SMS
    try:
        msg = f"Hello {name}, your new Bank Account {account_no} has been created successfully!"
        client.messages.create(to="+91" + mobile, from_=twilio_number, body=msg)
        print("SMS sent successfully!")
    except Exception as e:
        print("SMS could not be sent:", e)

    print(f"Account created successfully! Your Account No: {account_no}")

# --- ATM Login ---
def atm_login():
    acc = input("Enter Account Number: ")
    pin = input("Enter 4-digit PIN: ")
    mycursor.execute("SELECT * FROM customers WHERE account_no=%s AND pin=%s", (acc, pin))
    result = mycursor.fetchone()
    if result:
        print(f"Login successful! Welcome, {result[2]}")
        return acc
    else:
        print("Invalid Account Number or PIN!")
        return None

# --- Deposit Money ---
def deposit_money():
    acc = atm_login()
    if not acc:
        return
    amount = float(input("Enter amount to deposit: "))
    mycursor.execute("SELECT balance FROM customers WHERE account_no=%s", (acc,))
    result = mycursor.fetchone()
    new_balance = result[0] + amount
    mycursor.execute("UPDATE customers SET balance=%s WHERE account_no=%s", (new_balance, acc))
    mydb.commit()
    print(f"₹{amount} deposited successfully. New balance: ₹{new_balance}")

# --- Withdraw Money ---
def withdraw_money():
    acc = atm_login()
    if not acc:
        return
    amount = float(input("Enter amount to withdraw: "))
    mycursor.execute("SELECT balance FROM customers WHERE account_no=%s", (acc,))
    result = mycursor.fetchone()
    if result[0] >= amount:
        new_balance = result[0] - amount
        mycursor.execute("UPDATE customers SET balance=%s WHERE account_no=%s", (new_balance, acc))
        mydb.commit()
        print(f"₹{amount} withdrawn successfully. Remaining balance: ₹{new_balance}")
    else:
        print("Insufficient balance!")

# --- Balance Enquiry ---
def balance_enquiry():
    acc = atm_login()
    if not acc:
        return
    mycursor.execute("SELECT name, balance FROM customers WHERE account_no=%s", (acc,))
    result = mycursor.fetchone()
    print(f"Name: {result[0]} | Balance: ₹{result[1]}")

# --- Change PIN ---
def change_pin():
    acc = input("Enter your Account Number: ")
    old_pin = input("Enter your current PIN: ")
    mycursor.execute("SELECT pin FROM customers WHERE account_no=%s", (acc,))
    result = mycursor.fetchone()
    if result and result[0] == old_pin:
        new_pin = input("Enter new 4-digit PIN: ")
        confirm = input("Confirm new PIN: ")
        if new_pin == confirm and len(new_pin) == 4:
            mycursor.execute("UPDATE customers SET pin=%s WHERE account_no=%s", (new_pin, acc))
            mydb.commit()
            print("PIN changed successfully!")
        else:
            print("PINs do not match or not 4 digits!")
    else:
        print("Incorrect Account Number or Old PIN!")

# --- Show All Customers (Bank Mode only) ---
def show_all_customers():
    mycursor.execute("SELECT account_no, name, balance FROM customers")
    rows = mycursor.fetchall()
    for row in rows:
        print(row)

# --- Main Program ---
mode = welcome_screen()

while True:
    print("\n--- MAIN MENU ---")
    if mode == '2':  # Bank Mode
        print("1. Create Account")
        print("2. Deposit Money")
        print("3. Withdraw Money")
        print("4. Balance Enquiry")
        print("5. Show All Customers")
        print("6. Change PIN")
        print("7. Exit")
    else:  # ATM Mode
        print("1. Deposit Money")
        print("2. Withdraw Money")
        print("3. Balance Enquiry")
        print("4. Change PIN")
        print("5. Exit")

    ch = input("Enter your choice: ")

    if mode == '2':
        if ch == '1': create_account()
        elif ch == '2': deposit_money()
        elif ch == '3': withdraw_money()
        elif ch == '4': balance_enquiry()
        elif ch == '5': show_all_customers()
        elif ch == '6': change_pin()
        elif ch == '7':
            print("Thank you for using our Bank System!")
            break
        else: print("Invalid choice!")
    else:
        if ch == '1': deposit_money()
        elif ch == '2': withdraw_money()
        elif ch == '3': balance_enquiry()
        elif ch == '4': change_pin()
        elif ch == '5':
            print("Thank you for using our ATM!")
            break
        else: print("Invalid choice!")
