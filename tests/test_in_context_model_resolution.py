"""Tests for in-context dev model resolution (issue #179).

The in-context dev CLI used to hard-code Flux.1-dev, ignoring --model, so asking
for schnell still pulled the full dev weights. resolve_model_config honors the
user's choice and only falls back to dev when no model is given.
"""

from mflux.models.common.config.model_config import ModelConfig
from mflux.models.flux.cli.flux_generate_in_context_dev import resolve_model_config


def test_defaults_to_dev_when_no_model():
    assert resolve_model_config(None, None).model_name == ModelConfig.dev().model_name


def test_honors_schnell():
    config = resolve_model_config("schnell", None)
    assert config.model_name == "black-forest-labs/FLUX.1-schnell"


def test_honors_dev_explicitly():
    assert resolve_model_config("dev", None).model_name == ModelConfig.dev().model_name


def test_third_party_with_base_model():
    config = resolve_model_config("some-lab/some-flux", "schnell")
    assert config.model_name == "some-lab/some-flux"
