import pytest

from utils.cleanup import cleanup_each


class FakeResponse:
    def __init__(self, status_code, text=""):
        self.status_code = status_code
        self.text = text


def test_cleanup_keeps_going_after_http_error():
    calls = []

    def delete(resource_id):
        calls.append(resource_id)
        if len(calls) == 1:
            return FakeResponse(500, "boom")
        return FakeResponse(200, "ok")

    with pytest.raises(AssertionError, match="Провальный teardown"):
        cleanup_each(["user-a", "user-b"], delete, lambda resource_id: resource_id)

    assert calls == ["user-b", "user-a"]


@pytest.mark.parametrize("status_code", [500, 403])
def test_cleanup_reports_each_failed_status(status_code):
    calls = []

    def delete(resource_id):
        calls.append(resource_id)
        return FakeResponse(status_code, "denied")

    with pytest.raises(AssertionError, match="Провальный teardown") as error:
        cleanup_each(["first", "second"], delete, lambda resource_id: f"id={resource_id}")

    assert calls == ["second", "first"]
    message = str(error.value)
    assert f"id=second: HTTP {status_code}" in message
    assert f"id=first: HTTP {status_code}" in message
    assert "2 из 2" in message


def test_cleanup_continues_after_exception():
    calls = []

    def delete(resource_id):
        calls.append(resource_id)
        if resource_id == "second":
            raise RuntimeError("connection reset")
        return FakeResponse(403, "nope")

    with pytest.raises(AssertionError, match="Провальный teardown") as error:
        cleanup_each(["first", "second"], delete, lambda resource_id: resource_id)

    assert calls == ["second", "first"]
    message = str(error.value)
    assert "second: RuntimeError: connection reset" in message
    assert "first: HTTP 403" in message


def test_cleanup_accepts_200_and_404():
    calls = []

    def delete(resource_id):
        calls.append(resource_id)
        return FakeResponse(404 if resource_id == "gone" else 200)

    cleanup_each(["gone", "live"], delete, lambda resource_id: resource_id)

    assert calls == ["live", "gone"]
