# Scoring API

Example scoring service for bank-like organizations.


## Table of contents
1. [Server starting](#server-starting)
2. [API description](#api)
    * [Request structure](#request-structure)
    * [Methods](#methods)
3. [Testing](#testing)


## Server starting

1. *cd* to the dir with the scoring api
2. Run:

`$ python3 api.py [-p, --port (default: 8080)] [-l, --log (default - None)]`

3. If --log provided, log would be placed in logfile, else it goes to the stdout.


## API

API description:

* Request structure
* Online Score method
* clients Interests method


### Request structure

` {"account": "<company name>", "login": "<username>", "method": "<methodname>", "token": "<TOKEN>", "arguments": {<a dict-like object with arguments of the requested method>}} `

**Answer**

If OK:

`{"code": <HTTP-code>, "response": {<response>}}`

Else:

`{"code": <HTTP-code>, "error": {<error message>}}`

### Methods

1. **online_score**
2. **clients_interests**

#### online_score

Get client score.

**Arguments:**

You should provide at least one pair: *phone-email*, *first name-last name*, *gender-birthday* with non-null values.

* *phone* - string or integer, 11 digits starting from 7, optional, nullable
* *email* - string with @, optional, nullable
* *first_name* - string, optional, nullable
* *last_name* - string, optional, nullable
* *birthday* - date in DD.MM.YYYY format (< 70 years ago), optional, nullable
* *gender* - integer 0, 1 or 2, optional, nullable

**Answer**

`{"score": <some number>}`

Valid admin user will ever get '42' in answer.

If validation error:

`{"code": 422, "error": "<error message>"}`

**Working example:**

Request:

` $ curl -X POST -H "Content-Type: application/json" -d '{"account": "horns&hoofs", "login": "h&f", "method": "online_score", "token": "55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af34e14e1d5bcd5a08f21fc95", "arguments": {"phone": "79175002040", "email": "stupnikov@otus.ru", "first_name": "Стансилав, "last_name": "Ступников", "birthday": "01.01.1990", "gender": 1}}' http://127.0.0.1:8080/method/ `

Answer:

`{"response": {"score": 5}, "code": 200}`

#### clients_interests

Get client interests.

**Arguments:**

* *client_ids* - list of integers, mandatory, non-nullable
* *date* - date in DD.MM.YYYY format, optional, nullable

**Answer**

`{"client_id1": ["interest1", "interest2" ...], "client2": [...] ...}`

**Working example:**

Request:

`$ curl -X POST -H "Content-Type: application/json" -d '{"account": "horns&hoofs", "login": "admin", "method": "clients_interests", "token": "bf52645bc366bdc9ebb8c966812faf37035f6ac38792eb03366efb2ddde0b4aed4dccb318ee61393977eed37434a14d4ce5cb32c22b5535ae82300e3de5f7e79", "arguments": {"client_ids": [1,2,3,4], "date": "20.07.2017"}}' http://127.0.0.1:8080/method/`

Answer:

`{"response": {"1": ["pets", "hi-tech"], "2": ["hi-tech", "books"], "3": ["music", "otus"], "4": ["hi-tech", "sport"]}, "code": 200}`


## Testing

To run unit tests, run:

`$ python3 tests.py [testfile, optional (default: all tests)] [-v, --verbose]`

Currently 2 test files provided:

* *basic* - comes with homework assignment
* *fields* - test for fields classes

Optional arg -v (--verbose) can be used to get a more verbose answer.

` Ran 26 tests in 0.011s OK `