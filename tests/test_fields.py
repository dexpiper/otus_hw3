import unittest

from utils import fields
from tests.utils import cases


def parent_validation(slf, cls_for_test, empty_val=''):
    f = cls_for_test(required=True, nullable=False)
    slf.assertFalse(f.valid)
    slf.assertIn('LookupError', f.val_info())
    f.value = empty_val
    slf.assertFalse(f.valid)
    slf.assertIn('ValueError', f.val_info())


class TestValresultClass(unittest.TestCase):

    def setUp(self):
        self.v = fields.ValidationResult('Some error')
        self.str_message = 'Another error message'
        self.lst_messages = ['Error here', 'Error there']

    def test_bad_validation_result(self):
        self.assertEqual(self.v.error_message, 'Some error')
        self.assertEqual(bool(self.v), False)

    def test_good_validation_result(self):
        v = fields.ValidationResult()
        self.assertEqual(v.error_message, None)
        self.assertEqual(bool(v), True)

    def test_validation_message_append_empty(self):
        v = fields.ValidationResult()
        v.append(self.str_message)
        self.assertEqual(v.error_message, 'Another error message')
        self.assertEqual(v(), 'Another error message')

    def test_validation_message_append_notempty(self):
        self.v.append(self.str_message)
        self.assertEqual(self.v.error_message,
                         'Some error; Another error message')

    def test_validation_message_append_list(self):
        self.v.append(self.lst_messages)
        self.assertEqual(self.v.error_message,
                         'Some error; Error here; Error there')


class TestParentField(unittest.TestCase):

    def test_field_creation(self):
        f = fields.Field(required=True, nullable=False)
        f.value = 'Foobar123'
        self.assertEqual(f.value, 'Foobar123')
        self.assertEqual(f.valid, True)

    def test_field_creation_null(self):
        """No value inserted in mandatory field"""
        f = fields.Field(required=True)
        self.assertFalse(f.valid)
        self.assertIsNotNone(f.val_info())
        self.assertIn('LookupError', f.val_info())

    def test_field_creation_empty(self):
        """Empty string in non-nullable field"""
        f = fields.Field(required=False, nullable=False)
        f.value = ''
        self.assertFalse(f.valid)
        self.assertIn('ValueError', f.val_info())


class TestCharField(unittest.TestCase):

    def test_charfield_creation(self):
        f = fields.CharField(required=True, nullable=False)
        f.value = 'Foobar'
        self.assertTrue(f.valid)
        self.assertEqual(f.value, 'Foobar')

    def test_charfield_parent_validation(self):
        f = fields.CharField(required=True, nullable=False)
        f.value = 'Foobar'
        self.assertTrue(f.valid)
        f.value = None
        self.assertFalse(f.valid)
        self.assertIn('LookupError', f.val_info())
        f.value = ' '
        self.assertFalse(f.valid)
        self.assertIn('ValueError', f.val_info())

    def test_charfield_self_validation_fromnum(self):
        f = fields.CharField(required=True, nullable=False)
        f.value = 1234567889
        self.assertTrue(f.valid)
        self.assertEqual(f.value, '1234567889')


class TestArgumentsField(unittest.TestCase):

    @cases(['{"Foobar": 1234}', '{}', '{"Foo": "bar", "1": 2}'])
    def test_argfield_creation(self, value):
        f = fields.ArgumentsField(required=True, nullable=True)
        f.value = value
        self.assertTrue(f.valid, f'Error with {value}')
        self.assertIsInstance(f.value, dict)

    def test_argfield_parent_validation(self):
        parent_validation(self, fields.ArgumentsField, empty_val='{}')

    def test_argfield_self_validation(self):
        f = fields.ArgumentsField(required=True, nullable=False)
        f.value = 'Foobar'
        self.assertFalse(f.valid)
        self.assertIn('TypeError', f.val_info())
        f.value = 12345678
        self.assertFalse(f.valid)
        self.assertIn('TypeError', f.val_info())


class TestEmailField(unittest.TestCase):

    @cases(['foo@bar.com', 'stupnikov@otus.ru', 'eggs@spam.uk',
            'all@otus.rocks', 'b@egg.org'])
    def test_email_creation(self, email):
        f = fields.EmailField(required=True, nullable=False)
        f.value = email
        self.assertTrue(f.valid)

    @cases(['foobar.com', 'Foobar', 'Spam@eggs', 12345])
    def test_bad_email_creation(self, bad_email):
        f = fields.EmailField(required=True, nullable=False)
        f.value = bad_email
        self.assertFalse(f.valid)
        self.assertIn('ValueError', f.val_info())

    def test_email_parent_validation(self):
        parent_validation(self, fields.EmailField)


class TestPhoneField(unittest.TestCase):

    @cases(['+79121233239', 790111122233, '89998887766'])
    def test_phone_creation(self, phone):
        f = fields.PhoneField(required=True, nullable=False)
        f.value = phone
        self.assertTrue(f.valid)

    @cases([12345, 'Foobar', '+8nine890123456'])
    def test_bad_phone(self, bad_phone):
        f = fields.PhoneField(required=True, nullable=False)
        f.value = bad_phone
        self.assertFalse(f.valid)
        self.assertIn('ValueError', f.val_info())

    def test_phone_parent_validation(self):
        parent_validation(self, fields.PhoneField)


class TestDateField(unittest.TestCase):

    @cases(['27.12.2021', '01.01.1982', '06.11.1904'])
    def test_date_creation(self, date):
        f = fields.DateField(required=True, nullable=False)
        f.value = date
        self.assertTrue(f.valid, f'Not valid with {date}')

    @cases(['2712.2021', 24011992, '01011982', '06.11.19042'])
    def test_bad_date_creation(self, bad_date):
        f = fields.DateField(required=True, nullable=False)
        f.value = bad_date
        self.assertFalse(f.valid, f'Considered valid with {bad_date}')
        self.assertIn('ValueError', f.val_info())

    def test_date_parent_validation(self):
        parent_validation(self, fields.DateField)


class TestBirthDayField(unittest.TestCase):

    @cases(['27.12.2021', '01.01.1982', '06.11.1958'])
    def test_birthday_creation(self, date):
        f = fields.BirthDayField(required=True, nullable=False)
        f.value = date
        self.assertTrue(f.valid, f'Not valid with {date}')

    @cases(['27.12.1900', '18.09.1867', '01.01.1000'])
    def test_bad_date_creation(self, bad_date):
        f = fields.BirthDayField(required=True, nullable=False)
        f.value = bad_date
        self.assertFalse(f.valid, f'Considered valid with {bad_date}')
        self.assertIn('ValueError', f.val_info())

    def test_date_parent_validation(self):
        parent_validation(self, fields.BirthDayField)


class TestGenderField(unittest.TestCase):

    @cases([1, 2, 0, '1', '2', '0'])
    def test_good_gender_field(self, value):
        f = fields.GenderField(required=True, nullable=False)
        f.value = value
        self.assertTrue(f.valid, f'Not valid with {value}')

    @cases([3, 'male', 42, '13', 'Foobar', -1])
    def test_bad_gender_creation(self, bad_value):
        f = fields.GenderField(required=True, nullable=False)
        f.value = bad_value
        self.assertFalse(f.valid, f'Considered valid with {bad_value}')
        self.assertIn('ValueError', f.val_info())

    def test_gender_parent_validation(self):
        parent_validation(self, fields.GenderField)


class TestClientIDsField(unittest.TestCase):

    @cases([
            [123, 323, 98765],
            "[1, 2, 42, 12148124124]",
            "[42]"
    ])
    def test_good_id_field(self, value):
        f = fields.ClientIDsField(required=True, nullable=False)
        f.value = value
        self.assertTrue(f.valid, f'Not valid with {value}')

    @cases([42, 'Foobar', '[42, "Forty-two", 9, 8]'])
    def test_bad_id_field_creation(self, bad_value):
        f = fields.ClientIDsField(required=True, nullable=False)
        f.value = bad_value
        self.assertFalse(f.valid, f'Considered valid with {bad_value}')
        self.assertIn('ValueError', f.val_info())

    def test_id_parent_validation(self):
        parent_validation(self, fields.ClientIDsField, empty_val='[]')
