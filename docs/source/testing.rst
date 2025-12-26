Testing
=======

PyTropicSquare maintains a comprehensive test suite with automated testing and continuous integration.

Test Reports
------------

The following reports are automatically generated during documentation builds:

* :doc:`test_results` - Detailed test execution report (pass/fail status, duration, assertions, tracebacks)
* :doc:`coverage` - Code coverage analysis (overall percentage, per-module breakdown, line-by-line visualization)

Coverage Target
~~~~~~~~~~~~~~~

We maintain a minimum coverage threshold of **70%** across the codebase. Pull requests that reduce coverage below this threshold will fail CI checks.

Running Tests Locally
----------------------

Prerequisites
^^^^^^^^^^^^^

Install development dependencies::

    pip install -r requirements-dev.txt

Running the Full Test Suite
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run all tests with coverage::

    pytest tests/ -v --cov=tropicsquare --cov-report=html

This will:

* Execute all unit tests
* Generate coverage report in ``htmlcov/``
* Show coverage summary in terminal

Running Specific Tests
^^^^^^^^^^^^^^^^^^^^^^

Run a single test file::

    pytest tests/unit/test_crc.py -v

Run tests matching a pattern::

    pytest tests/ -k "test_crc" -v

Run with HTML report::

    pytest tests/ -v --html=report.html --self-contained-html

Continuous Integration
----------------------

GitHub Actions
^^^^^^^^^^^^^^

Our CI/CD pipeline runs on every push and pull request:

**Test Workflow** (``.github/workflows/tests.yml``)
  * Runs on Python 3.9, 3.10, 3.11, 3.12
  * Generates JUnit XML for GitHub annotations
  * Posts coverage comments on pull requests
  * Fails if coverage drops below 70%

**Documentation Workflow** (``.github/workflows/sphinx-docs.yml``)
  * Runs on master branch only
  * Executes full test suite
  * Generates HTML test reports
  * Builds Sphinx documentation
  * Deploys everything to GitHub Pages

Test Organization
-----------------

Test Structure
^^^^^^^^^^^^^^

Tests are organized by functionality::

    tests/
    ├── conftest.py              # Shared fixtures and mocks
    ├── unit/                    # Unit tests (no hardware)
    │   ├── test_crc.py         # CRC calculation tests
    │   ├── test_exceptions.py  # Exception hierarchy tests
    │   ├── test_chip_id.py     # Chip ID parsing tests
    │   └── config/             # Configuration tests
    └── fixtures/               # Test data from real hardware

Testing Strategy
^^^^^^^^^^^^^^^^

**Unit Tests**
  Tests that run without hardware, using mocked dependencies:

  * CRC calculations
  * Data parsing (ChipId, SerialNumber, Config)
  * Exception handling
  * Protocol logic with mocked transport

**Mock Infrastructure**
  The test suite includes comprehensive mocks:

  * ``MockL1Transport`` - Simulates SPI/UART communication
  * ``MockCrypto`` - Deterministic cryptographic operations
  * ``MockAESGCM`` - AES-GCM encryption/decryption

**Fixtures**
  Real hardware response data captured for realistic testing:

  * Chip ID structures
  * Configuration register values
  * Protocol responses
  * Error conditions

Writing Tests
-------------

Test Naming
^^^^^^^^^^^

Follow pytest conventions:

* Test files: ``test_*.py``
* Test classes: ``Test*``
* Test functions: ``test_*``

Example Test
^^^^^^^^^^^^

.. code-block:: python

    """Tests for CRC16 calculation."""

    import pytest
    from tropicsquare.crc import CRC

    class TestCRC16:
        """Test CRC16 functionality."""

        def test_crc16_empty_data(self):
            """Test CRC16 with empty input."""
            result = CRC.crc16(b'')
            assert isinstance(result, bytes)
            assert len(result) == 2

        def test_crc16_consistency(self):
            """Test that same input produces same output."""
            data = b'\\x12\\x34\\x56\\x78'
            result1 = CRC.crc16(data)
            result2 = CRC.crc16(data)
            assert result1 == result2

Using Fixtures
^^^^^^^^^^^^^^

.. code-block:: python

    @pytest.fixture
    def mock_transport():
        """Provide a mock L1 transport for testing."""
        return MockL1Transport()

    def test_with_mock(mock_transport):
        """Test using the mock transport."""
        ts = TropicSquare(mock_transport)
        # Test implementation here

Coverage Guidelines
-------------------

Target Coverage
^^^^^^^^^^^^^^^

============== ======= ===========
Module         Target  Difficulty
============== ======= ===========
crc.py         100%    Easy
exceptions/    100%    Easy
chip_id/       95%+    Easy
config/        90%+    Medium
l2_protocol    85%+    Medium
transports/    80%+    Medium
**Overall**    **70-80%** **-**
============== ======= ===========

What to Test
^^^^^^^^^^^^

**High Priority**
  * Core functionality (CRC, parsing, protocol)
  * Error handling and exceptions
  * Public API methods
  * Edge cases and boundary conditions

**Medium Priority**
  * Internal helper methods
  * Configuration options
  * Platform-specific code paths

**Low Priority**
  * Debug logging
  * String representations (``__repr__``, ``__str__``)
  * Trivial getters/setters

Troubleshooting
---------------

Common Issues
^^^^^^^^^^^^^

**Import errors**
  Ensure the package is installed in development mode::

      pip install -e .

**Coverage not generated**
  Make sure pytest-cov is installed::

      pip install pytest-cov

**Tests fail in CI but pass locally**
  Check Python version compatibility. CI tests on multiple versions.

**HTML report not found**
  Reports are generated in the working directory. Check::

      ls test-report.html htmlcov/

Contributing
------------

When contributing code:

1. Write tests for new functionality
2. Ensure existing tests pass
3. Maintain or improve coverage
4. Follow existing test patterns
5. Document complex test scenarios

See the `GitHub repository <https://github.com/tropicsquare/pytropicsquare>`_ for contribution guidelines.
