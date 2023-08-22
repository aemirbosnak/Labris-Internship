from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
import time

def test_login():
    username = "emir"
    password = "Emir12345"
    
    driver.get(url_login)
    
    driver.find_element(By.XPATH, "//input[@name='username']").send_keys(username)
    driver.find_element(By.XPATH, "//input[@name='password']").send_keys(password)

    driver.find_element(By.XPATH, "//input[@id='loginButton']").click()

    time.sleep(0.5)

    title = driver.title
    expected_title = "Users List"
    assert title == expected_title

    # Logout the user
    driver.find_element(By.XPATH, "//button[@id='logoutButton']").click()

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

def test_delete():
    username = "user"
    
    driver.get(url_users)
    
    title = driver.title
    expected_title = "Users List"
    assert title == expected_title

    # Find the user to delete
    users_table = driver.find_element(By.ID, "userList")
    rows = users_table.find_elements(By.TAG_NAME, "tr")
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        cell_username = cells[1].text
        if cell_username == username:
            # delete the user
            cells[5].find_element(By.NAME, "deleteButton").click()
            break
        
#---------------------------------------------------------

driver = webdriver.Firefox()

url_login = "http://0.0.0.0:8000/login.html"
url_register = "http://0.0.0.0:8000/register.html"
url_users = "http://0.0.0.0:8000/users.html"

#test_login()
test_register()
#test_delete()

driver.quit()
