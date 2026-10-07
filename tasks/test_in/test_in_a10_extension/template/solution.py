def transform(request):
    return request["text"].split(".")[-1]
