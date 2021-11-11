

def f():
    try:
        print(1)
        return 4
    finally:
        print(2)
        return 10

print(f"value = {f()}")