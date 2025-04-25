def generate_noun_prompt(rule_id, rule_type, article, rule_data):
    """Trả về prompt yêu cầu AI tạo danh từ tiếng Đức phù hợp với quy tắc"""
    if rule_type == "suffix":
        suffix = rule_data["suffix"]
        reason = rule_data["reason"]
        example = rule_data["example"]
        tip = rule_data["tip"]

        return f'''
Đây là chương trình tìm kiếm một danh từ tiếng Đức **thực sự tồn tại** và phổ biến ở trình độ A1-B1, nếu không có từ phù hợp ở trình độ này thì bắt buộc phải đưa ra một từ ở trình độ cao hơn, có giống là "{article}" và kết thúc chính xác bằng ký tự "{suffix}" giúp cho người dùng luyện tập nhớ các quy tắc nhớ giống của danh từ.
Không được tạo từ giả hoặc từ không tồn tại trong tiếng Đức.
Mô tả lý do vì sao danh từ đó có giống "{article}" và hậu tố đó có ý nghĩa gì.

Yêu cầu phản hồi phải hoàn toàn bằng tiếng Việt, không sử dụng lại từ trong ví dụ ("{example}"), gồm:
- "word": danh từ không chứa giống "{article}", phù hợp yêu cầu đuôi bằng "{suffix}"
- "article": giống của danh từ trên "{article}"
- "reason": giải thích nhanh bằng tiếng Việt
- "tip": mẹo ghi nhớ bằng tiếng Việt, sáng tạo, gợi ý cho người học ghi nhớ "{suffix}" thuộc "{article}"
- "meaning": nghĩa tiếng Việt của danh từ

Phản hồi phải ở định dạng JSON như sau:
```json
{{
  "word": "chỉ chứa Danh từ không chứa {article} ",
  "article": "{article}",
  "reason": "",
  "tip": "",
  "meaning": ""
}}
'''
    elif rule_type == "semantic":
        category = rule_data["category"]
        reason = rule_data["reason"]
        example = rule_data["example"]
        tip = rule_data["tip"]

        return f'''
Đây là chương trình tìm kiếm một danh từ tiếng Đức **thực sự tồn tại** và phổ biến ở trình độ A1-B1, nếu không có từ phù hợp ở trình độ này thì bắt buộc phải đưa ra một từ ở trình độ cao hơn, có giống là "{article}" và thuộc danh mục "{category}" (ví dụ: "{example}") giúp cho người dùng luyện tập nhớ các quy tắc nhớ giống của danh từ.
Không được tạo từ giả hoặc từ không tồn tại trong tiếng Đức.
Mô tả lý do vì sao danh từ đó thuộc danh mục này và vì sao nó có giống "{article}".

Yêu cầu phản hồi phải hoàn toàn bằng tiếng Việt, không sử dụng lại từ trong ví dụ ("{example}"), gồm:
- "word": danh từ tiếng Đức không chứa giống "{article}", phù hợp với "{category}"
- "article": giống "{article}"
- "reason": giải thích nhanh bằng tiếng Việt
- "tip": mẹo ghi nhớ bằng tiếng Việt, sáng tạo, gợi ý cho người học ghi nhớ "{category}" thuộc "{article}"
- "meaning": nghĩa tiếng Việt của danh từ

Phản hồi phải ở định dạng JSON như sau:
```json
{{
  "word": "chỉ chứa Danh từ không chứa {article} ",
  "article": "{article}",
  "reason": "",
  "tip": "",
  "meaning": ""
}}
'''
    else:
        return ""

def generate_verify_prompt(rule_id, rule_type, article, rule_data, word, provided_article):
    """Trả về prompt yêu cầu AI xác nhận tính hợp lệ của danh từ và sửa nếu cần"""
    if rule_type == "suffix":
        suffix = rule_data["suffix"]
        example = rule_data["example"]
        return f'''
Kiểm tra danh từ tiếng Đức "{word}" với giống "{provided_article}" có hợp lệ không. Danh từ phải:
- Là danh từ **thực sự tồn tại** trong tiếng Đức, phổ biến ở trình độ A1-B1 (hoặc cao hơn nếu không có từ phù hợp).
- Có giống là "{article}".
- Kết thúc chính xác bằng ký tự "{suffix}".
- Không trùng với ví dụ "{example}".

Nếu hợp lệ, trả về JSON xác nhận:
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

Nếu không hợp lệ, cung cấp một danh từ đúng thay thế với đầy đủ thông tin:
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
    elif rule_type == "semantic":
        category = rule_data["category"]
        example = rule_data["example"]
        return f'''
Kiểm tra danh từ tiếng Đức "{word}" với giống "{provided_article}" có hợp lệ không. Danh từ phải:
- Là danh từ **thực sự tồn tại** trong tiếng Đức, phổ biến ở trình độ A1-B1 (hoặc cao hơn nếu không có từ phù hợp).
- Có giống là "{article}".
- Thuộc danh mục "{category}" (ví dụ: "{example}").
- Không trùng với ví dụ "{example}".

Nếu hợp lệ, trả về JSON xác nhận:
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

Nếu không hợp lệ, cung cấp một danh từ đúng thay thế với đầy đủ thông tin:
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