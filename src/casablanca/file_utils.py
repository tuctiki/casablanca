import os
import shutil
import logging

def sanitize_title(title):
    return "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()

def generate_output_paths(video_id):
    output_dir = os.path.join("outputs", video_id)
    expert_summary_path = os.path.join(output_dir, "expert_summary.md")
    market_summary_path = os.path.join(output_dir, "market_summary.md")
    return output_dir, expert_summary_path, market_summary_path

def move_to_obsidian(video_title, video_date, expert_summary_path, market_summary_path, obsidian_path):
    if not obsidian_path:
        logging.warning("OBSIDIAN_VAULT_PATH not set. Skipping move to Obsidian.")
        return

    sanitized_title = sanitize_title(video_title)
    date_folder = video_date
    obsidian_dest_folder = os.path.expanduser(os.path.join(obsidian_path, date_folder, sanitized_title))
    
    try:
        os.makedirs(obsidian_dest_folder, exist_ok=True)

        shutil.move(expert_summary_path, os.path.join(obsidian_dest_folder, "expert_summary.md"))
        shutil.move(market_summary_path, os.path.join(obsidian_dest_folder, "market_summary.md"))
        logging.info(f"Moved summary files to Obsidian vault: {obsidian_dest_folder}")
    except Exception as e:
        logging.error(f"Error moving summary files: {e}")