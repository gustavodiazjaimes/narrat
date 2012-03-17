
def fullname(user):
    fullname = user.get_full_name()
    if not fullname:
        fullname = user.username
    return fullname