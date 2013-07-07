from fabric.api import local, lcd


def test():
    with lcd('test_project'):
        local('python manage.py test')
