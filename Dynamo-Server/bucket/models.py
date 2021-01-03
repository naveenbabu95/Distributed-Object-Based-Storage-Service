from django.db import models
from django.utils import timezone

def data_directory_path(instance, filename):
	return '{}/{}/{}'.format(instance.bucket_id.node_id, instance.bucket_id.name, filename)

# Create your models here.
class Bucket(models.Model):
	name = models.CharField(max_length=50)
	node_id = models.CharField(max_length=50)

class File(models.Model):
	bucket_id = models.ForeignKey(Bucket, on_delete=models.CASCADE)
	file_name = models.CharField(max_length=50)
	file = models.FileField(upload_to=data_directory_path, null=True)
	vector_1 = models.IntegerField(default=0)
	vector_2 = models.IntegerField(default=0)
	vector_3 = models.IntegerField(default=0)

