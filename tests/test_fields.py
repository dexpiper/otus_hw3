import unittest

import thetypes as t
from tests.utils import cases


kwargs = dict(required=False, nullable=True)


class R:

    field = t.Field(**kwargs)
    charfield = t.CharField(**kwargs)
    argfield = t.ArgumentsField(**kwargs)
    email = t.EmailField(**kwargs)
    phone = t.PhoneField(**kwargs)
    date = t.DateField(**kwargs)
    birthday = t.BirthDayField(**kwargs)
    gender = t.GenderField(**kwargs)
    clientids = t.ClientIDsField(**kwargs)

    def __init__(self, **kwargs):
        self.field = kwargs.get('field', None)
        self.charfield = kwargs.get('charfield', None)
        self.argfield = kwargs.get('argfield', None)
        self.email = kwargs.get('email', None)
        self.phone = kwargs.get('phone', None)
        self.date = kwargs.get('date', None)
        self.birthday = kwargs.get('birthday', None)
        self.gender = kwargs.get('gender', None)
        self.clientids = kwargs.get('clientids', None)


class TestField(unittest.TestCase):

    def test_basic_field_instantiation(self):
        r = R(**dict(field='foo'))
        self.assertEqual(r.field, 'foo')

    @cases([
            'FOObar', 12345, [], ['Foobar123', 'eggs', 'spam'],
            [1, 2, 3, 54657, 9834, 1274824, 1214214, 0],
            {}, {'foo': 'bar', 'bar': 'foo'}
        ])
    def test_basic_field(self, value):
        r = R(**dict(field=value))
        self.assertEqual(r.field, value)

    @cases(['FOObar', '12345', 'Fafaf81819*&%^@!%$'])
    def test_good_char_field(self, value):
        r = R(**dict(charfield=value))
        self.assertEqual(r.charfield, value)

    @cases([12345, 123456787, [], {'foo': 'bar'}])
    def test_bad_char_field(self, value):
        with self.assertRaises(TypeError):
            R(**dict(charfield=value))

    @cases([{'FOObar': '12345'}, {}, {'foobar': 1234, 'spam': 'eggs'}])
    def test_good_arg_field(self, value):
        r = R(**dict(argfield=value))
        self.assertEqual(r.argfield, value)

    @cases(['Foobar', 123456787, []])
    def test_bad_arg_field(self, value):
        with self.assertRaises(TypeError):
            R(**dict(argfield=value))

    @cases(['foo@bar.com', 'stupnikov@otus.ru', 'eggs@spam.uk',
            'all@otus.rocks', 'b@egg.org'])
    def test_good_email(self, value):
        r = R(**dict(email=value))
        self.assertEqual(r.email, value)

    @cases(['foobar.com', 'Foobar', 'Spam@eggs'])
    def test_bad_email(self, value):
        with self.assertRaises(ValueError):
            R(**dict(email=value))

    @cases(['79121233239', 79011122233, '79998887766'])
    def test_good_phone(self, value):
        r = R(**dict(phone=value))
        self.assertEqual(r.phone, str(value))

    @cases(['Foobar', 89123456789, '+79201234567', '789012345'])
    def test_bad_phone(self, value):
        with self.assertRaises(ValueError):
            R(**dict(phone=str(value)))

    @cases(['27.12.2021', '01.01.1982', '06.11.1904'])
    def test_good_date(self, value):
        r = R(**dict(date=value))
        self.assertEqual(r.date, value)

    @cases(['2712.2021', '01011982', '06.11.19042'])
    def test_bad_date(self, value):
        with self.assertRaises(ValueError):
            R(**dict(date=value))

    @cases(['27.12.2021', '01.01.1982', '06.11.1958'])
    def test_good_birthday(self, value):
        r = R(**dict(birthday=value))
        self.assertEqual(r.birthday, value)

    @cases(['27.12.1900', '18.09.1867', '01.01.1000'])
    def test_bad_birthday(self, value):
        with self.assertRaises(ValueError):
            R(**dict(birthday=value))

    @cases([1, 2, 0])
    def test_gender(self, value):
        r = R(**dict(gender=value))
        self.assertEqual(r.gender, value)

    @cases([3, '1', 'male', 42, '13', 'Foobar', -1])
    def test_gender_bad_value(self, value):
        with self.assertRaises(ValueError):
            R(**dict(gender=value))

    @cases([
            [123, 323, 98765],
            [1, 2, 42, 12148124124],
            [42], []
        ])
    def test_clientids(self, value):
        r = R(**dict(clientids=value))
        self.assertEqual(r.clientids, value)

    @cases([
            3, '1', "[42, 42]", ['1', '2'],
            'male', 42, '13', 'Foobar', -1
        ])
    def test_clientids_bad_value(self, value):
        with self.assertRaises(ValueError):
            R(**dict(clientids=value))
