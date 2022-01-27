#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import hashlib
import datetime
import json
import logging
import uuid
from optparse import OptionParser
from http.server import HTTPServer, BaseHTTPRequestHandler

from thetypes import (ClientsInterestsRequest, FieldError, OnlineScoreRequest,
                      MethodRequest)
from database import RedisStore
from scoring import get_interests, get_score
from const import (ADMIN_SALT, SALT, INVALID_REQUEST, OK, FORBIDDEN,
                   NOT_FOUND, BAD_REQUEST, INTERNAL_ERROR, ERRORS)


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
    except FieldError as exc:
        logging.debug('Invalid request. Exception: %s' % exc)
        return str(exc), INVALID_REQUEST
    has = [
        name for name in request.fields
        if getattr(request, name) is not None
    ]
    ctx.update(has=has)
    condition = any((
            ('phone' in has) and ('email' in has),
            ('first_name' in has) and ('last_name' in has),
            ('gender' in has) and ('birthday' in has)
        ))
    if not condition:
        response = ('Please provide more client details in arg field')
        logging.debug('Insufficient online_score request: %s' % has)
        logging.debug('Pairs expected: phone-email, first-last names,'
                      'gender-birthday')
        return response, INVALID_REQUEST
    dct = dict(phone=request.phone, email=request.email,
               birthday=request.birthday, gender=request.gender,
               first_name=request.first_name,
               last_name=request.last_name)
    logging.debug(f'Score requested with: {dct}')
    score = get_score(store, **dct)
    score = score if not is_admin else 42
    response = dict(score=score)
    code = OK
    return response, code


def clients_interests_handler(args: dict, ctx: dict, store,
                              is_admin=False) -> tuple:
    try:
        request = ClientsInterestsRequest(args)
    except FieldError as exc:
        logging.debug('Invalid request. Exception: %s' % exc)
        return str(exc), INVALID_REQUEST
    nclients = len(request.client_ids)
    ctx.update(nclients=nclients)
    response = {
        id: get_interests(store, cid=id)
        for id in request.client_ids
    }
    code = OK
    return response, code


def method_handler(request: dict, ctx: dict, store) -> tuple:
    response, code = None, None
    data = request['body']

    try:
        method_request = MethodRequest(data)
    except FieldError as exc:
        logging.debug('Invalid request. Exception: %s' % exc)
        return str(exc), INVALID_REQUEST

    if not check_auth(method_request):
        return 'Forbidden', FORBIDDEN

    methods = {'online_score': online_score_handler,
               'clients_interests': clients_interests_handler}
    method = method_request.method
    if method not in methods:
        response = f'Invalid method name ({method}) in field method'
        code = NOT_FOUND
        logging.debug('Bad method name: %s' % method)
        return response, code
    logging.info('Calling %s' % methods[method])
    response, code = methods[method](method_request.arguments, ctx,
                                     store, is_admin=method_request.is_admin)
    logging.debug('ctx is: %s' % ctx)
    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    redis_url = os.environ.get('REDIS_URL', 'localhost:6379')
    host, port = redis_url.split(':')
    store = RedisStore(host=host, port=port)

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
        self.wfile.write(json.dumps(r).encode(encoding='utf-8'))
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
