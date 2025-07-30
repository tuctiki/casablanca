import os
import shutil
import logging

def move_to_obsidian(video_title, video_date, expert_summary_path, market_summary_path, obsidian_path):
    if not obsidian_path:
        logging.warning("OBSIDIAN_VAULT_PATH not set. Skipping move to Obsidian.")
        return

    sanitized_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    date_folder = video_date
    obsidian_dest_folder = os.path.expanduser(os.path.join(obsidian_path, date_folder, sanitized_title))
    
    try:
        os.makedirs(obsidian_dest_folder, exist_ok=True)

        shutil.move(expert_summary_path, os.path.join(obsidian_dest_folder, "expert_summary.md"))
        shutil.move(market_summary_path, os.path.join(obsidian_dest_folder, "market_summary.md"))
        logging.info(f"Moved summary files to Obsidian vault: {obsidian_dest_folder}")
    except Exception as e:
        logging.error(f"Error moving summary files: {e}")