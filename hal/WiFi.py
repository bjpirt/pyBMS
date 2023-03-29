mpy = True
try:
    import network
except:
    mpy = False


def connect(ssid, password):
    if mpy:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if not wlan.isconnected():
            wlan.connect(ssid, password)
            while not wlan.isconnected():
                pass
