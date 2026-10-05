from tenacity import retry, stop_after_attempt, wait_fixed


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1), reraise=True)
def get_user_with_retry(user_service, token):
    get_resp = user_service.get_me(token=token)
    assert get_resp.status_code == 200
    return get_resp

