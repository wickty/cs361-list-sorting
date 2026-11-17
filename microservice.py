"""List Sorting microservice. ZeroMQ REQ/REP, JSON, TCP port 5551.
no dependency on any main program
"""
import json
import os
import zmq

PORT = 5551


def handle_request(request):
    if not isinstance(request, dict) or request.get("action") != "sort":
        return {"status": "error", "message": "action must be 'sort'"}
    items = request.get("items")
    field = request.get("field")
    order = request.get("order")
    if not isinstance(items, list) or any(not isinstance(x, dict) for x in items):
        return {"status": "error", "message": "items must be an array of objects"}
    if not isinstance(field, str) or not field:
        return {"status": "error", "message": "field must be a nonempty string"}
    if order not in ("asc", "desc"):
        return {"status": "error", "message": "order must be 'asc' or 'desc'"}
    missing = [i for i, item in enumerate(items) if field not in item]
    if missing:
        return {"status": "error", "message": f"missing field '{field}' in item {missing[0]}"}
    values = [item[field] for item in items]
    if any(type(value) not in (str, int, float) or isinstance(value, float) and (value != value or abs(value) == float('inf')) for value in values):
        return {"status": "error", "message": f"field '{field}' must contain strings or finite numbers"}
    if values and not (all(type(v) is str for v in values) or all(type(v) in (int, float) for v in values)):
        return {"status": "error", "message": f"field '{field}' has incompatible types"}
    sorted_items = sorted(items, key=lambda item: item[field], reverse=(order == "desc"))
    return {"status": "ok", "items": sorted_items}


def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.setsockopt(zmq.LINGER, 0)
    socket.bind(f"tcp://127.0.0.1:{PORT}")
    print(f"List Sorting ready on tcp://127.0.0.1:{PORT}", flush=True)
    try:
        while True:
            try:
                request = socket.recv_json()
                print(f"REQUEST: {json.dumps(request, ensure_ascii=False)}", flush=True)
                response = handle_request(request)
            except Exception as exc:
                response = {"status": "error", "message": f"invalid request: {exc}"}
            print(f"RESPONSE: {json.dumps(response, ensure_ascii=False)}", flush=True)
            socket.send_json(response)
    except KeyboardInterrupt:
        print("Service stopped.")
    finally:
        socket.close()
        context.term()


if __name__ == "__main__":
    main()
