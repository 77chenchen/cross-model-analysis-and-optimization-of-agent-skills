def transform(request):
    return sum(row.get("amount", 0) for row in request["rows"])
