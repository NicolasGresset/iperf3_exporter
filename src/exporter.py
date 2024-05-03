#!/usr/bin/python
import iperf3
import os
from prometheus_client import make_wsgi_app, Gauge, REGISTRY, PROCESS_COLLECTOR, PLATFORM_COLLECTOR
from flask import Flask, request, jsonify


'''
This exporter performs 2 successives tests (uplink and downlink)
'''


# Unregister irrelevant metrics
REGISTRY.unregister(PROCESS_COLLECTOR)
REGISTRY.unregister(PLATFORM_COLLECTOR)
REGISTRY.unregister(REGISTRY._names_to_collectors['python_gc_objects_collected_total'])

app = Flask("Iperf3 exporter")  # Create flask app


# Create metrics    
down_sent_bytes = Gauge(
    "iperf3_sent_bytes_down", "Number of bytes sent during the downlink test"
)
down_received_bytes = Gauge("iperf3_received_bytes_down", "Number of bytes received durng the downlink test")
down_duration = Gauge("iperf3_duration_down", "Duration in seconds of the downlink test")

up_sent_bytes = Gauge(
    "iperf3_sent_bytes_up", "Number of bytes sent during the uplink test"
)
up_received_bytes = Gauge("iperf3_received_bytes_up", "Number of bytes received durng the uplink test")
up_duration = Gauge("iperf3_duration_up", "Duration in seconds of the uplink test")

status = Gauge("iperf3_status", "Did the last scraped worked")


def run_test(reverse : bool, address : str, port : int, duration :  int, protocol : str) -> tuple:
    client = iperf3.Client()
    client.reverse = bool(reverse)
    client.duration = int(duration)
    client.server_hostname = address
    client.port = int(port)
    client.protocol = protocol

    result = client.run()
    
    if "error" in result.json:
        return 0, 0, 0, 0
    else:
        # should we use sum_sent_seconds instead ?
        return result.json["end"]["sum_received"]["bytes"], result.json["end"]["sum_sent"]["bytes"], result.json["end"]["sum_received"]["seconds"], 1
        


@app.route("/probe", methods=['GET'])
def run_tests():
    # parse request arguments
    target_ip = request.args.get('target')
    target_port = request.args.get('port', default=5201)
    test_duration = request.args.get('duration', default=1)
    test_protocol = request.args.get('protocol', default='tcp')

    if not target_ip:
        return jsonify({'error': 'You should provide target address and optionnaly a port.'}), 400

    
    r_down_received_bytes, r_down_sent_bytes, r_down_duration, r_up_status = run_test(False, target_ip, target_port, test_duration, test_protocol)
    r_up_received_bytes, r_up_sent_bytes, r_up_duration, r_down_status = run_test(True, target_ip, target_port, test_duration, test_protocol)
    
    # set metrics
    if r_up_status == 0 or r_down_status == 0:
        status.set(0)
    else:
        status.set(1)
        
    down_sent_bytes.set(r_down_sent_bytes)
    down_received_bytes.set(r_down_received_bytes)
    down_duration.set(r_down_duration)

    up_sent_bytes.set(r_up_sent_bytes)
    up_received_bytes.set(r_up_received_bytes)
    up_duration.set(r_up_duration)
    return make_wsgi_app()


@app.route("/")
def mainPage():
    return (
        "<h1>Welcome to Iperf3 Exporter.</h1>"
        + "Scrape <a href='/probe'>here</a> to start a test."
    )


if __name__ == "__main__":
    exporter_address = os.getenv("IPERF3_ADDRESS", "0.0.0.0")
    exporter_port = os.getenv("IPERF3_PORT", 9798)

    app.run(host=exporter_address, port=exporter_port)