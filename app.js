// Danh sách khóa API (minh họa, thêm tất cả từ config.json)
const API_KEYS = [
    "AIzaSyCdxcJf9F3myEQjI_1ogbS-6_0RLRtOEY8",
    "AIzaSyCp_VB-bpgQ6wEvVZBR04akkXcSVvwtoiQ",
    "AIzaSyAXlZH48sepbUXX5yV7IsnYmdMiwynWyBc"
    // Thêm các khóa khác
];

let PRIMARY_KEY = API_KEYS[Math.floor(Math.random() * API_KEYS.length)];
let VERIFY_KEY = API_KEYS.find(key => key !== PRIMARY_KEY) || API_KEYS[0];

// Bộ nhớ đệm danh từ
const nounCache = new Map();

// Quy tắc danh từ (đầy đủ 61 trường hợp từ chương trình gốc)
const suffixRules = {
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
};

const semanticRules = {
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
};

// Biến trạng thái
let ruleStack = [];
let totalNewQuestions = 0;
let reviewQuestions = JSON.parse(localStorage.getItem('wrongAnswers') || '[]');
let totalQuestions = 0;
let totalCorrect = 0;
let totalWrong = 0;
let currentNoun = "";
let currentArticle = "";
let currentReason = "";
let currentTip = "";
let currentMeaning = "";
let isAnswered = false;
const MAX_API_RETRIES = 5;

// Hiển thị popup
function showPopup(title, message) {
    document.getElementById('popupTitle').textContent = title;
    document.getElementById('popupMessage').textContent = message;
    document.getElementById('popup').classList.remove('hidden');
    document.body.classList.add('no-scroll');
}

// Ẩn popup
function hidePopup() {
    document.getElementById('popup').classList.add('hidden');
    document.body.classList.remove('no-scroll');
}

// Hiển thị popup danh sách từ sai
function showWrongWordsPopup() {
    const wrongWordsList = document.getElementById('wrongWordsList');
    if (reviewQuestions.length === 0) {
        wrongWordsList.innerHTML = '<p class="text-center">Chưa có từ nào sai!</p>';
    } else {
        wrongWordsList.innerHTML = '<ul>' + reviewQuestions.map((item, index) => `
            <li class="wrong-item">
                <p><strong>${index + 1}. Từ:</strong> ${item.noun}</p>
                <p><strong>Mạo từ đúng:</strong> ${item.correctArticle}</p>
                <p><strong>Mạo từ bạn nhập:</strong> ${item.userAnswer}</p>
                <p><strong>Lý do:</strong> ${item.reason}</p>
                <p><strong>Mẹo:</strong> ${item.tip}</p>
                <p><strong>Nghĩa:</strong> ${item.meaning}</p>
            </li>
        `).join('') + '</ul>';
    }
    document.getElementById('wrongWordsPopup').classList.remove('hidden');
    document.body.classList.add('no-scroll');
}

// Ẩn popup danh sách từ sai
function hideWrongWordsPopup() {
    document.getElementById('wrongWordsPopup').classList.add('hidden');
    document.body.classList.remove('no-scroll');
}

// Gọi API Gemini
async function callGeminiAPI(prompt, apiKey) {
    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-001:generateContent?key=${apiKey}`;
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }] })
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        return fixJson(data.candidates[0].content.parts[0].text);
    } catch (error) {
        throw error;
    }
}

// Thử với các khóa API khác nhau
async function tryWithDifferentKey(prompt, excludedKey) {
    const availableKeys = API_KEYS.filter(key => key !== excludedKey);
    for (const key of availableKeys) {
        try {
            const response = await callGeminiAPI(prompt, key);
            if (response) {
                PRIMARY_KEY = key;
                return response;
            }
        } catch (error) {
            if (error.message.includes('429')) {
                await new Promise(resolve => setTimeout(resolve, 500));
                continue;
            }
            console.warn(`Lỗi với key ${key.slice(0, 5)}...: ${error}`);
        }
    }
    throw new Error('Tất cả API key không hoạt động');
}

// Thử xác nhận với khóa khác
async function verifyWithDifferentKey(prompt, excludedKey) {
    const availableKeys = API_KEYS.filter(key => key !== excludedKey);
    for (const key of availableKeys) {
        try {
            const response = await callGeminiAPI(prompt, key);
            if (response) {
                VERIFY_KEY = key;
                return response;
            }
        } catch (error) {
            if (error.message.includes('429')) {
                await new Promise(resolve => setTimeout(resolve, 500));
                continue;
            }
            console.warn(`Lỗi với key ${key.slice(0, 5)}...: ${error}`);
        }
    }
    throw new Error('Tất cả API key không hoạt động');
}

// Sửa JSON không hợp lệ
function fixJson(jsonStr) {
    jsonStr = jsonStr.replace(/```json\s*|\s*```/g, '').trim();
    const startIdx = jsonStr.indexOf('{');
    const endIdx = jsonStr.lastIndexOf('}');
    if (startIdx !== -1 && endIdx !== -1 && endIdx > startIdx) {
        jsonStr = jsonStr.slice(startIdx, endIdx + 1);
    } else {
        return null;
    }

    try {
        return JSON.parse(jsonStr);
    } catch (e) {
        jsonStr = jsonStr.replace(/,\s*}/g, '}').replace(/(\w+)(?=\s*:)/g, '"$1"');
        try {
            return JSON.parse(jsonStr);
        } catch {
            return null;
        }
    }
}

// Tạo stack quy tắc
function createRuleStack() {
    const stack = [];
    const ruleSet = new Set();

    for (const article in suffixRules) {
        suffixRules[article].forEach((rule, idx) => {
            const ruleId = `suffix_${article}_${idx}`;
            if (!ruleSet.has(ruleId)) {
                stack.push(ruleId);
                ruleSet.add(ruleId);
            }
        });
    }

    for (const article in semanticRules) {
        semanticRules[article].forEach((rule, idx) => {
            const ruleId = `semantic_${article}_${idx}`;
            if (!ruleSet.has(ruleId)) {
                stack.push(ruleId);
                ruleSet.add(ruleId);
            }
        });
    }

    // Xáo trộn stack
    for (let i = stack.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [stack[i], stack[j]] = [stack[j], stack[i]];
    }

    return stack;
}

// Prompt tạo danh từ
function generateNounPrompt(ruleId, ruleType, article, ruleData) {
    if (ruleType === 'suffix') {
        const { suffix, example } = ruleData;
        return `
Đây là chương trình tìm kiếm một danh từ tiếng Đức **thực sự tồn tại** và phổ biến ở trình độ A1-B1, nếu không có từ phù hợp ở trình độ này thì bắt buộc phải đưa ra một từ ở trình độ cao hơn, có giống là "${article}" và kết thúc chính xác bằng ký tự "${suffix}" giúp cho người dùng luyện tập nhớ các quy tắc nhớ giống của danh từ.
Không được tạo từ giả hoặc từ không tồn tại trong tiếng Đức.
Mô tả lý do vì sao danh từ đó có giống "${article}" và hậu tố đó có ý nghĩa gì.

Yêu cầu phản hồi phải hoàn toàn bằng tiếng Việt, không sử dụng lại từ trong ví dụ ("${example}"), gồm:
- "word": danh từ không chứa giống "${article}", phù hợp yêu cầu đuôi bằng "${suffix}"
- "article": giống của danh từ trên "${article}"
- "reason": giải thích nhanh bằng tiếng Việt
- "tip": mẹo ghi nhớ bằng tiếng Việt, sáng tạo, gợi ý cho người học ghi nhớ "${suffix}" thuộc "${article}"
- "meaning": nghĩa tiếng Việt của danh từ

Phản hồi phải ở định dạng JSON như sau:
{
  "word": "chỉ chứa Danh từ không chứa ${article}",
  "article": "${article}",
  "reason": "",
  "tip": "",
  "meaning": ""
}`;
    } else if (ruleType === 'semantic') {
        const { category, example } = ruleData;
        return `
Đây là chương trình tìm kiếm một danh từ tiếng Đức **thực sự tồn tại** và phổ biến ở trình độ A1-B1, nếu không có từ phù hợp ở trình độ này thì bắt buộc phải đưa ra một từ ở trình độ cao hơn, có giống là "${article}" và thuộc danh mục "${category}" (ví dụ: "${example}") giúp cho người dùng luyện tập nhớ các quy tắc nhớ giống của danh từ.
Không được tạo từ giả hoặc từ không tồn tại trong tiếng Đức.
Mô tả lý do vì sao danh từ đó thuộc danh mục này và vì sao nó có giống "${article}".

Yêu cầu phản hồi phải hoàn toàn bằng tiếng Việt, không sử dụng lại từ trong ví dụ ("${example}"), gồm:
- "word": danh từ tiếng Đức không chứa giống "${article}", phù hợp với "${category}"
- "article": giống "${article}"
- "reason": giải thích nhanh bằng tiếng Việt
- "tip": mẹo ghi nhớ bằng tiếng Việt, sáng tạo, gợi ý cho người học ghi nhớ "${category}" thuộc "${article}"
- "meaning": nghĩa tiếng Việt của danh từ

Phản hồi phải ở định dạng JSON như sau:
{
  "word": "chỉ chứa Danh từ không chứa ${article}",
  "article": "${article}",
  "reason": "",
  "tip": "",
  "meaning": ""
}`;
    }
    return '';
}

// Prompt xác nhận danh từ
function generateVerifyPrompt(ruleId, ruleType, article, ruleData, word, providedArticle) {
    if (ruleType === 'suffix') {
        const { suffix, example } = ruleData;
        return `
Kiểm tra danh từ tiếng Đức "${word}" với mạo từ "${providedArticle}" có hợp lệ không. Danh từ phải:
- Là danh từ **thực sự tồn tại** trong tiếng Đức, phổ biến ở trình độ A1-B1 (hoặc cao hơn nếu không có từ phù hợp).
- Có giống là "${article}".
- Kết thúc chính xác bằng ký tự "${suffix}".
- Không trùng với ví dụ "${example}".

Nếu hợp lệ, trả về JSON xác nhận chú ý không được đưa giống vào ${word}:
{
  "is_valid": true,
  "word": "${word}",
  "article": "${providedArticle}",
  "reason": "Lý do tại sao danh từ hợp lệ",
  "tip": "Mẹo ghi nhớ sáng tạo",
  "meaning": "Nghĩa tiếng Việt"
}

Nếu không hợp lệ, cung cấp một danh từ đúng thay thế với đầy đủ thông tin chú ý không được đưa giống vào ${word}:
{
  "is_valid": false,
  "word": "danh từ đúng",
  "article": "${article}",
  "reason": "Lý do tại sao danh từ ban đầu sai và danh từ mới đúng",
  "tip": "Mẹo ghi nhớ sáng tạo",
  "meaning": "Nghĩa tiếng Việt"
}

Phản hồi phải bằng tiếng Việt, định dạng JSON chú ý không được đưa giống vào ${word}.
`;
    } else if (ruleType === 'semantic') {
        const { category, example } = ruleData;
        return `
Kiểm tra danh từ tiếng Đức "${word}" với mạo từ "${providedArticle}" có hợp lệ không. Danh từ phải:
- Là danh từ **thực sự tồn tại** trong tiếng Đức, phổ biến ở trình độ A1-B1 (hoặc cao hơn nếu không có từ phù hợp).
- Có giống là "${article}".
- Thuộc danh mục "${category}" (ví dụ: "${example}").
- Không trùng với ví dụ "${example}".

Nếu hợp lệ, trả về JSON xác nhận chú ý không được đưa giống vào ${word} :
{
  "is_valid": true,
  "word": "${word}",
  "article": "${providedArticle}",
  "reason": "Lý do tại sao danh từ hợp lệ",
  "tip": "Mẹo ghi nhớ sáng tạo",
  "meaning": "Nghĩa tiếng Việt"
}

Nếu không hợp lệ, cung cấp một danh từ đúng thay thế với đầy đủ thông tin chú ý không được đưa giống vào ${word}:
{
  "is_valid": false,
  "word": "danh từ đúng",
  "article": "${article}",
  "reason": "Lý do tại sao danh từ ban đầu sai và danh từ mới đúng",
  "tip": "Mẹo ghi nhớ sáng tạo",
  "meaning": "Nghĩa tiếng Việt"
}

Phản hồi phải bằng tiếng Việt, định dạng JSON.
`;
    }
    return '';
}

// Tạo danh từ từ quy tắc
async function getNounFromRule(ruleId) {
    if (nounCache.has(ruleId)) {
        return nounCache.get(ruleId);
    }

    const [ruleType, article, idx] = ruleId.split('_');
    const ruleData = ruleType === 'suffix' ? suffixRules[article][parseInt(idx)] : semanticRules[article][parseInt(idx)];
    const prompt = generateNounPrompt(ruleId, ruleType, article, ruleData);
    if (!prompt) throw new Error(`Không tạo được prompt cho quy tắc ${ruleId}`);

    for (let retry = 0; retry < MAX_API_RETRIES; retry++) {
        try {
            const response = await tryWithDifferentKey(prompt, VERIFY_KEY);
            if (!response) continue;

            if (response.word.toLowerCase() === ruleData.example.toLowerCase()) {
                continue;
            }

            const verifyPrompt = generateVerifyPrompt(ruleId, ruleType, article, ruleData, response.word, response.article);
            const verifyResponse = await verifyWithDifferentKey(verifyPrompt, PRIMARY_KEY);
            if (!verifyResponse) continue;

            const result = [
                verifyResponse.word,
                verifyResponse.article,
                verifyResponse.reason,
                verifyResponse.tip,
                verifyResponse.meaning || 'Không có nghĩa'
            ];

            nounCache.set(ruleId, result);
            return result;
        } catch (error) {
            if (retry === MAX_API_RETRIES - 1) throw error;
            await new Promise(resolve => setTimeout(resolve, 500));
        }
    }
}

// Phát âm danh từ
function speakNoun(noun) {
    const utterance = new SpeechSynthesisUtterance(noun);
    utterance.lang = 'de-DE';
    utterance.rate = 0.9;
    window.speechSynthesis.speak(utterance);
}

// Lưu câu trả lời sai
function saveWrongAnswer(noun, correctArticle, userAnswer, reason, tip, meaning) {
    reviewQuestions.push({ noun, correctArticle, userAnswer, reason, tip, meaning });
    localStorage.setItem('wrongAnswers', JSON.stringify(reviewQuestions.slice(-100)));
}

// Xóa câu trả lời đúng
function removeCorrectAnswer(noun, correctArticle) {
    reviewQuestions = reviewQuestions.filter(q => q.noun !== noun || q.correctArticle !== correctArticle);
    localStorage.setItem('wrongAnswers', JSON.stringify(reviewQuestions));
}

// Cập nhật thống kê
function updateStats() {
    totalQuestions = totalCorrect + totalWrong;
    document.getElementById('stats').textContent = `Tổng số câu hỏi: ${totalQuestions} | Đúng: ${totalCorrect} | Sai: ${totalWrong}`;
}

// Chuyển sang danh từ tiếp theo
async function nextNoun() {
    if (ruleStack.length > 0) {
        const ruleId = ruleStack.shift();
        try {
            [currentNoun, currentArticle, currentReason, currentTip, currentMeaning] = await getNounFromRule(ruleId);
        } catch (error) {
            showPopup('Lỗi API', `Không thể lấy danh từ từ API: ${error.message}. Vui lòng thử lại sau.`);
            document.getElementById('noun').textContent = 'Danh từ: Lỗi API';
            document.getElementById('feedback').textContent = 'Vui lòng thử lại sau';
            document.getElementById('feedback').classList.add('wrong');
            document.getElementById('answer').disabled = true;
            return;
        }
    } else if (reviewQuestions.length > 0) {
        const question = reviewQuestions[Math.floor(Math.random() * reviewQuestions.length)];
        currentNoun = question.noun;
        currentArticle = question.correctArticle;
        currentReason = question.reason;
        currentTip = question.tip;
        currentMeaning = question.meaning;
        reviewQuestions = reviewQuestions.filter(q => q.noun !== currentNoun || q.correctArticle !== currentArticle);
        localStorage.setItem('wrongAnswers', JSON.stringify(reviewQuestions));
    } else {
        showPopup('Hoàn thành', `Bạn đã hoàn thành!\nTổng số câu hỏi: ${totalQuestions}\nĐúng: ${totalCorrect}\nSai: ${totalWrong}`);
        document.getElementById('answer').disabled = true;
        document.getElementById('nextBtn').disabled = true;
        document.getElementById('speakBtn').disabled = true;
        document.getElementById('viewWrongBtn').disabled = true;
        document.getElementById('clearWrongBtn').disabled = true;
        return;
    }

    document.getElementById('noun').textContent = currentNoun;
    document.getElementById('feedback').textContent = '';
    document.getElementById('feedback').classList.remove('correct', 'wrong');
    document.getElementById('answer').value = '';
    document.getElementById('answer').disabled = false;
    isAnswered = false;
    document.getElementById('answer').focus();
    speakNoun(currentNoun);
}

// Kiểm tra câu trả lời
function checkAnswer() {
    const userAnswer = document.getElementById('answer').value.trim().toLowerCase();
    if (!userAnswer) {
        showPopup('Cảnh báo', 'Chưa nhập mạo từ!');
        return;
    }

    const isCorrect = userAnswer === currentArticle.toLowerCase();
    if (isCorrect) {
        totalCorrect++;
        document.getElementById('feedback').textContent = `Đúng! 🎉 '${currentNoun}' (Nghĩa: ${currentMeaning}) dùng mạo từ '${currentArticle}' vì: ${currentReason}\n${currentTip}`;
        document.getElementById('feedback').classList.add('correct');
        speakNoun(currentNoun);
        removeCorrectAnswer(currentNoun, currentArticle);
    } else {
        totalWrong++;
        document.getElementById('feedback').textContent = `Sai! 😔 Đáp án đúng là '${currentArticle}'. '${currentNoun}' (Nghĩa: ${currentMeaning}) dùng mạo từ '${currentArticle}' vì: ${currentReason}\n${currentTip}`;
        document.getElementById('feedback').classList.add('wrong');
        saveWrongAnswer(currentNoun, currentArticle, userAnswer, currentReason, currentTip, currentMeaning);
    }

    updateStats();
    isAnswered = true;
    document.getElementById('answer').focus();
}

// Khởi tạo ứng dụng
async function init() {
    ruleStack = createRuleStack();
    totalNewQuestions = ruleStack.length; // 61 quy tắc
    updateStats();
    await nextNoun();

    const answerInput = document.getElementById('answer');
    answerInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            if (!isAnswered) {
                checkAnswer();
            } else {
                nextNoun();
            }
        }
    });
    document.getElementById('nextBtn').addEventListener('click', () => {
        if (!isAnswered) {
            const userAnswer = document.getElementById('answer').value.trim().toLowerCase();
            if (!userAnswer) {
                showPopup('Cảnh báo', 'Chưa nhập mạo từ!');
                return;
            }
            checkAnswer();
        } else {
            nextNoun();
        }
    });
    document.getElementById('speakBtn').addEventListener('click', () => speakNoun(currentNoun));
    document.getElementById('popupClose').addEventListener('click', hidePopup);
    document.getElementById('wrongWordsPopupClose').addEventListener('click', hideWrongWordsPopup);
    document.getElementById('viewWrongBtn').addEventListener('click', showWrongWordsPopup);
    document.getElementById('clearWrongBtn').addEventListener('click', () => {
        reviewQuestions = [];
        localStorage.setItem('wrongAnswers', JSON.stringify([]));
        showPopup('Thông báo', 'Đã xóa lịch sử câu trả lời sai!');
    });
}

init();