

def get_proxy_config(enabled=False):
    if enabled:
        return {
            'http': 'http://192.168.1.102:12334',
            'https': 'http://192.168.1.102:12334',
            }
    else:
        return ""
