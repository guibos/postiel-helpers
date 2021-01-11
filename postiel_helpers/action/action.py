import pickle

from postiel_helpers.model.data import DataModel


class Action(DataModel):
    def serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def deserialize(data: bytes):
        return pickle.loads(data)
