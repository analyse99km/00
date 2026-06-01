def scan_page(driver):
    inputs = driver.find_elements("css selector","input")
    buttons = driver.find_elements("css selector","button")
    links = driver.find_elements("css selector","a")

    input_list = []
    button_list = []
    link_list = []

    for i, e in enumerate(inputs):
        try:
            if e.is_displayed():
                input_list.append({
                    "id": i,
                    "type": e.get_attribute("type") or "text",
                    "name": e.get_attribute("name") or "",
                    "placeholder": e.get_attribute("placeholder") or ""
                })
        except Exception:
            pass

    for i, b in enumerate(buttons):
        try:
            if b.is_displayed() and b.text.strip() != "":
                button_list.append({
                    "id": i,
                    "text": b.text.strip()
                })
        except Exception:
            pass
            
    for i, l in enumerate(links):
        try:
            if l.is_displayed() and l.text.strip() != "":
                link_list.append({
                    "id": i,
                    "text": l.text.strip(),
                    "href": l.get_attribute("href") or ""
                })
        except Exception:
            pass

    return {
        "url": driver.current_url,
        "inputs": input_list,
        "buttons": button_list,
        "links": link_list
    }
