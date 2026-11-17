"""Independent test client for list-sorting. Run microservice.py separately."""
import json
import zmq

ADDRESS = "tcp://127.0.0.1:5551"
TESTS = [('Ascending', {'action': 'sort', 'items': [{'name': 'A', 'score': 9}, {'name': 'B', 'score': 2}, {'name': 'C', 'score': 5}], 'field': 'score', 'order': 'asc'}), ('Descending', {'action': 'sort', 'items': [{'name': 'A', 'score': 9}, {'name': 'B', 'score': 2}, {'name': 'C', 'score': 5}], 'field': 'score', 'order': 'desc'}), ('Missing field', {'action': 'sort', 'items': [{'name': 'A', 'score': 9}], 'field': 'points', 'order': 'asc'})]


def call_service(socket, request):
    socket.send_json(request)
    return socket.recv_json()


def main():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.setsockopt(zmq.RCVTIMEO, 3000)
    socket.setsockopt(zmq.SNDTIMEO, 3000)
    socket.setsockopt(zmq.LINGER, 0)
    socket.connect(ADDRESS)
    try:
        for label, request in TESTS:
            print(f"\n--- {label} ---")
            print("REQUEST:", json.dumps(request))
            reply = call_service(socket, request)
            print("RESPONSE:", json.dumps(reply))
    except zmq.Again:
        print("Timed out. Start the microservice in another terminal first.")
        raise SystemExit(1)
    finally:
        socket.close()
        context.term()


if __name__ == "__main__":
    main()
