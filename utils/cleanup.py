def cleanup_each(resources, delete, label):
    """Удаляет ресурсы с конца и не останавливается на первой ошибке.

    delete(resource) возвращает ответ с status_code либо бросает исключение.
    200 и 404 считаются успехом. Остальные коды и исключения копятся,
    цикл идёт дальше. Если список ошибок не пуст, teardown падает один раз
    и перечисляет все неудачные ресурсы.
    """
    errors = []
    for resource in reversed(resources):
        name = label(resource)
        try:
            response = delete(resource)
        except Exception as exc:  # noqa: BLE001 — сбой одного DELETE не должен бросать остальные id
            errors.append(f"{name}: {type(exc).__name__}: {exc}")
            continue
        status = getattr(response, "status_code", None)
        body = getattr(response, "text", "")
        if status not in (200, 404):
            errors.append(f"{name}: HTTP {status} {body}".rstrip())
    if errors:
        details = "\n".join(errors)
        raise AssertionError(
            f"Провальный teardown, не очищено ресурсов: {len(errors)} из {len(resources)}\n{details}"
        )
