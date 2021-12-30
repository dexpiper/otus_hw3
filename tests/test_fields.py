import unittest

from utils import thetypes as t
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

    @cases([{'FOObar': '12345'}, {}, {'foobar': 1234, 'spam': 'eggs'}])
    def test_good_email(self, value):
        r = R(**dict(email=value))
        self.assertEqual(r.email, value)

    @cases(['Foobar', 123456787, []])
    def test_bad_email(self, value):
        with self.assertRaises(TypeError):
            R(**dict(email=value))
