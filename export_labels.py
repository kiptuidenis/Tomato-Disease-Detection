#!/usr/bin/env python3
"""
Export class names to JSON for deployment.
This script helps maintain consistency between training and inference.
"""
import json
import argparse
from pathlib import Path

DEFAULT_LABELS = [
    'Tomato___Bacterial_spot',
    'Tomato___Early_blight',
    'Tomato___Late_blight',
    'Tomato___Leaf_Mold',
    'Tomato___Septoria_leaf_spot',
    'Tomato___Spider_mites Two-spotted_spider_mite',
    'Tomato___Target_Spot',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
    'Tomato___Tomato_mosaic_virus',
    'Tomato___healthy'
]

def main():
    parser = argparse.ArgumentParser(
        description='Export class names to class_names.json for deployment'
    )
    parser.add_argument(
        '--output', 
        type=str, 
        default='class_names.json', 
        help='Output JSON path'
    )
    parser.add_argument(
        '--labels', 
        type=str, 
        nargs='*', 
        help='Override labels list (space separated)'
    )
    args = parser.parse_args()

    labels = args.labels if args.labels else DEFAULT_LABELS
    out_path = Path(args.output)
    
    # Write labels to JSON
    out_path.write_text(
        json.dumps(labels, ensure_ascii=False, indent=2), 
        encoding='utf-8'
    )
    print(f"✓ Wrote {len(labels)} labels to {out_path.resolve()}")
    print(f"  Labels: {', '.join(labels)}")

if __name__ == '__main__':
    main()
