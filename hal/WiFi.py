MPY = True
try:
    import network  # type: ignore
except:
    MPY = False


def connect(ssid, password):
    if MPY:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if not wlan.isconnected():
            wlan.connect(ssid, password)
            while not wlan.isconnected():
                pass
