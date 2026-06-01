def reflect(result):
    if result == "clicked" or result == "clicked_link":
        return "action_success"

    if result == "filled":
        return "input_filled"
        
    if result == "navigated":
        return "navigated_success"
        
    if result == "scrolled":
        return "scrolled_success"
        
    if result == "waited":
        return "wait_success"

    if "error" in result:
        return f"action_error_{result}"

    return "unknown"
