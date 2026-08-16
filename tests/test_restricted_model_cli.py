"""CLIs hard-wired to one model must honour or reject --model, never silently ignore it.

Regression tests for the bug where mflux-generate-krea2 --model dev still constructed
krea/Krea-2-Turbo without a word of warning (same story on the z-image-turbo and both
ernie CLIs). Each single-model CLI now routes --model through
resolve_restricted_model_config, which accepts only that model's registry aliases.
"""

import argparse

import pytest

from mflux.cli.parser.parsers import resolve_restricted_model_config
from mflux.models.common.config.model_config import AVAILABLE_MODELS
from mflux.utils.exceptions import ModelConfigError

# (registry key, a foreign model that must be rejected) for every single-model CLI.
CLI_MODELS = [
    ("krea-2", "dev"),
    ("z-image-turbo", "dev"),
    ("ernie-image", "ernie-image-turbo"),
    ("ernie-image-turbo", "ernie-image"),
    ("lens-turbo", "dev"),
]


def _args(model=None, model_path=None) -> argparse.Namespace:
    return argparse.Namespace(model=model, model_path=model_path)


@pytest.mark.fast
class TestRestrictedModelConfig:
    @pytest.mark.parametrize("registry_key,foreign", CLI_MODELS)
    def test_omitted_model_returns_registry_entry(self, registry_key, foreign):
        assert resolve_restricted_model_config(_args(), registry_key) is AVAILABLE_MODELS[registry_key]

    @pytest.mark.parametrize("registry_key,foreign", CLI_MODELS)
    def test_all_aliases_accepted(self, registry_key, foreign):
        expected = AVAILABLE_MODELS[registry_key]
        for alias in expected.aliases:
            assert resolve_restricted_model_config(_args(model=alias), registry_key) is expected

    @pytest.mark.parametrize("registry_key,foreign", CLI_MODELS)
    def test_foreign_model_rejected(self, registry_key, foreign):
        with pytest.raises(ModelConfigError, match="only accepts the aliases"):
            resolve_restricted_model_config(_args(model=foreign), registry_key)

    def test_krea2_raw_rejected_by_krea2_cli(self):
        # Same architecture, but the generate CLI runs the Turbo checkpoint only; Raw is
        # the training base and must not be silently swapped for Turbo.
        with pytest.raises(ModelConfigError, match="only accepts the aliases"):
            resolve_restricted_model_config(_args(model="krea-2-raw"), "krea-2")

    def test_z_image_controlnet_alias_rejected_despite_shared_repo_id(self):
        # z-image-turbo and its ControlNet share model_name "Tongyi-MAI/Z-Image-Turbo";
        # identity comparison keeps the ControlNet alias out of the plain turbo CLI.
        assert (
            AVAILABLE_MODELS["z-image-turbo"].model_name
            == AVAILABLE_MODELS["z-image-turbo-controlnet-union-2.1"].model_name
        )
        with pytest.raises(ModelConfigError, match="only accepts the aliases"):
            resolve_restricted_model_config(_args(model="z-image-controlnet"), "z-image-turbo")

    def test_unknown_name_without_model_path_raises(self):
        with pytest.raises(ModelConfigError):
            resolve_restricted_model_config(_args(model="totally-unknown-model"), "krea-2")

    def test_unknown_name_with_model_path_falls_back_to_default(self):
        # A saved checkpoint has no builtin config; with --model-path the CLI keeps its
        # own model config, matching the pre-existing lens behaviour.
        config = resolve_restricted_model_config(
            _args(model="totally-unknown-model", model_path="/tmp/saved"), "krea-2"
        )
        assert config is AVAILABLE_MODELS["krea-2"]


@pytest.mark.fast
class TestCliParsersStillBuild:
    def test_parsers_build(self):
        from mflux.models.ernie_image.cli.ernie_image_generate import build_parser as ernie
        from mflux.models.ernie_image.cli.ernie_image_turbo_generate import build_parser as ernie_turbo
        from mflux.models.krea2.cli.krea2_generate import build_parser as krea2
        from mflux.models.lens.cli.lens_generate import build_parser as lens
        from mflux.models.z_image.cli.z_image_turbo_generate import build_parser as z_turbo

        for build in (krea2, z_turbo, ernie, ernie_turbo, lens):
            assert build() is not None
