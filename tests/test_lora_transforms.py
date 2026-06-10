"""Regression tests for LoRA fused-projection split transforms.

See issue #423: the down weight (lora_A) of a fused QKV / QKV+MLP LoRA is the
shared low-rank input projection and must NOT be split along the rank dimension.
Only the up weight (lora_B) is split, along its output dimension.
"""

import mlx.core as mx

from mflux.models.common.lora.mapping.lora_transforms import LoraTransforms

RANK = 16  # divisible by both 3 and 4 only for 4; chosen as a common LoRA rank
IN_FEATURES = 128
OUT_PER_HEAD = 3072


def _fused_qkv_pair(num_splits: int):
    # Diffusers/PEFT convention: lora_A (down) = [rank, in], lora_B (up) = [out, rank]
    down = mx.random.normal((RANK, IN_FEATURES))
    up = mx.random.normal((num_splits * OUT_PER_HEAD, RANK))
    return up, down


def test_qkv_down_is_not_split():
    _, down = _fused_qkv_pair(num_splits=3)
    for fn in (LoraTransforms.split_q_down, LoraTransforms.split_k_down, LoraTransforms.split_v_down):
        out = fn(down)
        assert out.shape == down.shape, "qkv down weight must be returned unchanged"
        assert mx.array_equal(out, down)


def test_qkv_mlp_down_is_not_split():
    _, down = _fused_qkv_pair(num_splits=4)
    for fn in (
        LoraTransforms.split_single_q_down,
        LoraTransforms.split_single_k_down,
        LoraTransforms.split_single_v_down,
        LoraTransforms.split_single_mlp_down,
    ):
        out = fn(down)
        assert out.shape == down.shape, "qkv+mlp down weight must be returned unchanged"
        assert mx.array_equal(out, down)


def test_qkv_up_split_preserves_rank():
    up, _ = _fused_qkv_pair(num_splits=3)
    for fn in (LoraTransforms.split_q_up, LoraTransforms.split_k_up, LoraTransforms.split_v_up):
        out = fn(up)
        assert out.shape == (OUT_PER_HEAD, RANK), "up weight splits the output dim, keeps full rank"


def test_split_keeps_up_and_down_ranks_consistent():
    # The core invariant: after transforms, the up weight's rank dim must equal the
    # down weight's rank dim, otherwise lora_A @ lora_B is a shape mismatch at apply time.
    up, down = _fused_qkv_pair(num_splits=3)
    up_q = LoraTransforms.split_q_up(up)
    down_q = LoraTransforms.split_q_down(down)
    up_rank = up_q.shape[1]  # [out, rank]
    down_rank = down_q.shape[0]  # [rank, in]
    assert up_rank == down_rank == RANK
