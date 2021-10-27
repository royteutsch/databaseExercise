import database_manager

d = database_manager.Database()
d.set_value("1st", "First")
d.set_value("2st", "Seirst")
d.set_value("3st", "Thirst")
d.set_value("4st", "Fouirst")

print(d.data)

d.set_value("2st", "Second")

print(d.data)

print("The number after 3 is " + d.get_value("4st"))

print("The number before 2 is " + d.delete_value("1st"))

print(d.data)
