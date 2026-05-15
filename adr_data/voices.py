"""WeryAI 内置 voice_id 池 + 角色名 → 音色库 asset 映射。

ADSD_VOICES:
    角色名硬绑定 voice_id (内置 weryai TTS)
    旁白 默认走男声沉稳叙述（Lyrical Voice 68），不要用 News Anchor 76
    用户明示要女声旁白时显式传 voice_gender=female

ADSD_MALE_VOICE_POOL / ADSD_FEMALE_VOICE_POOL:
    weryai 中文男声 66-70 / 女声 76-80 完整目录
    未命中具体名字时按 hash(speaker) 选池

ADSD_SPEAKER_KEYWORD_TO_ASSET (P3):
    speaker name 含关键字 → 命中 voice_assets.json 注册的音色 asset
    用于 WERYDANCE almighty-reference-to-video 的 audio_dub 声纹 clone
    排除：歌声（BY2/orange4music/JJ Lin）、混音未分离（mettsarchive 原始）、
          高风险公众人物（Trump/JJ Lin 默认不用）
"""

ADSD_VOICES = {
    "记者": {"voice_id": 67, "voice_name": "Refreshing Young Man"},
    "职员": {"voice_id": 69, "voice_name": "Reliable Executive"},
    "旁白": {"voice_id": 68, "voice_name": "Lyrical Voice"},
}

ADSD_MALE_VOICE_POOL = [
    {"voice_id": 66, "voice_name": "Pure-hearted Boy"},
    {"voice_id": 67, "voice_name": "Refreshing Young Man"},
    {"voice_id": 68, "voice_name": "Lyrical Voice"},
    {"voice_id": 69, "voice_name": "Reliable Executive"},
    {"voice_id": 70, "voice_name": "Stubborn Friend"},
]

ADSD_FEMALE_VOICE_POOL = [
    {"voice_id": 76, "voice_name": "News Anchor"},
    {"voice_id": 77, "voice_name": "Intellectual Girl"},
    {"voice_id": 78, "voice_name": "Gentle Senior"},
    {"voice_id": 79, "voice_name": "Kind-hearted Antie"},
    {"voice_id": 80, "voice_name": "Arrogant Miss"},
]

ADSD_MALE_VOICE_IDS = {int(v["voice_id"]) for v in ADSD_MALE_VOICE_POOL}
ADSD_FEMALE_VOICE_IDS = {int(v["voice_id"]) for v in ADSD_FEMALE_VOICE_POOL}
ADSD_VOICE_GENDER_BY_ID = {
    **{vid: "male" for vid in ADSD_MALE_VOICE_IDS},
    **{vid: "female" for vid in ADSD_FEMALE_VOICE_IDS},
}

# P3 音色库智能匹配 — speaker name 关键字 → voice_assets.json 注册的 voice_id
# 顺序敏感：从上到下，第一个命中 keyword 的 entry 决定 asset。
# 排除歌声/混音/高风险公众人物（这些有专用 voice_id 但不放在通用 keyword 映射）
ADSD_SPEAKER_KEYWORD_TO_ASSET: list[tuple[list[str], str]] = [
    # 公众人物音色：仅在脚本显式标注 Trump/特朗普/川普 speaker 时命中；默认不会自动使用
    (["Trump", "Donald Trump", "特朗普", "川普"], "external_trump_tiktok_001"),
    # 法学 / 讲师 / 教授 / 旁白（沉稳叙述）
    (["法学", "律师", "讲师", "教授", "讲座", "理性", "罗翔", "旁白", "末日旁白", "解说", "总叙", "总结者", "narrator", "Narrator"], "external_luo_xiang_xyma_001"),
    # 知识型访谈 / 经济 / 作家 / 评论
    (["学者", "知识", "评论", "作家", "记者", "访谈", "许知远", "经济学家", "社会学家", "历史学家", "评论员"], "external_xu_zhiyuan_xyma_001"),
    # 科技 / 企业家 / 工程师 / 投资人 / 合伙人
    (["工程师", "科学家", "CEO", "投资", "企业家", "硅谷", "技术", "黄仁勋", "Jensen", "合伙人", "创始人", "VC", "GP"], "external_huang_renxun_fzh_001"),
    # 玄幻 / 古风长者 / 道士 / 牧神记男角 / 村长 / 修仙宗主
    (["道士", "玄幻", "宗师", "长者", "修真", "高人", "老人", "前辈", "老者", "绫璟", "道人", "村长", "教主", "宗主"], "external_mushenji_lingjing_001"),
    # 年轻男 / 弟子 / 学生 / 秦牧
    (["弟子", "学生", "少年", "孩子", "小子", "秦牧"], "external_mushenji_qinmu_001"),
    # 古装女 / 公主 / 夫人 / 虞渊初雨
    (["公主", "王后", "嫔", "贵妃", "千金", "夫人", "娘娘", "格格", "虞渊", "初雨"], "external_mushenji_chuyu_001"),
    # 影视演员 / 戏剧对白 / 民间老头 / 江湖匠人
    (["演员", "戏剧角色", "戏中人", "黄渤", "药师", "医师", "郎中", "铁匠", "屠夫", "船工"], "external_huang_bo_tiktok_7550564384750210321"),
    # 台湾国语 / 感情戏男
    (["台剧", "台湾", "感情戏"], "external_tiktok_comedydramatw_male_001"),
    # 印尼华侨 / 东南亚口音
    (["印尼", "华侨", "东南亚"], "external_mettsarchive_indo_chinese_speakerB_001"),
    # 街访 / 都市女
    (["街访", "都市女", "路人女", "市民女", "都市感"], "external_tiktok_urban_talk_7618042272130600212"),
    # 旅游 / 短视频女
    (["旅游", "向导女", "vlogger"], "external_tiktok_nghithao_0208_7624063339613752594"),
    # 干货 / 培训女
    (["电商", "培训", "干货", "讲解师", "运营"], "external_tiktok_ecom_female_001"),
    # 短视频高能女
    (["主播", "网红", "活力女"], "external_tiktok_fjl9fl6_7621754156704959765"),
]
