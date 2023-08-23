from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
import time

def test_login():
    username = "user"
    password = "User12345"
    
    driver.get(url_login)
    
    driver.find_element(By.XPATH, "//input[@name='username']").send_keys(username)
    driver.find_element(By.XPATH, "//input[@name='password']").send_keys(password)

    driver.find_element(By.XPATH, "//input[@id='loginButton']").click()

    time.sleep(2)

    title = driver.title
    expected_title = "Users List"
    assert title == expected_title

    # Logout the user
    driver.find_element(By.ID, "logoutButton").click()

    # Negotiate the pop-up alert
    alert_login_success = Alert(driver)
    alert_login_success.accept()

    time.sleep(0.5)
    
    # Check if we are back at login page
    title = driver.title
    expected_title = "Login Page"
    assert title == expected_title

def test_register():
    username = "user"
    first_name = "User"
    last_name = "Test"
    email = "user@test.com"
    password = "User12345"

    driver.get(url_register)

    title = driver.title
    expected_title = "Registration Page"
    assert title == expected_title

    driver.find_element(By.XPATH, "//input[@id='username']").send_keys(username)
    driver.find_element(By.XPATH, "//input[@id='firstname']").send_keys(first_name)
    driver.find_element(By.XPATH, "//input[@id='lastname']").send_keys(last_name)
    driver.find_element(By.XPATH, "//input[@id='email']").send_keys(email)
    driver.find_element(By.XPATH, "//input[@id='password']").send_keys(password)

    driver.find_element(By.XPATH, "//input[@type='submit']").click()
    
    time.sleep(0.5)
    
    # Negotiate the pop-up alert
    alert_register_success = Alert(driver)
    alert_register_success.accept()

    time.sleep(0.5)

    # Check if correctly redirected to login
    title = driver.title
    expected_title = "Login Page"
    assert title == expected_title

def test_update():
    username_to_change = "user"

    new_username = "new_user"
    new_firstname = "New"
    new_lastname = ""
    new_email = "new-user@new-test.com"

    driver.get(url_users)

    # First logout if logged in - api does not let updating an online user
    driver.find_element(By.ID, "logoutButton").click()

    alert = Alert(driver)
    alert.accept()

    time.sleep(2)

    # Go back to users page if we log out 
    page = driver.title
    if page == "Login Page":
        driver.find_element(By.ID, "goToUsers").click()
        time.sleeop(0.5)
    
    # Find the user to update
    user_elements = find_user_row_element(username_to_change)
    user_elements[5].find_element(By.NAME, "updateButton").click()
    
    time.sleep(0.5)

    # Enter new user info
    driver.find_element(By.ID, "newUsername").send_keys(new_username)
    driver.find_element(By.ID, "newFirstName").send_keys(new_firstname)
    driver.find_element(By.ID, "newLastName").send_keys(new_lastname)
    driver.find_element(By.ID, "newEmail").send_keys(new_email)

    driver.find_element(By.XPATH, "//input[@type='submit']").click()

    # Negotiate popup
    alert_update_success = Alert(driver)
    alert_update_success.accept()

    time.sleep(0.5)

    # Check if correctly directed to users
    title = driver.title
    expected_title = "Users List"
    assert title == expected_title

def test_delete():
    username_to_delete = "new_user"
    
    driver.get(url_users)
    
    title = driver.title
    expected_title = "Users List"
    assert title == expected_title

    # Find the user to delete
    user_elements = find_user_row_element(username_to_delete)
    user_elements[5].find_element(By.NAME, "deleteButton").click()

    # Negotiate popup alert
    alert_delete_success = Alert(driver)
    alert_delete_success.accept()

def find_user_row_element(username):
    users_table = driver.find_element(By.ID, "userList")
    rows = users_table.find_elements(By.TAG_NAME, "tr")
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        cell_username = cells[1].text
        if cell_username == username:
            return cells

driver = webdriver.Firefox()

url_login       = "http://0.0.0.0:8000/login.html"
url_register    = "http://0.0.0.0:8000/register.html"
url_users       = "http://0.0.0.0:8000/users.html"

try:
    test_register()
    print("Register test successful")
except Exception as e:
    print("Error in test_register:", e)

try:
    test_login()
    print("Login test successful")
except Exception as e:
    print("Error in test_login:", e)

try:
    test_update()
    print("Update test successful")
except Exception as e:
    print("Error in test_update:", e)

try:
    test_delete()
    print("Delete test successful")
except Exception as e:
    print("Error in test_delete:", e)

driver.quit()