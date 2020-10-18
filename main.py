import requests
from flask import Flask, request

from functions import *

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

    # query_plain = params.get("q")
    # printer(f"Plain query: {query_plain}")
    # query_encrypted = encrypt_query(query_plain, b"g" * 32)
    # printer(f"Encrypted query: {query_encrypted}")
    # params["q"] = query_encrypted
    # params["q"] = query_plain

    if request.method == 'GET':
        # SELECT, SHOW
        response = requests.get(f'http://{INFLUX_HOST}:{INFLUX_PORT}/query', params=params, headers=headers)
        response_data = json.loads(response.text)
        printer(response_data)
        return response.text, response.status_code
    elif request.method == 'POST':
        # ALTER CREATE DELETE DROP GRANT KILL REVOKE
        response = requests.post(f'http://{INFLUX_HOST}:{INFLUX_PORT}/query', params=params)
        # https://docs.influxdata.com/influxdb/v1.7/guides/querying_data/
        # if params["q"].split(" ")[0] == "select":
        #     to_client = Aggregation(json.loads(response.text))
        #     printer(json.loads(to_client.get_response_data()))
        #     columns = to_client.get_columns()
        #     name = to_client.get_name()
        #     values = to_client.get_values()
        #     for value in values:
        #         value[1] = f"Changed in proxy. origin: {value[1]}"
        #     response_data = to_client.set_new_data(values=values)
        #     return to_client.get_response_data(), response.status_code
        return response.text, response.status_code


@app.route('/write', methods=["POST"])
def write():
    data = request.get_data().decode()[1:-1]  # bytes
    printer(data)

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
