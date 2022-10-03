import json


class Program:
    definitions = []

    def __init__(self, definition):
        self.definitions = [definition]

    def __repr__(self) -> str:
        return json.dumps(self.definitions)

    def append(self, definition):
        self.definitions.append(definition)
        return self
