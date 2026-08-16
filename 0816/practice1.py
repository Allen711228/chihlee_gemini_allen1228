# 載入 Google Generative AI 套件與環境變數工具
from google import genai
from dotenv import load_dotenv

# 從 .env 檔案讀取環境變數（例如 GOOGLE_API_KEY）
load_dotenv()

# 建立 Gemini API 客戶端，會自動從環境變數取得 API 金鑰
client = genai.Client()

# 使用指定模型建立一次互動，並傳入提示問題
interaction = client.interactions.create(
    model="gemini-3.5-flash",
    input="天空為什麼是藍的"
)

# 印出模型回傳的文字回應
print(interaction.output_text)
