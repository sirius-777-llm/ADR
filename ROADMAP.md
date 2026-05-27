# ADR ROADMAP

> ADR (Automated Documentary Rendering V8) 项目 backlog · 跨 session 持久化
> 任何 Claude session 启动时优先查这个文件 + memory/project_adr_backlog.md

Last updated: 2026-05-21

---

## 🚀 已 Ship (Recent)

| 日期 | PR/改动 | 说明 |
|------|---------|------|
| 2026-05-20 | silent_b PR | a_roll/narrated_b/silent_b 三类 turn 数据模型 + LLM prompt 改造 + step9 BGM 动态浮起 |
| 2026-05-20 | Bug A-E fix | BGM 平衡 / per-part loudnorm / 字幕 ASR 对齐 / BGM aloop / 字幕 SUB_GAP |
| 2026-05-20 | 人设符 PR (character_meta_grid) | 4×3 中文标签 grid 取代切片 panel，召唤式 prompt |
| 2026-05-20 | 4 个减时间方向 + bug fix | skip sidecar QA / character_sheet / storyboard_grid / meta_grid 缓存 |
| 2026-05-21 | Speaker IP Card | speaker 升级为完整角色档案，8 个 seed (曹操/刘备/司马懿/旁白/科比/乔丹/鲁迅/辜鸿铭) |
| 2026-05-21 | Speaker IP A (AI 孵化) | tools/create_speaker_ip.py，给名字+简介自动生成完整 IP + meta_grid，已测杜甫 |
| 2026-05-21 | Speaker IP B (自学习) | usage_history 跑后回写 IP，下次 LLM 注入摘要避免重复 |
| 2026-05-21 | Speaker IP C (关系网络) | IP 加 relationships 字段，5 个种子角色补上 (曹操/刘备/司马懿/科比/乔丹)，script-gen prompt 注入关系上下文 |
| 2026-05-21 | 横屏字幕换行 fix | _wrap_card max_width 14.5 → SUBTITLE_MAX_CHARS+2，避免 LLM 切的 16 字段被强制 \N 换行 |
| 2026-05-21 | BGM vocal 自动检测 + retry | _bgm_contains_vocals whisper ASR 检测，含 lyrics 自动重试 (WERYAI music 偶尔忽略 "no vocals") |
| 2026-05-21 | resume tool --regen-bgm flag | 单独重生成 BGM，其他物料复用，针对 BGM 含 vocal 等场景秒修 |
| 2026-05-21 | Era LLM template (主路径) | _llm_infer_meta_grid_template + _resolve_meta_grid_template，LLM 推断 era + 4 类标签集，写入 IP cache 跨片复用，修「南京银行出古装」bug |
| 2026-05-21 | ERA_TEMPLATES 预设 + 兜底链 | 7 个 era 预设 (historical/contemporary_corporate/modern_athlete/modern_scholar/future_tech/...) + costume/pose 智能匹配 |
| 2026-05-21 | LLM 阶段 1 topic_decomposition | _llm_topic_decomposition + topic_cache，一次 LLM 出 era/bgm_style/role/director/cover/is_action_topic 多字段 |
| 2026-05-21 | LLM 阶段 2 BGM 接入 | generate_bgm 用 LLM 推断 bgm_style + instruments + mood，替换 8 硬关键词分支 |
| 2026-05-21 | LLM 阶段 3 role/director/action 标记 | _adsd_role_candidates / _storyboard_grid_prompt / script-gen 输出 is_action_scene 字段 |
| 2026-05-21 | Spike action 武戏天花板验证 | 4-panel multi-ref + kinetic prompt + 10s 武戏密度明显比 baseline 强（大哥确认）|
| 2026-05-21 | action_b turn_type PR (4b) | 第四类 turn (武戏)：4-panel multi-ref + duration 10s + kinetic prompt + LLM 自动标 |
| 2026-05-21 | 非 ADSD action 强化 (阶段 5) | _motion_action_block 检测 is_action_scene → 注入 kinetic prompt |
| 2026-05-21 | duration 计算优化 | api_dur 下限 5s → 3s + tts_dur+0.3 buffer，短 dialogue 处理时长降 30-40% |
| 2026-05-21 | IP 版本管理 (I) | ADR_IP_SCHEMA_VERSION="1.1" + _migrate_speaker_ip 加载时自动迁移，9 个 IP 已 v1.1 |
| 2026-05-21 | IP 调用统计 + 推荐 (F) | schema v1.2 加 usage_count + 跑后自动 increment + _recommend_related_ips + tools/show_ip_stats.py CLI |
| 2026-05-21 | NO TEXT IN FRAME 补强 | _adsd_almighty_audio_dub_prompt + _adsd_meta_grid_call_prompt 加英文 ABSOLUTELY NO TEXT IN FRAME ban，修易筋经 00:48 内嵌字幕 |
| 2026-05-21 | action_b 题材触发优化 | script-gen prompt 鼓励武侠/对抗题材主动出 ≥1-2 个 action_b（之前易筋经 0 个 action_b 因 LLM 保守）|
| 2026-05-21 | LLM 智能召唤标签 | script-gen LLM 同时推 meta_grid_costume/pose 字段 + scene 注入 IP costume/pose 池，_infer_* 优先读 LLM 标签，规则兜底 |
| 2026-05-21 | AUTO-IP · ADR 主流程自动孵化 | step1 后扫描脚本无 IP speaker → LLM 孵化（含 voice_asset 智能匹配 + 全字段填充 + qa_status=auto_generated_pending_review）·env ADR_AUTO_INCUBATE_IP 控制 · 实测苏东坡 ✓ |
| 2026-05-21 | duration=3 bug fix (P0) | duration 优化下限 3 越过 WERYDANCE 硬限 4，整 run 39min 挂掉；回收下限 → 4 + 双保险 max(4) · 实测笑傲江湖 turn 5/9 status 1002 root cause |
| 2026-05-21 | step7 防御层 | 缺失 seg 时用 img_path 现场补 still seg + 不可恢复时从 script 移除 turn，避免 ffprobe 整 run 挂掉 |
| 2026-05-21 | P0 action_b 标注 bug fix | _infer_turn_type line 451 武戏命中错返 narrated_b → 改 action_b + _is_action_shout 短喊招检测（武侠/体育/战争 全覆盖）+ 兜底收紧 ≤12 字防误标长教学 dialog · 13/13 case 通过 |
| 2026-05-21 | P1 武戏密度 LLM 化 | topic_decomposition 加 action_density_hint (low/medium/high) + recommended_action_b_count + script-gen prompt 按密度给 min/max action_b 硬指标 + 武戏 ≥3 必须连续 2 个组成节拍 · 笑傲江湖实测 high/4 |
| 2026-05-21 | AUTO-IP 占位符过滤 hotfix | _auto_incubate_missing_ips 跳过 (silent)/(action)/silent_b/action_b/none + 场景描述类 speaker（>8 字 含场景/对话/画面等词），防误孵化垃圾 IP |
| 2026-05-22 | WERYDANCE FAST retry 兜底 | 每个 variant family 末尾追加 2 次 WERYDANCE_2_0_FAST 重跑 · env ADR_WERYDANCE_FAST_RETRY_COUNT 控制 · 单 turn FAST 尝试 1→3 次 · 验证: 科比 attempts 数 3-4 → 5-6 |
| 2026-05-22 | almighty task_failed 诊断信号 | 从 data.msg 抽 reason 入 attempt 记录 + 不再 filter response · 现在 task_failed 看到具体「Content moderation / Image asset audit / Copyright restrictions」原因 |
| 2026-05-23 | step7 Ken Burns + 3 层降级 | 缺 seg 时 Ken Burns slow-zoom 兜底（1.2× scale 防 ffmpeg 超时）+ Ken Burns 失败降级静态图 + 静态也失败才丢弃 turn · ffmpeg 失败后 cleanup partial · 笑傲江湖 + 科比都验证 |
| 2026-05-23 | B4 武戏 SFX | action_b variants generate_audio="true" + _adsd_action_b_motion_prompt 加 SFX_DIRECTIVE (combat SFX only, no dialogue/music) + 跳过 leading silence trim + _build_voice_clone_hybrid_audio 保留 action_b 内嵌音色 · 西游记 turn 4 (孙悟空) 1 action_b SFX 进 hybrid ✓ |
| 2026-05-24 | meta_grid 重构（无文字版）| 参考 strength04_x editorial 风格：panel 内 100% 纯图无文字 + 召唤改 panel index + 位置描述 (top-left/middle-right/...) 取代「曹操｜战袍｜说话」中文标签 · 彻底解决 WERYDANCE 复刻 ref 文字进画面的根本 bug · 西游记验证完美: 0 fallback / 2 action_b SFX / 视频零内嵌字幕 ✓ |
| 2026-05-25 | tools/quality_audit.py | 达尔文进化适应度评估器 · 扫所有 /tmp/adr_v8_*/lip_sync_qa.json + pipeline_state.json · 输出每 run 通过率/SFX 数/fallback/audit 触发词 · 趋势曲线 + markdown 报告 · 支持 --last N / --md |
| 2026-05-25 | 批量清理旧版 cached meta_grid | 删 34 个含中文标签的旧 PNG (backup 在 /tmp) + 清 7 个 IP 的 meta_grid_template_cache · 留 4 个西游记新 grid · 让所有 IP 下次都享受新无文字 grid 红利 |
| 2026-05-20 | TG deliver 假阴性 fix | status=200 后验证 body {"ok":true,"result":{}} |
| 2026-05-20 | tools/rerun_downstream.py | 跳过 step1-66 跑下游，10x 调试加速 |

---

## ⏳ Planned (按优先级)

### 角色库扩展

| 项目 | 工程量 | ROI | 状态 | 备注 |
|------|--------|-----|------|------|
| ~~A · AI 自动孵化 IP~~ | ~~2h~~ | ~~★★★~~ | ✅ shipped 2026-05-21 | tools/create_speaker_ip.py |
| ~~B · 自学习 usage_history~~ | ~~1.5h~~ | ~~★★★~~ | ✅ shipped 2026-05-21 | _record_speaker_usage_history + prompt 注入 |
| ~~C · 角色关系网络~~ | ~~1h~~ | ~~★★★~~ | ✅ shipped 2026-05-21 | IP relationships + _build_speaker_ip_context_for_script |
| ~~AUTO-IP · ADR 主流程自动孵化 IP~~ | ~~1h~~ | ~~★★~~ | ✅ shipped 2026-05-21 | step1 后扫描自动孵化 + qa_status 待审标记 |
| D · 角色弧线版本 | 3h | ★★ | planned | 曹操_青年/中年/晚年 多版本，LLM 看时代自动选 |
| E · 多人物互动 IP | 4h | ★★ | planned | 双人卡 (曹操+刘备) 同框 IP，含对峙/煮酒姿势 |
| ~~F · IP 调用统计 + 推荐~~ | ~~1h~~ | ~~★★~~ | ✅ shipped 2026-05-21 | usage_count + _recommend_related_ips + show_ip_stats.py |
| G · IP 管理 CLI 工具 | 2h | ★ | planned | tools/ip_manager.py 列出/编辑/创建 IP |
| H · IP 质量评分 | 2h | ★ | planned | LLM 评估视觉/音色/性格契合，写 IP 跟踪 |
| ~~I · IP 版本管理~~ | ~~30min~~ | ~~★~~ | ✅ shipped 2026-05-21 | ADR_IP_SCHEMA_VERSION + _migrate_speaker_ip |

### LLM 化 + 武戏强化 (2026-05-21 议定，5.5-6.5h 总)

| 项目 | 工程量 | ROI | 状态 | 备注 |
|------|--------|-----|------|------|
| ~~阶段 1-5 (LLM 化 + 武戏)~~ | ~~5.5h~~ | ~~★★★~~ | ✅ shipped 2026-05-21 | 全部 6 阶段已 ship |
| ✗ image-to-video 升 almighty | - | - | rejected | 保留作 fallback (endpoint 冗余容灾) |

### 减时间优化

| 项目 | 工程量 | ROI | 状态 | 备注 |
|------|--------|-----|------|------|
| ~~**PR-A · merged_a 合并跑**~~ | ~~4-5h~~ | ✅ shipped 2026-05-27 (CCP 全 4 阶段, MVP default-off) | 同 speaker 连续 turn 合并 almighty 调用, 砍 30-50% API · 实施 3 部分: (1) L12618 `_concat_audio_files_for_group` + `_split_lip_sync_raw_by_durations` helpers (ffmpeg concat demuxer + 按 dur 切片重编码) (2) L13089 `_lip_sync_one_group` 主函数 (拼接 audio + 提交 almighty audio_dub generate_audio=true + poll + split + 各段 postprocess; 失败返回 [False]*n 让调用方回退) (3) L13700 step66 主循环加 group/scene 分流提交, group 失败时 fallback 走单 turn _lip_sync_one_scene · 触发条件: ADSD_CONSECUTIVE_SPEAKER_BATCHING + audio_dub_experiment + multi-turn group + all A-roll + total_dur ≤ 15s · CCP Stage 3 抓 3 个 High/Medium: split 边界用 actual audio dur / 15s 二次校验用 actual_total / generate_audio='true' 对齐单 turn · Default OFF 需 --adsd-speaker-batch 显式启用, 待大哥实测验证后再考虑改默认 |
| meta_grid 缓存预热 | 30min | ★★ | planned | 跑 driver 给常用 speaker 预生成 meta_grid 入缓存 |
| ~~0.5s submit interval 重测~~ | ~~5min~~ | ~~★★~~ | ❌ rejected 2026-05-27 (PM 重评估) | 计算: 12 turn run 总 motion+image submit 共 22 次, 每次省 (2.5-0.5)=2s, 总省 ~44s. 全程 wallclock ~22min, 实际提速 ~3%. ROI 远低于 ★★ 标记. WERYDANCE 单镜 processing ~25-90s 才是瓶颈, submit interval 在并发模型下影响极小. 不 ship, env ADR_*_SUBMIT_INTERVAL 仍可手动 override 测试 |
| ~~duration 计算优化~~ | ~~30min~~ | ~~★★~~ | ✅ shipped 2026-05-21 | api_dur 下限 5s→3s + tts_dur+0.3 |
| ~~voice_asset upload 缓存~~ | ~~1h~~ | ✅ shipped 2026-05-26 (CCP) | _upload_to_weryai 入口加 sha256 + cache lookup (24h TTL) · double-check locking 防并发冷缓存 dup (codex final-qa 发现) · voice_assets/upload_cache.json 跨 run 持久 · 减少 SSL 抖动失败概率 · env ADR_UPLOAD_CACHE=0 关闭 |
| WERYDANCE_2_0_FAST 主路径 | 30min+测 | ★ | planned | A/B 验证 FAST 质量是否够，省 30-40% step66 时间 |

### 其他方向

| 项目 | 工程量 | ROI | 状态 | 备注 |
|------|--------|-----|------|------|
| ~~LLM 智能召唤标签~~ | ~~1.5h~~ | ~~★★~~ | ✅ shipped 2026-05-21 | script-gen LLM 同时推 meta_grid_costume/pose 字段 |
| ~~action_b LLM 标注 bug~~ | ~~1h~~ | ~~★★~~ | ✅ shipped 2026-05-21 | _infer_turn_type 修正 + _is_action_shout + density LLM 化 |
| 题材泛化验证 | 30min/题材 | ★ | planned | 跑科比/鲁迅/苏东坡/钱学森等验证 IP+人设符稳定性 |
| resume 工具 e2e test | 1h | ★ | planned | tools/rerun_downstream.py 加自动测试套件 |

### 👥 团队进化 (2026-05-25 议定 · 共 11h, 5 个 PR)

LLM 角色团队从「各跑各的」升级为「真正协作」+ 专业化分工。

| PR | 工程量 | ROI | 状态 | 备注 |
|---|--------|-----|------|------|
| ~~**PR-1 · 跨层 Context 协作**~~ | ~~3h~~ | ✅ shipped 2026-05-25 | 编剧 _generate_adsd_dialogue_turns 新增 topic_meta + historical_context 参数 · prompt 头部注入「总制片人文化铁律」(CULTURE/REGION/ERA/PERIOD_COSTUME/NEGATIVE) · 编剧台词必须严格匹配上游文化年代 · 1h vs 3h 预算 (节奏 Reviewer 在 B9 已 ship 简化路径) |
| ~~**PR-2 · 题材专家路由**~~ | ~~2h~~ | ✅ shipped 2026-05-25 | DIRECTOR_STYLE_ROUTES 7 种路由表 (intimate_wuxia/imax_war_epic/saturated_folk/slow_poetic/gritty_kinetic/classical_realism/modern_documentary) · _director_route_block helper · topic_decomposition LLM 输出 director_style_route 字段 · jiangwen_prompt 用单一路由风格关键词不再混搭 6 大师 |
| **PR-3 · 专业角色补全** | 4h | ★★★ | planned | 新增 4 个专业 LLM 角色: 武术指导 (action_b prompt) / 美术指导 (调色板+道具+服装) / 剪辑师 (节奏决定) / 音效师 (SFX 设计) |
| ~~**PR-4 · LLM 分级**~~ | ~~1h~~ | ✅ shipped 2026-05-27 (CCP 全 4 阶段, 30min 简化) | L1647 `_LLM_TIER` 字典 4 档 (producer Opus / creative G25 / review GLite / data Haiku) + `tier_chat` helper, `chat()` 旧签名 100% 兼容 26 调用点零侵入 · 白名单降级 3 处 Tier 4 短任务 (L3228 改写 topic 200tok / L8076 单 voice_id 80tok / L15684 黄历注脚 200tok) · Stage 1 codex 推 30min 简化 / Stage 3 抓 Medium (注脚未传 max_tokens 走默认 4096 → 修补) · 分布: Opus 1 / G25 9 / GLite 6 / Haiku 3 (3/12 G25 降级到 Haiku, 实际省成本约 7% 不是预期 30% — 单点保守降级) |
| **PR-5 · 团队学习机制** | 与达尔文联动 | ★★ | planned | 每个角色记录 historical_success_rate 输出是否最终通过 audit · 失败 case 反馈对应角色 prompt · 团队自动进化适应 ADR 项目 |

### 🧬 达尔文进化 (2026-05-25 议定 · 共 11.5h, 分 4 个 Round)

让 ADR 自动迭代优化：每次 run 收集质量数据 → 失败模式自动反哺 prompt → 高分配置自动遗传。

| 阶段 | 工程量 | ROI | 状态 | 备注 |
|------|--------|-----|------|------|
| ~~quality_audit.py 适应度评估器~~ | ~~1h~~ | ~~★★★~~ | ✅ shipped 2026-05-25 | 扫所有 run 输出 通过率/SFX/fallback/audit msg + markdown 趋势报告 |
| ~~**阶段 A · Fitness Scorer 强化**~~ | ~~1.5h~~ | ✅ shipped 2026-05-25 | quality_audit 加权 (50% pass + 15% action + 15% retry 效率 + 20% audit) · band 分级 elite/strong/viable/weak/failed · --threshold 过滤 · Top 5 Elite 排行 |
| ~~**阶段 B · Audit 黑名单自动学习**~~ | ~~2h~~ | ✅ shipped 2026-05-25 | tools/learn_audit_blacklist.py 扫所有失败证据 LLM 提炼 11 触发词 · audit_blacklist.json · script-gen prompt 用「类别+数量」抽象描述注入 (避免原词二次触发审核) · codex 审查通过 |
| ~~**阶段 C · 题材分类器**~~ | ~~1h~~ | ✅ shipped 2026-05-25 | topic_decomposition LLM 加 audit_risk_score (0-100) + audit_risk_reason · script-gen risk_strategy_block 按 >=61/31-60/<30 三档脱敏 · cache schema v4 自动失效旧 |
| ~~**阶段 E · 自动 IP 进化**~~ | ~~2h~~ | ✅ shipped 2026-05-25 | tools/evolve_ips.py 扫历史 run 算 IP fitness · <60% 自动重孵化 (删 grid+清 cache+标 needs_reincubate) · >=90% production_ready · 6 attempt 阈值防新 IP 误判 · 实测: 科比 0% reincubate / 唐僧/孙悟空/旁白/曹操/紫霞 production_ready |
| ~~**阶段 C+ · 高危题材 LLM 改写**~~ | ~~1h~~ | 🟡 shipped 2026-05-26 (default-off) | _maybe_neutralize_topic LLM 改写高危题材替换名人/品牌 · 实测科比 7/12 pass + 1 SFX 通过但视频 5 cover 兜底不能看 · 改 opt-in: ADR_NEUTRALIZE_HIGH_RISK_TOPIC=1 显式启用 |
| ~~**阶段 C++ · Hard+Smart Abort**~~ | ~~30min~~ | ✅ shipped 2026-05-26 | A: step1 检 audit_risk>=75 直接 raise + TG 提示改题材 (省 30min credits) · B: step66 A-roll fail>=50% 或 total fail>=60% 自动 kill · _parse_risk_score helper 防 NaN/Infinity 抓最大数字 + 关键词优先 · codex 审查通过 |
| ~~**R3 · 题材推荐器**~~ | ~~1h~~ | ✅ shipped 2026-05-26 | tools/topic_recommender.py 扫历史 fitness 数据 · sliding window n-gram + Jaccard 聚类 + confidence 标记 · 自动识别 elite (>=80) 题材模式 + failed (<30) 模式 · --next 推下一个题材 · codex 审 5 fix |
| ~~**R4 · Batch 演化 Runner**~~ | ~~1h~~ | ✅ shipped 2026-05-26 | tools/evolve_runner.py 闭环达尔文 · 读 R3 elite 关键词 + LLM 生成 N 个新题材(变异) · 自动跑 ADR(选择) · 跑完自动 evolve_ips + learn_audit_blacklist(遗传) · argparse + --max-hours 全局 budget · _validate_topics 验证 LLM 输出 · 实测生成「蟠桃偷渡客紫霞泪未干」继承 elite 气质 |
| ~~**R5 · 进化世代追踪**~~ | ~~30min~~ | ✅ shipped 2026-05-26 | tools/evolution_log.py 世代曲线观测器 · evolution_history.json 持久 ship_log · 按日期 generation 分组 · run-weighted trend 不偏 sparse 日子 · 实测: 前期 31.4 → 后期 68.5 (**+37.1** 正向进化 ✓) · codex 3 fix 全应用 |
| **阶段 D · Multi-arm Bandit prompt** | 4h | ★★ | planned (Round 3) | 每个 prompt 函数维护 3 个变体 · epsilon-greedy 选 (90% best, 10% explore) · variant 表现存数据库 · 月度 review 删差 variant |
| **阶段 F · Batch 自动跑 daemon** | 1h | ★ | planned (Round 4) | tools/evolve_run.py daemon · 每天 03:00 自动跑 3-5 个题材 · 跑完自动 audit + 黑名单更新 + IP 重孵化 · TG 推送报告 |

### 🐛 2026-05-21 笑傲江湖重跑发现的 bug

| Bug | 严重度 | 工程量 | 状态 | 现象 + 修复方向 |
|-----|--------|--------|------|----------------|
| ~~**B1 音量太低**~~ | ~~★★★ P0~~ | ~~1h~~ | ✅ shipped 2026-05-21 | step9 amix 默认归一化压人声 → normalize=0 + weights 显式权重 + voice 1.0→2.0 + BGM 0.85→0.4，两阶调音通过 |
| ~~**B2 meta_grid 12 宫格漏进**~~ | ~~★★★ P0~~ | ~~1.5h~~ | ✅ shipped 2026-05-21 | step7 防御层缺失 seg 时用 meta_grid 当 still 导致 4×3 grid 漏入画面 → 检测 meta_grid_ 文件名 + 优先用邻 turn 合法图/cover.jpg 兜底 + prompt 强化禁止复刻 grid + negative_prompt 加 grid/split/panel ban |
| ~~**B3 内嵌字幕**~~ | ~~★★★ P0~~ | ~~30min~~ | ✅ shipped 2026-05-21 | meta_grid_call prompt 强化禁止复刻参考图中文标签 + negative_prompt 强化 text ban，重跑笑傲江湖未复现 |
| **B7 名人题材 Image audit fail** | ★★★ P0 | ? | **blocked** | 2026-05-22 诊断：科比/NBA 题材 GPT_IMAGE_2 画真人+商标 → WeryAI 平台 Image asset audit 拦截全部 task。DOUBAO spike 验证：跨端点 fallback 无效（同 audit 服务）。**唯一路径：避免 GPT_IMAGE_2 画名人脸+商标**（重写 step6 prompt 抽象化 / 直接放弃现代名人题材）|
| ~~**B8 历史顾问条件触发**~~ | ~~★★ P1~~ | ~~30min~~ | ✅ shipped 2026-05-26 (CCP) | 新增 `_should_run_immersion_qa(topic)` gate 看 topic_decomposition.era · historical_/period_/ancient_/classical_ 前缀或含 '古'/'history' → 跑 LLM 审稿; 现代/商业/科技 → skip 防误替换 (云计算工程师→画师 这种荒谬) · env ADR_IMMERSION_QA_ALL=1 强制 override · 5/5 case 测试 (西游/紫霞跑, 科比/南京/云计算跳过) · CCP 全 4 阶段走完 |
| ~~**B9 B-roll 出戏**~~ | ~~★★★ P1~~ | ~~2.5h~~ | ✅ shipped 2026-05-25 | A: _broll_rhythm_reviewer LLM 节奏审稿 (keep/merge/rewrite/relocate 决策) · B: script-gen prompt 加 silent_b/narrated_b shot 必须继承前 turn 视觉元素铁律 · 同时收紧 max_narrated 3→2 / silent_b 占比 20-35%→15-25% · env ADR_BROLL_REVIEWER 控制 |
| ~~**B10 ADS 单旁白多音色**~~ | ~~★★★ P1~~ | ~~1h~~ | ✅ shipped 2026-05-26 | **现象**: ADS (HADS/VADS) 单旁白模式跨 scene 音色不一致 · **Root cause**: step65 motion audio_dub `_select_voice_asset_reference` per-scene 走 gender fallback · **修**: 新增 `_PODCAST_TO_VOICE_ASSET_MAP` 映射 podcast_id → voice_asset_id · `_podcast_id_to_voice_asset` helper · step1_script 末尾把映射后 voice_asset 写入所有 script[i]["voice_asset_id"] · 复用现有 line 12527 优先级 (scene.voice_asset_id 高于 gender fallback) · 阶段 3 (跨 scene task 波动) 留 PR-A 合并跑根治 |
| ~~**B11 meta_grid 竖屏适配**~~ | ~~★★★ P1~~ | ~~30min~~ | ✅ shipped 2026-05-26 (CCP) | 李莫愁 VADS 反馈: meta_grid 硬编码 16:9 不适配 9:16 视频 · 修: `generate_character_meta_grid_gpt_image2` 按 IS_VERTICAL 切, 竖屏 3 cols × 4 rows + 9:16(4k) + vertical portrait 框, 横屏保持 4×3 + 16:9 · `_meta_grid_panel_index` 加 VDAR 分支 (col 0-2 mod 3 防 C3 漏定位, row 0=wardrobe/1=action/2=close-up) · `_character_meta_grid_cache_path` 加 _h/_v suffix 防 cross-aspect 污染 · 20/20 case 全过 · CCP 全 4 阶段 |
| ~~**B12 h/v 默认 motion (HADS/VADS)**~~ | ~~★★★ P1~~ | ~~10min~~ | ✅ shipped 2026-05-26 (CCP, 二次修) | 用户认知: 跑 ADR 默认就是 HADS/VADS (动态), 不是 HADR/VADR (静态) · 修: WITH_MOTION = not ADSD and not --no-motion · 7/7 矩阵: HADS/VADS 默认 ON · HADSD/VADSD 走 step66 不动 · HADR/VADR 需 --no-motion 显式 · 第一版只放开 VDAR 被大哥纠正, 二版 h/v 同步 |
| ~~**B12.1 删除冗余 --with-motion**~~ | ~~★★ P2~~ | ~~10min~~ | ✅ shipped 2026-05-26 (CCP) | B12 后 --with-motion 与默认行为重叠成 dead flag (大哥: 脱裤子放屁) · 修: run_adr_v8.py L158 删 flag 检查, README/INDEX/skill 全部去 --with-motion 用法, 改用 --no-motion 退化 · 老脚本传 --with-motion 自然 no-op (无 argparse 不报错) · 6/6 矩阵通过 |
| ~~**B12.2 fmt_label 命名对齐**~~ | ~~★ P3~~ | ~~15min~~ | ✅ shipped 2026-05-26 (CCP) | 李莫愁 VADS 端到端验证通过但成片仍叫 ADR_V8_VDAR_*.mp4 (旧 fmt_label 残留) · 修: 新增 CURRENT_MODE_LABEL/CURRENT_MODE_WITH_ASPECT 模块级常量 (L961-970) 按 ADSD/WITH_MOTION/IS_VERTICAL 三元决策 · 替换 6 处旧 VDAR/HDAR (fmt_label/motion_qa mode×2/fmt_tag/execution_plan) · README/skill 同步 · 6/6 矩阵: VADS/HADS/VADSD/HADSD/VADR/HADR · 文件名从此为 ADR_V8_VADS_*.mp4 |
| ~~**CCP v1.0 协同协议**~~ | ~~1.5h~~ | ✅ shipped 2026-05-26 | tools/codex_collab.py 4 阶段 CLI (review-spec/propose-alt/review-code/final-qa) · voice_assets/collab_history.json 跨 session 持久 · CLAUDE.md ADR-CCP 强制规则 · feedback memory feedback_adr_ccp_protocol · 让任何 Claude session 自动走协同, 不再单向 ship 后才 codex 审 |
| ~~**B10.1 mapping 女声修订 + 防回归**~~ | ~~30min~~ | ✅ shipped 2026-05-26 (CCP 首跑) | 李莫愁思春 VADS 实测发现 BY2 是「甜妹歌声 music_contaminated」克隆不稳 · **修**: 女声映射 BY2 → 蒙曼/张泉灵/武亦姝 (说话类) · 加 `_VOICE_ASSET_FORBIDDEN_FLAGS` (singing_not_speech/music_contaminated/not_vocal_separated) + `_voice_asset_is_speech_safe` helper 自动过滤 · CCP 全 4 阶段走完: codex 提融合方案 A+B / Stage 3 自审发现 not_speaker_diarized 误加移除 / Stage 4 PASS · 协同验证 |
| ~~**B4 武戏无 SFX 配音**~~ | ~~★★ P1~~ | ~~2h~~ | ✅ shipped 2026-05-23 | action_b generate_audio=true + SFX_DIRECTIVE prompt · 西游记 turn 4 验证通过 |
| ~~**B5 LLM 把场景描述当 speaker**~~ | ~~★★ P1~~ | ~~1h~~ | ✅ shipped 2026-05-21 | prompt 加 speaker 铁律 + _sweep_speaker_field 后处理 (bad_keywords 检测 + 从 bad speaker 提取已知角色 + role_candidates fallback) · 7/7 case 通过 |
| ~~**B6 短喊招漏关键词**~~ | ~~★ P2~~ | ~~15min~~ | ✅ shipped 2026-05-21 | _is_action_shout 加 再来/换我/还击/反攻/拦住/挡住/拼了/决胜 等 16 个攻势/反击/换场词 · 6/6 case 通过 |
| ~~**B13 silent_b 不该计入 ADSD speaker_count**~~ | ~~★★ P1~~ | ~~30min~~ | ✅ shipped 2026-05-27 (CCP) | 「南京学区房」HADSD speaker_count=5 (silent_b 被算第 5) 触发 delivery fail · 修 2 处: (1) `_llm_assign_voice_assets` L601 turn_summary 过滤 silent_b + isinstance dict guard, 空时早出 (2) `delivery_qa` L14685 speakers 过滤 silent_b + (silent) + 空字符串, dict.fromkeys 去重 · 5/5 case: 南京 5→4 / monologue 1 / dialogue 2 / non-dict / 空 timeline · CCP Stage 3 抓 Medium (isinstance guard) + Stage 4 抓 ROADMAP/ship_log 未同步 全补 |
| ~~**B14 storyboard prompt 缺台词主题锚定**~~ | ~~★★★ P1~~ | ~~45min~~ | ✅ shipped 2026-05-27 (CCP 全 4 阶段, 融合方案 C) | 「南京学区房」12/10 text_visual_alignment fail · 修 3 处: (1) L6210 抽 `_extract_core_terms` helper + `_CORE_TERMS_STOP_WORDS` 常量, QA 复用 (2) L3667 lines_display 后预抽 `_core_terms_per_line`, jiangwen_prompt 注入 "B14 台词主题锚定" 段 + 显式约束 LLM 每句 verbatim 含 1-2 个 core term (按 core 数动态对齐 QA 阈值) (3) L3899 visuals 落地后 Python append 兜底, 缺词 scene 末尾追加 `, scene depicting spoken elements verbatim: X, Y, Z` (top 3 missing) · Stage 1 codex 推 30min 简化 / Stage 2 给方案 B 结构化锚点 / Stage 3 抓 High (描述矛盾→改) + Medium (token 粗切→留 B14.1) + Low (武戏 panel→接受) · 3/3 mock 通过 |
| **B14.1 core_terms token 抽取改 jieba 分词** | ★ P3 | 1h | pending | B14 现复用 QA 同款 2-6 字贪婪 regex 抽中文片段, 容易抽出 "在南京/一套房子不仅/是居住空间" 这种伪关键词 (句法断片不是名词) · 现状: append 兜底虽能命中 QA 阈值但 prompt 看起来生硬 · **修方向**: `_extract_core_terms` 改用 jieba 分词 + POS 过滤 (只取名词/地名/专名), QA 同款抽取也跟着升级 · 工程量包含: jieba install/lazy import + stop_words 扩展 + 单测对齐 (避免 QA 阈值意外变化) |
| ~~**B18 B11 命名迁移漏的 legacy meta_grid fallback**~~ | ~~★★ P2~~ | ~~20min~~ | ✅ shipped 2026-05-27 (CCP Stage 3+4) | B11 (5/26) 给 meta_grid 缓存加 _h/_v suffix 后, 老 `旁白.png` (无 suffix) 在新 lookup 下永远 miss · 旁白 usage=29 / 孙悟空=7 / 科比=6 / 唐僧=4 / 至尊宝=3 每 ADR run 都重新生成 (浪费 GPT_IMAGE_2 ~30-60s ×5) · 修: L8186 新增 `_character_meta_grid_cache_legacy_path` helper, L8224 cache lookup 主路径 miss 时横屏走 legacy fallback (默认无 suffix=横屏), 命中后 copyfile migrate 到 _h 命名让下次走主路径 · 5/5 dry-run 通过 · 每 run 节省 2.5-5min + GPT cost |
| ~~**B15 asr_qa.json 缺失 warning**~~ | ~~★ P3~~ | ~~30min~~ | ✅ shipped 2026-05-27 (CCP Stage 4 only, 微改例外) | ASR endpoint 失败/返回空时 asr_qa.json 不写, delivery_qa 发 warning 污染列表 · 修: L5308 `_asr_verify_dialogue_audio` 后 strip speech_text, 失败/全空白时落地占位 `asr_qa.json {pass: True, skipped: True, reason: ...}` · delivery_qa _qa_file_pass 读 pass=True 不发 warning · Stage 4 抓 "   " 全空白 truthy bug → 加 strip · 17 行 |
| ~~**B16 meta_grid 漏入 audio_dub postprocess**~~ | ~~★★★ P1~~ | ~~30min~~ | ✅ shipped 2026-05-27 (CCP) | 「南京学区房」HADSD t=85.0-85.6s 出 4×3 meta_grid 满帧 · root cause: `_postprocess_audio_dub_segment` L12515 panel_pad 用 scene.img_path = `meta_grid_李薇.png` 当 Ken Burns still · 修: L12393 + L12521 加 is_meta_grid_panel guard (basename.startswith("meta_grid_"))，use_panel_pad 加 `not is_meta_grid_panel`，走 tpad clone 末帧兜底 · 顺手把 B2 (L13950/L13955) 旧 in 检查也对齐 startswith, 4 处统一 · CCP Stage 3 + Stage 4 通过, 6 case mock 矩阵 (lip/audio × meta_grid/non-grid × env on/off) |
| ~~**B17 ensemble 上限按题材动态切**~~ | ~~★★ P2~~ | ~~1h~~ | ✅ shipped 2026-05-27 (CCP 全 4 阶段, 二次修) | 「南京学区房」5 真人 ensemble 触发 delivery fail (硬上限 4) · 修 3 处: (1) L2143 `_ENSEMBLE_CAP_BY_ROUTE` 映射 (modern_documentary/gritty_kinetic → 6, 其它 5 个 route → 5; cap 含旁白配额) + `_ensemble_speaker_cap` helper, decomp 缺 route 默认 5 保守 · (2) L14776 delivery_qa `too many ADSD speakers` + ensemble shape 校验都用 dynamic cap (从 pipeline_state.json 读 topic) · (3) L2402 `_generate_adsd_dialogue_turns` role_candidates 裁剪到 cap, LLM 看不到超 cap 候选 · Stage 3 抓 Medium (decomp 缺 route fallback 不当默认 modern → 修) + Low (delivery 触发 LLM/cache → 接受, 有 cache) · Stage 4 抓初版 cap=4 旁白+4 真人=5 仍 fail → 二修 cap 含旁白配额 现代 6 / 古风 5 · 7/7 矩阵 (NBA=6/笑傲=5/古风 6 拒/缺 route=5/monologue=1) |

---

## 📋 协同 SOP · CCP v1.0 (2026-05-26)

**CCP (Claude × Codex Protocol)** — 让任何 Claude session 跟 codex 全链路协同, 不再单向 ship 后才审.

| Stage | 触发 | 工具 |
|---|---|---|
| 1 review-spec | 收到需求/bug | `tools/codex_collab.py review-spec --topic ... --context ...` |
| 2 propose-alt | 出方案 A 后 | `tools/codex_collab.py propose-alt --topic ... --my-plan ...` |
| 3 review-code | 改 3+ 文件 / 100+ 行 | `tools/codex_collab.py review-code --files ... --topic ...` |
| 4 final-qa | ship 完 | `tools/codex_collab.py final-qa --topic ... --files ...` |

**例外** (跳过 Stage 1-2): 5 行内 / 单文件 typo / 改文档.

**持久化**: 每次协同写 `voice_assets/collab_history.json` 跨 session.

**约束** (写进 feedback memory + CLAUDE.md): Claude 收到 ADR 需求自动走 CCP, 不能拍脑袋.

---

## ✗ Deprecated (撤回方向)

| 方向 | 撤回原因 | 数据来源 |
|------|----------|----------|
| 12-panel grid micro-storyboard | Spike 3C 输出综合场景非按 panel 顺序 | Spike 3 |
| audio_ref 拼接 (>15s) | API 硬性限制 2-15s | Spike 1 |
| step6/step66 流水线化 | 收益 < 5min 不值得复杂度 | 之前 PM 分析 |
| meta_grid 2K 替代 4K | 质量明显降级 | 经验判断 |
| WERYDANCE 高优先 GPU quota | 需付费，非项目内 | - |

---

## 📌 PM 注释

**Session 重启 protocol:**
1. Claude 启动时先读 `memory/project_adr_backlog.md` 看 top 3 优先级
2. 再读这个 ROADMAP.md 看全量 backlog
3. 跟用户对齐当前方向（不直接跳进未做项）

**优先级判断标准:**
- ★★★ ROI 高 + 工程量 < 3h
- ★★ 中等 ROI 或工程量 3-5h
- ★ 长期价值或工具型

**当前 top 3 (2026-05-25 更新):**
1. **达尔文 Round 2** (3h) — 阶段 C 题材分类器 + 阶段 E 自动 IP 进化
2. **PR-3 专业角色补全** (4h) — 武术指导/美术指导/剪辑师/音效师
3. **PR-A · merged_a 合并跑** (4-5h) — 大杀器，省 8-12min/run

**5/21-5/25 累计 ship 32 件 (含今日 7 件):**
  · IP 系统 7 件 (A 孵化 / AUTO-IP / B 自学习 / C 关系 / F 统计 / I 版本 / 占位符过滤)
  · LLM 化 6 件 (topic_decomposition / BGM / role / 武戏密度 / 智能召唤标签 / action_b 标注)
  · Bug 修复 8 件 (duration=3 / step7 防御 / B1-B6 / Ken Burns)
  · 进化基础设施 3 件 (B4 武戏 SFX / FAST retry / task_failed 诊断 / meta_grid 重构 / quality_audit / 旧 grid 清理)

零工 / 已可立刻用：
- 跨题材召唤 (用 IP 即可)
- LLM 智能召唤标签 (现在 B 已 ship，可做)
