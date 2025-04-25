import tkinter as tk
from tkinter import messagebox
import random
import sqlite3
from datetime import datetime, timedelta
import logging
import json
import os
import re
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, GoogleAPIError
import time
from gtts import gTTS
import pygame
from prompt import generate_noun_prompt

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Đọc API keys từ config.json
CONFIG_FILE = "config.json"

try:
    if not os.path.exists(CONFIG_FILE):
        logger.error(f"File {CONFIG_FILE} không tồn tại")
        raise FileNotFoundError(f"File {CONFIG_FILE} không tồn tại")
    
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
        API_KEYS = config.get('api_keys', [])
    
    if len(API_KEYS) < 2:
        logger.error("Cần ít nhất 2 API keys trong config.json")
        raise ValueError("Cần ít nhất 2 API keys trong config.json")
    
    logger.info(f"Đã tải {len(API_KEYS)} API keys từ config.json")
except Exception as e:
    logger.error(f"Lỗi khi đọc file config.json: {str(e)}")
    raise

# Biến toàn cục
MAX_ATTEMPTS = len(API_KEYS)
MAX_API_RETRIES = 5  # Số lần thử lại nếu danh từ sai
PRIMARY_KEY = random.choice(API_KEYS)
VERIFY_KEY = random.choice([key for key in API_KEYS if key != PRIMARY_KEY])
logger.info(f"Khởi tạo: primary_key={PRIMARY_KEY[:5]}..., verify_key={VERIFY_KEY[:5]}...")

# Quy tắc danh từ
suffix_rules = {
    "der": [
        {"suffix": "er", "reason": "Hậu tố -er (thường chỉ người hoặc vật).", "tip": "Mẹo: Đàn ông mạnh mẽ, chạy xe khắp hướng!", "example": "Lehrer"},
        {"suffix": "or", "reason": "Hậu tố -or (người làm nghề).", "tip": "Mẹo: Đàn ông mạnh mẽ, chạy xe khắp hướng!", "example": "Doktor"},
        {"suffix": "ling", "reason": "Hậu tố -ling (chỉ người trẻ).", "tip": "Mẹo: Đàn ông mạnh mẽ, chạy xe khắp hướng!", "example": "Jüngling"},
        {"suffix": "ismus", "reason": "Hậu tố -ismus (chủ nghĩa).", "tip": "Mẹo: Đàn ông mạnh mẽ, chạy xe khắp hướng!", "example": "Kapitalismus"},
        {"suffix": "ant", "reason": "Hậu tố -ant (người hành động).", "tip": "Mẹo: Đàn ông mạnh mẽ, chạy xe khắp hướng!", "example": "Musikant"},
        {"suffix": "ent", "reason": "Hậu tố -ent (người học).", "tip": "Mẹo: Đàn ông mạnh mẽ, chạy xe khắp hướng!", "example": "Student"},
        {"suffix": "ist", "reason": "Hậu tố -ist (người theo nghề).", "tip": "Mẹo: Đàn ông mạnh mẽ, chạy xe khắp hướng!", "example": "Pianist"},
        {"suffix": "eur", "reason": "Hậu tố -eur (người làm nghề).", "tip": "Mẹo: Đàn ông mạnh mẽ, chạy xe khắp hướng!", "example": "Amateur"},
        {"suffix": "är", "reason": "Hậu tố -är (người làm nghề).", "tip": "Mẹo: Đàn ông mạnh mẽ, chạy xe khắp hướng!", "example": "Sekretär"},
        {"suffix": "at", "reason": "Hậu tố -at (người làm nghề).", "tip": "Mẹo: Đàn ông mạnh mẽ, chạy xe khắp hướng!", "example": "Advokat"},
        {"suffix": "and", "reason": "Hậu tố -and (người học).", "tip": "Mẹo: Đàn ông mạnh mẽ, chạy xe khắp hướng!", "example": "Doktorand"},
        {"suffix": "tag", "reason": "Hậu tố -tag (chỉ ngày trong tuần).", "tip": "Mẹo: Đàn ông mạnh mẽ, chạy xe khắp hướng!", "example": "Montag"}
    ],
    "die": [
        {"suffix": "e", "reason": "Hậu tố -e (thường chỉ vật hoặc khái niệm).", "tip": "Mẹo: Phụ nữ dịu dàng, yêu hoa và số!", "example": "Tasche"},
        {"suffix": "ung", "reason": "Hậu tố -ung (hành động, kết quả).", "tip": "Mẹo: Phụ nữ dịu dàng, yêu hoa và số!", "example": "Zeitung"},
        {"suffix": "heit", "reason": "Hậu tố -heit (tính chất).", "tip": "Mẹo: Phụ nữ dịu dàng, yêu hoa và số!", "example": "Freiheit"},
        {"suffix": "keit", "reason": "Hậu tố -keit (tính chất).", "tip": "Mẹo: Phụ nữ dịu dàng, yêu hoa và số!", "example": "Möglichkeit"},
        {"suffix": "schaft", "reason": "Hậu tố -schaft (nhóm, tập thể).", "tip": "Mẹo: Phụ nữ dịu dàng, yêu hoa và số!", "example": "Freundschaft"},
        {"suffix": "ei", "reason": "Hậu tố -ei (cơ sở, tổ chức).", "tip": "Mẹo: Phụ nữ dịu dàng, yêu hoa và số!", "example": "Bäckerei"},
        {"suffix": "ie", "reason": "Hậu tố -ie (trừu tượng).", "tip": "Mẹo: Phụ nữ dịu dàng, yêu hoa và số!", "example": "Philosophie"},
        {"suffix": "in", "reason": "Hậu tố -in (phụ nữ làm nghề).", "tip": "Mẹo: Phụ nữ dịu dàng, yêu hoa và số!", "example": "Lehrerin"},
        {"suffix": "ion", "reason": "Hậu tố -ion (hành động, kết quả).", "tip": "Mẹo: Phụ nữ dịu dàng, yêu hoa và số!", "example": "Nation"},
        {"suffix": "tion", "reason": "Hậu tố -tion (hành động).", "tip": "Mẹo: Phụ nữ dịu dàng, yêu hoa và số!", "example": "Information"},
        {"suffix": "ät", "reason": "Hậu tố -ät (trừu tượng).", "tip": "Mẹo: Phụ nữ dịu dàng, yêu hoa và số!", "example": "Qualität"},
        {"suffix": "ur", "reason": "Hậu tố -ur (kết quả).", "tip": "Mẹo: Phụ nữ dịu dàng, yêu hoa và số!", "example": "Kultur"},
        {"suffix": "ik", "reason": "Hậu tố -ik (khoa học, nghệ thuật).", "tip": "Mẹo: Phụ nữ dịu dàng, yêu hoa và số!", "example": "Musik"},
        {"suffix": "anz", "reason": "Hậu tố -anz (trừu tượng).", "tip": "Mẹo: Phụ nữ dịu dàng, yêu hoa và số!", "example": "Tanz"},
        {"suffix": "enz", "reason": "Hậu tố -enz (trừu tượng).", "tip": "Mẹo: Phụ nữ dịu dàng, yêu hoa và số!", "example": "Konferenz"}
    ],
    "das": [
        {"suffix": "chen", "reason": "Hậu tố -chen (vật nhỏ).", "tip": "Mẹo: Trẻ em ngây thơ, thích màu và chữ!", "example": "Mädchen"},
        {"suffix": "lein", "reason": "Hậu tố -lein (vật nhỏ).", "tip": "Mẹo: Trẻ em ngây thơ, thích màu và chữ!", "example": "Fräulein"},
        {"suffix": "ment", "reason": "Hậu tố -ment (công cụ).", "tip": "Mẹo: Trẻ em ngây thơ, thích màu và chữ!", "example": "Instrument"},
        {"suffix": "um", "reason": "Hậu tố -um (trừu tượng, khoa học).", "tip": "Mẹo: Trẻ em ngây thơ, thích màu và chữ!", "example": "Museum"},
        {"suffix": "ma", "reason": "Hậu tố -ma (trừu tượng).", "tip": "Mẹo: Trẻ em ngây thơ, thích màu và chữ!", "example": "Thema"},
        {"suffix": "tum", "reason": "Hậu tố -tum (tập thể).", "tip": "Mẹo: Trẻ em ngây thơ, thích màu và chữ!", "example": "Christentum"},
        {"suffix": "nis", "reason": "Hậu tố -nis (kết quả).", "tip": "Mẹo: Trẻ em ngây thơ, thích màu và chữ!", "example": "Ergebnis"},
        {"suffix": "tel", "reason": "Hậu tố -tel (phân số).", "tip": "Mẹo: Trẻ em ngây thơ, thích màu và chữ!", "example": "Viertel"},
        {"suffix": "ett", "reason": "Hậu tố -ett (vật nhỏ).", "tip": "Mẹo: Trẻ em ngây thơ, thích màu và chữ!", "example": "Ballett"},
        {"suffix": "o", "reason": "Hậu tố -o (vật thể).", "tip": "Mẹo: Trẻ em ngây thơ, thích màu và chữ!", "example": "Auto"},
        {"suffix": "al", "reason": "Hậu tố -al (trừu tượng).", "tip": "Mẹo: Trẻ em ngây thơ, thích màu và chữ!", "example": "Signal"},
        {"suffix": "ar", "reason": "Hậu tố -ar (vật thể).", "tip": "Mẹo: Trẻ em ngây thơ, thích màu và chữ!", "example": "Dollar"},
        {"suffix": "ier", "reason": "Hậu tố -ier (vật thể).", "tip": "Mẹo: Trẻ em ngây thơ, thích màu và chữ!", "example": "Papier"}
    ]
}

semantic_rules = {
    "der": [
        {"category": "Nam giới", "reason": "Chỉ nam giới.", "tip": "Mẹo: Đàn ông mạnh mẽ, chạy xe khắp hướng!", "example": "Mann"},
        {"category": "Tháng", "reason": "Tháng.", "tip": "Mẹo: Đàn ông mạnh mẽ, chạy xe khắp hướng!", "example": "Januar"},
        {"category": "Mùa", "reason": "Mùa.", "tip": "Mẹo: Đàn ông mạnh mẽ, chạy xe khắp hướng!", "example": "Sommer"},
        {"category": "Hướng", "reason": "Hướng.", "tip": "Mẹo: Đàn ông mạnh mẽ, chạy xe khắp hướng!", "example": "Norden"},
        {"category": "Xe cộ", "reason": "Xe cộ.", "tip": "Mẹo: Đàn ông mạnh mẽ, chạy xe khắp hướng!", "example": "Wagen"},
        {"category": "Đá quý", "reason": "Đá quý.", "tip": "Mẹo: Đàn ông mạnh mẽ, chạy xe khắp hướng!", "example": "Diamant"},
        {"category": "Hiện tượng thời tiết", "reason": "Hiện tượng thời tiết.", "tip": "Mẹo: Đàn ông mạnh mẽ, chạy xe khắp hướng!", "example": "Regen"}
    ],
    "die": [
        {"category": "Phụ nữ", "reason": "Chỉ phụ nữ.", "tip": "Mẹo: Phụ nữ dịu dàng, yêu hoa và số!", "example": "Frau"},
        {"category": "Cây/Hoa", "reason": "Cây hoặc hoa.", "tip": "Mẹo: Phụ nữ dịu dàng, yêu hoa và số!", "example": "Rose"},
        {"category": "Số đếm", "reason": "Số đếm.", "tip": "Mẹo: Phụ nữ dịu dàng, yêu hoa và số!", "example": "Zwei"},
        {"category": "Thực phẩm", "reason": "Thực phẩm phổ biến.", "tip": "Mẹo: Phụ nữ dịu dàng, yêu hoa và số!", "example": "Suppe"},
        {"category": "Đồ vật", "reason": "Đồ vật hàng ngày.", "tip": "Mẹo: Phụ nữ dịu dàng, yêu hoa và số!", "example": "Tür"},
        {"category": "Tàu thuyền", "reason": "Tàu thuyền.", "tip": "Mẹo: Phụ nữ dịu dàng, yêu hoa và số!", "example": "Yacht"},
        {"category": "Côn trùng", "reason": "Côn trùng.", "tip": "Mẹo: Phụ nữ dịu dàng, yêu hoa và số!", "example": "Biene"}
    ],
    "das": [
        {"category": "Trẻ em", "reason": "Trẻ em.", "tip": "Mẹo: Trẻ em ngây thơ, thích màu và chữ!", "example": "Kind"},
        {"category": "Màu sắc", "reason": "Màu sắc.", "tip": "Mẹo: Trẻ em ngây thơ, thích màu và chữ!", "example": "Blau"},
        {"category": "Kim loại", "reason": "Kim loại.", "tip": "Mẹo: Trẻ em ngây thơ, thích màu và chữ!", "example": "Gold"},
        {"category": "Chữ cái", "reason": "Chữ cái.", "tip": "Mẹo: Trẻ em ngây thơ, thích màu và chữ!", "example": "A"},
        {"category": "Đồ vật trẻ em", "reason": "Đồ vật hàng ngày liên quan đến trẻ em.", "tip": "Mẹo: Trẻ em ngây thơ, thích màu và chữ!", "example": "Buch"},
        {"category": "Động vật trẻ", "reason": "Động vật trẻ.", "tip": "Mẹo: Trẻ em ngây thơ, thích màu và chữ!", "example": "Kätzchen"},
        {"category": "Tòa nhà", "reason": "Tòa nhà.", "tip": "Mẹo: Trẻ em ngây thơ, thích màu và chữ!", "example": "Schloss"}
    ]
}

# Khởi tạo cơ sở dữ liệu
def init_db():
    conn = sqlite3.connect('wrong_answers.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS wrong_answers
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  noun TEXT,
                  correct_article TEXT,
                  user_answer TEXT,
                  reason TEXT,
                  tip TEXT,
                  meaning TEXT,
                  timestamp DATETIME,
                  UNIQUE(noun, correct_article))''')
    conn.commit()
    conn.close()

# Lưu câu trả lời sai
def save_wrong_answer(noun, correct_article, user_answer, reason, tip, meaning):
    conn = sqlite3.connect('wrong_answers.db')
    c = conn.cursor()
    try:
        c.execute('''INSERT OR REPLACE INTO wrong_answers (noun, correct_article, user_answer, reason, tip, meaning, timestamp)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (noun, correct_article, user_answer, reason, tip, meaning, datetime.now()))
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Lỗi lưu câu trả lời sai: {e}")
    finally:
        conn.close()

# Xóa câu trả lời đúng
def remove_correct_answer(noun, correct_article):
    conn = sqlite3.connect('wrong_answers.db')
    c = conn.cursor()
    try:
        c.execute('''DELETE FROM wrong_answers WHERE noun = ? AND correct_article = ?''',
                  (noun, correct_article))
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Lỗi xóa câu trả lời đúng: {e}")
    finally:
        conn.close()

# Lấy câu hỏi ôn tập
def get_review_questions():
    conn = sqlite3.connect('wrong_answers.db')
    c = conn.cursor()
    review_time = datetime.now() - timedelta(days=1)
    c.execute('''SELECT noun, correct_article, reason, tip, meaning FROM wrong_answers
                 WHERE timestamp <= ?''', (review_time,))
    questions = c.fetchall()
    conn.close()
    return questions

# Sửa JSON sai cú pháp
def fix_json(json_str):
    json_str = json_str.strip()
    json_str = re.sub(r'```json\s*|\s*```', '', json_str)
    
    start_idx = json_str.find('{')
    end_idx = json_str.rfind('}')
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        json_str = json_str[start_idx:end_idx + 1]
    else:
        logger.warning("Không tìm thấy cặp {} hợp lệ trong JSON")
        return None
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON gốc không hợp lệ: {e}. Thử sửa...")
    
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r'(\w+)(?=\s*:)', r'"\1"', json_str)
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"Không thể sửa JSON: {e}. Chuỗi JSON: {json_str}")
        return None

# Thử gọi API lần đầu
def try_with_different_key(prompt, current_key=PRIMARY_KEY, excluded_key=VERIFY_KEY):
    global PRIMARY_KEY
    attempts = 0
    available_keys = [key for key in API_KEYS if key != excluded_key]

    while attempts < MAX_ATTEMPTS and available_keys:
        selected_key = current_key if attempts == 0 else random.choice(available_keys)
        logger.info(f"Thử API key (lần đầu): {selected_key[:5]}...")
        genai.configure(api_key=selected_key)
        model = genai.GenerativeModel("gemini-2.0-flash-001")

        try:
            response = model.generate_content(prompt)
            if not hasattr(response, 'text'):
                logger.error("Phản hồi Gemini không có thuộc tính text")
                raise ValueError("Phản hồi Gemini không hợp lệ")
            response_text = response.text.strip()
            json_data = fix_json(response_text)
            if json_data is None:
                logger.warning(f"Phản hồi không phải JSON hợp lệ, thử key khác")
                raise ValueError("Phản hồi không phải JSON hợp lệ")
            PRIMARY_KEY = selected_key  # Cập nhật key nếu thành công
            return response_text
        except GoogleAPIError as e:
            if "429" in str(e):  # Rate limit error
                logger.warning(f"Rate limit với key {selected_key[:5]}..., thử key khác")
                available_keys.remove(selected_key)
                attempts += 1
                time.sleep(random.uniform(0.5, 1.0))
                continue
            logger.warning(f"API key {selected_key[:5]}... thất bại: {str(e)}, thử key khác")
            available_keys.remove(selected_key)
            attempts += 1
            time.sleep(random.uniform(0.1, 0.5))
        except (ValueError, Exception) as e:
            logger.warning(f"API key {selected_key[:5]}... thất bại: {str(e)}, thử key khác")
            available_keys.remove(selected_key)
            attempts += 1
            time.sleep(random.uniform(0.1, 0.5))

    logger.error("Tất cả API key đều không hoạt động")
    raise ResourceExhausted("Tất cả API key đều không hoạt động")

# Thử gọi API xác nhận
def verify_with_different_key(prompt, current_key=VERIFY_KEY, excluded_key=PRIMARY_KEY):
    global VERIFY_KEY
    attempts = 0
    available_keys = [key for key in API_KEYS if key != excluded_key]

    while attempts < MAX_ATTEMPTS and available_keys:
        selected_key = current_key if attempts == 0 else random.choice(available_keys)
        logger.info(f"Thử API key (xác nhận): {selected_key[:5]}...")
        genai.configure(api_key=selected_key)
        model = genai.GenerativeModel("gemini-2.0-flash-001")

        try:
            response = model.generate_content(prompt)
            if not hasattr(response, 'text'):
                logger.error("Phản hồi Gemini không có thuộc tính text")
                raise ValueError("Phản hồi Gemini không hợp lệ")
            response_text = response.text.strip()
            json_data = fix_json(response_text)
            if json_data is None:
                logger.warning(f"Phản hồi không phải JSON hợp lệ, thử key khác")
                raise ValueError("Phản hồi không phải JSON hợp lệ")
            VERIFY_KEY = selected_key  # Cập nhật key nếu thành công
            return response_text
        except GoogleAPIError as e:
            if "429" in str(e):  # Rate limit error
                logger.warning(f"Rate limit với key {selected_key[:5]}..., thử key khác")
                available_keys.remove(selected_key)
                attempts += 1
                time.sleep(random.uniform(0.5, 1.0))
                continue
            logger.warning(f"API key {selected_key[:5]}... thất bại: {str(e)}, thử key khác")
            available_keys.remove(selected_key)
            attempts += 1
            time.sleep(random.uniform(0.1, 0.5))
        except (ValueError, Exception) as e:
            logger.warning(f"API key {selected_key[:5]}... thất bại: {str(e)}, thử key khác")
            available_keys.remove(selected_key)
            attempts += 1
            time.sleep(random.uniform(0.1, 0.5))

    logger.error("Tất cả API key đều không hoạt động")
    raise ResourceExhausted("Tất cả API key đều không hoạt động")

# Prompt xác nhận danh từ
def generate_verify_prompt(rule_id, rule_type, article, rule_data, word, provided_article):
    if rule_type == "suffix":
        suffix = rule_data["suffix"]
        example = rule_data["example"]
        return f'''
Kiểm tra danh từ tiếng Đức "{word}" với mạo từ "{provided_article}" có hợp lệ không. Danh từ phải:
- Là danh từ **thực sự tồn tại** trong tiếng Đức, phổ biến ở trình độ A1-B1 (hoặc cao hơn nếu không có từ phù hợp).
- Có giống là "{article}".
- Kết thúc chính xác bằng ký tự "{suffix}".
- Không trùng với ví dụ "{example}".

Nếu hợp lệ, trả về JSON xác nhận chú ý không được đưa giống vào {word}:
```json
{{
  "is_valid": true,
  "word": "{word}",
  "article": "{provided_article}",
  "reason": "Lý do tại sao danh từ hợp lệ",
  "tip": "Mẹo ghi nhớ sáng tạo",
  "meaning": "Nghĩa tiếng Việt"
}}
```

Nếu không hợp lệ, cung cấp một danh từ đúng thay thế với đầy đủ thông tin chú ý không được đưa giống vào {word}:
```json
{{
  "is_valid": false,
  "word": "danh từ đúng",
  "article": "{article}",
  "reason": "Lý do tại sao danh từ ban đầu sai và danh từ mới đúng",
  "tip": "Mẹo ghi nhớ sáng tạo",
  "meaning": "Nghĩa tiếng Việt"
}}
```

Phản hồi phải bằng tiếng Việt, định dạng JSON chú ý không được đưa giống vào {word}.
'''
    elif rule_type == "semantic":
        category = rule_data["category"]
        example = rule_data["example"]
        return f'''
Kiểm tra danh từ tiếng Đức "{word}" với mạo từ "{provided_article}" có hợp lệ không. Danh từ phải:
- Là danh từ **thực sự tồn tại** trong tiếng Đức, phổ biến ở trình độ A1-B1 (hoặc cao hơn nếu không có từ phù hợp).
- Có giống là "{article}".
- Thuộc danh mục "{category}" (ví dụ: "{example}").
- Không trùng với ví dụ "{example}".

Nếu hợp lệ, trả về JSON xác nhận chú ý không được đưa giống vào {word} :
```json
{{
  "is_valid": true,
  "word": "{word}",
  "article": "{provided_article}",
  "reason": "Lý do tại sao danh từ hợp lệ",
  "tip": "Mẹo ghi nhớ sáng tạo",
  "meaning": "Nghĩa tiếng Việt"
}}
```

Nếu không hợp lệ, cung cấp một danh từ đúng thay thế với đầy đủ thông tin chú ý không được đưa giống vào {word}:
```json
{{
  "is_valid": false,
  "word": "danh từ đúng",
  "article": "{article}",
  "reason": "Lý do tại sao danh từ ban đầu sai và danh từ mới đúng",
  "tip": "Mẹo ghi nhớ sáng tạo",
  "meaning": "Nghĩa tiếng Việt"
}}
```

Phản hồi phải bằng tiếng Việt, định dạng JSON.
'''
    return ""

# Hàm phát âm danh từ
def speak_noun(noun):
    try:
        tts = gTTS(text=noun, lang='de')
        audio_file = "temp_noun.mp3"
        tts.save(audio_file)
        logger.info(f"Đã lưu file âm thanh: {audio_file}")

        if not os.path.exists(audio_file):
            logger.error(f"File {audio_file} không tồn tại sau khi lưu")
            return
        if os.path.getsize(audio_file) == 0:
            logger.error(f"File {audio_file} rỗng")
            os.remove(audio_file)
            return

        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        
        os.remove(audio_file)
        logger.info(f"Đã xóa file tạm: {audio_file}")
    except Exception as e:
        logger.error(f"Lỗi khi phát âm danh từ {noun}: {str(e)}")
        if os.path.exists(audio_file):
            os.remove(audio_file)

# Chuẩn hóa chuỗi để kiểm tra hậu tố
def normalize_string(s):
    s = s.strip()
    s = s.replace('-', '')
    return s.lower()

# Tạo stack quy tắc
def create_rule_stack():
    stack = []
    rule_set = set()
    
    for article in suffix_rules:
        for idx, rule in enumerate(suffix_rules[article]):
            rule_id = f"suffix_{article}_{idx}"
            if rule_id not in rule_set:
                stack.append(rule_id)
                rule_set.add(rule_id)
    
    for article in semantic_rules:
        for idx, rule in enumerate(semantic_rules[article]):
            rule_id = f"semantic_{article}_{idx}"
            if rule_id not in rule_set:
                stack.append(rule_id)
                rule_set.add(rule_id)
    
    random.shuffle(stack)
    logger.info(f"Tạo stack với {len(stack)} quy tắc duy nhất")
    logger.info(f"Nội dung stack sau khi tạo: {stack}")
    return stack, len(stack)

# Tạo danh từ từ quy tắc
def get_noun_from_rule(rule_id):
    parts = rule_id.split('_')
    rule_type, article, idx = parts
    idx = int(idx)
    
    if rule_type == "suffix":
        rule_data = suffix_rules[article][idx]
    else:
        rule_data = semantic_rules[article][idx]
    
    prompt = generate_noun_prompt(rule_id, rule_type, article, rule_data)
    if not prompt:
        logger.error(f"Không tạo được prompt cho rule_id {rule_id}")
        raise Exception(f"Quy tắc không hợp lệ: {rule_id}")
    
    logger.info(f"Prompt gửi AI cho quy tắc {rule_id}:\n{prompt}")
    
    for retry in range(MAX_API_RETRIES):
        try:
            # Lần gọi đầu
            response = try_with_different_key(prompt, current_key=PRIMARY_KEY, excluded_key=VERIFY_KEY)
            logger.info(f"Phản hồi lần đầu từ AI:\n{response}")
            json_data = fix_json(response)
            if json_data is None:
                logger.warning(f"Phản hồi JSON không hợp lệ, thử lại lần {retry + 1}")
                continue
            
            # Kiểm tra từ ví dụ
            example = rule_data["example"].lower()
            if json_data["word"].lower() == example:
                logger.warning(f"Danh từ '{json_data['word']}' trùng với ví dụ '{example}', thử lại lần {retry + 1}")
                continue
            
            # Xác nhận qua API
            verify_prompt = generate_verify_prompt(rule_id, rule_type, article, rule_data, json_data["word"], json_data["article"])
            if not verify_prompt:
                logger.error(f"Không tạo được prompt xác nhận cho rule_id {rule_id}")
                raise Exception(f"Không tạo được prompt xác nhận")
            
            logger.info(f"Prompt xác nhận:\n{verify_prompt}")
            verify_response = verify_with_different_key(verify_prompt, current_key=VERIFY_KEY, excluded_key=PRIMARY_KEY)
            logger.info(f"Phản hồi xác nhận từ AI:\n{verify_response}")
            verify_data = fix_json(verify_response)
            if verify_data is None:
                logger.warning(f"Phản hồi xác nhận JSON không hợp lệ, thử lại lần {retry + 1}")
                continue
            
            if verify_data.get("is_valid", False):
                return (verify_data["word"], verify_data["article"], verify_data["reason"],
                        verify_data["tip"], verify_data.get("meaning", "Không có nghĩa"))
            else:
                logger.warning(f"Danh từ '{json_data['word']}' không hợp lệ, sử dụng danh từ thay thế: '{verify_data['word']}'")
                return (verify_data["word"], verify_data["article"], verify_data["reason"],
                        verify_data["tip"], verify_data.get("meaning", "Không có nghĩa"))
        
        except (ResourceExhausted, ValueError, KeyError) as e:
            logger.error(f"Lỗi khi lấy danh từ cho quy tắc {rule_id} (lần thử {retry + 1}): {str(e)}")
            if retry == MAX_API_RETRIES - 1:
                raise Exception(f"Không thể lấy danh từ hợp lệ sau {MAX_API_RETRIES} lần thử: {str(e)}")
            time.sleep(random.uniform(0.5, 1.0))
    
    raise Exception(f"Không thể lấy danh từ hợp lệ cho quy tắc {rule_id} sau {MAX_API_RETRIES} lần thử")

# Lớp GUI
class GermanArticleTrainerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Luyện tập mạo từ tiếng Đức")
        self.geometry("780x600")
        
        init_db()
        self.rule_stack, self.total_new_questions = create_rule_stack()
        self.review_questions = get_review_questions()
        self.total_review_questions = len(self.review_questions)
        self.total_questions = self.total_new_questions + self.total_review_questions
        self.total_correct = 0
        self.total_wrong = 0
        self.current_noun = ""
        self.current_article = ""
        self.current_reason = ""
        self.current_tip = ""
        self.current_meaning = ""
        self.is_answered = False
        
        self.theme = {
            "bg": "#f0f0f0",
            "fg": "#000000",
            "button_bg": "#4CAF50",
            "button_fg": "#ffffff",
            "entry_bg": "#ffffff",
            "feedback_correct": "#055005",
            "feedback_wrong": "#750a1d"
        }
        
        self.main_frame = tk.Frame(self, bg=self.theme["bg"])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.label_title = tk.Label(self.main_frame, text="Luyện tập mạo từ tiếng Đức", font=("Arial", 23, "bold"), bg=self.theme["bg"], fg=self.theme["fg"])
        self.label_title.pack(pady=5)
        
        self.label_stats = tk.Label(self.main_frame, text=f"Tổng số câu hỏi: {self.total_questions} | Đúng: {self.total_correct} | Sai: {self.total_wrong}", font=("Arial", 16), bg=self.theme["bg"], fg=self.theme["fg"])
        self.label_stats.pack(pady=5)
        
        self.label_noun = tk.Label(self.main_frame, text="Danh từ: Chưa có", font=("Arial", 18, "bold"), bg=self.theme["bg"], fg=self.theme["fg"])
        self.label_noun.pack(pady=10)
        
        self.label_prompt = tk.Label(self.main_frame, text="Nhập mạo từ (der/die/das):", font=("Arial", 18, "bold"), bg=self.theme["bg"], fg=self.theme["fg"])
        self.label_prompt.pack(pady=5)
        
        self.entry_answer = tk.Entry(self.main_frame, font=("Arial", 18, "bold"), width=10, bg=self.theme["entry_bg"], fg=self.theme["fg"])
        self.entry_answer.pack(pady=5)
        self.entry_answer.bind("<Return>", self.handle_enter)
        
        self.label_instruction = tk.Label(self.main_frame, text="Nhấn Enter để trả lời hoặc chuyển tiếp", font=("Arial", 16, "italic"), bg=self.theme["bg"], fg=self.theme["fg"])
        self.label_instruction.pack(pady=5)
        
        self.label_feedback = tk.Label(self.main_frame, text="", font=("Arial", 18, "bold"), bg=self.theme["bg"], fg=self.theme["fg"], wraplength=770)
        self.label_feedback.pack(pady=10)
        
        self.button_next = tk.Button(self.main_frame, text="Câu tiếp theo", command=self.next_noun, font=("Arial", 18, "bold"), bg=self.theme["button_bg"], fg=self.theme["button_fg"])
        self.button_next.pack(pady=5)
        
        self.next_noun()
    
    def handle_enter(self, event):
        if not self.is_answered:
            self.check_answer()
        else:
            self.next_noun()
    
    def next_noun(self):
        if self.review_questions:
            noun, article, reason, tip, meaning = random.choice(self.review_questions)
            self.current_noun = noun
            self.current_article = article
            self.current_reason = reason
            self.current_tip = tip
            self.current_meaning = meaning
            self.review_questions.remove((noun, article, reason, tip, meaning))
        else:
            if not self.rule_stack:
                messagebox.showinfo("Hoàn thành", f"Bạn đã hoàn thành! Tổng số câu hỏi: {self.total_questions}\nĐúng: {self.total_correct}\nSai: {self.total_wrong}")
                self.entry_answer.config(state=tk.DISABLED)
                self.button_next.config(state=tk.DISABLED)
                return
            rule_id = self.rule_stack.pop(0)
            try:
                self.current_noun, self.current_article, self.current_reason, self.current_tip, self.current_meaning = get_noun_from_rule(rule_id)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lấy danh từ từ API: {str(e)}")
                self.label_noun.config(text="Danh từ: Lỗi API")
                self.label_feedback.config(text="Vui lòng thử lại sau", fg=self.theme["feedback_wrong"])
                self.entry_answer.config(state=tk.DISABLED)
                return
        
        self.label_noun.config(text=f"Danh từ: {self.current_noun}")
        self.label_feedback.config(text="", fg=self.theme["fg"])
        self.entry_answer.delete(0, tk.END)
        self.entry_answer.config(state=tk.NORMAL)
        self.is_answered = False
        self.entry_answer.focus()
    
    def check_answer(self):
        user_answer = self.entry_answer.get().strip().lower()
        if not user_answer:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập mạo từ!")
            return
        
        is_correct = user_answer == self.current_article.lower()
        if is_correct:
            self.total_correct += 1
            self.label_feedback.config(
                text=f"Đúng! 🎉 '{self.current_noun}' (Nghĩa: {self.current_meaning}) dùng mạo từ '{self.current_article}' vì: {self.current_reason}\n{self.current_tip}",
                fg=self.theme["feedback_correct"]
            )
            speak_noun(self.current_noun)
            remove_correct_answer(self.current_noun, self.current_article)
        else:
            self.total_wrong += 1
            self.label_feedback.config(
                text=f"Sai! 😔 Đáp án đúng là '{self.current_article}'. '{self.current_noun}' (Nghĩa: {self.current_meaning}) dùng mạo từ '{self.current_article}' vì: {self.current_reason}\n{self.current_tip}",
                fg=self.theme["feedback_wrong"]
            )
            save_wrong_answer(self.current_noun, self.current_article, user_answer, self.current_reason, self.current_tip, self.current_meaning)
        
        self.label_stats.config(text=f"Tổng số câu hỏi: {self.total_questions} | Đúng: {self.total_correct} | Sai: {self.total_wrong}")
        self.is_answered = True
        self.entry_answer.config(state=tk.NORMAL)
        self.entry_answer.focus()

if __name__ == "__main__":
    app = GermanArticleTrainerGUI()
    app.mainloop()
