try:
    # use the fancy progress bar if 'rich' is installed
    # https://tqdm.github.io/docs/rich/
    from tqdm.rich import tqdm as progress
    from tqdm import TqdmExperimentalWarning

    import warnings

    warnings.filterwarnings("ignore", category=TqdmExperimentalWarning)
except ModuleNotFoundError as e:
    # gracefully use standard progress bar
    from tqdm import tqdm as progress

__all__ = ["progress"]
