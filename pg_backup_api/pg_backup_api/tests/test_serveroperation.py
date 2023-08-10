import pytest
from pg_backup_api.server_operation import ServerOperation


def mocked(arg): return True


def test_instance_with_no_args():
    with pytest.raises(TypeError):
        ServerOperation()


def test_static_method_time_event():
    hasattr(ServerOperation.__dict__['time_event_now'], '__call__')


def test_instance_with_one_arg(monkeypatch):
    monkeypatch.setattr('pg_backup_api.server_operation.get_server_by_name', mocked)
    a = 'one'
    obj = ServerOperation(a)
    assert isinstance(obj, ServerOperation)


def test_instance_variables(monkeypatch):
    monkeypatch.setattr('pg_backup_api.server_operation.get_server_by_name', mocked)
    a = 'server_name'
    obj = ServerOperation(a)
    assert obj.server_name == a


def test_creating_output_file(monkeypatch):
    monkeypatch.setattr('pg_backup_api.server_operation.get_server_by_name', mocked)
    #operation_id argument is optional for most cases but not for this
    a = 'one'
    obj = ServerOperation(a)
    with pytest.raises(Exception):
        obj.create_output_file('fake_content')


def test_instance_with_two_args(monkeypatch):
    monkeypatch.setattr('pg_backup_api.server_operation.get_server_by_name', mocked)
    a = 'one'
    b = 'two'
    obj = ServerOperation(a, b)
    assert isinstance(obj, ServerOperation)


def test_instance_methods(monkeypatch):
    monkeypatch.setattr('pg_backup_api.server_operation.get_server_by_name', mocked)

    obj = ServerOperation('arg')
    public_methods = ('get_operations_list', 'get_status_by_operation_id',
                      'copy_and_validate_options', 'create_job_file',
                      'create_output_file', 'get_job_file_content',
                      'get_output_file', 'get_job_file')
    for check in public_methods:
        getattr(obj, check)
