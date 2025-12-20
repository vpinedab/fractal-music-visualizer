"""
Video management system for storing and retrieving multiple videos per audio file.
All paths are stored as relative paths to ensure portability across systems.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Get app root directory (where this file is located)
APP_ROOT = Path(__file__).resolve().parent
VIDEOS_ROOT = APP_ROOT / "assets" / "output" / "videos"
MUSIC_ROOT = APP_ROOT / "assets" / "music"
METADATA_FILE = VIDEOS_ROOT / "metadata.json"

def ensure_video_directories():
    """Ensure video storage directories exist."""
    VIDEOS_ROOT.mkdir(parents=True, exist_ok=True)
    if not METADATA_FILE.exists():
        with open(METADATA_FILE, 'w') as f:
            json.dump({}, f)

def _to_relative_path(path: Path) -> str:
    """Convert absolute path to relative path from app root."""
    try:
        if not path:
            return ""

        path_obj = Path(path) if isinstance(path, str) else path
        if path_obj.is_absolute():
            # Try to make it relative to app root
            try:
                rel = path_obj.relative_to(APP_ROOT)
                return str(rel).replace('\\', '/')  # Use forward slashes for portability
            except ValueError:
                # If not under app root, try relative to videos root
                try:
                    rel = path_obj.relative_to(VIDEOS_ROOT)
                    return str(rel).replace('\\', '/')
                except ValueError:
                    # Try relative to music root
                    try:
                        rel = path_obj.relative_to(MUSIC_ROOT)
                        return str(rel).replace('\\', '/')
                    except ValueError:
                        # Fallback: store just the filename
                        return path_obj.name
        # Already relative, normalize separators
        return str(path_obj).replace('\\', '/')
    except Exception:
        return str(path) if path else ""

def _to_absolute_path(rel_path: str) -> Path:
    """Convert relative path to absolute path."""
    if not rel_path:
        return Path()

    # Normalize path separators (handle both / and \)
    rel_path_normalized = str(rel_path).replace('\\', '/')
    rel_path_obj = Path(rel_path_normalized)

    if rel_path_obj.is_absolute():
        # If it's already absolute, check if it exists
        # If not, try to convert it to relative first
        if not rel_path_obj.exists():
            # Try to make it relative and then absolute again
            try:
                rel = rel_path_obj.relative_to(APP_ROOT)
                return APP_ROOT / rel
            except ValueError:
                pass
        return rel_path_obj

    # Try relative to app root first (most common case)
    abs_path = APP_ROOT / rel_path_obj
    if abs_path.exists():
        return abs_path

    # Try relative to videos root
    abs_path = VIDEOS_ROOT / rel_path_obj
    if abs_path.exists():
        return abs_path

    # Try relative to music root
    abs_path = MUSIC_ROOT / rel_path_obj
    if abs_path.exists():
        return abs_path

    # If path doesn't start with .., assume it's relative to app root
    if not any(part == '..' for part in rel_path_obj.parts):
        return APP_ROOT / rel_path_obj

    # Return as-is (might be relative to current working directory)
    return rel_path_obj.resolve() if rel_path_obj.exists() else (APP_ROOT / rel_path_obj)

def load_metadata() -> Dict:
    """Load video metadata from JSON file and migrate absolute paths to relative."""
    ensure_video_directories()
    if not METADATA_FILE.exists():
        return {}
    try:
        with open(METADATA_FILE, 'r') as f:
            metadata = json.load(f)

        # Migrate absolute paths to relative paths
        migrated = False
        for audio_stem, videos in metadata.items():
            for video_info in videos:
                # Migrate video path
                if 'path' in video_info:
                    old_path = video_info['path']
                    new_path = _to_relative_path(old_path)
                    if old_path != new_path:
                        video_info['path'] = new_path
                        migrated = True

                # Migrate audio file path
                if 'audio_file' in video_info:
                    old_audio = video_info['audio_file']
                    new_audio = _to_relative_path(old_audio)
                    if old_audio != new_audio:
                        video_info['audio_file'] = new_audio
                        migrated = True

        # Save migrated metadata
        if migrated:
            save_metadata(metadata)

        return metadata
    except (json.JSONDecodeError, IOError):
        return {}

def save_metadata(metadata: Dict):
    """Save video metadata to JSON file with relative paths."""
    ensure_video_directories()
    # Ensure all paths are relative before saving
    for audio_stem, videos in metadata.items():
        for video_info in videos:
            if 'path' in video_info:
                video_info['path'] = _to_relative_path(video_info['path'])
            if 'audio_file' in video_info:
                video_info['audio_file'] = _to_relative_path(video_info['audio_file'])

    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=2)

def get_video_filename(audio_stem: str, video_title: str = None) -> str:
    """
    Generate a unique video filename.
    Format: audio_stem_timestamp_title.mp4
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if video_title:
        # Sanitize title for filename
        safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '_')[:50]  # Limit length
        filename = f"{audio_stem}_{timestamp}_{safe_title}.mp4"
    else:
        filename = f"{audio_stem}_{timestamp}.mp4"

    return filename

def register_video(audio_path: Path, video_path: Path, title: str = None, settings: Dict = None) -> Dict:
    """
    Register a new video in the metadata system.
    Returns the video info dict with relative paths.
    """
    ensure_video_directories()
    metadata = load_metadata()

    audio_stem = audio_path.stem
    if audio_stem not in metadata:
        metadata[audio_stem] = []

    video_info = {
        'id': len(metadata[audio_stem]) + 1,
        'title': title or f"Video {len(metadata[audio_stem]) + 1}",
        'filename': video_path.name,
        'path': _to_relative_path(video_path),  # Store as relative path
        'created': datetime.now().isoformat(),
        'audio_file': _to_relative_path(audio_path),  # Store as relative path
        'settings': settings or {}
    }

    metadata[audio_stem].append(video_info)
    save_metadata(metadata)

    return video_info

def get_videos_for_audio(audio_path: Path) -> List[Dict]:
    """Get all videos associated with an audio file."""
    metadata = load_metadata()
    audio_stem = audio_path.stem
    if audio_stem not in metadata:
        return []

    videos = []
    for video_info in metadata[audio_stem]:
        # Convert relative path to absolute for checking existence
        video_path = _to_absolute_path(video_info['path'])
        if video_path.exists():
            # Return with absolute path for use in GUI
            result = video_info.copy()
            result['path'] = str(video_path)
            if 'audio_file' in video_info:
                result['audio_file'] = str(_to_absolute_path(video_info['audio_file']))
            videos.append(result)
        else:
            # Video file doesn't exist, remove from metadata
            metadata[audio_stem].remove(video_info)

    save_metadata(metadata)
    return videos

def get_all_videos() -> List[Dict]:
    """Get all videos from all audio files."""
    metadata = load_metadata()
    all_videos = []

    for audio_stem, videos in metadata.items():
        for video_info in videos:
            # Convert relative path to absolute for checking existence
            video_path = _to_absolute_path(video_info['path'])
            if video_path.exists():
                # Return with absolute path for use in GUI
                result = video_info.copy()
                result['path'] = str(video_path)
                if 'audio_file' in video_info:
                    result['audio_file'] = str(_to_absolute_path(video_info['audio_file']))
                all_videos.append(result)

    # Sort by creation date (newest first)
    all_videos.sort(key=lambda x: x.get('created', ''), reverse=True)
    return all_videos

def delete_video(video_info: Dict) -> bool:
    """Delete a video file and remove it from metadata."""
    try:
        # Convert relative path to absolute if needed
        video_path = _to_absolute_path(video_info['path'])
        if video_path.exists():
            video_path.unlink()

        metadata = load_metadata()
        # Get audio stem from relative path
        audio_file_rel = video_info.get('audio_file', '')
        audio_stem = Path(audio_file_rel).stem if audio_file_rel else ''

        if audio_stem in metadata:
            metadata[audio_stem] = [v for v in metadata[audio_stem] if v['id'] != video_info['id']]
            if not metadata[audio_stem]:
                del metadata[audio_stem]
            save_metadata(metadata)

        return True
    except Exception as e:
        print(f"Error deleting video: {e}")
        return False

def get_video_path(audio_stem: str, video_filename: str) -> Path:
    """Get the full path to a video file."""
    return VIDEOS_ROOT / audio_stem / video_filename

def reset_metadata():
    """Reset metadata.json to empty state (useful for cleaning up absolute paths)."""
    ensure_video_directories()
    with open(METADATA_FILE, 'w') as f:
        json.dump({}, f, indent=2)

