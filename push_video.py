import cv2
import subprocess
import argparse
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import time
import ffmpeg


class CVCounter():
    def __init__(self, args):
        self._cnt = 0
        self.args = args

    def get_cnt(self):
        return self._cnt
      
    def set_cnt(self, new_cnt):
        self._cnt = new_cnt

    def create_img(self):
        def create_image_helper(size, bgColor, message, font, fontColor):
            W, H = size
            image = Image.new('RGB', size, bgColor)
            draw = ImageDraw.Draw(image)
            _, _, w, h = draw.textbbox((0, 0), message, font=font)
            draw.text(((W-w)/2, (H-h)/2), message, font=font, fill=fontColor)
            return image

        my_font = ImageFont.truetype('Roboto-Regular.ttf', self.args.fontsize)
        my_msg = str(self._cnt)
        my_img = create_image_helper((self.args.img_size[0], self.args.img_size[1]), '#F0F8FF', my_msg, my_font, 'black')
        
        my_img = np.array(my_img)
        frame_img = cv2.cvtColor(my_img, cv2.COLOR_RGB2BGR)
        return frame_img

def time_passed(old_time, sec=1):
    return time.time() - old_time >= sec

def start_streaming(args, fps):
    process = (
        ffmpeg
        .input('pipe:', format='rawvideo',codec="rawvideo", pix_fmt='bgr24', s=f"{args.img_size[0]}x{args.img_size[1]}",)
        .output(
            args.rtmp_mrl,
            #codec = "copy", # use same codecs of the original video
            listen=1, # enables HTTP server
            pix_fmt="yuv420p",
            preset="ultrafast",
            f='flv'
        )
        .overwrite_output()
        .run_async(pipe_stdin=True)
    )
    return process

def push_video_counter(args):
    cv_counter = CVCounter(args)
    start_time = time.time()
    old_time = time.time()

    command = ['ffmpeg',
            #    '-re',
               '-f', 'rawvideo',
            '-y',
               '-vcodec', 'rawvideo',
               '-pix_fmt', 'bgr24',
               '-s', f"{args.img_size[0]}x{args.img_size[1]}",
               '-r', '1',
               '-i', '-',
               '-c:v', 'libx264',
               '-pix_fmt', 'yuv420p',
               '-preset', 'ultrafast',
               '-flvflags', 'no_duration_filesize',
               '-f', 'flv',
               args.rtmp_mrl]
    p = subprocess.Popen(command, stdin=subprocess.PIPE, shell=False)

    pipe = (
        ffmpeg
            .input('pipe:', r='0.2', stream_loop='1')
            # .input('pipe:', r='3', f='image2')
            # .output(args.rtmp_mrl, vcodec='libx264', pix_fmt='yuv420p', preset='veryfast', r='20', g='50', video_bitrate='1.4M', maxrate='2M', bufsize='2M', segment_time='6', format='flv') # s?
            .output(args.rtmp_mrl, r='20', format='flv')
            .run_async(pipe_stdin=True)
    )

    while (not time_passed(start_time, sec=args.tot_sec)):
        img = cv_counter.create_img()
        print(cv_counter.get_cnt())
        p.stdin.write(img.tobytes())

        # cv2.imshow('Push Frame', img)
        # if cv2.waitKey(int(round(1000/1))) == 27:
        #     break
        # check time
        # while (not time_passed(old_time, sec=1)):
        #     time.sleep(0.2)
        
        # if (time_passed(old_time, sec=1)):
        #     # update old_time in the inner while loop
        #     old_time = time.time()
        time.sleep(1)
        # update cv_counter cnt
        cv_counter.set_cnt(cv_counter.get_cnt() + 1)

    time.sleep(20)
    p.stdin.close()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--video_source', type=str, default='rt_counter') # real-time counter
    parser.add_argument('--rtmp_mrl', type=str, default='rtmp://127.0.0.1:1935/live/stream')
    parser.add_argument('--tot_sec', type=int, default=180) # total seconds
    parser.add_argument('--img_size', type=int, nargs="*", default=[300, 200])
    parser.add_argument('--fontsize', type=int, default=24)


    args = parser.parse_args()

    if args.video_source == 'rt_counter':
        push_video_counter(args)


# ffmpeg -re -i test_youtube.mp4 -c:v copy -c:a aac -ar 44100 -ac 1 -f flv rtmp://127.0.0.1:1935/live/stream