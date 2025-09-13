import time
from datetime import timedelta
from typing import Optional


class TrainingProgressTracker:
    """Enhanced progress tracking with ETA, memory monitoring, and helpful tips."""

    def __init__(self, total_steps: int, checkpoint_frequency: int):
        self.total_steps = total_steps
        self.checkpoint_frequency = checkpoint_frequency
        self.start_time = time.time()
        self.step_times = []
        self.current_step = 0
        self.current_epoch = 0
        self.total_epochs = 0
        self.last_loss = None
        self.last_display_time = 0

        # Tips to show during training
        self.tips = [
            "💡 Tip: Check generated images every 20-50 steps to monitor quality",
            "💡 Tip: Loss may plateau - trust visual results over numbers",
            "💡 Tip: Use 'sks' as your trigger word in prompts after training",
            "💡 Tip: Training can be resumed if interrupted using --train-checkpoint",
            "💡 Tip: Higher LoRA rank = better quality but more memory usage",
            "💡 Tip: Overfitting shows as loss dropping but images looking identical to training data",
            "💡 Tip: More diverse training images generally lead to better results",
            "💡 Tip: Keep training prompts simple, get creative during inference",
        ]
        self.current_tip_index = 0

    def update(self, step: int, epoch: int, total_epochs: int, loss: Optional[float] = None):
        """Update progress with current step information."""
        self.current_step = step
        self.current_epoch = epoch
        self.total_epochs = total_epochs
        if loss is not None:
            self.last_loss = loss

        # Track step timing for ETA calculation
        current_time = time.time()
        if len(self.step_times) == 0:
            self.step_times.append(current_time)
        elif current_time - self.step_times[-1] > 0.5:  # Only track if enough time passed
            self.step_times.append(current_time)
            if len(self.step_times) > 100:  # Keep only recent timings
                self.step_times.pop(0)

        # Update display periodically
        if self.should_update_display():
            self.display_progress()

    def get_eta(self) -> Optional[str]:
        """Calculate estimated time remaining."""
        if len(self.step_times) < 2:
            return None

        # Calculate average time per step
        time_diffs = [self.step_times[i] - self.step_times[i - 1] for i in range(1, len(self.step_times))]
        avg_time_per_step = sum(time_diffs) / len(time_diffs)

        # Estimate remaining time
        steps_remaining = self.total_steps - self.current_step
        seconds_remaining = steps_remaining * avg_time_per_step

        if seconds_remaining < 60:
            return f"{int(seconds_remaining)}s"
        elif seconds_remaining < 3600:
            return f"{int(seconds_remaining / 60)}m {int(seconds_remaining % 60)}s"
        else:
            hours = int(seconds_remaining / 3600)
            minutes = int((seconds_remaining % 3600) / 60)
            return f"{hours}h {minutes}m"

    def display_progress(self):
        """Display progress information."""
        progress_pct = (self.current_step / self.total_steps) * 100
        elapsed = time.time() - self.start_time
        elapsed_str = str(timedelta(seconds=int(elapsed)))
        eta = self.get_eta()

        # Clear previous line and print progress
        print(
            f"\r🎨 Progress: {self.current_step}/{self.total_steps} ({progress_pct:.1f}%) | "
            f"Epoch: {self.current_epoch}/{self.total_epochs} | "
            f"Elapsed: {elapsed_str} | "
            f"ETA: {eta or 'calculating...'} | "
            f"Loss: {self.last_loss:.6f if self.last_loss else 'N/A'}",
            end="",
            flush=True,
        )

        # Occasionally print a tip
        if self.current_step % 100 == 0 and self.current_step > 0:
            print()  # New line
            print(f"💡 {self.get_next_tip()}")

        self.last_display_time = time.time()

    def get_next_tip(self) -> str:
        """Get the next training tip to display."""
        tip = self.tips[self.current_tip_index]
        self.current_tip_index = (self.current_tip_index + 1) % len(self.tips)
        return tip

    def print_checkpoint_info(self):
        """Print checkpoint information."""
        next_checkpoint = ((self.current_step // self.checkpoint_frequency) + 1) * self.checkpoint_frequency
        if next_checkpoint <= self.total_steps:
            steps_to_checkpoint = next_checkpoint - self.current_step
            print(f"\n💾 Next checkpoint in {steps_to_checkpoint} steps")

    def should_update_display(self) -> bool:
        """Determine if the display should be updated."""
        # Update every 5 steps or every 2 seconds
        return self.current_step % 5 == 0 or time.time() - self.last_display_time > 2
