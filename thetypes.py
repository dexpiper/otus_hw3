from abc import ABC, abstractmethod
from datetime import datetime
import re

from const import FEMALE, MALE, UNKNOWN, ADMIN_LOGIN


class FieldError(Exception):
    pass


class Validator(ABC):
    """
    Data-descriptor and base class for field descriptors.
    """
    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = '_' + name

    def __get__(self, obj, objtype=None):
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        self.validate(value)
        setattr(obj, self.private_name, value)

    @abstractmethod
    def validate(self, value):
        pass


class Field(Validator):

    def __init__(self, required=True, nullable=False):
        self.required = required
        self.nullable = nullable

    def validate(self, value):
        cond1 = False if self.required and value is None else True
        if not cond1:
            raise FieldError(f'Field {self.name} should be in request')
        cond2 = (False if not self.nullable and value in ('', [], {})
                 else True)
        if not cond2:
            raise FieldError(f'Field {self.name} cannot be empty')


class CharField(Field):

    def validate(self, value):
        super().validate(value)
        if not isinstance(value, (str, type(None))):
            raise FieldError(f'Field {self.name} should be a str')

    def __set__(self, obj, value):
        self.validate(value)
        setattr(obj, self.private_name, value)


class ArgumentsField(Field):

    def validate(self, value):
        super().validate(value)
        if not isinstance(value, (dict, type(None))):
            raise FieldError(
                f'Expected {value!r} in {self.name} to be dict-like object'
            )


class EmailField(CharField):
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'

    def validate(self, value):
        super().validate(value)
        if value is None:
            return
        if not re.fullmatch(EmailField.regex, value):
            raise FieldError(
                f'Bad email in field {self.name} ({value!r} not valid)'
            )


class PhoneField(Field):
    regex = r'^7\d{10}$'

    def validate(self, value):
        if isinstance(value, int):
            value = str(value)
        super().validate(value)
        if value is None:
            return
        if not re.fullmatch(PhoneField.regex, value):
            raise FieldError(
                f'Bad phone number in field {self.name} ({value!r} not valid)'
            )

    def __set__(self, obj, value):
        self.validate(value)
        if value:
            setattr(obj, self.private_name, str(value))
        else:
            setattr(obj, self.private_name, value)


class DateField(CharField):
    format = '%d.%m.%Y'

    def validate(self, value):
        super().validate(value)
        if value is None:
            return
        try:
            datetime.strptime(value, DateField.format)
        except ValueError:
            raise FieldError(
                f'Bad date format in field {self.name} ({value!r} not valid)'
            )


class BirthDayField(DateField):

    def validate(self, value):
        super().validate(value)
        if value is None:
            return
        date = datetime.strptime(value, DateField.format)
        delta = datetime.today() - date
        if delta.days > 365*70:
            raise FieldError(
                f'Bad date in field {self.name}: '
                f'more than 70 years since {value!r}'
            )


class GenderField(Field):
    genders = UNKNOWN, MALE, FEMALE

    def validate(self, value):
        super().validate(value)
        if value is None:
            return
        if value not in GenderField.genders:
            raise FieldError(
                f'Bad value for {self.name} field ({value!r}). '
                'Should be an integer from {0, 1, 2}'
            )


class ClientIDsField(Field):

    def validate(self, value):
        super().validate(value)
        if value is None:
            return
        err_message = (f'Bad value for {self.name} field ({value!r}). '
                       'Should be a list-like object of integers')
        if not isinstance(value, list):
            raise FieldError(err_message)
        if not all(
            [True if isinstance(el, int) else False
             for el in value]
        ):
            raise FieldError(err_message)


class Request:
    reserved_properties = ['is_admin']

    def __init__(self, dct: dict, default=None):
        '''
        Default request initializer from a dict.

        >>> r = Request({'attr1': 'value', 'attr2': 'value'})

        Any properties in the children Requsets should be defined
        in the <reserved_properties> base class var to avoid AttributeError
        '''
        attrs = [
                    key for key in dir(self)
                    if not any((
                        key.startswith('_'),
                        key in Request.reserved_properties
                    ))
                ]
        for attr in attrs:
            setattr(self, attr, dct.get(attr, default))


class ClientsInterestsRequest(Request):
    client_ids = ClientIDsField(required=True, nullable=False)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest(Request):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)


class MethodRequest(Request):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN
