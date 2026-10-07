def transform(request):
    return int(request["text"][:-1])
