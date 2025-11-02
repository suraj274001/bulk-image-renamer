#!/usr/bin/env python3
import os
import re
from pathlib import Path
from typing import List, Dict, Optional
import argparse


class ImageRenamer:
    def __init__(self, directory: str, pattern: str = "product", start_number: int = 1,
                 prefix: str = "", suffix: str = "", padding: int = 3, dry_run: bool = False):
        self.directory = Path(directory)
        self.pattern = pattern
        self.start_number = start_number
        self.prefix = prefix
        self.suffix = suffix
        self.padding = padding
        self.dry_run = dry_run
        self.supported_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.svg'}

    def get_image_files(self) -> List[Path]:
        image_files = []
        for file in sorted(self.directory.iterdir()):
            if file.is_file() and file.suffix.lower() in self.supported_extensions:
                image_files.append(file)
        return image_files

    def generate_new_name(self, index: int, extension: str) -> str:
        number = str(self.start_number + index).zfill(self.padding)
        new_name = f"{self.prefix}{self.pattern}_{number}{self.suffix}{extension}"
        return new_name

    def rename_sequential(self) -> Dict[str, str]:
        image_files = self.get_image_files()
        rename_map = {}

        for index, file in enumerate(image_files):
            new_name = self.generate_new_name(index, file.suffix.lower())
            new_path = self.directory / new_name
            rename_map[str(file)] = str(new_path)

        return rename_map

    def rename_by_date(self) -> Dict[str, str]:
        image_files = self.get_image_files()
        image_files.sort(key=lambda x: x.stat().st_mtime)
        rename_map = {}

        for index, file in enumerate(image_files):
            new_name = self.generate_new_name(index, file.suffix.lower())
            new_path = self.directory / new_name
            rename_map[str(file)] = str(new_path)

        return rename_map

    def rename_with_custom_pattern(self, custom_pattern: str) -> Dict[str, str]:
        image_files = self.get_image_files()
        rename_map = {}

        for index, file in enumerate(image_files):
            number = str(self.start_number + index).zfill(self.padding)
            new_name = custom_pattern.replace('{n}', number).replace('{ext}', file.suffix.lower())
            new_path = self.directory / new_name
            rename_map[str(file)] = str(new_path)

        return rename_map

    def clean_filename(self, filename: str) -> str:
        name_without_ext = filename.rsplit('.', 1)[0]
        extension = '.' + filename.rsplit('.', 1)[1] if '.' in filename else ''

        cleaned = re.sub(r'[^\w\s-]', '', name_without_ext)
        cleaned = re.sub(r'[-\s]+', '_', cleaned)
        cleaned = cleaned.strip('_').lower()

        return cleaned + extension

    def rename_clean(self) -> Dict[str, str]:
        image_files = self.get_image_files()
        rename_map = {}

        for file in image_files:
            new_name = self.clean_filename(file.name)
            new_path = self.directory / new_name

            counter = 1
            while new_path.exists() and new_path != file:
                name_parts = new_name.rsplit('.', 1)
                new_name = f"{name_parts[0]}_{counter}.{name_parts[1]}"
                new_path = self.directory / new_name
                counter += 1

            rename_map[str(file)] = str(new_path)

        return rename_map

    def execute_rename(self, rename_map: Dict[str, str]) -> None:
        if not rename_map:
            print("No files to rename.")
            return

        print(f"\n{'DRY RUN - ' if self.dry_run else ''}Renaming {len(rename_map)} files:\n")

        for old_path, new_path in rename_map.items():
            print(f"  {Path(old_path).name} -> {Path(new_path).name}")

            if not self.dry_run:
                try:
                    os.rename(old_path, new_path)
                except Exception as e:
                    print(f"    ERROR: {e}")

        if self.dry_run:
            print("\nDry run completed. Use --execute to apply changes.")
        else:
            print(f"\nSuccessfully renamed {len(rename_map)} files.")


def main():
    parser = argparse.ArgumentParser(
        description='Bulk rename product image files with various naming patterns',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python bulk_image_renamer.py /path/to/images --pattern product --start 1
  python bulk_image_renamer.py /path/to/images --mode date --prefix shop_ --suffix _v1
  python bulk_image_renamer.py /path/to/images --mode custom --custom-pattern "item_{n}_photo{ext}"
  python bulk_image_renamer.py /path/to/images --mode clean
  python bulk_image_renamer.py /path/to/images --dry-run
        '''
    )

    parser.add_argument('directory', help='Directory containing images to rename')
    parser.add_argument('--mode', choices=['sequential', 'date', 'custom', 'clean'],
                        default='sequential', help='Renaming mode (default: sequential)')
    parser.add_argument('--pattern', default='product', help='Base pattern for file names (default: product)')
    parser.add_argument('--custom-pattern', help='Custom pattern using {n} for number and {ext} for extension')
    parser.add_argument('--start', type=int, default=1, help='Starting number (default: 1)')
    parser.add_argument('--prefix', default='', help='Prefix to add before pattern')
    parser.add_argument('--suffix', default='', help='Suffix to add after number')
    parser.add_argument('--padding', type=int, default=3, help='Number padding zeros (default: 3)')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without renaming')
    parser.add_argument('--execute', action='store_true', help='Execute the renaming')

    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Error: Directory '{args.directory}' does not exist.")
        return

    dry_run = not args.execute

    renamer = ImageRenamer(
        directory=args.directory,
        pattern=args.pattern,
        start_number=args.start,
        prefix=args.prefix,
        suffix=args.suffix,
        padding=args.padding,
        dry_run=dry_run
    )

    if args.mode == 'sequential':
        rename_map = renamer.rename_sequential()
    elif args.mode == 'date':
        rename_map = renamer.rename_by_date()
    elif args.mode == 'custom':
        if not args.custom_pattern:
            print("Error: --custom-pattern is required for custom mode")
            return
        rename_map = renamer.rename_with_custom_pattern(args.custom_pattern)
    elif args.mode == 'clean':
        rename_map = renamer.rename_clean()

    renamer.execute_rename(rename_map)


if __name__ == '__main__':
    main()
