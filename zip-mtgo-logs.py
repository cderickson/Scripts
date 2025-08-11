import argparse
import os
import sys
import zipfile
from typing import List, Dict, Tuple

def get_logtype_from_filename(filename: str) -> str:
    """
    Classify a file by name as 'GameLog', 'DraftLog', or 'NA'.
    Mirrors the original heuristic while being explicit and side-effect free.
    """
    # GameLog example: contains 'Match_GameLog_' and ends with .dat
    if ('Match_GameLog_' in filename) and filename.lower().endswith('.dat') and len(filename) >= 30:
        return 'GameLog'

    # DraftLog heuristic from original script
    if (filename.count('.') != 3) or (filename.count('-') != 4) or (not filename.lower().endswith('.txt')):
        return 'NA'
    split_dash = filename.split('-')
    try:
        if (len(split_dash[1].split('.')[0]) != 4) or (len(split_dash[2]) != 4):
            return 'NA'
    except Exception:
        return 'NA'
    return 'DraftLog'

EXCLUDE_TOP_LEVEL_DIRS = {
    'Windows',
    'Program Files',
    'Program Files (x86)',
    'ProgramData',
    '$Recycle.Bin',
    'System Volume Information',
    'Recovery',
    'PerfLogs',
    'MSOCache',
    'Documents and Settings',
}

def is_drive_root(path: str) -> bool:
    p = os.path.abspath(path)
    # Typical Windows drive root is like 'C:\\'
    return len(p) == 3 and p[1] == ':' and p.endswith('\\')

def iter_log_files(root_path: str):
    """
    Walk root_path and yield absolute file paths that look like MTGO logs.
    - Skips known system directories when scanning the drive root (e.g., C:\\).
    - Does not follow symlinks.
    """
    def _ignore_error(err: BaseException):
        # Silently ignore inaccessible directories/files during walk
        return None

    for current_root, dirnames, filenames in os.walk(
        root_path, topdown=True, onerror=_ignore_error, followlinks=False
    ):
        if is_drive_root(current_root):
            # prune noisy/system directories at the top level only
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_TOP_LEVEL_DIRS]
        for name in filenames:
            kind = get_logtype_from_filename(name)
            if kind in {'GameLog', 'DraftLog'}:
                yield os.path.join(current_root, name)

def create_zip_of_logs(root_path: str, output_zip_path: str) -> Tuple[int, Dict[str, int]]:
    """
    Find all MTGO log files under root_path and write them to output_zip_path.
    - Preserves file modification times inside the ZIP (zipfile.write uses file mtime)
    - Stores files with paths relative to root_path to avoid name collisions
    Returns the number of files added.
    """
    files_added = 0
    type_counts: Dict[str, int] = {"GameLog": 0, "DraftLog": 0}
    with zipfile.ZipFile(output_zip_path, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        for full_path in iter_log_files(root_path):
            try:
                kind = get_logtype_from_filename(os.path.basename(full_path))
                arcname = os.path.relpath(full_path, start=root_path)
                # Normalize arcname to forward slashes for ZIP consistency
                arcname = arcname.replace('\\', '/')
                zf.write(full_path, arcname=arcname)
                files_added += 1
                if kind in type_counts:
                    type_counts[kind] += 1
            except Exception as exc:
                # Skip problematic files but continue processing
                print(f"Warning: failed to add {full_path}: {exc}", file=sys.stderr)
    return files_added, type_counts

def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(
        description=(
            'Zip MTGO GameLog and DraftLog files while preserving original timestamps. '
            'Scans a chosen root folder (default: your user profile) and writes MTGO-Log-Files.zip.'
        )
    )
    default_root = os.environ.get('USERPROFILE') or os.getcwd()
    parser.add_argument('--root', type=str, default=default_root, help='Root folder to scan (default: %%USERPROFILE%%)')
    parser.add_argument('--output', type=str, default=os.path.join(os.getcwd(), 'MTGO-Log-Files.zip'), help='Output ZIP path')
    args = parser.parse_args(argv)

    root_path = os.path.abspath(args.root)
    output_zip_path = os.path.abspath(args.output)

    if not os.path.exists(root_path) or not os.path.isdir(root_path):
        print(f"Error: root path does not exist or is not a directory: {root_path}", file=sys.stderr)
        return 2

    print(f"Scanning for MTGO logs under: {root_path}")
    print(f"Writing ZIP to: {output_zip_path}")

    count, type_counts = create_zip_of_logs(root_path, output_zip_path)
    if count == 0:
        print("No MTGO GameLog or DraftLog files found.")
        exit_code = 1
    else:
        print(f"Done. Added {count} file(s) to {output_zip_path}")
        print("Summary:")
        print(f"  GameLogs:  {type_counts.get('GameLog', 0)}")
        print(f"  DraftLogs: {type_counts.get('DraftLog', 0)}")
        print(f"  Total:     {count}")
        exit_code = 0

    # If packaged as an executable (e.g., PyInstaller), pause before exit so users can read output
    if getattr(sys, 'frozen', False):
        try:
            input("\nPress Enter to exit...")
        except EOFError:
            pass
    return exit_code

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))