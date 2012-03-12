

def fullname(user):
    if user.last_name:
        fullname = user.last_name
        if user.first_name:
            fullname += " " + user.first_name
    else:
        fullname = user.username
    return fullname