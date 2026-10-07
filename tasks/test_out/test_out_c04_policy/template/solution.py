def transform(request):
    return [row["user"] for row in request["rows"]]
