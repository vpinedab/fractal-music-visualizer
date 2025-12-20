"""
Video management system for storing and retrieving multiple videos per audio file.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

VIDEOS_ROOT = Path(__file__).resolve().parent / "assets" / "output" / "videos"
METADATA_FILE = VIDEOS_ROOT / "metadata.json"

def ensure_video_directories():
    """Ensure video storage directories exist."""
    VIDEOS_ROOT.mkdir(parents=True, exist_ok=True)
    if not METADATA_FILE.exists():
        with open(METADATA_FILE, 'w') as f:
            json.dump({}, f)

def load_metadata() -> Dict:
    """Load video metadata from JSON file."""
    ensure_video_directories()
    if not METADATA_FILE.exists():
        return {}
    try:
        with open(METADATA_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def save_metadata(metadata: Dict):
    """Save video metadata to JSON file."""
    ensure_video_directories()
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
    Returns the video info dict.
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
        'path': str(video_path),
        'created': datetime.now().isoformat(),
        'audio_file': str(audio_path),
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
        video_path = Path(video_info['path'])
        if video_path.exists():
            videos.append(video_info)
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
            video_path = Path(video_info['path'])
            if video_path.exists():
                all_videos.append(video_info)

    # Sort by creation date (newest first)
    all_videos.sort(key=lambda x: x.get('created', ''), reverse=True)
    return all_videos

def delete_video(video_info: Dict) -> bool:
    """Delete a video file and remove it from metadata."""
    try:
        video_path = Path(video_info['path'])
        if video_path.exists():
            video_path.unlink()

        metadata = load_metadata()
        audio_stem = Path(video_info['audio_file']).stem

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

