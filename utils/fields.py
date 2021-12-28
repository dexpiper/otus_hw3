import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
import json

from utils.vars import FEMALE, MALE, UNKNOWN


@dataclass
class ValidationResult:
    """
    Store validation results and accumulate error messages.
    """
    error_message: str = None

    def __bool__(self) -> bool:
        return True if not self.error_message else False

    def __call__(self) -> str:
        return self.error_message

    def append(self, other) -> None:
        """
        Append error_message to existent one.
        """
        if isinstance(other, str):
            old_errs = self.error_message if self.error_message else ''
            unite_errs = '; '.join((old_errs, other)) if old_errs else other
            if unite_errs.strip() == ';':
                return
            self.error_message = unite_errs.strip()
        if isinstance(other, list or tuple):
            self.append('; '.join(other))


class BaseField(ABC):

    @abstractmethod
    def validation() -> ValidationResult:
        """
        Should always return ValidationResult
        """
        return ValidationResult()


class Field(BaseField):

    def __init__(self, value=None, required=True, nullable=False):
        self._value = value
        self.required = required
        self.nullable = nullable

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, arg):
        self._value = arg

    @property
    def valid(self) -> bool:
        self.val_info = self.validation()
        assert isinstance(self.val_info, ValidationResult)
        return bool(self.val_info)

    def validation(self) -> ValidationResult:
        """
        Provides basic validation for any Field.
        In child classes should call super().validation() before
        other validation checks.
        """
        cond1 = False if self.required and self.value is None else True
        cond2 = (False if not self.nullable and self.value in ('', [], {})
                 else True)
        if not bool(cond1 and cond2):
            message = (
                'LookupError. Mandatory field not defined' if not cond1
                else 'ValueError. Field cannot be empty'
            )
            return ValidationResult(message)
        else:
            return ValidationResult()


class CharField(Field):

    @property
    def value(self):
        return super().value

    @value.setter
    def value(self, arg):
        self._value = str(arg).strip() if arg is not None else arg


class ArgumentsField(Field):

    @property
    def value(self):
        return super().value

    @value.setter
    def value(self, arg):
        if not isinstance(arg, str):
            self._value = arg
            return
        try:
            self._value = json.loads(arg)
        except json.decoder.JSONDecodeError as exc:
            self._value = f'DecodeError: {exc}'
        except TypeError as exc:
            self._value = f'DecodeError: {exc}'

    def validation(self):
        v = super().validation()
        if (not v) or (v and not self.value):
            return v
        if not isinstance(self.value, dict):
            return ValidationResult('TypeError. Expected dict (JSON object)')
        return v


class EmailField(CharField):
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'

    def validation(self):
        v = super().validation()
        if (not v) or (v and not self.value):
            return v
        if not re.fullmatch(EmailField.regex, self.value):
            return ValidationResult('ValueError. Bad email address')
        return v


class PhoneField(CharField):
    regex = r'^\+?\d{7,12}$'

    def validation(self):
        if isinstance(self.value, int):
            self.value = str(self.value)
        v = super().validation()
        if (not v) or (v and not self.value):
            return v
        if not re.fullmatch(PhoneField.regex, self.value):
            return ValidationResult('ValueError. Bad phone number')
        return v


class DateField(CharField):
    format = '%d.%m.%Y'

    def validation(self):
        v = super().validation()
        if (not v) or (v and not self.value):
            return v
        try:
            datetime.strptime(self.value, DateField.format)
        except ValueError:
            return ValidationResult(
                'ValueError. Bad date (expected DD.MM.YYYY)'
            )
        return v


class BirthDayField(DateField):

    def validation(self):
        v = super().validation()
        if (not v) or (v and not self.value):
            return v
        date = datetime.strptime(self.value, DateField.format)
        delta = datetime.today() - date
        if delta.days > 365*70:
            return ValidationResult(
                f'ValueError. Bad date: more than 70 years since {self.value}'
            )
        return v


class GenderField(Field):

    def validation(self):
        v = super().validation()
        if (not v) or (v and not self.value):
            return v
        try:
            gender = int(self.value)
            grs = UNKNOWN, MALE, FEMALE
            if gender not in grs:
                raise ValueError
        except ValueError:
            return ValidationResult('ValueError. Only 0, 1 or 2 excepted')
        return v


class ClientIDsField(Field):

    @property
    def value(self):
        return super().value

    @value.setter
    def value(self, arg):
        if isinstance(arg, list):
            self._value = arg
            return
        try:
            self._value = json.loads(arg)
        except json.decoder.JSONDecodeError:
            self._value = 'DecodeError'
        except TypeError:
            self._value = 'TypeError'

    def validation(self):
        v = super().validation()
        if (not v) or (v and not self.value):
            return v
        try:
            if not isinstance(self.value, list):
                raise ValueError
            self.value = [int(el) for el in self.value]
        except ValueError:
            return ValidationResult(
                'ValueError. Only massive of integers excepted'
            )
        return v
