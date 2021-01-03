from dynamo import settings
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def gossip_message(request):
	return JsonResponse({'success': True, 'node': request.POST['node_number']})