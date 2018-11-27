# Check type of property, and check if it is in list of types.
def check_type(value, t, name):
    if type(value) not in t:
        raise TypeError("{} is not type {}.".format(name, str(t)))


# Check bound of numeric values.
def check_bound(value, min_v, max_v, text):
    if min_v is not None:
        if value < min_v:
            raise ValueError(text)
    if max_v is not None:
        if value > max_v:
            raise ValueError(text)
