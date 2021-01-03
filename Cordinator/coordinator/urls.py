from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from .read_views import read_file, get_file
from .views import *
from .handoff import *
from django.views.generic.base import TemplateView


urlpatterns = [
    path(
    	'create_bucket/',
    	create_bucket,
    	name='create_bucket'
    	),
    
    path(
        'create_file/',
        create_file,
        name='create_file'
        ),
    path(
        'delete_bucket/',
        delete_bucket,
        name='delete_bucket'
        ),
    
    path(
        'delete_file/',
        delete_file,
        name='delete_file'
        ),
    path(
        'update_file/',
        update_file,
        name='update_file'
        ),
    path(
        'handoff_node/',
        handoff_node,
        name='handoff_node'
        ),
    path(
        'failback/',
        failback,
        name='failback'
        ),

    path(
    	'gossip/',
    	gossip,
    	name='gossip'
    	),
    path(
        'read_file/',
        read_file,
        name='read_file'),
    path(
        'get_file/',
        get_file,
        name='get_file')
    ]
