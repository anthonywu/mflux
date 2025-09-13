import json
from pathlib import Path
from typing import Any, List, Tuple

from mflux.error.exceptions import MFluxUserException


class ConfigValidationError(MFluxUserException):
    """Raised when training configuration validation fails."""

    def __init__(self, errors: List[str]):
        self.errors = errors
        message = "Configuration validation failed:\n" + "\n".join(f"  • {error}" for error in errors)
        super().__init__(message)


class DreamBoothConfigValidator:
    """Validates DreamBooth training configurations with helpful error messages."""

    # Memory estimates in GB for different configurations
    MEMORY_ESTIMATES = {
        (4, 4): 16,  # quantize=4, rank=4
        (4, 8): 20,  # quantize=4, rank=8
        (4, 16): 28,  # quantize=4, rank=16
        (8, 4): 12,  # quantize=8, rank=4
        (8, 8): 14,  # quantize=8, rank=8
        (8, 16): 18,  # quantize=8, rank=16
    }

    @staticmethod
    def validate(config: dict[str, Any], base_path: Path) -> Tuple[bool, List[str]]:
        """Validate training configuration and return (is_valid, errors)."""
        errors = []

        # Check required fields
        required_fields = ["model", "training_loop", "optimizer", "save", "lora_layers", "examples"]
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: '{field}'")  # noqa: PERF401

        if errors:
            return False, errors

        # Validate model
        if config.get("model") not in ["dev", "schnell"]:
            errors.append(f"Invalid model: '{config.get('model')}'. Must be 'dev' or 'schnell'")

        # Validate dimensions
        width = config.get("width", 512)
        height = config.get("height", 512)
        if width % 64 != 0 or height % 64 != 0:
            errors.append(f"Image dimensions must be multiples of 64. Got {width}x{height}")
        if width < 256 or height < 256:
            errors.append(f"Image dimensions too small. Minimum is 256x256, got {width}x{height}")

        # Validate training parameters
        training_loop = config.get("training_loop", {})
        if training_loop.get("batch_size", 1) > 4:
            errors.append("Batch size > 4 may cause memory issues on most systems")

        num_epochs = training_loop.get("num_epochs", 100)
        if num_epochs < 20:
            errors.append(f"num_epochs={num_epochs} is too low. Recommended minimum is 20")

        # Validate optimizer
        optimizer = config.get("optimizer", {})
        lr = optimizer.get("learning_rate", 1e-4)
        if lr > 1e-3:
            errors.append(f"learning_rate={lr} is too high. Recommended range: 1e-5 to 1e-4")
        elif lr < 1e-6:
            errors.append(f"learning_rate={lr} is too low. Training may not converge")

        # Validate LoRA configuration
        errors.extend(DreamBoothConfigValidator._validate_lora_config(config.get("lora_layers", {})))

        # Validate examples
        errors.extend(DreamBoothConfigValidator._validate_examples(config.get("examples", {}), base_path))

        return len(errors) == 0, errors

    @staticmethod
    def _validate_lora_config(lora_config: dict) -> List[str]:
        """Validate LoRA layer configuration."""
        errors = []

        if not lora_config:
            errors.append("No LoRA layers specified. At least one layer type must be configured")
            return errors

        # Check transformer blocks
        if "transformer_blocks" in lora_config:
            block_config = lora_config["transformer_blocks"]
            errors.extend(
                DreamBoothConfigValidator._validate_block_range(
                    block_config.get("block_range", {}), "transformer_blocks", max_blocks=19
                )
            )

            rank = block_config.get("lora_rank", 4)
            if rank < 1 or rank > 64:
                errors.append(f"transformer_blocks lora_rank={rank} out of range. Must be 1-64")

        # Check single transformer blocks
        if "single_transformer_blocks" in lora_config:
            block_config = lora_config["single_transformer_blocks"]
            errors.extend(
                DreamBoothConfigValidator._validate_block_range(
                    block_config.get("block_range", {}), "single_transformer_blocks", max_blocks=38
                )
            )

            rank = block_config.get("lora_rank", 4)
            if rank < 1 or rank > 64:
                errors.append(f"single_transformer_blocks lora_rank={rank} out of range. Must be 1-64")

        return errors

    @staticmethod
    def _validate_block_range(block_range: dict, layer_name: str, max_blocks: int) -> List[str]:
        """Validate block range configuration."""
        errors = []

        if "indices" in block_range:
            indices = block_range["indices"]
            if not isinstance(indices, list):
                errors.append(f"{layer_name}: 'indices' must be a list")
            else:
                for idx in indices:
                    if idx < 0 or idx >= max_blocks:
                        errors.append(f"{layer_name}: index {idx} out of range (0-{max_blocks - 1})")  # noqa: PERF401

        elif "start" in block_range and "end" in block_range:
            start = block_range["start"]
            end = block_range["end"]
            if start < 0:
                errors.append(f"{layer_name}: start={start} must be >= 0")
            if end > max_blocks:
                errors.append(f"{layer_name}: end={end} exceeds maximum ({max_blocks})")
            if start >= end:
                errors.append(f"{layer_name}: start={start} must be < end={end}")
        else:
            errors.append(f"{layer_name}: must specify either 'indices' or both 'start' and 'end'")

        return errors

    @staticmethod
    def _validate_examples(examples_config: dict, base_path: Path) -> List[str]:
        """Validate training examples."""
        errors = []

        if "images" not in examples_config:
            errors.append("No training images specified in 'examples.images'")
            return errors

        images = examples_config.get("images", [])
        if len(images) < 3:
            errors.append(f"Too few training images ({len(images)}). Minimum recommended is 3-5")

        if len(images) > 100:
            errors.append(f"Too many training images ({len(images)}). This may cause memory issues")

        # Check image paths
        image_dir = examples_config.get("path", "")
        if not image_dir:
            errors.append("Missing 'examples.path' field")
        else:
            full_image_dir = base_path / image_dir
            if not full_image_dir.exists():
                errors.append(f"Image directory not found: {full_image_dir}")
            else:
                # Validate individual images
                for i, img_config in enumerate(images):
                    if "image" not in img_config:
                        errors.append(f"Image {i + 1}: missing 'image' field")
                        continue

                    if "prompt" not in img_config:
                        errors.append(f"Image {i + 1}: missing 'prompt' field")
                        continue

                    # Check if image file exists
                    img_path = full_image_dir / img_config["image"]
                    if not img_path.exists():
                        errors.append(f"Image not found: {img_path}")
                    elif img_path.stat().st_size == 0:
                        errors.append(f"Image file is empty: {img_path}")

                    # Validate prompt
                    prompt = img_config.get("prompt", "")
                    if not prompt:
                        errors.append(f"Image {i + 1}: empty prompt")
                    elif "sks" not in prompt and "xyz" not in prompt and "tkn" not in prompt:
                        errors.append(f"Image {i + 1}: prompt should include trigger word (e.g., 'sks')")

        return errors

    @staticmethod
    def _get_max_lora_rank(lora_config: dict) -> int:
        """Get the maximum LoRA rank from configuration."""
        max_rank = 4
        if "transformer_blocks" in lora_config:
            max_rank = max(max_rank, lora_config["transformer_blocks"].get("lora_rank", 4))
        if "single_transformer_blocks" in lora_config:
            max_rank = max(max_rank, lora_config["single_transformer_blocks"].get("lora_rank", 4))
        return max_rank

    @staticmethod
    def load_and_validate(config_path: str) -> dict[str, Any]:
        """Load and validate a configuration file, raising an exception if invalid."""
        config_path = Path(config_path)

        if not config_path.exists():
            raise ConfigValidationError([f"Configuration file not found: {config_path}"])

        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigValidationError([f"Invalid JSON in configuration file: {e}"])
        except Exception as e:  # noqa: BLE001
            raise ConfigValidationError([f"Error reading configuration file: {e}"])

        # Validate configuration
        is_valid, errors = DreamBoothConfigValidator.validate(config, config_path.parent)

        if not is_valid:
            raise ConfigValidationError(errors)

        return config
