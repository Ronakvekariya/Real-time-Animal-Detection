# Real-Time Animal Detection

A real-time computer-vision prototype that runs a custom YOLO model on webcam frames, records detected animal classes, and sends detection events to a network receiver over TCP.

## Pipeline

```
Webcam
  ↓
Threaded frame capture
  ↓
YOLO object detection
  ↓
Top predictions
  ↓
Detection event (JSON)
  ├── local records.json
  └── TCP socket → receiver
```

The repository also includes a trained YOLO model (`best.pt`) and a small example event log.

## What the project demonstrates

- Real-time video capture with a dedicated frame-reading thread.
- YOLO-based object detection.
- Confidence-ranked predictions.
- Event serialization with JSON.
- TCP client/server communication.
- Persistent detection records.
- Timestamped annotated image output.

## Files

| File | Purpose |
| --- | --- |
| `best.pt` | Trained YOLO model used for inference. |
| `run_with_yolo.py` | Captures webcam frames, performs detection, records events, and sends them to the receiver. |
| `server_receive.py` | TCP server that receives and prints detection events. |
| `records.json` | Example detection-event history. |

## Setup

```bash
python -m venv .venv
pip install -r requirements.txt
```

Configure local values in a `.env` file based on `.env.example`.

## Run

Start the receiver first:

```bash
python server_receive.py
```

Then start detection:

```bash
python run_with_yolo.py
```

The detection program uses the webcam and the YOLO model in `best.pt`.

Press **s** to trigger a detection and **q** to quit.

## Configuration

The sender supports environment variables for:

- YOLO model path
- receiver host and port
- Raspberry Pi identifier / IP metadata
- test location
- annotated-output directory

Do not commit machine-specific network configuration or local output directories.

## Engineering notes

This is a real-time prototype rather than a production monitoring system.

Useful future improvements include:

- configurable confidence thresholds;
- asynchronous / buffered event transmission;
- reconnect logic and connection health checks;
- structured logging;
- schema validation for detection events;
- unit tests for networking and event serialization;
- running inference directly on the target edge device and benchmarking latency / FPS.

## Author

**Ronak Vekariya**

[GitHub](https://github.com/Ronakvekariya)
