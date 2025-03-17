import os
import cv2

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

# 測試程式碼（可根據需要移除或註解）
if __name__ == "__main__":
    test_video = "path/to/your/video.mp4"  # 請修改成你本地的影片路徑
    output_image = "frame.png"
    
    valid, message = check_video_file(test_video)
    print(message)
    
    if valid:
        if extract_middle_frame(test_video, output_image):
            print(f"成功擷取中間幀，圖片儲存至 {output_image}")
        else:
            print("擷取中間幀失敗。")
