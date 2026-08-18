# A ControlNet checkpoint written by mflux-save keeps its ControlNet under
# transformer_controlnet/. The initializer used to fetch that component from the remote
# repo unconditionally, so reloading a saved checkpoint silently swapped its ControlNet
# weights (a -q quantization, a fine-tune) for the hub's and broke offline use. These
# tests pin the routing decision: model_path with a saved ControlNet loads locally,
# everything else keeps the hub path.

import pytest

from mflux.models.common.config.model_config import ModelConfig
from mflux.models.common.weights.loading.weight_loader import WeightLoader
from mflux.models.flux.flux_initializer import FluxInitializer


@pytest.fixture
def loader_calls(monkeypatch):
    seen = {}

    def record_local(component, root_path):
        seen["local"] = {"component": component, "root_path": root_path}
        return "local-weights"

    def record_hub(component, repo_id):
        seen["hub"] = {"component": component, "repo_id": repo_id}
        return "hub-weights"

    monkeypatch.setattr(WeightLoader, "load_single_local", record_local)
    monkeypatch.setattr(WeightLoader, "load_single", record_hub)
    return seen


@pytest.mark.fast
def test_a_saved_checkpoint_loads_its_own_controlnet(loader_calls, tmp_path):
    (tmp_path / "transformer_controlnet").mkdir()
    (tmp_path / "transformer_controlnet" / "0.safetensors").touch()

    component, weights = FluxInitializer._load_controlnet_weights(
        model_config=ModelConfig.dev_controlnet_canny(),
        model_path=str(tmp_path),
    )

    assert "hub" not in loader_calls
    assert loader_calls["local"]["root_path"] == tmp_path
    assert component.name == "transformer_controlnet"
    assert component.hf_subdir == "transformer_controlnet"
    assert weights == "local-weights"


@pytest.mark.fast
def test_a_builtin_name_still_downloads_the_controlnet(loader_calls):
    component, weights = FluxInitializer._load_controlnet_weights(
        model_config=ModelConfig.dev_controlnet_canny(),
        model_path=None,
    )

    assert "local" not in loader_calls
    assert loader_calls["hub"]["repo_id"] == ModelConfig.dev_controlnet_canny().controlnet_model
    assert component.name == "transformer_controlnet"
    assert weights == "hub-weights"


@pytest.mark.fast
def test_a_local_path_without_a_saved_controlnet_falls_back_to_the_hub(loader_calls, tmp_path):
    # A diffusers-format or base-only directory has no transformer_controlnet/ shards;
    # the component still has to come from somewhere, so the hub path stays.
    (tmp_path / "transformer").mkdir()

    component, weights = FluxInitializer._load_controlnet_weights(
        model_config=ModelConfig.dev_controlnet_canny(),
        model_path=str(tmp_path),
    )

    assert "local" not in loader_calls
    assert loader_calls["hub"]["repo_id"] == ModelConfig.dev_controlnet_canny().controlnet_model
    assert weights == "hub-weights"
