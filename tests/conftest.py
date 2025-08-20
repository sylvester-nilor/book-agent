import os
import sys

import pytest

# Append the 'src' directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# from src.main import app


# @pytest.fixture
# def client():
#     with app.test_client() as client:
#         yield client
