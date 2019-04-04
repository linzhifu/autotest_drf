import requests


def test():
    url = 'http://127.0.0.1:8000/'
    params = {"projectId": 52}
    response = requests.request(
        'get', url + '/api/v1/projectTest/', params=params)
    print(response.json())


if __name__ == '__main__':
    test()
