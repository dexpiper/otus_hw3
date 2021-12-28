from copy import deepcopy

from utils.fields import (ArgumentsField, BirthDayField, CharField,
                          ClientIDsField, DateField, EmailField,
                          GenderField, PhoneField, Field, ValidationResult)
from utils.vars import ADMIN_LOGIN


class Request:

    def __init__(self):
        self._fields = None

    @property
    def fields(self):
        return self._fields

    @fields.setter
    def fields(self, arg):
        if not self._fields:
            self._fields = self.get_fields()
        else:
            self._fields = arg

    @classmethod
    def get_fields(cls) -> dict:
        return {
            n: f for n, f in cls.__dict__.items()
            if not n.startswith('_') and isinstance(f, Field)
        }

    # TODO: Here is a mistake...
    def update_fields(self, request) -> None:
        print('    *** METHOD CALLED')
        f = deepcopy(self.fields)
        for el in request:
            f[el].value = request[el]
        self.fields = f

    def validate(self) -> ValidationResult:
        result = ValidationResult()
        for name in self.fields:
            field = self.fields[name]
            if not field.valid:
                result.append(field.val_info.error_message)
        return result

    def get_dict(self) -> dict:
        dct = {
            f_name: field_obj.value
            for f_name, field_obj in self.fields
        }
        return dct


class ClientsInterestsRequest(Request):
    client_ids = ClientIDsField(required=True, nullable=False)
    date = DateField(required=False, nullable=True)

    @property
    def nclients(self):
        return self._nclients()

    def _nclients(self):
        client_ids = self.fields['client_ids'].value
        return len(client_ids) if client_ids else 0


class OnlineScoreRequest(Request):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    @property
    def has(self):
        return self._filled_fields()

    def _filled_fields(self):
        return [name for name in self.fields if self.fields[name].value]

    def validate(self) -> ValidationResult:
        v = super().validate()
        condition = any((
            'phone' and 'email' in self.has,
            'first_name' and 'last_name' in self.has,
            'gender' and 'birthday' in self.has
        ))
        if not condition:
            v.append('LookupError. Please provide more information '
                     'about client in your request')
        return v


class MethodRequest(Request):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN
