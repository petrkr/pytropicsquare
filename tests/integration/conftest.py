"""Pytest configuration for integration tests.

Integration test fixtures that require ts-tvl model server.
These fixtures handle:
- Model server lifecycle (start/stop)
- TCP transport connection
- TropicSquare instance creation
"""

import pytest
import subprocess
import time
import socket
import sys
from pathlib import Path


def is_port_in_use(port, host="127.0.0.1"):
    """Check if TCP port is in use.

    :param port: Port number
    :param host: Hostname
    :returns: True if port is in use
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            return True
        except (ConnectionRefusedError, OSError):
            return False


@pytest.fixture(scope="session")
def model_yaml():
    """Path to static model configuration YAML.

    :returns: Path to model.yaml
    """
    model_path = Path(__file__).parent.parent / "fixtures" / "model" / "model.yaml"

    if not model_path.exists():
        pytest.skip(f"Model config not found: {model_path}")

    return model_path


@pytest.fixture(scope="session")
def tvl_installed():
    """Ensure ts-tvl package is installed.

    :returns: True if installation successful
    """
    try:
        import tvl
        return True
    except ImportError:
        pytest.skip("ts-tvl not installed - run: pip install -r requirements-dev.txt")


@pytest.fixture(scope="session")
def model_server(tvl_installed, model_yaml):
    """Start model server for integration tests.

    Automatically starts the model_server TCP process before tests
    and stops it after all tests complete.

    If server is already running on port 28992, uses existing server
    and skips cleanup (assumes externally managed).

    :param tvl_installed: Ensures tvl is installed
    :param model_yaml: Path to model configuration

    :yields: Model server process or None (if using existing server)
    """
    # Check if server already running
    server_already_running = is_port_in_use(28992)

    if server_already_running:
        print("\nUsing existing model_server on port 28992")
        yield None  # No process to manage
        return  # Skip cleanup

    # Find model_server command in same venv as Python
    # This works both locally (./venv/bin/pytest) and in CI
    python_path = Path(sys.executable)
    model_server_path = python_path.parent / "model_server"

    if not model_server_path.exists():
        pytest.fail(f"model_server not found at {model_server_path}")

    # Start model server
    print("\nStarting model_server...")
    try:
        # Don't capture stdout/stderr to avoid buffer deadlock
        # Model server output goes to pytest's output
        process = subprocess.Popen(
            [str(model_server_path), "tcp", "--configuration", str(model_yaml)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        pytest.fail(f"Failed to start model_server: {e}")

    # Wait for server to be ready (max 5 seconds)
    max_wait = 5
    start_time = time.time()
    while time.time() - start_time < max_wait:
        if is_port_in_use(28992):
            print("Model server ready!")
            break
        time.sleep(0.1)
    else:
        process.kill()
        pytest.fail("Model server failed to start within 5 seconds")

    # Yield to tests
    yield process

    # Cleanup: stop server
    print("\nStopping model_server...")
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()

    print("Model server stopped")


@pytest.fixture(scope="session")
def tcp_transport(model_server):
    """Provide TcpTransport connected to local model server.

    Session-scoped to share single TCP connection across all tests.
    Model server works better with single connection + multiple sessions
    than multiple connections.

    :param model_server: Model server fixture

    :returns: TcpTransport instance

    Example::

        @pytest.mark.integration
        def test_basic_communication(tcp_transport):
            from tropicsquare.ports.cpython import TropicSquareCPython
            ts = TropicSquareCPython(tcp_transport)
            print(ts.chipid)
    """
    from tropicsquare.transports.tcp import TcpTransport

    transport = TcpTransport("127.0.0.1", port=28992, timeout=5.0)
    yield transport

    # Close TCP connection after all tests
    try:
        transport._sock.close()
    except Exception:
        pass  # Ignore cleanup errors


@pytest.fixture(scope="session")
def tropic_square(tcp_transport):
    """Provide TropicSquare instance connected to model server.

    Session-scoped to share single instance across all tests.
    Mirrors tcp_model_quickstart.py behavior where single instance
    handles multiple session starts.

    :param tcp_transport: TCP transport fixture

    :returns: TropicSquareCPython instance

    Example::

        @pytest.mark.integration
        def test_get_chipid(tropic_square):
            chipid = tropic_square.chipid
            assert chipid is not None
    """
    from tropicsquare.ports.cpython import TropicSquareCPython

    ts = TropicSquareCPython(tcp_transport)
    yield ts

    # No cleanup needed - session ends when tests finish
