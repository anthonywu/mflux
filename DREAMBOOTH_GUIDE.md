# 🎯 DreamBooth Fine-Tuning Guide for MFLUX

Welcome! This guide will walk you through creating your own custom AI model using DreamBooth fine-tuning. No prior experience needed!

## 📚 Table of Contents

- [What is DreamBooth?](#what-is-dreambooth)
- [Quick Start](#quick-start)
- [Understanding the Process](#understanding-the-process)
- [Configuration Templates](#configuration-templates)
- [Troubleshooting](#troubleshooting)
- [Tips for Success](#tips-for-success)

## What is DreamBooth?

DreamBooth is a technique that teaches AI to recognize and generate images of a specific subject (person, pet, object, or style) by training on just a few photos. Think of it as teaching the AI to remember your specific subject.

### Key Concepts:

- **Trigger Word**: A unique identifier (like "sks") that tells the AI to use your trained subject
- **LoRA**: A efficient training method that creates a small adapter file instead of modifying the entire model
- **Epochs**: How many times the AI studies your images (like reviewing flashcards)

## Quick Start

### 1. Prepare Your Images

For detailed instructions on image preparation and labeling, see the [📸 Image Preparation Guide](DREAMBOOTH_IMAGE_PREP_GUIDE.md).

Quick summary:

- Gather 5-20 high-quality images of your subject
- Images should show different angles, expressions, or contexts
- Crop to focus on the subject (512x512 or larger)
- Save as JPEG or PNG
- Label each image with a simple prompt containing your trigger word (e.g., "photo of sks dog")

### 2. Choose a Configuration Template

#### 🐕 For Pets/Animals

```json
{
  "model": "dev",
  "seed": 42,
  "steps": 20,
  "guidance": 3.0,
  "quantize": 4,
  "width": 512,
  "height": 512,
  "training_loop": {
    "num_epochs": 100,
    "batch_size": 1
  },
  "optimizer": {
    "name": "AdamW",
    "learning_rate": 1e-4
  },
  "save": {
    "output_path": "~/Desktop/my_pet_model",
    "checkpoint_frequency": 20
  },
  "instrumentation": {
    "plot_frequency": 5,
    "generate_image_frequency": 20,
    "validation_prompt": "photo of sks dog"
  },
  "lora_layers": {
    "single_transformer_blocks": {
      "block_range": { "start": 0, "end": 38 },
      "layer_types": ["proj_out", "proj_mlp", "attn.to_q", "attn.to_k", "attn.to_v"],
      "lora_rank": 4
    }
  },
  "examples": {
    "path": "images/",
    "images": [
      { "image": "01.jpg", "prompt": "photo of sks dog" },
      { "image": "02.jpg", "prompt": "photo of sks dog" },
      { "image": "03.jpg", "prompt": "photo of sks dog" },
      { "image": "04.jpg", "prompt": "photo of sks dog" },
      { "image": "05.jpg", "prompt": "photo of sks dog" }
    ]
  }
}
```

#### 👤 For People

```json
{
  "model": "dev",
  "seed": 42,
  "steps": 25,
  "guidance": 4.0,
  "quantize": 4,
  "width": 512,
  "height": 512,
  "training_loop": {
    "num_epochs": 150,
    "batch_size": 1
  },
  "optimizer": {
    "name": "AdamW",
    "learning_rate": 5e-5
  },
  "save": {
    "output_path": "~/Desktop/my_person_model",
    "checkpoint_frequency": 25
  },
  "instrumentation": {
    "plot_frequency": 5,
    "generate_image_frequency": 25,
    "validation_prompt": "portrait of sks person"
  },
  "lora_layers": {
    "single_transformer_blocks": {
      "block_range": { "start": 10, "end": 38 },
      "layer_types": ["proj_out", "proj_mlp", "attn.to_q", "attn.to_k", "attn.to_v"],
      "lora_rank": 8
    }
  },
  "examples": {
    "path": "images/",
    "images": [
      { "image": "face1.jpg", "prompt": "portrait of sks person" },
      { "image": "face2.jpg", "prompt": "portrait of sks person" },
      { "image": "face3.jpg", "prompt": "portrait of sks person" },
      { "image": "face4.jpg", "prompt": "portrait of sks person" },
      { "image": "face5.jpg", "prompt": "portrait of sks person" }
    ]
  }
}
```

#### 🎨 For Art Styles

```json
{
  "model": "dev",
  "seed": 42,
  "steps": 20,
  "guidance": 3.5,
  "quantize": 8,
  "width": 512,
  "height": 512,
  "training_loop": {
    "num_epochs": 80,
    "batch_size": 2
  },
  "optimizer": {
    "name": "AdamW",
    "learning_rate": 2e-4
  },
  "save": {
    "output_path": "~/Desktop/my_style_model",
    "checkpoint_frequency": 10
  },
  "instrumentation": {
    "plot_frequency": 2,
    "generate_image_frequency": 10,
    "validation_prompt": "artwork in sks style"
  },
  "lora_layers": {
    "transformer_blocks": {
      "block_range": { "start": 5, "end": 15 },
      "layer_types": ["attn.to_q", "attn.to_k", "attn.to_v"],
      "lora_rank": 16
    },
    "single_transformer_blocks": {
      "block_range": { "start": 20, "end": 38 },
      "layer_types": ["proj_out", "proj_mlp"],
      "lora_rank": 8
    }
  },
  "examples": {
    "path": "images/",
    "images": [
      { "image": "style1.jpg", "prompt": "artwork in sks style" },
      { "image": "style2.jpg", "prompt": "artwork in sks style" },
      { "image": "style3.jpg", "prompt": "artwork in sks style" }
    ]
  }
}
```

### 3. Start Training

1. Save your configuration as `config.json`
2. Create an `images/` folder next to your config file
3. Add your images to the folder
4. Run: `mflux-train --train-config config.json`

## Understanding the Process

### What Happens During Training?

1. **Image Encoding**: Your images are converted into a format the AI understands
2. **Learning**: The AI adjusts its internal "knowledge" to remember your subject
3. **Validation**: Periodically generates test images to check progress
4. **Checkpointing**: Saves progress so you can resume if interrupted

### Memory Requirements

| Configuration                        | RAM Needed | Training Time\* |
| ------------------------------------ | ---------- | --------------- |
| Basic (quantize: 8, rank: 4)         | 16GB       | 1-2 hours       |
| Standard (quantize: 4, rank: 8)      | 24GB       | 2-3 hours       |
| High Quality (quantize: 4, rank: 16) | 32GB+      | 3-4 hours       |

\*On M1/M2 Macs. Training time varies based on dataset size and epochs.

### Understanding Parameters

#### Essential Parameters:

- **num_epochs**: How many times to study your images (50-200 typical)
- **learning_rate**: How fast the AI learns (1e-4 to 1e-5 typical)
- **lora_rank**: Model complexity (4-16, higher = better quality but more memory)
- **quantize**: Memory optimization (4 or 8, higher = less memory but lower quality)

#### Layer Selection:

- **transformer_blocks**: Early layers, learn general features
- **single_transformer_blocks**: Later layers, learn specific details
- Training more layers = better results but slower/more memory

## Troubleshooting

### "Out of Memory" Error

**Solutions:**

1. Increase quantization: Change `"quantize": 4` to `"quantize": 8`
2. Reduce rank: Change `"lora_rank": 8` to `"lora_rank": 4`
3. Train fewer layers: Reduce the block range
4. Close other applications

### Poor Results

**Common causes:**

1. **Too few images**: Add more varied images (aim for 10-20)
2. **Inconsistent prompts**: Ensure all training prompts include your trigger word
3. **Overfitting**: Reduce epochs if generated images look identical to training
4. **Underfitting**: Increase epochs if the subject isn't recognized

### Training Interrupted

**To resume:**

```bash
mflux-train --train-checkpoint ~/Desktop/my_model/_checkpoints/0001000_checkpoint.zip
```

## Tips for Success

### 📸 Image Selection

- **Quality over quantity**: 10 great images > 50 poor ones
- **Variety matters**: Different angles, lighting, expressions
- **Consistency helps**: Similar image quality and resolution
- **Avoid**: Blurry, cropped faces, heavy filters

### 🏷️ Choosing Your Trigger Word

- Default "sks" works well
- Can customize: "xyz", "tkn", or any rare token
- Avoid common words that might confuse the AI

### 🎯 Prompt Engineering

During training, keep prompts simple:

- ✅ "photo of sks dog"
- ✅ "portrait of sks person"
- ❌ "beautiful photo of sks dog in a park during sunset"

After training, get creative:

- "sks dog wearing a spacesuit on mars"
- "oil painting of sks person in van gogh style"

### 📊 Monitoring Progress

- Check generated images every 20-50 iterations
- Loss curve may plateau - this is normal
- Trust visual results over loss numbers

### 💾 Using Your Model

After training completes:

1. Find your adapter at: `~/Desktop/my_model/_checkpoints/[final]_checkpoint.zip`
2. Unzip to get the `.safetensors` file
3. Use with: `mflux-generate --model dev --lora-paths your_adapter.safetensors --prompt "sks dog wearing a hat"`

## Advanced Tips

### Fine-Tuning for Specific Use Cases

#### Preserving Likeness (People/Pets)

- Train more attention layers: `["attn.to_q", "attn.to_k", "attn.to_v"]`
- Use higher rank: 8-16
- More epochs: 100-200

#### Learning Styles

- Focus on projection layers: `["proj_out", "proj_mlp"]`
- Train both transformer types
- Fewer epochs to avoid overfitting: 50-100

#### Fast Iterations

- Use `"quantize": 8` for 2x faster training
- Reduce to essential layers only
- Lower resolution: 384x384

### Multi-Subject Training

Train multiple subjects by using different trigger words:

```json
"images": [
  {"image": "dog1.jpg", "prompt": "photo of sks dog"},
  {"image": "cat1.jpg", "prompt": "photo of xyz cat"}
]
```

Remember: Training AI is part science, part art. Experiment, have fun, and don't be afraid to try different settings!
