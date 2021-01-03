import os,json
from django.views.decorators.csrf import csrf_exempt
from dynamo import settings
import subprocess
import delegator
from django.http import JsonResponse, HttpResponse

filepath = settings.BASE_DIR + "/dynamo_env.json"
with open(filepath) as json_file:
	data = json.load(json_file)

@csrf_exempt
def untar_file(request):
	if request.method == 'POST':
		# failback is true when node is going down
		flag = request.POST['failBack']
	print(flag)

	if flag != 'True': # since json response is always string
		chdir = 'cd ' + settings.MEDIA_ROOT
		os.system(chdir)
		arch = subprocess.check_output("pwd")
		print(arch)
		cmd3 = "tar xvzf ../media/"+(data["send_back_name"])+".tar.gz --strip 3 --directory " + settings.MEDIA_ROOT
		print(cmd3)
		database_name = data["send_back_name"]
		delegator.run('PGPASSWORD={} psql -h localhost -U {} {} < ../media/{}.sql'.format(database_name,database_name,database_name, database_name))

		os.system(cmd3)
		print("File untar successfully")
		cmd4 = 'rm ../media/'+(data["send_back_name"])+".tar.gz"
		cmd5 = 'rm ../media/' + (data["send_back_name"]) + '.sql'
		#os.system(cmd4)
		os.system(cmd4)
		os.system(cmd5)
	else:
		chdir = 'cd ' + settings.MEDIA_ROOT
		os.system(chdir)
		arch = subprocess.check_output("pwd")
		print(arch)
		cmd3 = "tar xvzf ../media/"+(data["handoff_name"])+".tar.gz --strip 3 --directory " + settings.MEDIA_ROOT
		print(cmd3)
		database_name = data["handoff_name"]
		delegator.run('PGPASSWORD={} psql -h localhost -U {} {} < ../media/{}.sql'.format(database_name,database_name,database_name, database_name))

		os.system(cmd3)
		print("File untar successfully")
		cmd4 = 'rm ../media/'+(data["handoff_name"])+".tar.gz"
		cmd5 = 'rm ../media/' + (data["handoff_name"]) + '.sql'
		#os.system(cmd4)
		os.system(cmd4)
		os.system(cmd5)

	return HttpResponse("untar successfully")
	# os.chdir(data["node_name"])
	# arch = subprocess.check_output("ls")
	# print(arch)
	# os.system(cmd2)



	