"""情绪推断 — 关键字表 + 表情描述。

EMOTION_KEYWORDS:
    text 命中某情绪的关键字越多 → 该情绪得分越高 → top score 作为推断结果。
    未命中按 speaker 类型给默认 (旁白 → contemplative，其他 → neutral)。

EMOTION_EXPRESSION_PHRASE:
    每种 emotion 对应的英文表情描述，注入 WERYDANCE / GPT Image 2 prompt
    替代僵化的 "stable face" 让 storyboard 出现差异化表情。

加新 emotion 时两个表都要同步加 entry。
"""

EMOTION_KEYWORDS = {
    "weary": ["累", "翻不了身", "不容失败", "压得", "喘不过气", "苦累", "操劳", "心力交瘁", "卷"],
    "tense": ["焦虑", "无处可逃", "挖坑", "淘汰", "紧迫", "抢", "厮杀", "崩溃", "卡死", "陷阱"],
    "wry": ["神仙", "煤灰", "牛马", "西瓜皮", "赚到了", "毫不起眼", "傻", "脚踩", "歪打正着", "凡尔赛"],
    "warm": ["拥抱", "奇迹", "赡养", "感性和身体", "温暖", "亲人", "陪伴", "守护", "回家", "拥抱日常"],
    "solemn": ["剥掉", "巨大的坑", "深渊", "代价", "残酷真相", "毁灭", "黑暗", "末日"],
    "contemplative": ["其实", "实际上", "本质上", "为什么", "或许", "我们都在", "复杂", "并不是"],
    "encouraging": ["可以", "不要怕", "相信", "勇敢", "迈出", "你能", "你已经"],
    "playful": ["哈哈", "嘿嘿", "搞笑", "调侃"],
}

EMOTION_EXPRESSION_PHRASE = {
    "neutral": "natural observational face, soft eyes, light breath",
    "tense": "tense, slight brow furrow, jaw tight, urgent narrowed gaze, shallow breath",
    "solemn": "solemn, lowered brow, heavy eyes, slow deep breath, restrained posture",
    "explanatory": "engaged explanatory face, alive eyes, occasional gestural emphasis, lecturer presence",
    "warm": "warm gentle smile, soft glowing eyes, slight head tilt, comforting body posture",
    "weary": "tired droop, half-closed eyelids, slumped shoulders, audible sigh, defeated body angle",
    "wry": "wry half-smile, raised eyebrow, slight head shake, self-aware knowing look",
    "playful": "playful eye sparkle, mischievous half-smile, light shoulder shrug, animated gestures",
    "contemplative": "thoughtful inward gaze, slow blink, gentle drift, fingers near chin or temple",
    "encouraging": "uplifted brow, encouraging smile, warm direct eye contact, open hands",
}

# step1_script 白名单：未列出的 emotion 会被打回 "neutral"
SUPPORTED_EMOTIONS = (
    "neutral", "tense", "solemn", "explanatory",
    "warm", "weary", "wry", "playful", "contemplative", "encouraging",
)
