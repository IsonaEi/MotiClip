import os
import subprocess
import json
import numpy as np
import cv2
import av
from imageio_ffmpeg import get_ffmpeg_exe
from fractions import Fraction

# 定義允許的影片格式與最大檔案大小 (MB)
ALLOWED_FORMATS = ['.mp4', '.avi', '.mts', '.mov']
MAX_FILE_SIZE_MB = 3000  # 3GB

def check_video_file(file_path: str):
    """
    檢查影片檔案格式與大小是否符合要求。
    
    參數:
      file_path (str): 影片檔案的路徑

    回傳:
      tuple(bool, str): 第一個元素為檢查結果 (True: 通過, False: 不通過)
                         第二個元素為相關訊息
    """
    if not os.path.exists(file_path):
        return False, f"檔案不存在: {file_path}"
    
    # 取得檔案大小 (單位: MB)
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    _, ext = os.path.splitext(file_path)
    
    if ext.lower() not in ALLOWED_FORMATS:
        return False, f"不合法的檔案格式 '{ext}'. 允許格式: {', '.join(ALLOWED_FORMATS)}"
    
    if file_size_mb > MAX_FILE_SIZE_MB:
        return False, f"檔案過大 ({file_size_mb:.2f}MB)，最大允許大小為 {MAX_FILE_SIZE_MB}MB"
    
    return True, f"檔案檢查通過: {os.path.basename(file_path)} ({file_size_mb:.2f}MB)"

def extract_middle_frame(file_path: str, output_path: str):
    """
    從影片中擷取中間幀並儲存為圖片。
    
    參數:
      file_path (str): 影片檔案的路徑
      output_path (str): 擷取後的圖片儲存路徑 (例如 'frame.png')

    回傳:
      bool: 是否成功擷取與儲存中間幀 (True: 成功, False: 失敗)
    """
    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        print("無法開啟影片檔案。")
        return False
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        print("影片沒有取得有效幀數。")
        cap.release()
        return False

    mid_frame = total_frames // 2
    cap.set(cv2.CAP_PROP_POS_FRAMES, mid_frame)
    
    ret, frame = cap.read()
    if not ret:
        print("讀取中間幀失敗。")
        cap.release()
        return False
    
    success = cv2.imwrite(output_path, frame)
    cap.release()
    
    if success:
        return True
    else:
        print("儲存圖片失敗。")
        return False


import os
import subprocess
import numpy as np
from PIL import Image
from imageio_ffmpeg import get_ffmpeg_exe
import json

def get_video_metadata(video_path):
    """
    使用 FFmpeg ffprobe 取得影片 metadata，回傳字典格式：
    fps、total_frames、size (width, height)、duration。
    """
    command = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,avg_frame_rate,duration,nb_frames",
        "-of", "json", video_path
    ]
    
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if result.returncode != 0:
        raise ValueError("ffprobe error: " + result.stderr)
    
    # 解析 JSON 格式 metadata
    info = json.loads(result.stdout)
    if "streams" not in info or len(info["streams"]) == 0:
        raise ValueError("No video stream found in file")
    
    stream = info["streams"][0]
    width = int(stream.get("width", 0))
    height = int(stream.get("height", 0))
    
    # 解析 FPS
    avg_frame_rate = stream.get("avg_frame_rate", "0/0")
    if avg_frame_rate and avg_frame_rate != "0/0":
        num, den = avg_frame_rate.split('/')
        fps = float(num) / float(den) if float(den) != 0 else 30.0  # 預設 30 FPS 避免錯誤
    else:
        fps = 30.0

    duration = float(stream.get("duration", 0))
    total_frames = stream.get("nb_frames", None)
    if total_frames is not None:
        total_frames = int(total_frames)
    else:
        total_frames = int(duration * fps)

    return {
        "fps": fps,
        "nframes": total_frames,
        "size": (width, height),
        "duration": duration
    }


class ReadArray:
    """
    使用 FFmpeg 持續解碼影片，支援隨機存取並兼容 MTS、MP4、AVI 等格式。
    """
    def __init__(self, video_path):
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"File not found: {video_path}")
        
        self.video_path = video_path
        self.video_name = os.path.basename(video_path)

        # 取得影片 metadata，確保能解析 MTS
        metadata = get_video_metadata(video_path)
        self.fps = metadata["fps"]
        self.total_frames = metadata["nframes"]
        self.width, self.height = metadata["size"]
        self.duration = metadata["duration"]

        # 設定 FFmpeg 解碼相關參數
        self.frame_size = self.width * self.height * 3
        self.index = -1
        self.ffmpeg_exe = get_ffmpeg_exe()
        self._start_process(0)

        self.buffer = np.empty((self.height, self.width, 3), dtype=np.uint8)
        self.raw_buffer = memoryview(self.buffer)

    def _start_process(self, start_index):
        """
        透過 FFmpeg (-ss 快速定位) 啟動持續解碼。
        """
        timestamp = start_index / self.fps
        if hasattr(self, 'process'):
            try:
                self.process.stdout.close()
                self.process.kill()
            except Exception:
                pass
        command = [
            self.ffmpeg_exe,
            "-ss", str(timestamp),
            "-i", self.video_path,
            "-f", "image2pipe",
            "-pix_fmt", "rgb24",
            "-vf", "yadif",
            "-vcodec", "rawvideo",
            "-"
        ]
        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.index = start_index - 1

    def __len__(self):
        return self.total_frames

    def __getitem__(self, frame_index):
        if frame_index < 0 or frame_index >= self.total_frames:
            raise IndexError("Frame index out of range")

        fs = self.frame_size
        gap = frame_index - self.index - 1

        if gap < 0 or gap > 10:
            # 大幅跳躍或倒退，直接重啟FFmpeg程序定位
            self._start_process(frame_index)
        elif gap > 0:
            # 少量跳躍，直接在現有管道上快速跳過影格 (不分配臨時記憶體)
            for _ in range(gap):
                skipped = self.process.stdout.read(fs)
                if len(skipped) != fs:
                    raise ValueError("Skipping frame failed")
                self.index += 1

        # 統一使用 readinto，讀取到事先配置的 buffer
        read_bytes = self.process.stdout.readinto(self.raw_buffer)
        if read_bytes != fs:
            raise ValueError(f"Could not read frame {frame_index}")

        self.index += 1
        return self.buffer


    def __del__(self):
        try:
            self.process.stdout.close()
            self.process.kill()
        except Exception:
            pass


class WriteArray:
    def __init__(self, video_path, fps, crf=23, use_hw=True, Preset='p1'):
        self.output = av.open(video_path, 'w')

        if use_hw:
            self.stream = self.output.add_stream('h264_nvenc', rate=Fraction(fps).limit_denominator(), options={'preset': Preset})

        else:
            self.stream = self.output.add_stream('libx264', Fraction(fps).limit_denominator(), options={'preset': Preset})

        self.stream.options = {'crf': str(crf)}
        self.stream.pix_fmt = 'yuv420p'
        self.init = False
        self._closed = False

    def append(self, frame): #frame: ndarray, H, W, C
        if frame.ndim != 3 or frame.shape[2] != 3:
            raise ValueError("Expected frame with shape (H, W, 3)")

        if not self.init:
            self.stream.height, self.stream.width = frame.shape[:2]
            self.init = True
            
        frame = av.VideoFrame.from_ndarray(frame, format='rgb24')
        
        for packet in self.stream.encode(frame):
            self.output.mux(packet)
        
    def close(self):
        if self._closed:
            return
        for packet in self.stream.encode():
            self.output.mux(packet)
        self.output.close()
        self._closed = True

    def __del__(self):
        self.close()