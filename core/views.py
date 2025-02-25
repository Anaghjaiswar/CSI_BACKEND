from django.http import JsonResponse


def warm_up(request):
    return JsonResponse({"message": "Server is warm!"})

