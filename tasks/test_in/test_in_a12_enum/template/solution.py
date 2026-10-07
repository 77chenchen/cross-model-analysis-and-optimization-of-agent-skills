def transform(request):
    return request["mapping"].get(request["value"])
