from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    
    # Negotiate the pop-up alert
    alert_register_success = wait.until(EC.alert_is_present())
    alert_register_success.accept()

    # Check if correctly redirected to login
    wait.until(lambda driver: driver.current_url == "http://0.0.0.0:8000/login.html")
    title = driver.title
    expected_title = "Login Page"
    assert title == expected_title

def test_login():
    username = "user"
    password = "User12345"
    
    driver.get(url_login)
    
    driver.find_element(By.XPATH, "//input[@name='username']").send_keys(username)
    driver.find_element(By.XPATH, "//input[@name='password']").send_keys(password)

    driver.find_element(By.XPATH, "//input[@id='loginButton']").click()

    # Check if correctly redirected to users
    wait.until(lambda driver: driver.current_url == "http://0.0.0.0:8000/users.html")
    title = driver.title
    expected_title = "Users List"
    assert title == expected_title

    # Logout the user
    driver.find_element(By.ID, "logoutButton").click()

    # Negotiate the pop-up alert
    alert_logout_success = wait.until(EC.alert_is_present())
    alert_logout_success.accept()
    
    # Check if we are back at login page
    wait.until(lambda driver: driver.current_url == "http://0.0.0.0:8000/login.html")
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

    # Negotiate the pop-up alert
    alert_logout_success = wait.until(EC.alert_is_present())
    alert_logout_success.accept()

    # Go back to users page if we log out 
    page = driver.title
    if page == "Login Page":
        driver.find_element(By.ID, "goToUsers").click()
        wait.until(lambda driver: driver.current_url == "http://0.0.0.0:8000/users.html")
    
    # Find the user to update
    user_elements = find_user_row_element(username_to_change)
    user_elements[5].find_element(By.NAME, "updateButton").click()

    # Enter new user info
    driver.find_element(By.ID, "newUsername").send_keys(new_username)
    driver.find_element(By.ID, "newFirstName").send_keys(new_firstname)
    driver.find_element(By.ID, "newLastName").send_keys(new_lastname)
    driver.find_element(By.ID, "newEmail").send_keys(new_email)

    driver.find_element(By.XPATH, "//input[@type='submit']").click()

    # Negotiate popup
    alert_update_success = wait.until(EC.alert_is_present())
    alert_update_success.accept()

    # Check if correctly directed to users
    wait.until(lambda driver: driver.current_url == "http://0.0.0.0:8000/users.html")
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
    alert_delete_success = wait.until(EC.alert_is_present())
    alert_delete_success.accept()

def find_user_row_element(username):
    users_table = driver.find_element(By.ID, "userList")
    rows = users_table.find_elements(By.TAG_NAME, "tr")
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        cell_username = cells[1].text
        if cell_username == username:
            return cells

# Set driver preferences
driver = webdriver.Firefox()
#driver.manage().window().maximize()
driver.implicitly_wait(10)
wait = WebDriverWait(driver, 10)

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
