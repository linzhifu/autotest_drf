from django.test import TestCase, Client

# Create your tests here.


class DemoTest(TestCase):
    def test(self):
        client = Client()
        response = client.post('http://127.0.0.1:8000/v1/login/', {
            "email": "linzhifu222@163.com",
            "password": "123"
        })
        print(response.content)
        self.assertEqual(True, True)
