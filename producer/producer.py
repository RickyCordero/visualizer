import json
import time
import platform
import os
import socket
import subprocess
import atexit
import logging
from datetime import datetime
from decimal import Decimal
import zmq
import LinkToPy


# Setup structured logging according to AGENTS.md guidelines
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("producer.log")
    ]
)
logger = logging.getLogger("producer")
# Suppress noisy logs from third-party library edn_format
logging.getLogger("edn_format").setLevel(logging.WARNING)

SYSTEM_OS = platform.system()
CARABINER_PORT = 17000
ZMQ_PORT = 5555


def is_running_in_docker():
    """Checks if running inside a Docker container."""
    return os.path.exists('/.dockerenv')


def get_carabiner_binary():
    """Detects and returns the path to the appropriate Carabiner binary based on the OS."""
    if SYSTEM_OS == "Windows":
        candidates = ["Carabiner.exe", "producer/Carabiner.exe", "../Carabiner.exe"]
        for c in candidates:
            if os.path.exists(c):
                return c
        return "Carabiner.exe"
    else:
        candidates = ["./Carabiner_Linux_x64", "producer/Carabiner_Linux_x64", "../producer/Carabiner_Linux_x64"]
        for c in candidates:
            if os.path.exists(c):
                return c
        return "./Carabiner_Linux_x64"


def is_port_open(host, port):
    """Checks if a TCP port is open on a host."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    try:
        s.connect((host, port))
        s.close()
        return True
    except Exception:
        return False


def setup_carabiner():
    """Determines the Carabiner host, starts it if not running, and returns the host and process handle."""
    carabiner_host = "127.0.0.1"
    
    if is_running_in_docker():
        if is_port_open("host.docker.internal", CARABINER_PORT):
            logger.info("Detected Carabiner running on host machine via host.docker.internal.")
            return "host.docker.internal", None
        else:
            logger.info("Carabiner not running on host machine. Falling back to container-local Carabiner.")
            carabiner_host = "127.0.0.1"
            
    if is_port_open(carabiner_host, CARABINER_PORT):
        logger.info(f"Carabiner is already running on {carabiner_host}:{CARABINER_PORT}.")
        return carabiner_host, None
        
    binary_path = get_carabiner_binary()
    logger.info(f"Carabiner not detected on {carabiner_host}:{CARABINER_PORT}. Starting {binary_path}...")
    
    kwargs = {}
    if SYSTEM_OS == "Windows":
        kwargs["creationflags"] = 0x08000000  # CREATE_NO_WINDOW
        
    try:
        if SYSTEM_OS != "Windows" and os.path.exists(binary_path):
            os.chmod(binary_path, 0o755)
            
        process = subprocess.Popen(
            [binary_path],
            stdout=open("car_logs.log", "w"),
            stderr=subprocess.STDOUT,
            **kwargs
        )
        logger.info("Carabiner started successfully in the background.")
        return carabiner_host, process
    except Exception as e:
        logger.error(f"Error starting Carabiner: {e}")
        return carabiner_host, None


def default(obj):
    if isinstance(obj, datetime):
        return {'_isoformat': obj.isoformat()}
    if isinstance(obj, Decimal):
        return str(obj)
    return obj


def validate_sync_data(bpm, beat):
    """Validates the BPM and Beat readings from Link interface."""
    if not isinstance(bpm, (int, float)) or bpm <= 0:
        logger.warning(f"Invalid BPM reading ignored: {bpm}. Must be positive number.")
        return False
    if not isinstance(beat, (int, float)):
        logger.warning(f"Invalid Beat reading ignored: {beat}. Must be numeric.")
        return False
    return True


def main():
    # Setup OS configurations and start Carabiner if needed
    carabiner_host, carabiner_process = setup_carabiner()

    # Register clean-up handler to terminate the Carabiner process on exit
    if carabiner_process:
        def cleanup_carabiner():
            logger.info("Terminating Carabiner process...")
            carabiner_process.terminate()
            try:
                carabiner_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                carabiner_process.kill()
        atexit.register(cleanup_carabiner)

    # Setup ZeroMQ Context and PUB socket
    zmq_context = zmq.Context()
    zmq_socket = zmq_context.socket(zmq.PUB)
    try:
        zmq_socket.bind(f"tcp://0.0.0.0:{ZMQ_PORT}")
        logger.info(f"ZeroMQ PUB socket bound successfully to tcp://0.0.0.0:{ZMQ_PORT}")
    except Exception as e:
        logger.critical(f"Failed to bind ZeroMQ socket to port {ZMQ_PORT}: {e}")
        raise e

    def cleanup_zmq():
        logger.info("Closing ZeroMQ sockets and context...")
        zmq_socket.close()
        zmq_context.term()
    atexit.register(cleanup_zmq)

    # Initialize Carabiner client LinkInterface
    link = LinkToPy.LinkInterface(
        path_to_carabiner=get_carabiner_binary(),
        tcp_ip=carabiner_host,
        tcp_port=CARABINER_PORT
    )
    logger.info(f"Link interface initialized. Monotonic time: {link.now()}")

    last_bpm = None
    last_sync_time = 0.0

    # Main loop: read status from Ableton Link and publish over ZeroMQ
    while True:
        try:
            link.status()
            time.sleep(0.05)  # 20Hz status checks for ultra-responsive updates
            
            current_time = time.time()
            new_bpm = link.bpm_
            new_beat = link.beat_
            
            if validate_sync_data(new_bpm, new_beat):
                # Send sync message if BPM changes OR if 1 second has passed (heartbeat)
                if last_bpm != new_bpm or (current_time - last_sync_time) >= 1.0:
                    sync_payload = {
                        "bpm": new_bpm,
                        "beat": new_beat,
                        "timestamp": current_time
                    }
                    logger.info(f"Publishing sync payload -> BPM: {new_bpm:.2f}, Beat: {new_beat:.2f}")
                    
                    try:
                        message_str = json.dumps(sync_payload, default=default)
                        zmq_socket.send_string(message_str)
                    except Exception as send_err:
                        logger.error(f"Error publishing message to ZMQ: {send_err}")
                    
                    last_bpm = new_bpm
                    last_sync_time = current_time
                    
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received, exiting loop gracefully...")
            break
        except Exception as loop_err:
            logger.error(f"Unexpected error in main loop: {loop_err}")
            time.sleep(1.0)  # prevent tight failure loops


if __name__ == "__main__":
    main()


