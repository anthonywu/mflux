"""Tests for ModelConfig.canonical_alias and its use in image metadata.

See issue #415: FLUX.2-klein-9b-kv (and other built-in models) stored only the
full HF repo path in metadata, making the model hard to recognize. We now also
expose a short, human-readable alias without losing third-party model identity.
"""

from mflux.models.common.config.model_config import ModelConfig
from mflux.utils.info_util import InfoUtil


def test_kv_variant_canonical_alias():
    config = ModelConfig.from_name("flux2-klein-9b-kv")
    assert config.model_name == "black-forest-labs/FLUX.2-klein-9b-kv"
    assert config.canonical_alias == "flux2-klein-9b-kv"


def test_builtin_alias_input_resolves_to_canonical():
    # A non-canonical alias still resolves to the canonical short form.
    config = ModelConfig.from_name("klein-9b-kv")
    assert config.canonical_alias == "flux2-klein-9b-kv"


def test_named_model_canonical_alias():
    config = ModelConfig.from_name("schnell")
    assert config.model_name == "black-forest-labs/FLUX.1-schnell"
    assert config.canonical_alias == "schnell"


def test_third_party_repo_keeps_model_name():
    # Third-party repos inherit the base aliases but must keep their own identity.
    config = ModelConfig.from_name("some-lab/some-flux", base_model="dev")
    assert config.canonical_alias == "some-lab/some-flux"


def test_info_util_shows_alias_and_repo():
    metadata = {
        "exif": {
            "model": "black-forest-labs/FLUX.2-klein-9b-kv",
            "model_alias": "flux2-klein-9b-kv",
        }
    }
    out = InfoUtil.format_metadata(metadata)
    assert "Model: flux2-klein-9b-kv (black-forest-labs/FLUX.2-klein-9b-kv)" in out


def test_info_util_no_alias_falls_back_to_model():
    metadata = {"exif": {"model": "some-lab/some-flux"}}
    out = InfoUtil.format_metadata(metadata)
    assert "Model: some-lab/some-flux" in out
