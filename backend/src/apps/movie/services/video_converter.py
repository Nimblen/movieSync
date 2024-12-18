import subprocess
import os

def convert_to_hls(input_file_path, output_dir):
    """
    Конвертирует видео в HLS формат с помощью FFmpeg.
    :param input_file_path: Путь к исходному видео файлу
    :param output_dir: Директория для хранения HLS файлов
    :return: Ссылка на HLS m3u8 файл
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    hls_output_path = os.path.join(output_dir, 'index.m3u8')
    
    command = [
        'ffmpeg',
        '-i', input_file_path,             
        '-codec:', 'copy',                 
        '-start_number', '0',
        '-hls_time', '10',
        '-hls_list_size', '0',
        '-f', 'hls',
        hls_output_path
    ]
    subprocess.run(command, check=True)
    return hls_output_path
