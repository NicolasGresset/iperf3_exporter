# Iperf3 exporter

This simple Python-written iperf3 exporter allows to scrape metrics on the /probe path.
It performs two consecutives tests to measure respectively down and uplink capacity. 

# Usage

## From Git repository

Clone the repository
```bash
git clone https://github.com/NicolasGresset/iperf3_exporter.git
cd iperf3_exporter
```

Install dependencies
```bash
pip install -r src/requirements.txt
```

Run the exporter
```bash
python3 src/exporter.py
```

## Using Docker image

```bash
docker run --rm -p 9798:9798 --name iperf3_exporter nicolasgresset/iperf3_exporter:1.0
```

should do the job

# Prometheus configuration
```yaml
global:
  scrape_interval: 1m
  scrape_timeout: 30s

scrape_configs:
  - job_name: "iperf3"
    metrics_path: /probe
    static_configs:
      - targets:
          - 192.168.15.185 # Static IP address of the host running iperf3 server
    params:
      port: ["5201"] # Port used by the iperf3 server (default to 5201)
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: 192.168.15.185:9798 # Static IP address of the host running iperf3 exporter
```

# Metrics exposed
```plain
# HELP iperf3_sent_bytes_down Number of bytes sent during the downlink test
# TYPE iperf3_sent_bytes_down gauge
iperf3_sent_bytes_down 2.74555576e+09
# HELP iperf3_received_bytes_down Number of bytes received durng the downlink test
# TYPE iperf3_received_bytes_down gauge
iperf3_received_bytes_down 2.745434112e+09
# HELP iperf3_duration_down Duration in seconds of the downlink test
# TYPE iperf3_duration_down gauge
iperf3_duration_down 1.001003
# HELP iperf3_sent_bytes_up Number of bytes sent during the uplink test
# TYPE iperf3_sent_bytes_up gauge
iperf3_sent_bytes_up 2.88489472e+09
# HELP iperf3_received_bytes_up Number of bytes received durng the uplink test
# TYPE iperf3_received_bytes_up gauge
iperf3_received_bytes_up 2.884107156e+09
# HELP iperf3_duration_up Duration in seconds of the uplink test
# TYPE iperf3_duration_up gauge
iperf3_duration_up 1.000027
```

You can then use promql syntax to query bandwith e.g
```
(iperf3_received_bytes_down * 8)/(iperf3_duration_down * 1000000)
```
to get the result in Mbps