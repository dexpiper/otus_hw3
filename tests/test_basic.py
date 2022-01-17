import hashlib
import datetime
import unittest

from api import method_handler
from database import RedisStore
from tests.utils import cases
from const import ADMIN_LOGIN, ADMIN_SALT, SALT, INVALID_REQUEST, FORBIDDEN, OK


class TestSuite(unittest.TestCase):
    def setUp(self):
        self.context = {}
        self.headers = {}
        self.store = RedisStore(db=3)

    def get_response(self, request):
        return method_handler(
            {"body": request, "headers": self.headers},
            self.context,
            self.store
        )

    def set_valid_auth(self, request):
        if request.get("login") == ADMIN_LOGIN:
            request["token"] = hashlib.sha512(
                    (
                        datetime.datetime.now().strftime("%Y%m%d%H")
                        + ADMIN_SALT
                    ).encode('utf-8')
                ).hexdigest()
        else:
            msg = (
                request.get("account", "")
                + request.get("login", "")
                + SALT
            )
            request["token"] = hashlib.sha512(msg.encode('utf-8')).hexdigest()

    def test_empty_request(self):
        _, code = self.get_response({})
        self.assertEqual(INVALID_REQUEST, code)

    @cases([
        {
            "account": "horns&hoofs", "login": "h&f",
            "method": "online_score", "token": "",
            "arguments": {}
        },
        {
            "account": "horns&hoofs",
            "login": "h&f", "method": "online_score",
            "token": "sdd", "arguments": {}
        },
        {
            "account": "horns&hoofs",
            "login": "admin", "method": "online_score",
            "token": "", "arguments": {}
        },
    ])
    def test_bad_auth(self, request):
        msg, code = self.get_response(request)
        self.assertEqual(
            FORBIDDEN, code, f'Faild with {request}. Message: {msg}')

    @cases([
        {"account": "horns&hoofs", "login": "h&f", "method": "online_score"},
        {"account": "horns&hoofs", "login": "h&f", "arguments": {}},
        {"account": "horns&hoofs", "method": "online_score", "arguments": {}},
    ])
    def test_invalid_method_request(self, request):
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(INVALID_REQUEST, code)
        self.assertTrue(len(response))

    @cases([
        {},
        {"phone": "79175002040"},
        {"phone": "89175002040", "email": "stupnikov@otus.ru"},
        {"phone": "79175002040", "email": "stupnikovotus.ru"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": -1},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": "1"},
        {
            "phone": "79175002040", "email": "stupnikov@otus.ru",
            "gender": 1, "birthday": "01.01.1890"
        },
        {
            "phone": "79175002040", "email": "stupnikov@otus.ru",
            "gender": 1, "birthday": "XXX"
        },
        {
            "phone": "79175002040", "email": "stupnikov@otus.ru",
            "gender": 1, "birthday": "01.01.2000", "first_name": 1
        },
        {
            "phone": "79175002040", "email": "stupnikov@otus.ru",
            "gender": 1, "birthday": "01.01.2000",
            "first_name": "s", "last_name": 2
        },
        {"phone": "79175002040", "birthday": "01.01.2000", "first_name": "s"},
        {"email": "stupnikov@otus.ru", "gender": 1, "last_name": 2},
    ])
    def test_invalid_score_request(self, arguments):
        request = {
            "account": "horns&hoofs", "login": "h&f",
            "method": "online_score", "arguments": arguments
        }
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(INVALID_REQUEST, code,
                         f'Failed with {arguments}. Response: {response}')
        self.assertTrue(len(response))

    @cases([
        {"phone": "79175002040", "email": "stupnikov@otus.ru"},
        {"phone": 79175002040, "email": "stupnikov@otus.ru"},
        {
            "gender": 1, "birthday": "01.01.2000",
            "first_name": "a", "last_name": "b"
        },
        {"gender": 0, "birthday": "01.01.2000"},
        {"gender": 2, "birthday": "01.01.2000"},
        {"first_name": "a", "last_name": "b"},
        {
            "phone": "79175002040", "email": "stupnikov@otus.ru",
            "gender": 1, "birthday": "01.01.2000",
            "first_name": "a", "last_name": "b"
        },
    ])
    def test_ok_score_request(self, arguments):
        request = {
            "account": "horns&hoofs", "login": "h&f",
            "method": "online_score", "arguments": arguments
        }
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(OK, code,
                         f'Failed with {arguments}. Response: {response}')
        score = response.get("score")
        self.assertTrue(
            isinstance(score, (int, float)) and score >= 0,
            arguments
        )
        self.assertEqual(
            sorted(self.context["has"]),
            sorted(arguments.keys()),
            f'Original request: {arguments}')

    def test_ok_score_admin_request(self):
        arguments = {"phone": "79175002040", "email": "stupnikov@otus.ru"}
        request = {
            "account": "horns&hoofs", "login": "admin",
            "method": "online_score", "arguments": arguments
        }
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(OK, code,
                         f'Failed with {arguments}. Response: {response}')
        score = response.get("score")
        self.assertEqual(score, 42)

    @cases([
        {},
        {"date": "20.07.2017"},
        {"client_ids": [], "date": "20.07.2017"},
        {"client_ids": {1: 2}, "date": "20.07.2017"},
        {"client_ids": ["1", "2"], "date": "20.07.2017"},
        {"client_ids": [1, 2], "date": "XXX"},
    ])
    def test_invalid_interests_request(self, arguments):
        request = {
            "account": "horns&hoofs", "login": "h&f",
            "method": "clients_interests", "arguments": arguments
        }
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(INVALID_REQUEST, code, arguments)
        self.assertTrue(len(response))

    @cases([
        {
            "client_ids": [1, 2, 3],
            "date": datetime.datetime.today().strftime("%d.%m.%Y")
        },
        {"client_ids": [1, 2], "date": "19.07.2017"},
        {"client_ids": [0]},
    ])
    def test_ok_interests_request(self, arguments):
        request = {
            "account": "horns&hoofs",
            "login": "h&f", "method": "clients_interests",
            "arguments": arguments
        }
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        self.assertEqual(OK, code, arguments)
        self.assertEqual(len(arguments["client_ids"]), len(response))
        self.assertTrue(
            all(
                (
                    v
                    and isinstance(v, list)
                    and all(isinstance(i, str) for i in v)
                ) for v in response.values()
            )
        )
        self.assertEqual(
            self.context.get("nclients"),
            len(arguments["client_ids"])
        )

    def tearDown(self):
        self.store.r.flushdb()
