import os
import subprocess


def convert_to_hls(input_path, output_dir, base_name="index"):
    """
    Convert video to HLS with different resolutions and bitrates using ffmpeg
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    profiles = [
        ("480p", "854:480", "800k", 800000),
        ("720p", "1280:720", "2000k", 2000000),
        ("1080p", "1920:1080", "4000k", 4000000),
    ]

    for pname, scale, vb, _ in profiles:
        variant_m3u8 = f"{base_name}_{pname}.m3u8"
        variant_path = os.path.join(output_dir, variant_m3u8)

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_path,
            "-vf",
            f"scale={scale}",
            "-c:v",
            "libx264",
            "-b:v",
            vb,
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-hls_time",
            "10",
            "-hls_list_size",
            "0",
            "-f",
            "hls",
            variant_path,
        ]

        subprocess.run(cmd, check=True)
    master_path = os.path.join(output_dir, f"{base_name}.m3u8")
    with open(master_path, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n\n")
        for pname, scale, _, bandwidth in profiles:
            f.write(f"#EXT-X-STREAM-INF:BANDWIDTH={bandwidth},RESOLUTION={scale}\n")
            f.write(f"{base_name}_{pname}.m3u8\n\n")

    return master_path
