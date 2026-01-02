#!/usr/bin/env python3
"""Entry point for DreamBooth GUI."""

import sys


def main():
    try:
        from mflux.dreambooth.gui.gradio_interface import main as gui_main

        gui_main()
    except ImportError as e:
        if "gradio" in str(e).lower():
            print("\n❌ Gradio is not installed. The GUI requires the optional 'gui' dependencies.")
            print("\nTo install, run:")
            print("  pip install 'mflux[gui]'")
            print("\nOr install Gradio directly:")
            print("  uv pip install 'gradio>=5.44.0'\n")
            sys.exit(1)
        else:
            raise
    except (KeyboardInterrupt, Exception) as e:
        if isinstance(e, KeyboardInterrupt):
            print("Training Job cancelled by user")
            sys.exit(0)
        else:
            raise


if __name__ == "__main__":
    main()
