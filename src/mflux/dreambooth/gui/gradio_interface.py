"""Gradio-based GUI for MFLUX DreamBooth training."""

try:
    import gradio as gr
except ImportError:
    raise ImportError("Gradio is not installed. Please install it with: pip install 'mflux[gui]' or pip install gradio")

import functools
import json
import os
import platform
import random
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

import platformdirs
from PIL import Image

from mflux.dreambooth.dreambooth import DreamBooth
from mflux.dreambooth.dreambooth_initializer import DreamBoothInitializer
from mflux.error.exceptions import StopTrainingException


class DreamBoothGUI:
    """Gradio interface to support novice users in DreamBooth training."""

    def __init__(self):
        self.temp_dir = None
        self.config_path = None

    def _count_caption_files(self, file_paths: List[str]) -> int:
        """Count how many images have adjacent caption files."""
        count = 0
        for file_path in file_paths:
            src = Path(file_path)
            caption_patterns = [
                src.with_name(f"{src.stem}-caption.txt"),
                src.with_name(f"{src.stem}.txt"),
                src.with_name(f"{src.stem}_caption.txt"),
            ]
            if any(p.exists() for p in caption_patterns):
                count += 1
        return count

    def validate_images(self, files: List[str]) -> Tuple[bool, str, List[Image.Image], List[str]]:
        """Validate uploaded images, skipping corrupted files."""
        if not files:
            return False, "Please upload at least 3 images", [], []

        # Check image validity, skipping problematic files
        valid_images = []
        valid_paths = []
        skipped = []

        for file_path in files:
            try:
                img = Image.open(file_path)
                # Force load to catch truncated images
                img.load()
                if img.mode != "RGB":
                    img = img.convert("RGB")
                valid_images.append(img)
                valid_paths.append(file_path)
            except (FileNotFoundError, OSError) as e:  # noqa: PERF203
                skipped.append(f"{Path(file_path).name}: {e}")

        if len(valid_images) < 3:
            skip_msg = f" Skipped: {', '.join(skipped)}" if skipped else ""
            return False, f"Too few valid images ({len(valid_images)}). Need at least 3.{skip_msg}", [], []

        if len(valid_images) > 30:
            return False, f"Too many images ({len(valid_images)}). Maximum recommended is 30.", [], []

        # Count caption files
        captions_found = self._count_caption_files(valid_paths)

        status = f"✅ {len(valid_images)} valid images loaded, {captions_found} caption files found"
        if skipped:
            status += (
                f" (skipped {len(skipped)} corrupted: {', '.join(skipped[:3])}{'...' if len(skipped) > 3 else ''})"
            )

        return True, status, valid_images, valid_paths

    def load_images_from_folder(self, folder_path: str) -> Tuple[List[Image.Image], str, List[str]]:
        """Load images from a local folder path."""
        if not folder_path:
            return [], "Please enter a folder path", []

        folder = Path(folder_path).expanduser()
        if not folder.exists():
            return [], f"❌ Folder not found: {folder}", []

        if not folder.is_dir():
            return [], f"❌ Not a directory: {folder}", []

        # Find image files
        image_extensions = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
        image_files = sorted(f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in image_extensions)

        if not image_files:
            return [], f"❌ No images found in {folder}", []

        # Validate using existing method
        file_paths = [str(f) for f in image_files]
        valid, status, images, valid_paths = self.validate_images(file_paths)

        if valid:
            return images, status, valid_paths
        return [], status, []

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
        steps: int,
        guidance: float,
        width: int,
        height: int,
        plot_frequency: int,
        generate_image_frequency: int,
    ) -> Tuple[str, str]:
        """Generate training configuration from GUI inputs."""
        if not files:
            return "❌ No images uploaded", ""

        # Create temporary directory for images
        self.temp_dir = Path(tempfile.mkdtemp(prefix="dreambooth_"))
        # a unique enough timestamped training id
        # for our use case, unlikely that any user can launch more than 1 training per minute
        self.training_id = datetime.now().strftime("%Y%m%d-%H%M")
        self.output_path = (
            platformdirs.user_desktop_path()
            / "mflux-dreambooth"
            / f"{subject_type}-{trigger_word}-model-{model}-{num_epochs}-epochs-q{quantize}-{self.training_id}"
        )

        images_dir = self.temp_dir / "images"
        images_dir.mkdir(exist_ok=True)

        # Copy images to temp directory
        image_configs = []
        captions_found = 0
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

            # Look for caption file adjacent to image (e.g., foo.png -> foo-caption.txt or foo.txt)
            prompt = None
            caption_patterns = [
                src.with_name(f"{src.stem}-caption.txt"),
                src.with_name(f"{src.stem}.txt"),
                src.with_name(f"{src.stem}_caption.txt"),
            ]
            for caption_path in caption_patterns:
                if caption_path.exists():
                    prompt = caption_path.read_text().strip()
                    # Ensure trigger word is present in custom caption
                    if trigger_word not in prompt:
                        prompt = f"{trigger_word} {subject_type}, {prompt}"
                    captions_found += 1
                    break

            # Fall back to auto-generated prompt
            if not prompt:
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

        config = {
            "model": model,
            "seed": random.randint(0, int(1e6)),
            "steps": steps,
            "guidance": guidance,
            "quantize": quantize,
            "width": width,
            "height": height,
            "training_loop": {
                "num_epochs": num_epochs,
                "batch_size": batch_size,
            },
            "optimizer": {
                "name": "AdamW",
                "learning_rate": learning_rate,
            },
            "save": {
                "output_path": str(self.output_path),
                "checkpoint_frequency": max(10, num_epochs // 10),
            },
            "instrumentation": {
                "plot_frequency": plot_frequency,
                "generate_image_frequency": generate_image_frequency,
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

📄 Training Config path: {self.config_path}
📁 Training Output path: {self.output_path}

👤 Subject type: {subject_type}
🏷️ Trigger word: {trigger_word}
🤖 Model: {model}
📊 Learning rate: {learning_rate:.1e}
🎚️ LoRA rank: {lora_rank}
💾 Quantization: {quantize}-bit
📦 Batch size: {batch_size}

🖼️ Training images: {len(image_configs)}
📝 Custom captions found: {captions_found} / {len(image_configs)}
🔄 Epochs: {num_epochs}
⏳ Total steps: {len(image_configs) * num_epochs} (images × epochs)

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
            progress(0, desc="Loading Flux model and preparing dataset (this may take several minutes)...")

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
                        # arg: (steps completed, total steps)
                        (batch_count, num_batches_for_progress),
                        desc=f"Completed Batch {batch_count} / {num_batches_for_progress}",
                    ),
                )

                if self.output_path.exists() and platform.system() == "Darwin":
                    # convenience for users - open/show the output folder in Finder
                    try:
                        subprocess.call(["open", self.output_path])
                    except subprocess.CalledProcessError:
                        # if the terminal/gui controller cannot access open or the Finder
                        print(f"📂 Training output available at {self.output_path}")

                return "✅ Training succeeded. Check your training output directory for the LoRA safetensors file."
            except StopTrainingException as stop_exc:
                training_state.save(training_spec)
                return str(f"❌ {stop_exc!s}")
        except Exception as e:  # noqa: BLE001
            return f"❌ Training failed: {e!s}"

    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface."""
        with gr.Blocks(title="MFLUX DreamBooth Training GUI") as interface:
            gr.Markdown("""
            # 🎨 MFLUX DreamBooth Training Interface

            Train your own LoRA model with Flux DreamBooth.
            """)

            with gr.Row():
                with gr.Column(scale=1):
                    # Image input options
                    gr.Markdown("#### Image Input (choose one method)")

                    gr.Markdown(
                        "*Use 10-40 high-quality images with varied angles, expressions, lighting, "
                        "and backgrounds. 1:1 aspect ratio works best.*"
                    )

                    with gr.Tab("Upload Files"):
                        file_input = gr.File(
                            label="📸 Drop Training Images Here",
                            file_count="multiple",
                            file_types=["image"],
                            interactive=True,
                        )

                    with gr.Tab("Local Folder Path"):
                        folder_path_input = gr.Textbox(
                            label="📁 Local Folder Path",
                            placeholder="/path/to/your/training/images",
                            info="Enter the full path to a folder containing training images",
                        )
                        load_folder_btn = gr.Button("Load Images from Folder", variant="secondary")

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

                    # Hidden state to track loaded image paths (from either method)
                    loaded_image_paths = gr.State([])

                    training_output = gr.Textbox(
                        label="Training Status",
                        lines=20,
                        interactive=False,
                    )

                with gr.Column(scale=1):
                    # Training parameters
                    gr.Markdown("### 📝 Training Configuration")

                    subject_type = gr.Textbox(
                        label="Subject Type",
                        placeholder="e.g., woman, man, dog, cat, toy, style",
                        value="dog",
                        info="For humans, use 'woman' or 'man' rather than 'person' for better results",
                    )

                    trigger_word = gr.Textbox(
                        label="Trigger Word",
                        value="sks",
                        info="Unique token to identify your subject. Keep it short and uncommon (e.g., sks, txcl, ohwx)",
                    )

                    model = gr.Dropdown(
                        label="Model",
                        choices=["dev", "schnell"],
                        value="dev",
                        info="'dev' is higher quality but slower; 'schnell' is faster",
                    )

                    with gr.Accordion("Advanced Settings", open=False):
                        num_epochs = gr.Slider(
                            label="Number of Epochs",
                            minimum=int(os.environ.get("MFLUX_EPOCH_MIN_VALUE", 20)),
                            maximum=300,
                            value=int(os.environ.get("MFLUX_EPOCH_DEFAULT_VALUE", 100)),
                            step=10,
                            info="~1000-1250 total steps is ideal for faces. Total steps = epochs × image count",
                        )

                        learning_rate = gr.Number(
                            label="Learning Rate",
                            value=1e-4,
                            info="1e-4 is a good default. Lower (1e-5) for fine details, higher risks overfitting",
                        )

                        lora_rank = gr.Slider(
                            label="LoRA Rank",
                            minimum=4,
                            maximum=32,
                            value=8,
                            step=4,
                            info="16-32 recommended for faces. Higher = better quality but more memory",
                        )

                        quantize = gr.Radio(
                            label="Quantization",
                            choices=[4, 8],
                            value=4,
                            info="4-bit uses less memory; 8-bit slightly better quality",
                        )

                        batch_size = gr.Slider(
                            label="Batch Size",
                            minimum=1,
                            maximum=4,
                            value=1,
                            step=1,
                            info="Keep at 1 unless you have >48GB RAM",
                        )

                        steps = gr.Slider(
                            label="Validation Steps",
                            minimum=10,
                            maximum=50,
                            value=20,
                            step=5,
                            info="Inference steps for validation images during training",
                        )

                        guidance = gr.Slider(
                            label="Validation Guidance",
                            minimum=1.0,
                            maximum=7.0,
                            value=3.0,
                            step=0.1,
                            info="CFG scale for validation images. 3.0-3.5 works well for Flux",
                        )

                        dimension_slider = functools.partial(
                            gr.Slider,
                            minimum=512,
                            maximum=1024,
                            value=512,
                            step=256,
                        )

                        width = dimension_slider(
                            label="Validation Image Width",
                        )

                        height = dimension_slider(
                            label="Validation Image Height",
                        )

                        plot_frequency = gr.Slider(
                            label="Plot Frequency (epochs)",
                            minimum=1,
                            maximum=50,
                            value=5,
                            step=5,
                        )

                        generate_image_frequency = gr.Slider(
                            label="Image Generation Frequency (epochs)",
                            minimum=10,
                            maximum=100,
                            value=10,
                            step=10,
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

            # Wire up the interface
            def on_file_upload(files):
                if not files:
                    return None, "No files uploaded", []
                valid, status, images, valid_paths = self.validate_images(files)
                if valid:
                    return images, status, valid_paths
                return None, status, []

            def on_folder_load(folder_path):
                images, status, file_paths = self.load_images_from_folder(folder_path)
                if images:
                    return images, status, file_paths
                return None, status, []

            file_input.change(
                on_file_upload,
                inputs=[file_input],
                outputs=[image_preview, validation_status, loaded_image_paths],
            )

            load_folder_btn.click(
                on_folder_load,
                inputs=[folder_path_input],
                outputs=[image_preview, validation_status, loaded_image_paths],
            )

            create_config_btn.click(
                self.generate_config,
                inputs=[
                    loaded_image_paths,
                    subject_type,
                    trigger_word,
                    model,
                    num_epochs,
                    learning_rate,
                    lora_rank,
                    quantize,
                    batch_size,
                    steps,
                    guidance,
                    width,
                    height,
                    plot_frequency,
                    generate_image_frequency,
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
            ### 💡 Tips for Best Results
            **Images:** Use 10-40 diverse, high-quality images. Vary angles, expressions, lighting, and backgrounds.
            Flux benefits from background variety—it helps isolate the subject.

            **For faces:** Use 'woman' or 'man' as subject type. Aim for ~1000-1250 total training steps
            (e.g., 100 epochs × 12 images). LoRA rank 16-32 works best.

            **Captions:** Flux works best with full-sentence captions. Place a text file next to each image:
            `photo.png` → `photo.txt` or `photo-caption.txt`. Example caption:
            *"sks woman, professional headshot, soft studio lighting, slight smile, facing camera"*

            **If results look overtrained:** Reduce LoRA strength at inference (try 0.5-0.7) or retrain with fewer epochs.
            """)

        return interface


def main():
    """Launch the GUI."""
    gui = DreamBoothGUI()
    interface = gui.create_interface()
    interface.queue().launch(server_name="127.0.0.1", server_port=7860, share=False, inbrowser=False)


if __name__ == "__main__":
    main()
