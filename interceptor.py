import grpc
import pytest
from grpc_interceptor.testing import dummy_client, DummyRequest, raises

class MockErrorLogger():
    def __init__(self):
        self.logged_exception = None

    def log_error(self, e: Exception) -> None:
        self.logged_exception = e

def test_log_error():
    mock = MockErrorLogger()
    ex = Exception()
    special_cases = {"error": raises(ex)}

    with dummy_client(special_cases=special_cases, interceptors=[mock]) as client:
        # Test no exception
        assert client.Execute(DummyRequest(input="foo")).output == "foo"
        assert mock.logged_exception is None

        # Test exception
        with pytest.raises(grpc.RpcError) as e:
            client.Execute(DummyRequest(input="error"))
        assert mock.logged_exception is ex