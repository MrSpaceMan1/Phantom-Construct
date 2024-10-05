import json
class ExtJSONEncoder(json.JSONEncoder):
    def default(self, o):
        to_dict = {}
        for field, value in vars(o).items():
           to_dict[field] = value

        return to_dict