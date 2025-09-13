"""Gradio-based GUI for MFLUX DreamBooth training."""

import json
import os
import random
import tempfile
from pathlib import Path
from typing import List, Tuple

from PIL import Image

try:
    import gradio as gr
except ImportError:
    raise ImportError("Gradio is not installed. Please install it with: pip install 'mflux[gui]' or pip install gradio")


class DreamBoothGUI:
    """Gradio interface to support novice users in DreamBooth training."""

    def __init__(self):
        self.temp_dir = None
        self.config_path = None

    def validate_images(self, files: List[str]) -> Tuple[bool, str, List[Image.Image]]:
        """Validate uploaded images."""
        if not files:
            return False, "Please upload at least 3 images", []

        if len(files) < 3:
            return False, f"Too few images ({len(files)}). Please upload at least 3-5 images.", []

        if len(files) > 30:
            return False, f"Too many images ({len(files)}). Maximum recommended is 30.", []

        # Check image validity
        valid_images = []
        try:
            for file_path in files:
                img = Image.open(file_path)
                if img.mode != "RGB":
                    img = img.convert("RGB")
                valid_images.append(img)
        except FileNotFoundError:
            return False, f"Invalid image {Path(file_path).name}", []

        return True, f"✅ {len(valid_images)} valid images loaded", valid_images

    def generate_config(
        self,
        files: List[str],
        subject_type: str,
        trigger_word: str,
        model: str,
        num_epochs: int,
        learning_rate: float,
        lora_rank: int,
        quantize: int,
        batch_size: int,
    ) -> Tuple[str, str]:
        """Generate training configuration from GUI inputs."""
        if not files:
            return "❌ No images uploaded", ""

        # Create temporary directory for images
        self.temp_dir = Path(tempfile.mkdtemp(prefix="dreambooth_"))
        images_dir = self.temp_dir / "images"
        images_dir.mkdir(exist_ok=True)

        # Copy images to temp directory
        image_configs = []
        for i, file_path in enumerate(files):
            src = Path(file_path)
            dst = images_dir / f"{i:03d}{src.suffix}"

            # Copy and possibly resize image
            img = Image.open(src)
            if img.mode != "RGB":
                img = img.convert("RGB")

            if img.width > 1024 or img.height > 1024:
                img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)

            img.save(dst)

            # Create prompt based on subject type
            prompt = f"photo of {trigger_word} {subject_type}"
            image_configs.append({"image": dst.name, "prompt": prompt})

        # Determine template based on subject type
        template_map = {
            "dog": "pet",
            "cat": "pet",
            "pet": "pet",
            "person": "person",
            "face": "person",
            "object": "object",
            "style": "style",
            "art": "style",
        }
        template = template_map.get(subject_type.lower(), "object")

        # Create configuration
        config = {
            "model": model,
            "seed": random.randint(0, int(1e6)),
            "steps": 20,
            "guidance": 3.5 if template == "style" else 3.0,
            "quantize": quantize,
            "width": 512,
            "height": 512,
            "training_loop": {
                "num_epochs": num_epochs,
                "batch_size": batch_size,
            },
            "optimizer": {
                "name": "AdamW",
                "learning_rate": learning_rate,
            },
            "save": {
                "output_path": str(self.temp_dir / "output"),
                "checkpoint_frequency": max(10, num_epochs // 10),
            },
            "instrumentation": {
                "plot_frequency": 5,
                "generate_image_frequency": max(10, num_epochs // 10),
                "validation_prompt": f"photo of {trigger_word} {subject_type}",
            },
            "lora_layers": self._get_lora_config(template, lora_rank),
            "examples": {
                "path": "images/",
                "images": image_configs,
            },
        }

        # Save configuration
        self.config_path = self.temp_dir / "config.json"
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=2)

        # Create summary
        summary = f"""
✅ Configuration created successfully!

📄 Config path: {self.config_path}
🎯 Subject type: {subject_type}
🏷️ Trigger word: {trigger_word}
🤖 Model: {model}
📊 Learning rate: {learning_rate:.1e}
🎚️ LoRA rank: {lora_rank}
💾 Quantization: {quantize}-bit
📦 Batch size: {batch_size}

 Training images: {len(image_configs)}
🔄 Epochs: {num_epochs}
⏳ Total Number of Steps (image count x epochs count): {len(image_configs) * num_epochs}

🤞🏼 Ready to start training!
"""
        return summary, str(self.config_path)

    def _get_lora_config(self, template: str, rank: int) -> dict:
        """Get LoRA configuration based on template."""
        if template == "style":
            return {
                "transformer_blocks": {
                    "block_range": {"start": 5, "end": 15},
                    "layer_types": ["attn.to_q", "attn.to_k", "attn.to_v"],
                    "lora_rank": rank,
                },
                "single_transformer_blocks": {
                    "block_range": {"start": 20, "end": 38},
                    "layer_types": ["proj_out", "proj_mlp"],
                    "lora_rank": max(4, rank // 2),
                },
            }
        else:
            return {
                "single_transformer_blocks": {
                    "block_range": {"start": 0 if template == "pet" else 10, "end": 38},
                    "layer_types": ["proj_out", "proj_mlp", "attn.to_q", "attn.to_k", "attn.to_v"],
                    "lora_rank": rank,
                }
            }

    def start_training(self, config_path: str, progress=gr.Progress()) -> str:
        """Start the training process."""
        if not config_path:
            return "❌ No configuration created. Please upload images first."

        try:
            from mflux.dreambooth.dreambooth import DreamBooth
            from mflux.dreambooth.dreambooth_initializer import DreamBoothInitializer
            from mflux.error.exceptions import StopTrainingException

            progress(0, desc="Initializing DreamBooth training...")

            # this section is the same controller as train.py
            flux, runtime_config, training_spec, training_state = DreamBoothInitializer.initialize(
                config_path=config_path,
                checkpoint_path=None,  # TODO: support checkpoints in UI?
            )

            progress(1, desc="Start the training process..")

            num_batches_for_progress = training_state.iterator.total_number_of_steps()
            try:
                DreamBooth.train(
                    flux=flux,
                    runtime_config=runtime_config,
                    training_spec=training_spec,
                    training_state=training_state,
                    on_batch_update=lambda batch_count: progress(
                        # (steps completed, total steps)
                        (batch_count, num_batches_for_progress),
                        desc=f"Completed Batch {batch_count} / {num_batches_for_progress}",
                    ),
                )
            except StopTrainingException as stop_exc:
                training_state.save(training_spec)
                return str(stop_exc)
        except Exception as e:  # noqa: BLE001
            return f"❌ Training failed: {str(e)}"

    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface."""
        with gr.Blocks(title="MFLUX DreamBooth Training GUI") as interface:
            gr.Markdown("""
            # 🎨 MFLUX DreamBooth Training Interface

            Drag and drop your images below to start training your own LoRA model!
            """)

            with gr.Row():
                with gr.Column(scale=1):
                    # Image upload
                    file_input = gr.File(
                        label="📸 Drop Training Images Here",
                        file_count="multiple",
                        file_types=["image"],
                        interactive=True,
                    )

                    # Image preview
                    image_preview = gr.Gallery(
                        label="Image Preview",
                        show_label=True,
                        elem_id="gallery",
                        columns=3,
                        rows=2,
                        height="auto",
                    )

                    validation_status = gr.Textbox(
                        label="Validation Status",
                        interactive=False,
                    )

                with gr.Column(scale=1):
                    # Training parameters
                    gr.Markdown("### 📝 Training Configuration")

                    subject_type = gr.Textbox(
                        label="Subject Type",
                        placeholder="e.g., dog, person, toy, style",
                        value="dog",
                    )

                    trigger_word = gr.Textbox(
                        label="Trigger Word",
                        value="sks",
                        info="Unique identifier for your subject",
                    )

                    model = gr.Dropdown(
                        label="Model",
                        choices=["dev", "schnell"],
                        value="dev",
                    )

                    with gr.Accordion("Advanced Settings", open=False):
                        num_epochs = gr.Slider(
                            label="Number of Epochs",
                            minimum=int(os.environ.get("MFLUX_EPOCH_MIN_VALUE", 20)),
                            maximum=300,
                            value=int(os.environ.get("MFLUX_EPOCH_DEFAULT_VALUE", 100)),
                            step=10,
                        )

                        learning_rate = gr.Number(
                            label="Learning Rate",
                            value=1e-4,
                            info="Scientific notation: 1e-4 = 0.0001",
                        )

                        lora_rank = gr.Slider(
                            label="LoRA Rank",
                            minimum=4,
                            maximum=32,
                            value=8,
                            step=4,
                            info="Higher = better quality, more memory",
                        )

                        quantize = gr.Radio(
                            label="Quantization",
                            choices=[4, 8],
                            value=4,
                            info="Higher = less memory usage",
                        )

                        batch_size = gr.Slider(
                            label="Batch Size",
                            minimum=1,
                            maximum=4,
                            value=1,
                            step=1,
                            info="Higher = faster but more memory",
                        )

                    # Action buttons
                    config_output = gr.Textbox(
                        label="Configuration Status",
                        interactive=False,
                        lines=15,
                    )

                    config_path_output = gr.Textbox(
                        label="Config Path",
                        visible=False,
                    )

                    create_config_btn = gr.Button(
                        "📝 Create Configuration",
                        variant="secondary",
                    )

                    start_training_btn = gr.Button(
                        "🚀 Start Training",
                        variant="primary",
                    )

                    training_output = gr.Textbox(
                        label="Training Status",
                        interactive=False,
                    )

            # Wire up the interface
            def on_file_upload(files):
                if not files:
                    return None, "No files uploaded"
                valid, status, images = self.validate_images(files)
                if valid:
                    return images, status
                return None, status

            file_input.change(
                on_file_upload,
                inputs=[file_input],
                outputs=[image_preview, validation_status],
            )

            create_config_btn.click(
                self.generate_config,
                inputs=[
                    file_input,
                    subject_type,
                    trigger_word,
                    model,
                    num_epochs,
                    learning_rate,
                    lora_rank,
                    quantize,
                    batch_size,
                ],
                outputs=[config_output, config_path_output],
            )

            start_training_btn.click(
                self.start_training,
                inputs=[config_path_output],
                outputs=[training_output],
            )

            # Add tips
            gr.Markdown("""
            ### 💡 Tips
            - Use 5-20 diverse images of your subject
            - Keep trigger word unique (default "sks" works well)
            - Start with default settings for first attempts
            - Training typically takes 1-3 hours depending on settings
            - Check [Image Preparation Guide](DREAMBOOTH_IMAGE_PREP_GUIDE.md) for best practices
            """)

        return interface


def main():
    """Launch the GUI."""
    gui = DreamBoothGUI()
    interface = gui.create_interface()
    interface.launch(server_name="127.0.0.1", server_port=7860, share=False, inbrowser=True)


if __name__ == "__main__":
    main()
