#!/usr/bin/env python3
"""Interactive configuration generator for DreamBooth training."""

import json
from pathlib import Path
from typing import Any, Dict


class ConfigGenerator:
    """Interactive configuration generator for first-time users."""

    TEMPLATES = {
        "pet": {
            "name": "Pet/Animal Training",
            "description": "Optimized for training on photos of pets or animals",
            "num_epochs": 100,
            "learning_rate": 1e-4,
            "lora_rank": 4,
            "quantize": 4,
            "prompt_template": "photo of sks {subject}",
        },
        "person": {
            "name": "Person/Face Training",
            "description": "Optimized for training on photos of people",
            "num_epochs": 150,
            "learning_rate": 5e-5,
            "lora_rank": 8,
            "quantize": 4,
            "prompt_template": "portrait of sks {subject}",
        },
        "style": {
            "name": "Art Style Training",
            "description": "Optimized for learning artistic styles",
            "num_epochs": 80,
            "learning_rate": 2e-4,
            "lora_rank": 16,
            "quantize": 8,
            "prompt_template": "artwork in sks style",
        },
        "object": {
            "name": "Object Training",
            "description": "Optimized for specific objects or products",
            "num_epochs": 100,
            "learning_rate": 1e-4,
            "lora_rank": 8,
            "quantize": 4,
            "prompt_template": "photo of sks {subject}",
        },
    }

    def __init__(self):
        pass

    def run(self) -> Dict[str, Any]:
        """Run the interactive configuration generator."""
        print("\n🎨 DreamBooth Configuration Generator\n")
        print("This tool will help you create a training configuration file.")
        print("Let's start with a few questions...\n")

        # 1. Choose template
        template = self._choose_template()

        # 2. Get subject details
        default_subject = "dog" if template == "pet" else "person"
        subject_type = input(f"What are you training on? [{default_subject}]: ") or default_subject

        # 3. Model selection
        model = self._choose_model()

        # 4. Image setup
        image_dir, images = self._setup_images(template, subject_type)

        # 5. Output configuration
        output_path = self._get_output_path(subject_type)

        # 6. Advanced options
        config = self._build_config(template, model, subject_type, image_dir, images, output_path)

        response = input("\nWould you like to customize advanced settings? [y/N]: ").lower()
        if response == "y":
            config = self._customize_advanced(config)

        # 7. Save configuration
        config_path = self._save_config(config)

        # 8. Show next steps
        self._show_next_steps(config_path, image_dir)

        return config

    def _choose_template(self) -> str:
        """Let user choose a training template."""
        print("\nTraining Templates:")
        print("-" * 60)
        for i, (key, template) in enumerate(self.TEMPLATES.items(), 1):
            print(f"{i}. {template['name']:25} - {template['description']}")
        print("-" * 60)

        while True:
            choice_str = input("\nSelect a template (1-4) [1]: ") or "1"
            try:
                choice = int(choice_str)
                if 1 <= choice <= len(self.TEMPLATES):
                    return list(self.TEMPLATES.keys())[choice - 1]
            except:
                pass
            print("Invalid choice. Please select 1-4.")

    def _choose_model(self) -> str:
        """Let user choose between dev and schnell models."""
        print("\nModel Selection:")
        print("1. dev - Higher quality, slower (recommended)")
        print("2. schnell - Faster, lower quality")

        choice_str = input("\nSelect model [1]: ") or "1"
        return "dev" if choice_str == "1" else "schnell"

    def _setup_images(self, template: str, subject_type: str) -> tuple[str, list[dict]]:
        """Setup training images."""
        print("\nImage Setup:")

        # Get image directory
        image_dir = input("Where are your training images located? [./images]: ") or "./images"

        # Check if directory exists
        image_path = Path(image_dir)
        if not image_path.exists():
            response = input(f"\nDirectory '{image_dir}' doesn't exist. Create it? [Y/n]: ").lower()
            if response != "n":
                image_path.mkdir(parents=True, exist_ok=True)
                print(f"Created directory: {image_dir}")
                print("\nPlease add your training images to this directory and run again.")
                raise SystemExit(0)

        # Find images
        image_files = list(image_path.glob("*.jpg")) + list(image_path.glob("*.jpeg")) + list(image_path.glob("*.png"))

        if not image_files:
            print(f"\nNo images found in {image_dir}")
            print("Please add .jpg, .jpeg, or .png files and run again.")
            raise SystemExit(1)

        print(f"\nFound {len(image_files)} images")

        # Generate prompt template
        template_data = self.TEMPLATES[template]
        prompt = template_data["prompt_template"].replace("{subject}", subject_type)

        response = input(f"\nUse prompt '{prompt}' for all images? [Y/n]: ").lower()
        if response != "n":
            images = [{"image": f.name, "prompt": prompt} for f in sorted(image_files)]
        else:
            # Custom prompts for each image
            images = []
            for f in sorted(image_files):
                custom_prompt = input(f"Prompt for {f.name} [{prompt}]: ") or prompt
                images.append({"image": f.name, "prompt": custom_prompt})

        return image_dir, images

    def _get_output_path(self, subject_type: str) -> str:
        """Get output path for training artifacts."""
        default_path = f"~/Desktop/dreambooth_{subject_type}"
        return input(f"\nWhere should training outputs be saved? [{default_path}]: ") or default_path

    def _build_config(
        self, template: str, model: str, subject_type: str, image_dir: str, images: list[dict], output_path: str
    ) -> Dict[str, Any]:
        """Build the configuration dictionary."""
        template_data = self.TEMPLATES[template]

        config = {
            "model": model,
            "seed": 42,
            "steps": 20,
            "guidance": 3.5 if template == "style" else 3.0,
            "quantize": template_data["quantize"],
            "width": 512,
            "height": 512,
            "training_loop": {"num_epochs": template_data["num_epochs"], "batch_size": 1},
            "optimizer": {"name": "AdamW", "learning_rate": template_data["learning_rate"]},
            "save": {"output_path": output_path, "checkpoint_frequency": 20 if len(images) < 10 else 50},
            "instrumentation": {
                "plot_frequency": 5,
                "generate_image_frequency": 20 if len(images) < 10 else 50,
                "validation_prompt": template_data["prompt_template"].replace("{subject}", subject_type),
            },
            "lora_layers": self._get_lora_config(template, template_data["lora_rank"]),
            "examples": {"path": image_dir, "images": images},
        }

        return config

    def _get_lora_config(self, template: str, rank: int) -> Dict[str, Any]:
        """Get LoRA configuration based on template."""
        if template == "style":
            # For styles, train both transformer types
            return {
                "transformer_blocks": {
                    "block_range": {"start": 5, "end": 15},
                    "layer_types": ["attn.to_q", "attn.to_k", "attn.to_v"],
                    "lora_rank": rank,
                },
                "single_transformer_blocks": {
                    "block_range": {"start": 20, "end": 38},
                    "layer_types": ["proj_out", "proj_mlp"],
                    "lora_rank": rank // 2,
                },
            }
        else:
            # For subjects, focus on single transformer blocks
            return {
                "single_transformer_blocks": {
                    "block_range": {"start": 0 if template == "pet" else 10, "end": 38},
                    "layer_types": ["proj_out", "proj_mlp", "attn.to_q", "attn.to_k", "attn.to_v"],
                    "lora_rank": rank,
                }
            }

    def _customize_advanced(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Allow customization of advanced settings."""
        print("\nAdvanced Settings:")

        # Epochs
        default_epochs = config["training_loop"]["num_epochs"]
        epochs_str = input(f"Number of epochs [{default_epochs}]: ") or str(default_epochs)
        config["training_loop"]["num_epochs"] = int(epochs_str)

        # Learning rate
        default_lr = f"{config['optimizer']['learning_rate']:.0e}"
        lr_str = input(f"Learning rate (scientific notation) [{default_lr}]: ") or default_lr
        config["optimizer"]["learning_rate"] = float(lr_str)

        # LoRA rank
        if "single_transformer_blocks" in config["lora_layers"]:
            default_rank = config["lora_layers"]["single_transformer_blocks"]["lora_rank"]
            rank_str = input(f"LoRA rank (higher = better quality, more memory) [{default_rank}]: ") or str(
                default_rank
            )
            config["lora_layers"]["single_transformer_blocks"]["lora_rank"] = int(rank_str)

        # Quantization
        default_quant = config["quantize"]
        quant_str = input(f"Quantization (4 or 8, higher = less memory) [{default_quant}]: ") or str(default_quant)
        config["quantize"] = int(quant_str)

        return config

    def _save_config(self, config: Dict[str, Any]) -> Path:
        """Save the configuration file."""
        config_path = Path("dreambooth_config.json")

        # Check if file exists
        if config_path.exists():
            response = input(f"\n{config_path} already exists. Overwrite? [y/N]: ").lower()
            if response != "y":
                custom_name = input("Enter new filename [dreambooth_config_new.json]: ") or "dreambooth_config_new.json"
                config_path = Path(custom_name)

        # Save configuration
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

        print(f"\n✅ Configuration saved to: {config_path}")
        return config_path

    def _show_next_steps(self, config_path: Path, image_dir: str):
        """Show next steps to the user."""
        print("\n🎉 Configuration complete!\n")
        print("Next steps:")
        print(f"1. Make sure your images are in: {image_dir}")
        print(f"2. Run training with: mflux-train --train-config {config_path}")
        print("3. Monitor the generated images during training to check progress")
        print("4. After training, find your LoRA adapter in the output directory")
        print("\nTip: Training can be interrupted and resumed using the checkpoint files")


def main():
    """Main entry point for the config generator."""
    generator = ConfigGenerator()
    try:
        generator.run()
    except KeyboardInterrupt:
        print("\nConfiguration cancelled.")
    except Exception as e:
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    main()
