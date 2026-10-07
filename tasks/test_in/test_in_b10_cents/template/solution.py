def transform(request):
    return int(float(request["text"]) * 100)
