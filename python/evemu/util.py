import subprocess


def get_test_directory():
    from evemu import tests
    return tests.__path__[0]


def get_test_module():
    return get_test_directory().replace("/", ".")


def lsinput():
    command_parts = ["lsinput"]
    return subprocess.check_output(command_parts)
