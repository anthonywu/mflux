# 📸 DreamBooth Image Preparation Guide

This guide will help you prepare your images for optimal DreamBooth training results.

## Table of Contents

- [Quick Checklist](#quick-checklist)
- [Image Requirements](#image-requirements)
- [Image Selection Guidelines](#image-selection-guidelines)
- [Image Preparation Steps](#image-preparation-steps)
- [Labeling Your Images](#labeling-your-images)
- [Common Mistakes to Avoid](#common-mistakes-to-avoid)
- [Examples by Use Case](#examples-by-use-case)

## Quick Checklist

✅ **Before you start training, ensure:**

- [ ] 3-20 images of your subject
- [ ] Images are 512x512 pixels or larger
- [ ] Clear, well-lit photos
- [ ] Variety of angles/poses/contexts
- [ ] Consistent file naming
- [ ] Each image has a proper prompt/label

## Image Requirements

### Technical Specifications

- **Format**: JPEG (.jpg, .jpeg) or PNG (.png)
- **Minimum size**: 512x512 pixels (will be resized if larger)
- **Recommended size**: 512x512 to 1024x1024
- **File size**: Under 10MB per image
- **Color mode**: RGB (not CMYK or grayscale)

### Quality Requirements

- **Resolution**: High resolution, not pixelated
- **Focus**: Subject should be in sharp focus
- **Lighting**: Well-lit, avoid heavy shadows
- **Compression**: Avoid heavily compressed images

## Image Selection Guidelines

### What Makes a Good Training Set

#### 1. **Variety is Key**

Include images with:

- Different angles (front, side, 3/4 view)
- Various expressions (for people/animals)
- Different backgrounds
- Multiple distances (close-up, medium, full)
- Various lighting conditions

#### 2. **Consistency of Subject**

- The subject should be clearly recognizable in all images
- Avoid images where the subject is too small or obscured
- For people: same person, similar age
- For objects: same specific item

#### 3. **Optimal Quantity**

| Subject Type | Minimum | Recommended | Maximum |
| ------------ | ------- | ----------- | ------- |
| Person       | 5       | 10-15       | 20      |
| Pet/Animal   | 5       | 8-12        | 20      |
| Object       | 3       | 5-10        | 15      |
| Art Style    | 3       | 10-20       | 30      |

### What to Avoid

- ❌ Blurry or out-of-focus images
- ❌ Heavy filters or effects
- ❌ Images with complicated backgrounds (i.e. using the macOS [Service to remove background](https://support.apple.com/guide/preview/extract-an-image-or-remove-a-background-prvw15636/mac) can be helpful)
- ❌ Images with multiple subjects (unless training for groups)
- ❌ Extremely dark or overexposed photos
- ❌ Heavy watermarks or text overlays
- ❌ Cropped faces (for person training)
- ❌ Images where subject is less than 20% of frame

## Image Preparation Steps

### Step 1: Collect Your Images

Gather all potential training images in one folder.

### Step 2: Review and Filter

Remove images that:

- Are blurry or low quality
- Don't clearly show the subject
- Are too similar to each other
- Have heavy processing/filters

### Step 3: Crop and Center (Optional but Recommended)

#### For People/Pets:

```bash
# Example: Create square crops centered on subject
# You can use any image editor, or command line tools like ImageMagick:
magick input.jpg -gravity center -crop 1:1 output.jpg
```

#### Tips for Cropping:

- Keep the subject centered
- Include some background context
- Don't crop too tightly
- Maintain aspect ratio when possible

### Step 4: Resize Images

While MFLUX will automatically resize images, pre-resizing can speed up training:

```bash
# Resize to 512x512 (maintains aspect ratio, pads if needed)
magick input.jpg -resize 512x512 -background white -gravity center -extent 512x512 output.jpg
```

### Step 5: Organize and Name Files

Use clear, consistent naming:

```
images/
├── 01_front_view.jpg
├── 02_side_view.jpg
├── 03_sitting.jpg
├── 04_outdoor.jpg
└── 05_closeup.jpg
```

## Labeling Your Images

### Understanding Prompts/Labels

Each image needs a text description (prompt) that tells the AI what it's looking at. This is crucial for training success.

### The Trigger Word

The trigger word (typically "sks") is a unique identifier for your subject:

- **Purpose**: Tells the AI "this is my special subject"
- **Usage**: Must appear in EVERY training prompt
- **After training**: Use this word to generate images of your subject

### Prompt Structure

#### Basic Format:

```
[description] of sks [subject_type]
```

#### Examples:

- "photo of sks dog"
- "portrait of sks person"
- "painting of sks cat"
- "illustration in sks style"

### Labeling Strategies by Use Case

#### For Pets/Animals:

```json
{
  "images": [
    { "image": "01.jpg", "prompt": "photo of sks dog" },
    { "image": "02.jpg", "prompt": "photo of sks dog sitting" },
    { "image": "03.jpg", "prompt": "photo of sks dog outdoors" },
    { "image": "04.jpg", "prompt": "closeup photo of sks dog" },
    { "image": "05.jpg", "prompt": "photo of sks dog playing" }
  ]
}
```

**Tips:**

- Keep prompts simple during training
- Can add simple descriptors: "sitting", "running", "sleeping"
- Avoid complex scenes in training prompts

#### For People:

```json
{
  "images": [
    { "image": "01.jpg", "prompt": "portrait of sks person" },
    { "image": "02.jpg", "prompt": "photo of sks person" },
    { "image": "03.jpg", "prompt": "headshot of sks person" },
    { "image": "04.jpg", "prompt": "photo of sks person smiling" },
    { "image": "05.jpg", "prompt": "portrait of sks person outdoors" }
  ]
}
```

**Tips:**

- Use "person" not the actual name
- Can specify photo type: "portrait", "headshot", "photo"
- Simple emotional descriptors are okay: "smiling", "serious"

#### For Objects:

```json
{
  "images": [
    { "image": "01.jpg", "prompt": "photo of sks toy" },
    { "image": "02.jpg", "prompt": "photo of sks toy on white background" },
    { "image": "03.jpg", "prompt": "closeup of sks toy" },
    { "image": "04.jpg", "prompt": "photo of sks toy from side" }
  ]
}
```

#### For Art Styles:

```json
{
  "images": [
    { "image": "01.jpg", "prompt": "artwork in sks style" },
    { "image": "02.jpg", "prompt": "painting in sks style" },
    { "image": "03.jpg", "prompt": "illustration in sks style" },
    { "image": "04.jpg", "prompt": "drawing in sks style" },
    { "image": "05.jpg", "prompt": "landscape in sks style" }
  ]
}
```

**Tips:**

- Be consistent with style descriptor
- Can include subject matter: "landscape", "portrait", "abstract"

### Advanced Labeling

#### When to Add More Detail:

Only add details that vary between images and you want the model to learn:

```json
{
  "images": [
    { "image": "01.jpg", "prompt": "photo of sks dog with red collar" },
    { "image": "02.jpg", "prompt": "photo of sks dog with blue collar" },
    { "image": "03.jpg", "prompt": "photo of sks dog without collar" }
  ]
}
```

#### Regularization Images (Advanced):

For better results, you can include regularization images (optional):

```json
{
  "images": [
    { "image": "my_dog_01.jpg", "prompt": "photo of sks dog" },
    { "image": "my_dog_02.jpg", "prompt": "photo of sks dog" },
    { "image": "regular_dog_01.jpg", "prompt": "photo of dog" }, // No 'sks'
    { "image": "regular_dog_02.jpg", "prompt": "photo of dog" } // No 'sks'
  ]
}
```

## Common Mistakes to Avoid

### 1. **Over-complicated Prompts**

❌ Bad: "beautiful professional photograph of sks dog sitting in a sunny garden with flowers"
✅ Good: "photo of sks dog sitting"

### 2. **Inconsistent Trigger Word**

❌ Bad: Mixing "sks", "my dog", "fluffy" as identifiers
✅ Good: Always use "sks" (or your chosen trigger word)

### 3. **Too Similar Images**

❌ Bad: 10 photos from the same photoshoot
✅ Good: Images from different days/locations/angles

### 4. **Mixing Subjects**

❌ Bad: Photos with multiple dogs when training for one specific dog
✅ Good: Only your target subject clearly visible

### 5. **Wrong Image Orientation**

❌ Bad: Mix of portrait and landscape orientations
✅ Good: Consistent orientation (square is best)

## Examples by Use Case

### Example 1: Training Your Pet Dog

**Image Collection:**

```
images/
├── 01_park_front.jpg      # Dog at park, front view
├── 02_home_side.jpg        # Dog at home, side view
├── 03_beach_running.jpg    # Dog at beach, running
├── 04_portrait_close.jpg   # Close-up portrait
├── 05_garden_sitting.jpg   # Dog in garden, sitting
├── 06_indoor_lying.jpg     # Dog indoors, lying down
├── 07_snow_playing.jpg     # Dog in snow, playing
└── 08_car_happy.jpg        # Dog in car, happy expression
```

**Configuration:**

```json
"examples": {
  "path": "images/",
  "images": [
    {"image": "01_park_front.jpg", "prompt": "photo of sks dog"},
    {"image": "02_home_side.jpg", "prompt": "photo of sks dog"},
    {"image": "03_beach_running.jpg", "prompt": "photo of sks dog running"},
    {"image": "04_portrait_close.jpg", "prompt": "closeup photo of sks dog"},
    {"image": "05_garden_sitting.jpg", "prompt": "photo of sks dog sitting"},
    {"image": "06_indoor_lying.jpg", "prompt": "photo of sks dog lying down"},
    {"image": "07_snow_playing.jpg", "prompt": "photo of sks dog playing"},
    {"image": "08_car_happy.jpg", "prompt": "photo of sks dog"}
  ]
}
```

### Example 2: Training a Person

**Image Collection:**

```
images/
├── 01_headshot_formal.jpg     # Professional headshot
├── 02_casual_outdoor.jpg      # Casual outdoor photo
├── 03_portrait_smiling.jpg    # Smiling portrait
├── 04_profile_view.jpg        # Side profile
├── 05_full_body.jpg           # Full body shot
├── 06_different_lighting.jpg  # Different lighting condition
├── 07_candid_natural.jpg      # Natural candid shot
└── 08_different_outfit.jpg    # Different clothing
```

### Example 3: Training an Art Style

**Image Collection:**

```
images/
├── 01_landscape.jpg        # Landscape in the style
├── 02_portrait.jpg         # Portrait in the style
├── 03_still_life.jpg       # Still life in the style
├── 04_abstract.jpg         # Abstract piece
├── 05_architecture.jpg     # Architecture in the style
├── 06_nature.jpg           # Nature scene
├── 07_urban.jpg            # Urban scene
├── 08_character.jpg        # Character art
├── 09_animals.jpg          # Animals in the style
└── 10_objects.jpg          # Objects in the style
```

## After Training: Using Your Model

Once training is complete, you can generate images using your trigger word:

### Basic Usage:

```bash
mflux-generate \
    --model dev \
    --lora-paths your_lora.safetensors \
    --prompt "sks dog wearing a superhero cape"
```

### Creative Prompts:

- "sks dog as a renaissance painting"
- "sks person as a wizard in fantasy art style"
- "sks toy in a futuristic sci-fi setting"
- "landscape painting in sks style with mountains and lake"

### Tips for Generation:

1. **Be creative**: Now you can use complex prompts!
2. **Combine styles**: "sks dog in van gogh style"
3. **Add details**: "sks person wearing a red suit in a library"
4. **Specify settings**: "sks cat in space", "sks dog underwater"

## Troubleshooting

### Images Look Nothing Like Training Data

- Check if you used the trigger word in prompts
- Verify images were properly loaded (check file paths)
- May need more training epochs

### Model Only Generates One Specific Image

- Training data too similar (overfitting)
- Add more variety to training images
- Reduce number of epochs

### Poor Quality Results

- Check image quality (resolution, focus)
- Ensure proper lighting in training images
- May need to adjust LoRA rank or learning rate

## Quick Reference Card

```
📁 Image Prep Checklist:
├── ✅ 5-20 images collected
├── ✅ Images are high quality (sharp, well-lit)
├── ✅ Variety of angles/contexts
├── ✅ 512x512 pixels or larger
├── ✅ RGB format (JPEG/PNG)
├── ✅ Consistent subject across all images
├── ✅ Simple, consistent prompts with trigger word
└── ✅ Images organized in single folder

🏷️ Prompt Template:
"[photo/portrait/artwork] of sks [subject]"

🚀 Ready to train:
mflux-train-config  # Interactive setup
mflux-train --train-config your_config.json
```

Remember: Quality over quantity! 10 well-chosen, diverse images will train better than 50 similar ones.
