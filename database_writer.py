"""
Uses serialisation with the dictionary
"""
import os
import pickle
import database_manager


class DatabaseWriter(database_manager.DatabaseManager):
    write_num = 0
    def __init__(self, file_location: str):
        super().__init__()

        self.file_loc = file_location

        db_file = open(self.file_loc, 'wb')  # Creates the file location if it didn't exist
        db_file.close()

    def set_value(self, key, val):
        super().set_value(key, val)
        DatabaseWriter.write_num += 1
        print(f"DatabaseWriter.set_value: set count {DatabaseWriter.write_num}")

        print(f"DatabaseWriter.set_value:{os.getpid()} enter")
        # start critical section
        db_file = open(self.file_loc, 'wb')  # Changes the file
        pickle.dump(self.data, db_file)
        db_file.close()
        # end critical section
        print(f"DatabaseWriter.set_value:{os.getpid()} exit")

    def get_value(self, key):
        print(self.file_loc)
        print("DatabaseWriter.get_value: enter")
        # start critical section
        db_file = open(self.file_loc, 'rb')
        print("DatabaseWriter.get_value: Database: " + db_file.read().decode(encoding="latin1"))
        self.data = pickle.load(db_file)
        db_file.close()
        print("DatabaseWriter.get_value: exit")

        return super().get_value(key)
        # end critical section

    def delete_value(self, key):
        val = super().delete_value(key)

        print("DatabaseWriter.delete_value: enter")
        # start critical section
        db_file = open(self.file_loc, 'wb')  # Removes the key from the file
        pickle.dump(self.data, db_file)
        db_file.close()
        # end critical section
        print("DatabaseWriter.delete_value: exit")

        return val
