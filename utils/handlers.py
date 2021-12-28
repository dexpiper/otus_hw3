import hashlib
import datetime

from utils import requests
from utils.requests import MethodRequest, Request
from utils.vars import (SALT, ADMIN_LOGIN, ADMIN_SALT, OK,
                        BAD_REQUEST, FORBIDDEN, NOT_FOUND,
                        INVALID_REQUEST, INTERNAL_ERROR,
                        ERRORS, UNKNOWN, MALE, FEMALE,
                        GENDERS)
from scoring import get_score, get_interests


def check_auth(request: Request) -> bool:
    if request.is_admin:
        digest = hashlib.sha512(
                (
                    datetime.datetime.now().strftime("%Y%m%d%H")
                    + ADMIN_SALT
                ).encode('utf-8')
            ).hexdigest()
    else:
        digest = hashlib.sha512(
                (
                    request.account.value
                    + request.login.value
                    + SALT
                ).encode('utf-8')
            ).hexdigest()
    if digest == request.token:
        return True
    return False


def method_handler(request: dict, ctx: dict, store) -> tuple:
    response, code = None, None
    data = request['body']
    r = MethodRequest()
    if not data:
        print('   *** NO DATA!')
    r.update_fields(data)
    methods = {'online_score': online_score_handler,
               'clients_interests': clients_interests_handler}

    # validation
    # TODO: here is a mistake...
    print(f'   *** r.method.value: {r.method.value}')
    if r.method.value not in methods:
        print(f'   *** GOT HERE!')
        error = "ValueError. Invalid method name"
        code = INVALID_REQUEST
        response = dict(code=code, error=error)
        return response, code
    validation = r.validate()
    if not bool(validation):
        error = validation.error_message
        code = INVALID_REQUEST
        response = dict(code=code, error=error)
        return response, code

    # authentication
    if not check_auth(r):
        error = "Forbidden"
        code = FORBIDDEN
        response = dict(code=code, error=error)
        return response, code

    # calling appropriate handler with args
    method = methods[r.method.value]
    response, code = method(r.arguments, ctx, store, isadmin=r.is_admin)
    return response, code


def online_score_handler(args: dict, ctx: dict, store,
                         isadmin=False) -> tuple:
    response, code = None, None
    r = requests.OnlineScoreRequest(args)
    validation = r.validate()
    if not bool(validation):
        error = validation.error_message
        code = INVALID_REQUEST
        response = dict(code=code, error=error)
        return response, code
    ctx.update(r.has)
    dct = r.get_dict()
    dct.update(store=store)
    score = get_score(dct) if not isadmin else 42
    response = dict(score=score)
    code = OK
    return response, code


def clients_interests_handler(args: dict, ctx: dict, store) -> tuple:
    response, code = None, None
    r = requests.ClientsInterestsRequest(args)
    validation = r.validate()
    if not bool(validation):
        error = validation.error_message
        code = INVALID_REQUEST
        response = dict(code=code, error=error)
        return response, code
    ctx.update(r.nclients)
    response = {
        id: get_interests(store, cid=None)
        for id in r.client_ids
    }
    code = OK
    return response, code
