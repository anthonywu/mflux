import os
import platform
import subprocess
from pathlib import Path
from typing import Any, List, Tuple

import mlx.core as mx


class PreflightCheck:
    """Performs pre-flight checks before starting training."""

    @staticmethod
    def run_all_checks(training_spec: Any) -> Tuple[bool, List[str]]:
        """Run all pre-flight checks and return (success, warnings)."""
        warnings = []

        # Check system resources
        warnings.extend(PreflightCheck._check_system_resources())

        # Check output directory
        warnings.extend(PreflightCheck._check_output_directory(training_spec.saver.output_path))

        # Check MLX device
        warnings.extend(PreflightCheck._check_mlx_device())

        # Check for common issues
        warnings.extend(PreflightCheck._check_common_issues())

        return len([w for w in warnings if w.startswith("ERROR:")]) == 0, warnings

    @staticmethod
    def _check_system_resources() -> List[str]:
        """Check available system resources."""
        warnings = []

        # Check available memory using vm_stat on macOS
        if platform.system() == "Darwin":
            try:
                result = subprocess.run(["vm_stat"], capture_output=True, text=True, check=False)
                if result.returncode == 0:
                    # Parse vm_stat output
                    lines = result.stdout.strip().split("\n")
                    stats = {}
                    for line in lines[1:]:  # Skip header
                        if ":" in line:
                            key, value = line.split(":", 1)
                            stats[key.strip()] = int(value.strip().rstrip(".").replace(",", ""))

                    # Calculate memory in GB (page size is typically 4096 bytes)
                    page_size = 4096
                    free_pages = stats.get("Pages free", 0)
                    inactive_pages = stats.get("Pages inactive", 0)
                    available_gb = (free_pages + inactive_pages) * page_size / (1024**3)

                    if available_gb < 8:
                        warnings.append(
                            f"ERROR: Insufficient memory. Available: ~{available_gb:.1f}GB, recommended minimum: 8GB"
                        )
                    elif available_gb < 16:
                        warnings.append(f"WARNING: Low memory. Available: ~{available_gb:.1f}GB, recommended: 16GB+")
            except Exception:
                warnings.append("WARNING: Could not check available memory")

        # Check disk space
        try:
            stat = os.statvfs(Path.home())
            free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)

            if free_gb < 5:
                warnings.append(f"ERROR: Insufficient disk space. Available: {free_gb:.1f}GB, required minimum: 5GB")
            elif free_gb < 10:
                warnings.append(f"WARNING: Low disk space. Available: {free_gb:.1f}GB, recommended: 10GB+")
        except Exception:
            warnings.append("WARNING: Could not check disk space")

        # Check if on battery (macOS)
        if platform.system() == "Darwin":
            try:
                result = subprocess.run(["pmset", "-g", "batt"], capture_output=True, text=True, check=False)
                if "Battery Power" in result.stdout:
                    warnings.append(
                        "WARNING: Running on battery power. Training will be slower and may drain battery quickly"
                    )
            except Exception:
                pass

        return warnings

    @staticmethod
    def _check_output_directory(output_path: str) -> List[str]:
        """Check output directory permissions and existence."""
        warnings = []

        output_path = Path(output_path).expanduser()

        try:
            # Try to create the directory if it doesn't exist
            output_path.mkdir(parents=True, exist_ok=True)

            # Test write permissions
            test_file = output_path / ".test_write_permission"
            test_file.touch()
            test_file.unlink()

        except PermissionError:
            warnings.append(f"ERROR: No write permission for output directory: {output_path}")
        except Exception as e:
            warnings.append(f"ERROR: Cannot create output directory: {output_path} - {e}")

        # Check if directory already contains training artifacts
        if output_path.exists():
            existing_checkpoints = list(output_path.glob("*_checkpoint.zip"))
            if existing_checkpoints:
                warnings.append(
                    f"WARNING: Output directory contains {len(existing_checkpoints)} existing checkpoints. "
                    "Consider using a new directory or backing up existing files"
                )

        return warnings

    @staticmethod
    def _check_mlx_device() -> List[str]:
        """Check MLX device availability."""
        warnings = []

        try:
            # Check if Metal is available
            device = mx.default_device()
            if device.type != mx.gpu:
                warnings.append("WARNING: GPU not available. Training will use CPU and be significantly slower")

            # Try to get GPU info
            if platform.system() == "Darwin":
                try:
                    result = subprocess.run(
                        ["system_profiler", "SPDisplaysDataType"], capture_output=True, text=True, check=False
                    )
                    if "Apple M" not in result.stdout and "GPU" not in result.stdout:
                        warnings.append("WARNING: No Apple Silicon GPU detected. Performance may be limited")
                except Exception:
                    pass
        except Exception as e:
            warnings.append(f"WARNING: Could not check MLX device: {e}")

        return warnings

    @staticmethod
    def _check_common_issues() -> List[str]:
        """Check for common issues that might affect training."""
        warnings = []

        # Check for common memory-intensive processes on macOS
        if platform.system() == "Darwin":
            try:
                # Use ps to check for memory-intensive processes
                result = subprocess.run(["ps", "aux"], capture_output=True, text=True, check=False)
                if result.returncode == 0:
                    lines = result.stdout.strip().split("\n")[1:]  # Skip header
                    memory_hogs = []
                    for line in lines:
                        parts = line.split(None, 10)
                        if len(parts) >= 11:
                            try:
                                mem_percent = float(parts[3])
                                if mem_percent > 10:
                                    process_name = parts[10].split()[0]
                                    memory_hogs.append((process_name, mem_percent))
                            except ValueError:
                                continue

                    if memory_hogs:
                        memory_hogs.sort(key=lambda x: x[1], reverse=True)
                        warnings.append(
                            "WARNING: High memory usage detected from other processes:\n"
                            + "\n".join(f"  - {name}: {mem:.1f}%" for name, mem in memory_hogs[:3])
                        )
            except Exception:
                pass

        return warnings

    @staticmethod
    def print_system_info():
        """Print system information for debugging."""
        print("\n🖥️  System Information:")
        print(f"  • Platform: {platform.system()} {platform.release()}")
        print(f"  • Processor: {platform.processor() or platform.machine()}")

        # Get RAM info on macOS
        if platform.system() == "Darwin":
            try:
                result = subprocess.run(["sysctl", "hw.memsize"], capture_output=True, text=True, check=False)
                if result.returncode == 0:
                    memsize = int(result.stdout.strip().split(": ")[1])
                    print(f"  • Total RAM: {memsize / (1024**3):.1f}GB")
            except Exception:
                print("  • Total RAM: Unknown")

        try:
            device = mx.default_device()
            print(f"  • MLX Device: {device.type}")
        except Exception:
            print("  • MLX Device: Unknown")

        print()
