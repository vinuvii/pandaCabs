# Panda Cabs Management System

This is a Python-based system for managing ride-hailing services, allowing customers and drivers to register, log in, request rides, and process payments. The system also includes an admin panel for managing discount coupons and generating reports.

## Features

### Customer Features
- **Register as a new customer** with a username, password, name, and phone number.
- **Log in as an existing customer** using credentials.
- **Request a ride** by providing pickup and drop-off locations.
- **Redeem discount coupons** during payment.
- **View assigned driver details** upon ride confirmation.

### Driver Features
- **Register as a new driver** with details including vehicle number plate, capacity, and availability.
- **Log in as an existing driver** using credentials.
- **Accept ride requests** and view customer details.

### Admin Features
- **Generate and assign discount coupons** to top customers.
- **View payment reports** for completed rides.
- **Analyze discount usage and customer frequency.**

## Technologies Used
- **Python**
- **MySQL** (via `mysql.connector`) for database operations.
- **Pandas** for handling and sorting customer data.
- **Geopy** for calculating distances between locations.
- **Hashlib** for password encryption.

## Database Schema (Key Tables)
- **`customer`**: Stores customer details (ID, name, phone number, password).
- **`driver`**: Stores driver details (ID, availability, location, pricing, etc.).
- **`request`**: Stores ride requests with pickup/drop-off details.
- **`ride`**: Stores ride details including assigned driver and final payment.
- **`discount_coupon`**: Stores discount codes, assigned customers, and usage status.

## How to Run
1. Install dependencies:
   ```sh
   pip install mysql-connector-python pandas geopy
2. Ensure MySQL is running and update database connection details in the script.
3. Run the script
4. Follow on-screen prompts to register/log in as a customer, driver, or admin.

## Notes
- The system supports recursive login attempts for incorrect credentials.
- Customers are matched with the cheapest available driver.
- Discount codes have expiration dates and can only be used once.
