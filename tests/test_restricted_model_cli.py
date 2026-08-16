# CLIs hard-wired to one model must honour or reject --model, never silently ignore it.
# Regression tests for the bug where mflux-generate-krea2 --model dev still constructed
# krea/Krea-2-Turbo without a word of warning (same story on the z-image-turbo and both
# ernie CLIs). Each single-model CLI now routes --model through
# ConfigResolution.resolve_restricted: the model's registry aliases are accepted, a
# checkpoint name that is unknown or infers to the CLI's own root is accepted alongside
# --model-path, and anything foreign errors.

import pytest

from mflux.models.common.config.model_config import AVAILABLE_MODELS
from mflux.models.common.resolution.config_resolution import ConfigResolution
from mflux.utils.exceptions import ModelConfigError

# (registry key, a foreign model that must be rejected) for every single-model CLI.
CLI_MODELS = [
    ("krea-2", "dev"),
    ("z-image-turbo", "dev"),
    ("ernie-image", "ernie-image-turbo"),
    ("ernie-image-turbo", "ernie-image"),
    ("lens-turbo", "dev"),
]


@pytest.mark.fast
class TestRestrictedModelConfig:
    @pytest.mark.parametrize("registry_key,foreign", CLI_MODELS)
    def test_omitted_model_returns_registry_entry(self, registry_key, foreign):
        assert ConfigResolution.resolve_restricted(None, registry_key) is AVAILABLE_MODELS[registry_key]

    @pytest.mark.parametrize("registry_key,foreign", CLI_MODELS)
    def test_all_aliases_accepted(self, registry_key, foreign):
        expected = AVAILABLE_MODELS[registry_key]
        for alias in expected.aliases:
            assert ConfigResolution.resolve_restricted(alias, registry_key) is expected

    @pytest.mark.parametrize("registry_key,foreign", CLI_MODELS)
    def test_foreign_model_rejected(self, registry_key, foreign):
        with pytest.raises(ModelConfigError, match="only accepts the aliases"):
            ConfigResolution.resolve_restricted(foreign, registry_key)

    @pytest.mark.parametrize("registry_key,foreign", CLI_MODELS)
    def test_foreign_model_rejected_even_with_model_path(self, registry_key, foreign):
        with pytest.raises(ModelConfigError, match="only accepts the aliases"):
            ConfigResolution.resolve_restricted(foreign, registry_key, model_path="/tmp/saved")

    def test_krea2_raw_rejected_by_krea2_cli(self):
        # Same architecture, but the generate CLI runs the Turbo checkpoint only; Raw is
        # the training base and must not be silently swapped for Turbo.
        with pytest.raises(ModelConfigError, match="only accepts the aliases"):
            ConfigResolution.resolve_restricted("krea-2-raw", "krea-2")

    def test_z_image_controlnet_alias_rejected_despite_shared_repo_id(self):
        # z-image-turbo and its ControlNet share model_name "Tongyi-MAI/Z-Image-Turbo";
        # identity comparison keeps the ControlNet alias out of the plain turbo CLI.
        assert (
            AVAILABLE_MODELS["z-image-turbo"].model_name
            == AVAILABLE_MODELS["z-image-turbo-controlnet-union-2.1"].model_name
        )
        with pytest.raises(ModelConfigError, match="only accepts the aliases"):
            ConfigResolution.resolve_restricted("z-image-controlnet", "z-image-turbo")

    def test_unknown_name_without_model_path_raises(self):
        with pytest.raises(ModelConfigError):
            ConfigResolution.resolve_restricted("totally-unknown-model", "krea-2")

    def test_unknown_name_with_model_path_falls_back_to_default(self):
        # A saved checkpoint has no builtin config; with --model-path the CLI keeps its
        # own model config, matching the pre-existing lens behaviour.
        config = ConfigResolution.resolve_restricted("totally-unknown-model", "krea-2", model_path="/tmp/saved")
        assert config is AVAILABLE_MODELS["krea-2"]

    def test_inferred_own_family_name_with_model_path_accepted(self):
        # A custom checkpoint name containing this CLI's own alias substring-infers to
        # its root; alongside --model-path that is this model, not a foreign one.
        config = ConfigResolution.resolve_restricted("my-krea-2-finetune", "krea-2", model_path="/tmp/saved")
        assert config is AVAILABLE_MODELS["krea-2"]

    def test_inferred_own_family_name_without_model_path_rejected(self):
        with pytest.raises(ModelConfigError, match="only accepts the aliases"):
            ConfigResolution.resolve_restricted("my-krea-2-finetune", "krea-2")

    def test_inferred_foreign_family_name_with_model_path_rejected(self):
        # A custom name that infers to a different root stays an error even with a path.
        with pytest.raises(ModelConfigError, match="only accepts the aliases"):
            ConfigResolution.resolve_restricted("my-dev-finetune", "krea-2", model_path="/tmp/saved")


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
