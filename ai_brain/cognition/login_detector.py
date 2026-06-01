def check_login(driver):
    url = driver.current_url

    if "login" in url.lower():
        return False

    password = driver.find_elements("css selector","input[type='password']")

    if password:
        return False

    return True
