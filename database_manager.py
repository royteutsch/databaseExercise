
class DatabaseManager:

    def __init__(self):
        self.data = {}

    def set_value(self, key, val):
        """
        sets the value for the specified key to the specified value
        returns 0 if successful and 1 if unsuccessful
        """
        try:
            self.data[key] = val
            return 0
        except:
            return 1

    def get_value(self, key):
        ret_val = None
        if key in self.data:
            ret_val = self.data[key]
        return ret_val

    def delete_value(self, key):
        if key in self.data:
            val = self.data[key]
            self.data.pop(key)
            return val
        return None
