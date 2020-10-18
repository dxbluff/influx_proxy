import json
import pprint


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


def printer(data):
    print("\n\n\n====================================================\n")
    pprint.pprint(data)
    print("\n====================================================\n\n\n")
