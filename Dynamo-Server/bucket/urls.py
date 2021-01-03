from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from . import views
from . import backup_views
from django.views.generic.base import TemplateView
from . import handoff_untar


urlpatterns = [
    path(
    	'create_bucket/',
    	views.create_bucket,
    	name='create_bucket'
    	),
    path(
    	'delete_bucket/',
    	views.delete_bucket,
    	name='create_bucket'
    	),
    path(
    	'create_file/',
    	views.create_file,
    	name='create_file'
    	),
    path(
        'read_file/',
        views.read_file,
        name='read_file'
        ),
    path(
        'get_file/',
        views.get_file,
        name='get_file'
        ),
    path(
        'update_file/',
        views.update_file,
        name='update_file'
        ),
    path(
    	'delete_file/',
    	views.delete_file,
    	name='create_file'
    	),
    path(
        'create_db_backup/',
        backup_views.create_db_backup,
        name='create_db_backup'
        ),
    path(
        'restore_db/',
        backup_views.restore_db,
        name='restore_db'
        ),
    path(
        'handoff_node/',
    	backup_views.handoff_node,
    	name='handoff'
    	),
    path(
    	'node_up/',
    	backup_views.node_up,
    	name='handoff'
    	),
    path(
    	'untar_file/',
    	handoff_untar.untar_file,
    	name='handoff'
    	),
    ]
