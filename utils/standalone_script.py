#!/usr/bin/env python3
"""
Standalone background removal CLI script.
Usage: python standalone_script.py <input_image> [output_image]
See BACKGROUND_REMOVAL_DOCUMENTATION.md for details.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.background_removal import remove_background_from_image


def main():
    if len(sys.argv) < 2:
        print("Usage: python standalone_script.py <input_image> [output_image]")
        print("Example: python standalone_script.py photo.jpg photo_no_bg.png")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    else:
        input_name = Path(input_path).stem
        output_path = f"{input_name}_no_bg.png"
    
    try:
        print(f"Processing {input_path}...")
        remove_background_from_image(
            image_path=input_path,
            output_path=output_path
        )
        print(f"✓ Background removed! Output saved to: {output_path}")
    except Exception as e:
        print(f"✗ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

