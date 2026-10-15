from pytest_bdd import scenarios

# every .feature under ../features; the steps come from the plugins listed in conftest.py
scenarios(".")
