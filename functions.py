import json
import pprint

from write_crypter import det_decrypt_string, ope_decrypt_int, base64padder


class Aggregation:
    def __init__(self, response_data):
        self.response_data = response_data
        self.results = response_data["results"][0]
        self.columns = response_data["results"][0]["series"][0]["columns"]
        self.name = response_data["results"][0]["series"][0]["name"]
        self.values = response_data["results"][0]["series"][0]["values"]

    def get_columns(self):
        return self.columns

    def get_name(self):
        return self.name

    def get_values(self):
        return self.values

    def set_new_data(self, columns=None, name=None, values=None):
        if columns:
            self.response_data["results"][0]["series"][0]["columns"] = columns
        if name:
            self.response_data["results"][0]["series"][0]["name"] = name
        if values:
            self.response_data["results"][0]["series"][0]["values"] = values
        return self.response_data

    def get_response_data(self):
        return json.dumps(self.response_data)


def decrypt_response(response: json) -> json:
    series = response["results"][0]["series"][0]
    name = series["name"]  # name of table
    series["name"] = det_decrypt_string(base64padder(name))

    columns = series["columns"]  # array with columns
    values = series["values"]  # array of arrays of values

    for i in range(len(columns)):
        if columns[i] == "time":
            continue
        elif columns[i][:4] == "ope_":
            columns[i] = det_decrypt_string(base64padder(columns[i][4:]))
            for j in range(len(values)):
                values[j][i] = ope_decrypt_int(values[j][i])
            continue
        elif columns[i][:4] == "phe_":
            columns.pop(i)
            # columns[i] = det_decrypt_string(base64padder(columns[i][4:]))
            for j in range(len(values)):
                values[j].pop(i)
                # values[j][i] = he_decrypt(values[j][i].as_integer_ratio()[0])
            continue
        else:
            columns[i] = det_decrypt_string(base64padder(columns[i]))
            for j in range(len(values)):
                values[j][i] = det_decrypt_string(base64padder(values[j][i]))

    return response


def printer(data):
    print("\n\n\n====================================================\n")
    pprint.pprint(data)
    print("\n====================================================\n\n\n")
