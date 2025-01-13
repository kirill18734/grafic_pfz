foo = {'c': 2, 5: 4, 'J': 7}
foo = {key if key != 5 else 'B': value for key, value in foo.items()}
print(foo)