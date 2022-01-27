import unittest

from thetypes import (Field, CharField, ArgumentsField, EmailField,
                      MethodRequest, PhoneField, DateField, BirthDayField,
                      GenderField, ClientIDsField, FieldError, Request)
from const import ADMIN_LOGIN
from tests.utils import cases


#
# Field testing
#
kwargs = dict(required=False, nullable=True)  # the most unpretentious options


class DummyClass:
    """
    Emulating real Field instantiation from a
    dict. R contains all possible fields.
    """
    field = Field(**kwargs)
    charfield = CharField(**kwargs)
    argfield = ArgumentsField(**kwargs)
    email = EmailField(**kwargs)
    phone = PhoneField(**kwargs)
    date = DateField(**kwargs)
    birthday = BirthDayField(**kwargs)
    gender = GenderField(**kwargs)
    clientids = ClientIDsField(**kwargs)

    def __init__(self, **dct):
        self.field = dct.get('field', None)
        self.charfield = dct.get('charfield', None)
        self.argfield = dct.get('argfield', None)
        self.email = dct.get('email', None)
        self.phone = dct.get('phone', None)
        self.date = dct.get('date', None)
        self.birthday = dct.get('birthday', None)
        self.gender = dct.get('gender', None)
        self.clientids = dct.get('clientids', None)


class TestField(unittest.TestCase):
    """
    Testing fields descriptor machinery via dummy R class.
    """
    def test_basic_field_instantiation(self):
        r = DummyClass(**dict(field='foo'))
        self.assertEqual(r.field, 'foo')

    @cases([
            'FOObar', 12345, [], ['Foobar123', 'eggs', 'spam'],
            [1, 2, 3, 54657, 9834, 1274824, 1214214, 0],
            {}, {'foo': 'bar', 'bar': 'foo'}
        ])
    def test_basic_field(self, value):
        r = DummyClass(**dict(field=value))
        self.assertEqual(r.field, value)


class TestCharField(unittest.TestCase):

    @cases(['FOObar', '12345', 'Fafaf81819*&%^@!%$'])
    def test_good_char_field(self, value):
        r = DummyClass(**dict(charfield=value))
        self.assertEqual(r.charfield, value)

    @cases([12345, 123456787, [], {'foo': 'bar'}])
    def test_bad_char_field(self, value):
        with self.assertRaises(FieldError):
            DummyClass(**dict(charfield=value))


class TestArgField(unittest.TestCase):

    @cases([{'FOObar': '12345'}, {}, {'foobar': 1234, 'spam': 'eggs'}])
    def test_good_arg_field(self, value):
        r = DummyClass(**dict(argfield=value))
        self.assertEqual(r.argfield, value)

    @cases(['Foobar', 123456787, []])
    def test_bad_arg_field(self, value):
        with self.assertRaises(FieldError):
            DummyClass(**dict(argfield=value))


class TestEmailField(unittest.TestCase):

    @cases(['foo@bar.com', 'stupnikov@otus.ru', 'eggs@spam.uk',
            'all@otus.rocks', 'b@egg.org'])
    def test_good_email(self, value):
        r = DummyClass(**dict(email=value))
        self.assertEqual(r.email, value)

    @cases(['foobar.com', 'Foobar', 'Spam@eggs'])
    def test_bad_email(self, value):
        with self.assertRaises(FieldError):
            DummyClass(**dict(email=value))


class TestPhoneField(unittest.TestCase):

    @cases(['79121233239', 79011122233, '79998887766'])
    def test_good_phone(self, value):
        r = DummyClass(**dict(phone=value))
        self.assertEqual(r.phone, str(value))

    @cases(['Foobar', 89123456789, '+79201234567', '789012345'])
    def test_bad_phone(self, value):
        with self.assertRaises(FieldError):
            DummyClass(**dict(phone=str(value)))


class TestDateField(unittest.TestCase):

    @cases(['27.12.2021', '01.01.1982', '06.11.1904'])
    def test_good_date(self, value):
        r = DummyClass(**dict(date=value))
        self.assertEqual(r.date, value)

    @cases(['2712.2021', '01011982', '06.11.19042', 'hello', 42])
    def test_bad_date(self, value):
        with self.assertRaises(FieldError):
            DummyClass(**dict(date=value))


class TestBirthDayField(unittest.TestCase):

    @cases(['27.12.2021', '01.01.1982', '06.11.1958'])
    def test_good_birthday(self, value):
        r = DummyClass(**dict(birthday=value))
        self.assertEqual(r.birthday, value)

    @cases(['27.12.1900', '18.09.1867', '01.01.1000', 'Foobar', 42])
    def test_bad_birthday(self, value):
        with self.assertRaises(FieldError):
            DummyClass(**dict(birthday=value))


class TestGenderField(unittest.TestCase):

    @cases([1, 2, 0])
    def test_gender(self, value):
        r = DummyClass(**dict(gender=value))
        self.assertEqual(r.gender, value)

    @cases([3, '1', 'male', 42, '13', -1])
    def test_gender_bad_value(self, value):
        with self.assertRaises(FieldError):
            DummyClass(**dict(gender=value))


class TestClientIDsField(unittest.TestCase):

    @cases([
            [123, 323, 98765],
            [1, 2, 42, 12148124124],
            [42], []
        ])
    def test_clientids(self, value):
        r = DummyClass(**dict(clientids=value))
        self.assertEqual(r.clientids, value)

    @cases([
            3, '1', "[42, 42]", ['1', '2'],
            'male', 42, '13', 'Foobar', -1
        ])
    def test_clientids_bad_value(self, value):
        with self.assertRaises(FieldError):
            DummyClass(**dict(clientids=value))


#
# Request testing
#
class Req(Request):
    """
    A valid Request class with all possible fields
    """
    field = Field(**kwargs)
    charfield = CharField(**kwargs)
    argfield = ArgumentsField(**kwargs)
    email = EmailField(**kwargs)
    phone = PhoneField(**kwargs)
    date = DateField(**kwargs)
    birthday = BirthDayField(**kwargs)
    gender = GenderField(**kwargs)
    clientids = ClientIDsField(**kwargs)


class Simple(Request):
    """
    Just basic fields
    """
    field1 = Field(**kwargs)
    field2 = Field(**kwargs)
    field3 = Field(**kwargs)


class Demanding(Request):
    """
    Empty or unset field should raise a FieldError
    """
    field = Field(required=True, nullable=False)


class TestRequest(unittest.TestCase):
    """
    Testing basic Request class and its machinery
    """
    def setUp(self):
        self.valid_dct = dict(
            filed='Basicfield', charfield='Charfield',
            argfield={'foobar': 1234, 'spam': 'eggs'},
            email='all@otus.rocks', phone='79121233239',
            date='27.12.2021', birthday='27.12.1995',
            gender=1, clientids=[1, 2, 42, 12148124124]
        )
        self.req_fields = [
                'field', 'charfield', 'argfield', 'email', 'phone',
                'date', 'birthday', 'gender', 'clientids'
            ]
        self.simple_fields = ['field1', 'field2', 'field3']

    def test_basic_init(self):
        r = Req(self.valid_dct, validate=False)
        self.assertEqual(r._dct, self.valid_dct)

    def test_fields_property(self):
        r = Req(self.valid_dct, validate=False)
        self.assertEqual(
            r.fields.sort(),
            self.req_fields.sort()
        )

    def test_good_validation(self):
        r = Req(self.valid_dct, validate=False)
        r.validate()
        for f in self.req_fields:
            self.assertEqual(getattr(r, f), self.valid_dct.get(f))

    @cases([{}, {'field': ''}, {'field': None}])
    def test_bad_validation(self, dct):
        r = Demanding(dct, validate=False)
        with self.assertRaises(FieldError):
            r.validate()

    def test_check_default_value_none(self):
        r = Req(dict())
        for f in self.req_fields:
            self.assertEqual(getattr(r, f), None)

    @cases(['Foobar', False, True, 21345, [], {'foo': 'bar'}, ('Foo',)])
    def test_check_other_default_value(self, def_value):
        r = Simple(dict(), default=def_value)
        for f in self.simple_fields:
            self.assertEqual(getattr(r, f), def_value)

    def test_undemanding_with_random_dict(self):
        dct = dict(nobody_expects=' ===> Spanish Inquisition')
        r = Req(dct)
        for f in self.req_fields:
            # should be no errors, just None in all the Fields
            self.assertEqual(getattr(r, f), None)

    def test_demanding_with_random_dict(self):
        dct = dict(nobody_expects=' ===> Spanish Inquisition')
        with self.assertRaises(FieldError):
            Demanding(dct)


class TestMethodRequest(unittest.TestCase):

    def test_good_method_request(self):
        dct = dict(
            account='hoofs', login='h&h', token='spam',
            arguments={'spam': 'witheggs'},
            method='eggswithspam'
        )
        r = MethodRequest(dct)
        for key, value in dct.items():
            self.assertEqual(getattr(r, key), value)

    def test_bad_method_request(self):
        dct = dict(nobody_expects=' ===> Spanish Inquisition')
        with self.assertRaises(FieldError):
            MethodRequest(dct)

    @cases(['horns&hoofs', 'ADMIN', 'theboss', 'King Arthur'])
    def test_method_request_not_admin_login(self, login):
        dct = dict(
            account='hoofs', login=login, token='spam',
            arguments={'spam': 'witheggs'},
            method='eggswithspam'
        )
        r = MethodRequest(dct)
        self.assertFalse(r.is_admin)

    def test_method_request_valid_admin_login(self):
        dct = dict(
            account='hoofs', login=ADMIN_LOGIN, token='spam',
            arguments={'spam': 'witheggs'},
            method='eggswithspam'
        )
        r = MethodRequest(dct)
        self.assertTrue(r.is_admin)
