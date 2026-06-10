import mlx.core as mx


class LoraTransforms:
    @staticmethod
    def split_q_up(tensor: mx.array) -> mx.array:
        return LoraTransforms._split_qkv_up(tensor, 0)

    @staticmethod
    def split_k_up(tensor: mx.array) -> mx.array:
        return LoraTransforms._split_qkv_up(tensor, 1)

    @staticmethod
    def split_v_up(tensor: mx.array) -> mx.array:
        return LoraTransforms._split_qkv_up(tensor, 2)

    @staticmethod
    def split_q_down(tensor: mx.array) -> mx.array:
        return LoraTransforms._split_qkv_down(tensor, 0)

    @staticmethod
    def split_k_down(tensor: mx.array) -> mx.array:
        return LoraTransforms._split_qkv_down(tensor, 1)

    @staticmethod
    def split_v_down(tensor: mx.array) -> mx.array:
        return LoraTransforms._split_qkv_down(tensor, 2)

    @staticmethod
    def split_single_q_up(tensor: mx.array) -> mx.array:
        return LoraTransforms._split_qkv_mlp_up(tensor, 0)

    @staticmethod
    def split_single_k_up(tensor: mx.array) -> mx.array:
        return LoraTransforms._split_qkv_mlp_up(tensor, 1)

    @staticmethod
    def split_single_v_up(tensor: mx.array) -> mx.array:
        return LoraTransforms._split_qkv_mlp_up(tensor, 2)

    @staticmethod
    def split_single_mlp_up(tensor: mx.array) -> mx.array:
        return LoraTransforms._split_qkv_mlp_up(tensor, 3)

    @staticmethod
    def split_single_q_down(tensor: mx.array) -> mx.array:
        return LoraTransforms._split_qkv_mlp_down(tensor, 0)

    @staticmethod
    def split_single_k_down(tensor: mx.array) -> mx.array:
        return LoraTransforms._split_qkv_mlp_down(tensor, 1)

    @staticmethod
    def split_single_v_down(tensor: mx.array) -> mx.array:
        return LoraTransforms._split_qkv_mlp_down(tensor, 2)

    @staticmethod
    def split_single_mlp_down(tensor: mx.array) -> mx.array:
        return LoraTransforms._split_qkv_mlp_down(tensor, 3)

    @staticmethod
    def _transpose(tensor: mx.array) -> mx.array:
        return tensor.T

    @staticmethod
    def _split_qkv_up(tensor: mx.array, index: int, num_splits: int = 3) -> mx.array:
        split_size = tensor.shape[0] // num_splits
        start = index * split_size
        end = start + split_size
        return tensor[start:end, :]

    @staticmethod
    def _split_qkv_down(tensor: mx.array, index: int, num_splits: int = 3) -> mx.array:
        # The down weight (lora_A) of a fused QKV LoRA is the shared low-rank input
        # projection: shape [rank, in_features]. When splitting a fused qkv linear into
        # separate q/k/v targets, only the up weight (lora_B) is split along its output
        # dimension; q/k/v all share the same full down weight. Slicing the rank dimension
        # here corrupts the decomposition (the resulting lora_A rank no longer matches the
        # un-split lora_B rank). Return the down weight unchanged. See issue #423.
        del index, num_splits  # kept for call-site signature compatibility
        return tensor

    @staticmethod
    def _split_qkv_mlp_up(tensor: mx.array, index: int, dims: list[int] | None = None) -> mx.array:
        if dims is None:
            dims = [3072, 3072, 3072, 12288]

        start = sum(dims[:index])
        end = start + dims[index]
        return tensor[start:end, :]

    @staticmethod
    def _split_qkv_mlp_down(tensor: mx.array, index: int, num_splits: int = 4) -> mx.array:
        # Same reasoning as _split_qkv_down, for fused qkv+mlp single-stream blocks: the
        # down weight (lora_A) is the shared low-rank input projection and must not be
        # split. Only the up weight is split across the fused output dims. See issue #423.
        del index, num_splits  # kept for call-site signature compatibility
        return tensor
