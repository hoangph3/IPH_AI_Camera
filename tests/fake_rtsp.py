import subprocess
import multiprocessing

def run_ffmpeg_process(input_file, output_url):
    command = [
        'ffmpeg',
        '-re',
        '-i', input_file,
        
        '-preset', 'ultrafast',
        '-tune', 'zerolatency',
        '-strict', 'experimental',
        '-f', 'rtsp', output_url
    ]
    subprocess.run(command)

if __name__ == '__main__':
    # Specify the input file and RTSP base URL
    input_file = '/home/dev-vm/Desktop/IPHCam/12.mp4'
    rtsp_base_url = 'rtsp://192.168.0.149:8554/stream'

    # Number of RTSP streams to run
    num_streams = 21

    # Create a list of RTSP URLs for each stream
    rtsp_urls = [f"{rtsp_base_url}_{i}" for i in range(num_streams)]

    # Create a Pool of processes to run FFmpeg for each RTSP stream
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        pool.starmap(run_ffmpeg_process, [(input_file, rtsp_url) for rtsp_url in rtsp_urls])
