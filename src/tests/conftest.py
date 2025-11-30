import os
import sys
import pytest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT = os.path.dirname(SRC_DIR)

sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, SRC_DIR)

from src.tests.fake_llm import FakeLLM, FakeLLMFailOnce, FakeLLMAlwaysFail


@pytest.fixture
def fake_llm():
    return FakeLLM()


@pytest.fixture
def fake_llm_fail_once():
    return FakeLLMFailOnce()


@pytest.fixture
def fake_llm_always_fail():
    return FakeLLMAlwaysFail()
