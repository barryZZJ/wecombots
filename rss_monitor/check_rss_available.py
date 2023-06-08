import requests as r

def is_rss_available(path, url='http://yy.barryzzj.asia:23200', timeout=10):
    try:
        resp = r.get(url + path, timeout=timeout)
        return resp.ok
    except r.ReadTimeout:
        return False

if __name__ == '__main__':
    print(is_rss_available('/youtube/channel/UCJ0-OtVpF0wOKEqT2Z1HEtA'))