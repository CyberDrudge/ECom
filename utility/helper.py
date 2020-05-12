
def response_format(success, message, data=None):
    obj = {
        'message': message
    }
    if success:
        obj['data'] = data
        obj['type'] = "success"
    else:
        obj['type'] = "failed"
    return obj
    