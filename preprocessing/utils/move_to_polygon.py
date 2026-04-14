import os
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from dotenv import load_dotenv
from config import PROJECT_PATH, SERVER_PATH

SOURCE_DIR = Path(PROJECT_PATH) / "data" / "raw" / "raw_videos"
DEST_DIR = Path(SERVER_PATH) / "data" / "raw"/ "original_videos" / "webm"

WORKERS = 64  # high for network I/O — tune down if server struggles

def move_file(src: Path, dest_dir: Path, existing: set) -> str:
    if src.name in existing:
        return f"{src.name} (skipped)"
    dest = dest_dir / src.name
    # copy + unlink is faster than shutil.move across filesystems:
    # shutil.move always tries os.rename first (fails cross-device), then falls back
    shutil.copy(src, dest)
    src.unlink()
    return src.name


def main():
    DEST_DIR.mkdir(parents=True, exist_ok=True)
    webm_files = list(SOURCE_DIR.glob("*.webm"))
    if not webm_files:
        print(f"No .webm files found in {SOURCE_DIR}")
        return

    existing = {f.name for f in DEST_DIR.glob("*.webm")}

    total = len(webm_files)
    print(f"Moving {total} files to {DEST_DIR} using {WORKERS} threads ...")

    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = {executor.submit(move_file, f, DEST_DIR, existing): f for f in webm_files}
        for i, future in enumerate(as_completed(futures), 1):
            name = future.result()
            print(f"[{i}/{total}] {name}")

    print("Done.")


if __name__ == "__main__":
    main()
