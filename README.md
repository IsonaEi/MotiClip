# This README was written by ChatGPT4o.

# MotiClip：用於創建微調動物視覺基礎模型的訓練資料集  
# MotiClip: Creating Training Dataset for Finetuning Animal Visual Foundation Models

---

## 簡介 / Overview

### 繁體中文 (Traditional Chinese)
MotiClip 是一個開源平台，旨在自動收集並處理小鼠行為影片資料，最終生成用於微調動物視覺基礎模型的高品質訓練資料集。  
本系統結合了以下技術與模組：
- **使用者互動前端：**  
  基於 Gradio 的直覺化介面，使用者可以上傳影片、輸入實驗資訊，並利用畫布工具進行 arena 標註。
- **GPU 加速影片處理管線：**  
  利用 NVIDIA DALI 進行影片解碼，並在 GPU 上實現裁切、透視校正、運動檢測（TensorRT 加速光流計算）與轉碼（例如 PyNvCodec），確保處理效率與效能。
- **自動化訓練資料生成：**  
  系統會自動篩選出有效運動片段，並將相關影片片段及對應 metadata 匯出，作為訓練資料集，供後續微調動物視覺基礎模型之用。

### English
MotiClip is an open-source platform designed to automatically collect and process mouse behavior video data to ultimately generate a high-quality training dataset for finetuning animal visual foundation models.  
The system integrates the following technologies and modules:
- **Interactive Frontend:**  
  An intuitive Gradio-based interface that allows users to upload videos, input experimental details, and annotate regions of interest (arenas) using an interactive canvas.
- **GPU-Accelerated Video Processing Pipeline:**  
  Leverages NVIDIA DALI for video decoding and performs cropping, perspective correction, motion detection (using TensorRT-accelerated optical flow), and transcoding (e.g., with PyNvCodec) on the GPU to ensure high efficiency and performance.
- **Automated Training Data Generation:**  
  The system automatically extracts significant motion segments and exports the corresponding video clips and metadata as a training dataset for finetuning animal visual foundation models.

---

## 系統架構 / System Architecture

### 繁體中文 (Traditional Chinese)
整個系統主要包含以下模組：
- **前端介面：**  
  - 使用 Gradio 建構的 UI，負責收集實驗資訊與影片上傳。  
  - 提供互動式 arena 標註工具，讓使用者對影片關鍵區域進行標記。
- **影片處理管線：**  
  - **影片 I/O 與 GPU 解碼：** 使用 NVIDIA DALI 在 GPU 上快速解碼影片。  
  - **Arena 裁切與透視校正：** 根據 JSON metadata 中定義的座標，在 GPU 上進行多邊形裁切。  
  - **運動檢測與片段擷取：** 利用 TensorRT 加速的光流計算篩選出有效運動區段。  
  - **最終影片轉碼：** 使用 GPU 編碼工具（如 PyNvCodec）統一轉碼為 H.264 (mp4) 格式。
- **資料輸出：**  
  自動產生包含影片 clip 與 metadata 的訓練資料集，供後續模型微調使用。

### English
The system comprises the following key modules:
- **Frontend Interface:**  
  - A Gradio-based UI for collecting experimental details and video uploads.  
  - Provides an interactive canvas for annotating regions of interest (arenas) on videos.
- **Video Processing Pipeline:**  
  - **Video I/O and GPU Decoding:** Uses NVIDIA DALI to rapidly decode videos on the GPU.  
  - **Arena Cropping and Perspective Correction:** Performs polygonal cropping on the GPU based on coordinates defined in JSON metadata.  
  - **Motion Detection and Clip Extraction:** Utilizes TensorRT-accelerated optical flow to filter out significant motion segments.  
  - **Final Video Transcoding:** Employs GPU encoding tools (e.g., PyNvCodec) to uniformly transcode videos to H.264 (mp4) format.
- **Data Output:**  
  Automatically generates a training dataset comprising video clips and associated metadata for finetuning animal visual foundation models.

---

## 功能特點 / Features

### 繁體中文 (Traditional Chinese)
- **自動化數據收集：**  
  高效收集並處理大量小鼠行為影片，減少手動篩選工作量。
- **GPU 加速處理：**  
  全流程在 GPU 上執行，從解碼到轉碼均確保高效能與低延遲。
- **互動式前端介面：**  
  直覺化操作，方便使用者輸入實驗資訊、上傳影片及進行 arena 標註。
- **高品質訓練資料集：**  
  自動生成標註完整的影片片段與 metadata，為動物視覺基礎模型微調提供理想數據。

### English
- **Automated Data Collection:**  
  Efficiently collects and processes large volumes of mouse behavior videos, reducing manual effort.
- **GPU-Accelerated Processing:**  
  The entire pipeline runs on the GPU, ensuring high performance and low latency from decoding to transcoding.
- **Interactive Frontend Interface:**  
  Provides an intuitive user experience for entering experimental details, uploading videos, and annotating arenas.
- **High-Quality Training Dataset:**  
  Automatically generates well-annotated video clips and metadata, serving as an ideal dataset for finetuning animal visual foundation models.
