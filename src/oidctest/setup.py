def test_summation(conv, sid):
    status = 0
    for item in conv.events.get_data('test_output'):
        if item["status"] > status:
            status = item["status"]

    if status == 0:
        status = 1

    info = {
        "id": sid,
        "status": status,
        "tests": conv.test_output
    }

    return info