import ffmpeg
import cv2
import subprocess

video_format = "flv"
server_url = "rtmp://127.0.0.1:1935/live/stream"




def start_streaming(width, height,fps):
    process = (
        ffmpeg
        .input('pipe:', format='rawvideo',codec="rawvideo", pix_fmt='bgr24', s='{}x{}'.format(width, height))
        .output(
            server_url,
            #codec = "copy", # use same codecs of the original video
            listen=1, # enables HTTP server
            pix_fmt="yuv420p",
            preset="ultrafast",
            f=video_format
        )
        .overwrite_output()
        .run_async(pipe_stdin=True)
    )
    return process

def init_cap():
    cap = cv2.VideoCapture('test_youtube.mp4')
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    return cap, width, height

def run():
    cap, width, height = init_cap()
    fps = cap.get(cv2.CAP_PROP_FPS)
    streaming_process = start_streaming(width, height,fps)
    while True:
        ret, frame = cap.read()
        if ret:
            streaming_process.stdin.write(frame.tobytes())
        else:
            break
    streaming_process.stdin.close()
    streaming_process.wait()
    cap.release()

if __name__ == "__main__":
    run()