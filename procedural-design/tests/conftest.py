"""Pytest configuration and fixtures."""

import pytest
import numpy as np


@pytest.fixture
def random_seed():
    """Provide consistent random seed for tests."""
    return 42


@pytest.fixture
def rng(random_seed):
    """Provide numpy random generator."""
    return np.random.default_rng(random_seed)


@pytest.fixture
def small_field(rng):
    """Provide small test field."""
    return rng.random((32, 32), dtype=np.float32)


@pytest.fixture
def medium_field(rng):
    """Provide medium test field."""
    return rng.random((128, 128), dtype=np.float32)

