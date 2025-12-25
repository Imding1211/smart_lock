# Smart Lock 電子鎖 AI 客服

本專案是一個 電子鎖 AI 客服系統，整合 LINE 官方帳號、FastAPI 與資料庫，可用於回覆常見問題、產品操作說明與故障排除。

---

## 專案功能  
	•	🤖 LINE AI 客服自動回覆  
	•	🔎 支援產品型號 / 問題分類查詢  
	•	🗂️ 使用資料庫管理對話與知識內容  
	•	☁️ 整合 Google Drive API（文件來源）  
	•	⚡ 使用 FastAPI + Uvicorn 提供 API 服務  

---

## 環境需求  
	•	Python 3.9+（建議 3.10 以上）  
	•	Google Cloud Platform 帳號  
	•	LINE 官方帳號（Messaging API 已啟用）  

---

## 啟用 Google Drive API  
	1.	前往 Google Cloud Console  
	2.	建立或選擇專案  
	3.	啟用 Google Drive API  
	4.	建立 Service Account / OAuth 憑證  
	5.	下載憑證檔案（JSON）並妥善保存  

---

## 設定環境變數

在專案根目錄建立 .env 檔案，加入以下內容：
```
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
LINE_CHANNEL_SECRET=your_line_channel_secret
```
---

## 建立虛擬環境並安裝套件
```
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

pip install -r requirements.txt
```

---

## 初始化資料庫
```
python message_db.py
```
成功後將會建立客服對話與知識庫所需的資料表。

---

## 啟動 FastAPI（LINE Webhook）
```
uvicorn line_api:app --host 0.0.0.0 --port 8000
```
啟動後即可將 API URL 設定為 LINE Webhook 端點。

---

## 專案結構
```
smart_lock/
├── line_api.py        # LINE Webhook API
├── message_db.py      # 資料庫初始化
├── requirements.txt   # Python 套件清單
├── .env               # 環境變數（不提交）
└── README.md
```
