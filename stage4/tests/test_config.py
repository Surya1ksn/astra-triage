"""
STAGE 4 TODO: these tests currently fail against the broken Stage-2
config.py on purpose. Once you've fixed config.py in Stage 2, they should
pass unmodified. Add more cases if you want extra coverage (e.g. env var
override behavior) but don't weaken the existing assertions.
"""

import importlib

import astra.config as config_module


def test_thresholds_are_floats():
    importlib.reload(config_module)
    assert isinstance(config_module.CLASSIFICATION_THRESHOLD, float)
    assert isinstance(config_module.RETRIEVAL_THRESHOLD, float)


def test_thresholds_in_valid_range():
    importlib.reload(config_module)
    assert 0.0 <= config_module.CLASSIFICATION_THRESHOLD <= 1.0
    assert 0.0 <= config_module.RETRIEVAL_THRESHOLD <= 1.0


def test_no_hardcoded_key_in_source():
    import pathlib

    source = pathlib.Path(config_module.__file__).read_text()
    assert "sk-astra" not in source, "Hardcoded API key must be removed from config.py"


def test_missing_api_key_does_not_raise():
    # Loading the config module with no env vars set must not crash —
    # offline mode is a supported, first-class mode.
    importlib.reload(config_module)
    assert config_module.LLM_API_KEY is None or isinstance(config_module.LLM_API_KEY, str)
