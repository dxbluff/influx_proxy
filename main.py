import requests
from flask import Flask, request

from functions import *
from write_crypter import encrypt_write_query, encrypt_query

app = Flask(__name__)
INFLUX_HOST = "127.0.0.1"
INFLUX_PORT = "8086"


@app.route('/')
def index():
    return 'Flask is running!'


# ==============================================================================================================
# https://docs.influxdata.com/influxdb/v1.8/tools/api/#query-http-endpoint

@app.route('/debug', defaults={'path': ''})
@app.route('/debug/<path:path>', methods=["GET"])
def debug(path):
    print(path)
    params = request.args.to_dict()
    headers = request.headers
    response = requests.get(f'http://{INFLUX_HOST}:{INFLUX_PORT}/debug/{path}', params=params, headers=headers)
    return response.content


@app.route('/query', methods=["POST", "GET"])
def query():
    params = request.args.to_dict()
    headers = request.headers

    query_plain = params.get("q")
    printer(f"Plain query: {query_plain}")
    query_encrypted = encrypt_query(query_plain)
    printer(f"Encrypted query: {query_encrypted}")
    params["q"] = query_encrypted

    if request.method == 'GET':
        # SELECT, SHOW
        response = requests.get(f'http://{INFLUX_HOST}:{INFLUX_PORT}/query', params=params, headers=headers)
        return response.text, response.status_code
    elif request.method == 'POST':
        # ALTER CREATE DELETE DROP GRANT KILL REVOKE
        response = requests.post(f'http://{INFLUX_HOST}:{INFLUX_PORT}/query', params=params)
        # https://docs.influxdata.com/influxdb/v1.7/guides/querying_data/
        printer(response.json())
        if params["q"].split(" ")[0] == "SELECT":
            return decrypt_response(response.json()), response.status_code
        return response.text, response.status_code


@app.route('/write', methods=["POST"])
def write():
    data = request.get_data().decode()  # bytes
    printer(data)

    # data = 'weather5,location=us-midwest temperature=82 1465839830100400200'
    encrypted_data = encrypt_write_query(data).encode()
    printer(encrypted_data)

    params = request.args
    headers = request.headers

    response = requests.post(f'http://{INFLUX_HOST}:{INFLUX_PORT}/write', params=params, data=encrypted_data)
    return response.content, response.status_code, response.headers.items()


@app.route('/ping', methods=['GET'])
def ping():
    response = requests.get(f'http://{INFLUX_HOST}:{INFLUX_PORT}/ping')
    return response.content, response.status_code, response.headers.items()


if __name__ == '__main__':
    app.run(debug=True, port=8087, host="0.0.0.0")
