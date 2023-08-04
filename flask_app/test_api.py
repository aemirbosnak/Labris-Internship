import requests
import urllib3

# Ignore SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Replace these URLs with the appropriate endpoints of your Flask application
base_url = "https://192.168.0.178"
login_url = f"{base_url}/login"
insecure_endpoint_url = f"{base_url}/insecure_endpoint"

# Replace these with valid credentials if your application requires authentication
username = "emir"
password = "EmiR12345"

# Test for OWASP Top 10 Metric: A2 - Broken Authentication
def test_broken_authentication():
    print("\n-----Testing for broken authentication-----\n")
    login_data = {"username": username, "password": password}
    response = requests.post(login_url, json=login_data, verify=False) 
    if response.status_code == 200:
        print("Login successful")
    else:
        print("Login failed")
        
# Test for OWASP Top 10 Metric: A1 - Injection
def test_injection_vulnerability():
    print("\n-----Testing for SQL injection-----\n")
    # Example of SQL Injection
    login_data = {"username": "admin' OR 1=1 --", "password": "some_password"}
    response = requests.post(login_url, json=login_data, verify=False) 
    if "Login successful" in response.text:
        print("Injection vulnerability present (Login successful with malicious input)")
    else:
        print("Injection vulnerability not found")
        
# Test for OWASP Top 10 Metric: A7 - Cross-Site Scripting (XSS)
def test_xss_vulnerability():
    print("\n-----Testing for XSS-----\n")
    # Example of a malicious script injection
    malicious_script = "<script>alert('XSS Attack!');</script>"
    headers = {"Content-Type": "application/json"}
    payload = {"message": malicious_script}
    response = requests.post(insecure_endpoint_url, json=payload, headers=headers, verify=False)  
    if malicious_script in response.text:
        print("XSS vulnerability present (Malicious script found in response)")
    else:
        print("XSS vulnerability not found")
        
# Test for OWASP Top 10 Metric: A4 - XML External Entity (XXE)
def test_xxe_vulnerability():
    print("\n-----Testing for XEE-----\n")
    xml_payload = '<?xml version="1.0" encoding="ISO-8859-1"?><!DOCTYPE foo [<!ELEMENT foo ANY ><!ENTITY xxe SYSTEM "file:///etc/passwd" >]><foo>&xxe;</foo>'
    headers = {"Content-Type": "application/xml"}
    response = requests.post(insecure_endpoint_url, data=xml_payload, headers=headers, verify=False)  
    if response.status_code == 200:
        print("XXE Vulnerability may be present")
    else:
        print("No XXE Vulnerability")

# Run the test functions
if __name__ == "__main__":
    test_broken_authentication()
    test_injection_vulnerability()
    test_xss_vulnerability()
    test_xxe_vulnerability()

