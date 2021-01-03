Python3.6
virtualenv
pip
setup virtualenv: virtualenv dynamo-venv
activate venv: dynamo-venv/Scripts/activate (check for ubuntu how to actuvate venv : go to bin the  $. activate) 
pip install django-admin
django-admin createproject dynamo
cd dynamo
python manage.py startapp bucket //to create app
python manage.py runserver 0.0.0.0:<port>

