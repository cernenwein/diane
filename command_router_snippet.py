import re
from wifi_voice_commands import handle_add_wifi, handle_forget_wifi, handle_list_wifi

def process_wifi_commands(text):
    if "add wifi network" in text:
        match = re.search(r"add wifi network (\S+) with password (\S+)", text)
        if match:
            ssid, password = match.groups()
            return handle_add_wifi(ssid, password)

    if "forget wifi network" in text:
        match = re.search(r"forget wifi network (\S+)", text)
        if match:
            return handle_forget_wifi(match.group(1))

    if "list wifi" in text:
        return handle_list_wifi()

    return None
