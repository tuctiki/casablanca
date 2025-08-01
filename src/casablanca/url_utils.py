
def extract_video_id(video_url):
    if "v=" in video_url:
        return video_url.split("v=")[1].split("&")[0]
    return None
