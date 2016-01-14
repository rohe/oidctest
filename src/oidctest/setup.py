def test_summation(conv, sid):
    status = 0
    for item in conv.events.get_data('condition'):
        if item["status"] > status:
            status = item["status"]

    if status == 0:
        status = 1

    return {"id": sid, "status": status}
