from django.http import HttpResponse
from datetime import datetime
from zoneinfo import ZoneInfo

def dummypage(request):
     if request.method == "GET": 
         return HttpResponse("No content here, sorry!")

def time_now(request):
    # CDT/CST per America/Chicago regardless of server UTC
    now = datetime.now(ZoneInfo("America/Chicago"))
    return HttpResponse(now.strftime("%H:%M"))

def sum_view(request):
    n1 = request.GET.get("n1")
    n2 = request.GET.get("n2")
    if n1 is None or n2 is None:
        return HttpResponse("Missing n1 or n2", status=400)
    try:
        total = float(n1) + float(n2)
    except ValueError:
        return HttpResponse("n1 and n2 must be numbers", status=400)
    
    result = str(int(total)) if total.is_integer() else str(total)
    return HttpResponse(result)