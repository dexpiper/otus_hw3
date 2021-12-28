import unittest

from utils import requests
# from tests.utils import cases


class TestRequestClass(unittest.TestCase):

    def setUp(self):
        self.request = dict(
            account='Boo',
            login='BooBoo',
            token='112124124124124214egeg1r3',
            arguments={'Foo': 'bar'},
            method='Goo',
        )

    def test_request_creation(self):
        r = requests.MethodRequest()
        field_names = ('account login token arguments method'.split())
        for f in field_names:
            self.assertIn(f, r.fields.keys())

    def test_request_fillup(self):
        r = requests.MethodRequest()
        r.account.value = 'Boo'
        r.login.value = 'BooBoo'
        r.token.value = '112124124124124214egeg1r3'
        r.arguments.value = '[1, 2, "Foo", 4]'
        r.method.value = 'Goo'
        for f in r.fields:
            self.assertTrue(r.fields[f].value)

    def test_method_fromdict(self):
        r = requests.MethodRequest()
        r.update_fields(self.request)
        for k in self.request:
            if isinstance(r.fields[k].value, dict):
                self.assertEqual(
                    r.fields[k].value,
                    self.request[k]
                )

    def test_request_validation(self):
        r = requests.MethodRequest()
        r.update_fields(self.request)
        validation = r.validate()
        self.assertTrue(bool(validation))

    def test_request_bad_validation(self):
        r = requests.OnlineScoreRequest()
        r.update_fields(dict(
                    first_name='John',
                    phone='iPhone',
                    birthday='12.05.1900'
                ))
        validation = r.validate()
        self.assertFalse(bool(validation))
        self.assertIn('ValueError', validation.error_message)

    def test_client_interst_nclients_method(self):
        r = requests.ClientsInterestsRequest()
        r.update_fields(dict(client_ids=[12345, 98765, 76545, 42]))
        self.assertTrue(bool(r.validate()))
        self.assertEqual(r.nclients, 4)

    def test_client_onlinescore_has_method(self):
        r = requests.OnlineScoreRequest()
        r.update_fields(dict(
                    first_name='John',
                    phone='iPhone',
                    birthday='12.05.1900'
                ))
        self.assertEqual(len(r.has), 3)

    def test_empty_request(self):
        r = requests.MethodRequest()
        validation = r.validate()
        self.assertFalse(bool(validation))
        print(validation.error_message)
