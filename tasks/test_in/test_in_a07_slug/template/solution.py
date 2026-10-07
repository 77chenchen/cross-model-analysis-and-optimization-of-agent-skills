def transform(request):
    return request.get("text", "").lower()
