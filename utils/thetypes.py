from abc import ABC, abstractmethod
from datetime import datetime
import re

from api import FEMALE, MALE, UNKNOWN


class Validator(ABC):

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
            raise LookupError(f'Field {self.name} should be in request')
        cond2 = (False if not self.nullable and value in ('', [], {})
                 else True)
        if not cond2:
            raise ValueError(f'Field {self.name} cannot be empty')


class CharField(Field):

    def validate(self, value):
        super().validate(value)
        if not isinstance(value, (str, type(None))):
            raise TypeError(f'Field {self.name} should be a str')

    def __set__(self, obj, value):
        self.validate(value)
        setattr(obj, self.private_name, value)


class ArgumentsField(Field):

    def validate(self, value):
        super().validate(value)
        if not isinstance(value, (dict, type(None))):
            raise TypeError(
                f'Expected {value!r} in {self.name} to be dict-like object'
            )


class EmailField(CharField):
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'

    def validate(self, value):
        super().validate(value)
        if value is None:
            return
        if not re.fullmatch(EmailField.regex, value):
            raise ValueError(
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
            raise ValueError(
                f'Bad phone number in field {self.name} ({value!r} not valid)'
            )

    def __set__(self, obj, value):
        self.validate(value)
        setattr(obj, self.private_name, str(value))


class DateField(CharField):
    format = '%d.%m.%Y'

    def validate(self, value):
        super().validate(value)
        if value is None:
            return
        try:
            datetime.strptime(value, DateField.format)
        except ValueError:
            raise ValueError(
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
            raise ValueError(
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
            raise ValueError(
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
            raise ValueError(err_message)
        if not all(
            [True if isinstance(el, int) else False
             for el in value]
        ):
            raise ValueError(err_message)


class ClientsInterestsRequest():
    client_ids = ClientIDsField(required=True, nullable=False)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest():
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)


class MethodRequest():
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)
