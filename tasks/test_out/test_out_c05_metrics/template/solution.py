def transform(request):
    return {"count": len(request["values"])}
