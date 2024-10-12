try:
    # use the fancy progress bar if 'rich' is installed
    # https://tqdm.github.io/docs/rich/
    import warnings
    from functools import partial

    from rich.console import Console
    from tqdm import TqdmExperimentalWarning
    from tqdm.rich import tqdm

    warnings.filterwarnings("ignore", category=TqdmExperimentalWarning)
    # see help(Console), used to print messages to user
    # https://rich.readthedocs.io/en/stable/console.html#printing
    console = Console(color_system="auto")
    progress = partial(
        tqdm,
        # options: see help(rich.progress.Progress)
        options=dict(console=console, transient=True),
    )
except ModuleNotFoundError:
    # gracefully use standard progress bar
    from unittest.mock import Mock
    from tqdm import tqdm as progress
    progress.console = Mock(print=print)

__all__ = ["progress"]
