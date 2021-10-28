"""
Uses serialisation with the dictionary
"""
import pickle
import database_manager


class DatabaseWriter(database_manager.DatabaseManager):

    def __init__(self, file_location: str):
        super().__init__()

        self.file_loc = file_location

        db_file = open(self.file_loc, 'wb')  # Creates the file location if it didn't exist
        db_file.close()

    def set_value(self, key, val):
        super().set_value(key, val)

        db_file = open(self.file_loc, 'wb')  # Changes the file
        pickle.dump(self.data, db_file)
        db_file.close()

    def delete_value(self, key):
        val = super().delete_value(key)

        db_file = open(self.file_loc, 'wb')  # Removes the key from the file
        pickle.dump(self.data, db_file)
        db_file.close()

        return val