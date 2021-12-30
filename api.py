#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
import datetime
import json
import logging
import uuid
from optparse import OptionParser
from http.server import HTTPServer, BaseHTTPRequestHandler

from thetypes import (ClientsInterestsRequest, OnlineScoreRequest,
                      MethodRequest)
from scoring import get_interests, get_score


SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}


def check_auth(request) -> bool:
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
                    request.account
                    + request.login
                    + SALT
                ).encode('utf-8')
            ).hexdigest()
    if digest == request.token:
        return True
    return False


def online_score_handler(args: dict, ctx: dict, store,
                         is_admin=False) -> tuple:
    try:
        request = OnlineScoreRequest(args)
    except Exception as exc:
        return exc, INVALID_REQUEST
    request.has = [
        name for name, value in request.__dict__.items()
        if not name.startswith('_') and value
    ]
    ctx.update(has=request.has)
    condition = any((
            'phone' and 'email' in request.has,
            'first_name' and 'last_name' in request.has,
            'gender' and 'birthday' in request.has
        ))
    if not condition:
        response = ('Please provide more information '
                    'about client in your request. At least pairs: '
                    'phone-email, first-last names, gender-birthday')
        return response, INVALID_REQUEST
    score = get_score(store, phone=request.phone, email=request.email,
                      birthday=request.birthday, first_name=request.first_name,
                      last_name=request.last_name)
    score = score if not is_admin else 42
    response = dict(score=score)
    code = OK
    return response, code


def clients_interests_handler(args: dict, ctx: dict, store,
                              is_admin=False) -> tuple:
    try:
        request = ClientsInterestsRequest(args)
    except Exception as exc:
        return exc, INVALID_REQUEST
    ctx.update(nclients=len(request.client_ids))
    response = {
        id: get_interests(store, cid=None)
        for id in request.client_ids
    }
    code = OK
    return response, code


def method_handler(request: dict, ctx: dict, store) -> tuple:
    response, code = None, None
    data = request['body']
    try:
        method_request = MethodRequest(data)
    except Exception as exc:
        return exc, INVALID_REQUEST

    if not check_auth(method_request):
        return 'Invalid token', FORBIDDEN

    methods = {'online_score': online_score_handler,
               'clients_interests': clients_interests_handler}
    method = method_request.method.value
    if method not in methods:
        response = f'Invalid method name ({method}) in field method'
        code = NOT_FOUND
        return response, code
    response, code = methods[method](method.arguments, ctx,
                                     store, is_admin=method.is_admin)
    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except Exception:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info(
                "%s: %s %s" % (self.path, data_string, context["request_id"])
            )
            if path in self.router:
                try:
                    response, code = self.router[path](
                        {"body": request, "headers": self.headers},
                        context,
                        self.store
                    )
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {
                "error": response or ERRORS.get(code, "Unknown Error"),
                "code": code
            }
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r))
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(
        filename=opts.log, level=logging.INFO,
        format='[%(asctime)s] %(levelname).1s %(message)s',
        datefmt='%Y.%m.%d %H:%M:%S'
    )
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
