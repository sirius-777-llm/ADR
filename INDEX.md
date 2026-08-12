# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (22315 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-125 (125 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L126-2535 (2410 lines · 74 fn · 5 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L2536-5187 (2652 lines · 33 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L5188-6420 (1233 lines · 22 fn · 2 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L6421-6972 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L6973-12667 (5695 lines · 131 fn · 8 sub)
- [`第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）`](#第-6-5-步-动态化-hads-vads-默认-on---no-motion-关) — L12668-18591 (5924 lines · 130 fn · 6 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L18592-18927 (336 lines · 3 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L18928-19886 (959 lines · 10 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L19887-20177 (291 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L20178-22060 (1883 lines · 19 fn · 6 sub)
- [`主流程`](#主流程) — L22061-22315 (255 lines · 3 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L125** (125 lines)

**Sub-sections:**
- _老黄历数据模块_ — L33-125 (93 lines)

**Functions:**
- `get_almanac_data` — L61

---

### 配置
Range: **L126 – L2535** (2410 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L368-497 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L498-1241 (744 lines)
- _工具函数_ — L1242-1617 (376 lines)
- _B87 纹理档系统：LLM 提名 + 代码护栏 + 确定性渲染_ — L1618-1880 (263 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1881-2535 (655 lines)

**Top-level constants:**
- `HEADERS` — L165
- `VIDEO_FORMAT_RAW` — L173
- `MTV_MODE` — L174
- `VIDEO_FORMAT` — L179
- `ADS_DIALOGUE_MODE_EARLY_CHECK` — L190
- `WITH_MOTION` — L197
- `BGM_ONLY_REQUESTED` — L202
- `ADS_DIALOGUE_MODE` — L209
- `GPT_IMAGE2_STORYBOARD` — L221
- `STORYBOARD_REFERENCE_MOTION` — L225
- `STORYBOARD_ANNOTATED_MOTION` — L229
- `GPT_IMAGE2_DIRECT_ANNOTATED_STORYBOARD` — L233
- `GPT_IMAGE2_STORYBOARD_GRID` — L238
- `ADSD_STORYBOARD_GRID` — L246
- `ADS_CHARACTER_SHEET_REQUESTED` — L252
- `STORYBOARD_GRID_MULTIREF_MOTION` — L256
- `STORYBOARD_GRID_MULTIREF_SEGMENTS` — L260
- `STORYBOARD_GRID_MULTIREF_MAIN` — L266
- `GRID_MULTIREF_PRIMARY` — L276
- `PREVIS_PAGE_MOTION` — L288
- `STORYBOARD_TRAILER_MODE` — L292
- `MOTION_ACTION_STORYBOARD` — L297
- `MOTION_BRIDGE_REFS` — L301
- `CHARACTER_TRAILER_MODE` — L305
- `STORYBOARD_TRAILER_MAIN` — L313
- `ADSD_LIP_SYNC_EXPERIMENT` — L326
- `ADSD_RICH_MOTION_PROMPT` — L334
- `ADSD_LLM_VOICE_ASSIGN` — L342
- `ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT` — L346
- `ADSD_CONSECUTIVE_SPEAKER_BATCHING` — L360
- `ADSD_GENDER_FALLBACK_VOICE_ASSET` — L371
- `SILENT_B_SPEAKERS` — L503
- `_PODCAST_TO_VOICE_ASSET_MAP` — L881
- `_VOICE_ASSET_FORBIDDEN_FLAGS` — L899
- `_GENERIC_NARRATOR_NAMES` — L943
- `VOICE_ASSET_AUDIO_DUB_EXPERIMENT` — L980
- `VOICE_ASSET_AUDIO_DUB_PARTIAL_OK` — L988
- `MOTION_VISUAL_QA` — L992
- `MOTION_VOICE_REPAIR` — L1000
- `MOTION_VOICE_STRICT_LOCK` — L1005
- `WERYDANCE_CAPTIONS` — L1010
- `ADSD_ONSITE_POV_MODE` — L1022
- `ADSD_LIPS_CHANGE_REPAIR` — L1027
- `ADSD_LIPS_CHANGE_ALL` — L1032
- `ADS_REPORTER_MODE` — L1043
- `ADS_STORYBOARD_FLOW_DEFAULT` — L1060
- `ADS_RETENTION_MODE` — L1074
- `ADSD_MODE_NAME` — L1080
- `EMOTION_STYLE` — L1221
- `EMOTION_STYLE_BRIGHT` — L1233
- `_REDACT_PATTERNS_DEFAULT` — L1247
- `_TG_DASHBOARD_STAGES` — L1299
- `_TG_NOISY_PATTERNS` — L1314
- `_TG_IMMEDIATE_PATTERNS` — L1332
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1611
- `_TEXTURE_MODE_ENUM` — L1619
- `_TEXTURE_SUFFIX_MAP` — L1624
- `_TEXTURE_BODY_DIRECTIVE` — L1651
- `_TEXTURE_SCENE_PHRASE` — L1658
- `_TEXTURE_GRID_PHRASE` — L1665
- `_TEXTURE_MOTION_PHRASE` — L1673
- `_LLM_TIER` — L2061
- `_TOPIC_MODIFIERS` — L2288
- `_TONE_PANTONE_OVERRIDE` — L2305

**Functions:**
- `_read_almighty_model` — L145
- `_is_action_scene` — L380
- `_needs_storyboard_flow_character_sheet` — L391
- `_wuxia_action_panel_prompt` — L420
- `_action_motion_fragment` — L442
- `_infer_emotion_from_text` — L457
- `_emotion_expression_phrase` — L472
- `_infer_needs_lip_sync` — L479
- `_infer_turn_type` — L506
- `_is_action_shout` — L531
- `_resolve_turn_type` — L557
- `_is_silent_b` — L572
- `_is_narrated_b` — L576
- `_is_a_roll` — L580
- `_is_action_b` — L584
- `_voice_asset_id_for_speaker` — L588
- `_llm_assign_voice_assets` — L616
- `_apply_llm_voice_assignment` — L745
- `_voice_asset_is_speech_safe` — L906
- `_podcast_id_to_voice_asset` — L912
- `_resolve_voice_asset_for_ads_speaker` — L946
- `_redact_for_stdout` — L1262
- `log` — L1287
- `_tg_send_raw` — L1355
- `_tg_matches` — L1371
- `_tg_summarize` — L1375
- `_tg_dashboard_stage_for` — L1382
- `_tg_progress_bar` — L1390
- `_tg_dashboard_text` — L1396
- `_tg_dashboard_update` — L1414
- `_tg_maybe_digest` — L1451
- `tg` — L1466
- `_wait_image_submit_slot` — L1515
- `_wait_motion_submit_slot` — L1528
- `_is_rate_limited_error` — L1541
- `_is_rate_limited_response` — L1551
- `_is_transient_workflow_error` — L1563
- `_is_llm_rate_limited_error` — L1587
- `_era_is_pre_photographic` — L1685
- `_texture_mode_fallback` — L1713
- `_texture_guardrail` — L1734
- `_set_active_texture_profile` — L1773
- `_active_texture_suffix` — L1786
- `_active_texture_body_directive` — L1790
- `_active_texture_scene_phrase` — L1794
- `_active_texture_grid_phrase` — L1798
- `_active_texture_motion_phrase` — L1802
- `_inject_image2_quality_suffix` — L1806
- `submit_text_to_image` — L1826
- `req_post` — L1862
- `req_get` — L1876
- `_tg_probe_send` — L1884
- `_tg_probe_delete` — L1904
- `_tg_upload_with_probe_gap` — L1917
- `poll` — L1957
- `poll_podcast` — L1982
- `poll_task_status` — L2004
- `poll_storyboard_task` — L2026
- `tier_chat` — L2069
- `chat` — L2075
- `pick_image_model` — L2134
- `detect_topic_meta` — L2159
- `_topic_culture_guard` — L2209
- `_write_cultural_visual_qa` — L2235
- `is_1919_global_topic` — L2282
- `_strip_topic_modifiers` — L2293
- `apply_1919_global_guardrails` — L2311
- `build_1919_global_cover_prompt` — L2340
- `_shot_blueprint_enums` — L2372
- `build_shot_blueprint` — L2448
- `ffprobe_duration` — L2474
- `ffprobe_video_size` — L2485
- `_video_decode_probe` — L2506
- `ffmpeg` — L2524

---

### 第一步：双导演生成剧本
Range: **L2536 – L5187** (2652 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L4168-5187 (1020 lines)

**Top-level constants:**
- `_ENSEMBLE_CAP_BY_ROUTE` — L2688

**Functions:**
- `_extract_json_array` — L2537
- `_extract_json_object` — L2547
- `_voice_for_speaker` — L2557
- `_adsd_gender_from_voice` — L2593
- `_adsd_infer_gender_from_speaker` — L2601
- `_adsd_gender_lock_phrase` — L2610
- `_adsd_visual_subject_has_gender_conflict` — L2625
- `_adsd_default_roles` — L2637
- `_adsd_allows_media_role` — L2642
- `_adsd_role_candidates` — L2650
- `_adsd_dialogue_shape` — L2677
- `_ensemble_speaker_cap` — L2699
- `_ip_voice_asset_for_speaker` — L2712
- `_finalize_adsd_turns` — L2736
- `_parse_adsd_override_turns` — L2782
- `_parse_timecode_seconds` — L2875
- `_clean_override_line_text` — L2884
- `_parse_override_script_text` — L2890
- `_adsd_pov_contract` — L2924
- `_load_audit_blacklist_block` — L2937
- `_generate_adsd_dialogue_turns` — L2975
- `_broll_rhythm_reviewer` — L3402
- `_sweep_speaker_field` — L3509
- `_should_run_immersion_qa` — L3569
- `_adsd_immersion_qa_rewrite_turns` — L3592
- `_adsd_visual_contract` — L3656
- `_parse_risk_score` — L3708
- `_check_high_risk_hard_abort` — L3737
- `_maybe_neutralize_topic` — L3764
- `_apply_render_budget_scene_cap` — L3803
- `_apply_llm_mode_decision` — L3830
- `step1_script` — L3885
- `_write_ads_retention_qa` — L5131

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L5188 – L6420** (1233 lines)

**Sub-sections:**
- _B88: 内容审核(1002) → 分级软化 → 中性兜底句 → 静音 backstop，绝不崩管线_ — L5883-5911 (29 lines)
- _非内容审核(网络/transient): 有限退避重试，耗尽才抛_ — L5912-6420 (509 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L5263
- `_ADSD_POLICY_REWRITE_TERMS` — L5269
- `_TTS_SAFE_FALLBACK_LINE` — L5370
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L5438

**Functions:**
- `_openai_tts_fallback` — L5189
- `_edge_tts_fallback` — L5235
- `_sanitize_for_external_api` — L5294
- `_is_content_policy_error` — L5303
- `_rewrite_adsd_tts_text_for_policy` — L5317
- `_tts_safe_fallback_line` — L5379
- `_tts_silent_placeholder` — L5384
- `_record_adsd_tts_rewrite` — L5419
- `_build_silence_mp3` — L5444
- `_audio_duration_seconds` — L5457
- `_text_to_audio_master_voice_timed` — L5469
- `_text_to_audio_master_voice` — L5594
- `step2_master_voice` — L5707
- `_tts_turn_to_audio` — L5835
- `_asr_verify_dialogue_audio` — L5922
- `_asr_verify_dialogue_turns` — L5984
- `_normalize_cn_number_token` — L6026
- `_compact_zh_text` — L6048
- `_write_adsd_asr_text_qa` — L6055
- `_write_adsd_speaker_focus_qa` — L6094
- `_write_adsd_gender_voice_qa` — L6154
- `step2_dialogue_voice` — L6207

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L6421 – L6972** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L6428-6550 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L6551-6585 (35 lines)
- _第二层：字符数插值_ — L6586-6610 (25 lines)
- _第三层：silencedetect 物理校准_ — L6611-6972 (362 lines)

**Functions:**
- `_detect_silences` — L6429
- `_calibrate_boundaries` — L6464
- `_enforce_monotonic` — L6498
- `_manual_override_segments` — L6510
- `_calc_sentence_boundaries` — L6531
- `step345_timeline` — L6642
- `_analyze_bgm_energy_cuts` — L6701
- `_snap_bgm_only_boundaries` — L6764
- `step345_bgm_only_timeline` — L6824

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L6973 – L12667** (5695 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L8202-8252 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L8253-9111 (859 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L9112-9599 (488 lines)
- _Speaker IP Card (2026-05-21)_ — L9600-11244 (1645 lines)
- _MTV：原创歌曲 + 主唱人物库 + WeryDance MV_ — L11245-12267 (1023 lines)
- _B68 (2026-05-30) WERYDANCE 段长合规 gate_ — L12268-12500 (233 lines)
- _审批流程_ — L12501-12557 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L12558-12667 (110 lines)

**Top-level constants:**
- `_CORE_TERMS_STOP_WORDS` — L7375
- `CHARACTER_META_GRID_COSTUMES` — L8208
- `CHARACTER_META_GRID_POSES` — L8209
- `CHARACTER_META_GRID_SCENES` — L8210
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L8213
- `_SFX_TYPE_ENUM` — L8581
- `_SFX_INTENSITY_ENUM` — L8586
- `_SFX_POSITION_ENUM` — L8587
- `_GRAIN_LEVEL_ENUM` — L8732
- `_CUSTOM_STYLE_BANNED_NAMES` — L9167
- `_DUANGE_XING_TEXT` — L11246

**Functions:**
- `_extract_img_url` — L6974
- `_extract_img_urls` — L6996
- `_extract_video_url` — L7029
- `_count_bands` — L7054
- `_detect_contact_sheet_like_image` — L7066
- `_file_sha256` — L7127
- `_load_upload_cache` — L7140
- `_save_upload_cache` — L7149
- `_cached_upload_url` — L7157
- `_store_upload_url` — L7174
- `_guess_upload_mime` — L7184
- `_upload_to_weryai` — L7207
- `_send_for_approval` — L7268
- `_wait_approval` — L7332
- `_render_still_segment` — L7344
- `_extract_core_terms` — L7381
- `_scene_text_visual_alignment` — L7400
- `_write_text_visual_alignment_qa` — L7421
- `_scene_motion_action_plan` — L7444
- `_ensure_motion_action_plan` — L7498
- `_motion_action_block` — L7507
- `_motion_plan_for_qa` — L7535
- `_write_motion_action_plan_qa` — L7545
- `_write_motion_bridge_refs_qa` — L7575
- `_motion_bridge_ref_prompt` — L7582
- `generate_motion_bridge_refs_gpt_image2` — L7615
- `generate_image` — L7730
- `generate_storyboard_images_gpt_image2` — L7777
- `_storyboard_grid_aspect` — L7963
- `_storyboard_grid_cols_rows` — L7970
- `_storyboard_grid_prompt` — L7992
- `_storyboard_grid_prompt_limit` — L8050
- `_is_prompt_limit_response` — L8054
- `_production_storyboard_prompt` — L8060
- `_write_production_storyboard_page_qa` — L8094
- `_character_sheet_prompt` — L8104
- `_is_audit_blocked` — L8230
- `_paraphrase_sensitive_dialogue` — L8243
- `_topic_cache_dir` — L8257
- `_topic_cache_path` — L8263
- `_load_topic_decomposition_cache` — L8276
- `_save_topic_decomposition_cache` — L8294
- `_briefs_dir` — L8331
- `_brief_path` — L8337
- `_empty_brief` — L8342
- `_deep_merge_brief_skeleton` — L8382
- `_load_brief` — L8396
- `_save_brief` — L8420
- `_brief_get` — L8439
- `_brief_field` — L8451
- `_brief_set` — L8462
- `_brief_claim` — L8478
- `_brief_agent_status` — L8521
- `_brief_from_topic_decomposition` — L8534
- `_rule_based_sfx_design` — L8590
- `_validate_sfx_entry` — L8641
- `_audio_director_design` — L8679
- `_hex_color_validate` — L8735
- `_rule_based_art_design` — L8747
- `_validate_art_design` — L8828
- `_art_director_design` — L8866
- `_coordinator_review` — L8888
- `_llm_topic_decomposition` — L8989
- `_validate_custom_visual_style` — L9174
- `_resolve_route_style` — L9196
- `_director_route_block` — L9221
- `_llm_infer_meta_grid_template` — L9288
- `_resolve_meta_grid_template` — L9345
- `_infer_meta_grid_costume` — L9388
- `_infer_meta_grid_pose` — L9437
- `_adsd_meta_grid_call_prompt` — L9484
- `_meta_grid_panel_index` — L9526
- `_migrate_speaker_ip` — L9606
- `_speaker_ips_dir` — L9631
- `_list_speaker_ips` — L9638
- `_match_speaker_ip` — L9652
- `_build_speaker_ip_context_for_script` — L9672
- `_ip_usage_stats` — L9728
- `_recommend_related_ips` — L9746
- `_save_speaker_ip` — L9771
- `_record_speaker_usage_history` — L9780
- `_format_speaker_usage_history_for_prompt` — L9827
- `_llm_infer_ip_skeleton` — L9845
- `_llm_pick_voice_asset_for_ip` — L9890
- `_auto_incubate_missing_ips` — L9939
- `_character_meta_grid_cache_dir` — L10023
- `_character_meta_grid_cache_path` — L10031
- `_character_meta_grid_cache_legacy_path` — L10039
- `_character_meta_grid_path` — L10046
- `generate_character_meta_grid_gpt_image2` — L10052
- `_generate_all_character_meta_grids` — L10224
- `_write_character_sheet_qa` — L10265
- `generate_character_sheet_gpt_image2` — L10275
- `generate_production_storyboard_page_gpt_image2` — L10375
- `_qa_clean_storyboard_panel` — L10438
- `_crop_storyboard_grid_panels` — L10619
- `generate_storyboard_grid_gpt_image2` — L10666
- `_gpt_image2_direct_annotated_aspect` — L10898
- `_gpt_image2_direct_annotated_prompt` — L10905
- `generate_gpt_image2_direct_annotated_storyboards` — L10935
- `_llm_bgm_description` — L11036
- `_bgm_contains_vocals` — L11075
- `generate_bgm` — L11109
- `_arg_value` — L11258
- `_infer_mtv_singer` — L11267
- `_ensure_mtv_singer_ip` — L11281
- `_mtv_source_lyrics` — L11336
- `_mtv_build_plan` — L11348
- `_generate_mtv_song` — L11433
- `_trim_mtv_song` — L11472
- `_mtv_generate_visual_segments` — L11485
- `_mtv_ass_time` — L11711
- `_mtv_ass_escape` — L11720
- `_mtv_wrap_lyric` — L11726
- `_mtv_vocal_span_from_asr` — L11751
- `_mtv_split_lyric_clauses` — L11795
- `_mtv_split_lyric_phrases` — L11807
- `_mtv_norm_zh` — L11820
- `_mtv_best_phrase_offset` — L11824
- `_mtv_asr_phrase_records` — L11844
- `_mtv_alignment_from_script` — L11887
- `_mtv_split_span` — L11940
- `_mtv_song_slice` — L11950
- `_mtv_normalize_segment_duration` — L11958
- `_mtv_static_fallback_segment` — L11994
- `_mtv_lip_sync_segment` — L12016
- `_write_mtv_subtitles` — L12131
- `_mtv_concat_and_render` — L12203
- `run_mtv_pipeline` — L12253
- `_b68_clamp_scene_durations_to_werydance_bounds` — L12276
- `step6_parallel` — L12336

---

### 第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）
Range: **L12668 – L18591** (5924 lines)

**Sub-sections:**
- _B92 (2026-06-05): 轨迹标记运镜 (Seedance 红线技法)_ — L13999-16526 (2528 lines)
- _PR-A (2026-05-27): merged_a 合并跑 helpers_ — L16527-18326 (1800 lines)
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L18327-18369 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L18370-18407 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回时间轴锚定音轨_ — L18408-18546 (139 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L18547-18591 (45 lines)

**Top-level constants:**
- `_PR3B1_SHOT_TYPE_ENUM` — L13319
- `_PR3B1_CAMERA_ANGLE_ENUM` — L13323
- `_PR3B1_LIGHTING_ENUM` — L13328
- `_PR3B1_CAMERA_MOTION_ENUM` — L13333
- `_SEEDANCE_CAMERA_GRAMMAR` — L13357
- `_DOLLY_ZOOM_EMOTIONS` — L13370
- `_GRAND_EMOTIONS` — L13375
- `_SEEDANCE_CAMERA_COMPACT` — L13380
- `_B92_HIDE_NEGATIVES` — L14002
- `_EMOTION_NARRATION_STYLE_MAP` — L14693

**Functions:**
- `_generate_motion_prompts` — L12671
- `_motion_tasks_file` — L12738
- `_motion_qa_file` — L12744
- `_append_motion_qa` — L12748
- `_finalize_motion_qa` — L12772
- `_lip_sync_tasks_file` — L12856
- `_normalize_generation_interface` — L12860
- `_generation_task_record` — L12870
- `_normalize_cached_task` — L12888
- `_load_generation_tasks` — L12915
- `_atomic_write_json` — L12932
- `_load_motion_tasks` — L12957
- `_save_motion_task` — L12963
- `_remove_motion_task` — L12983
- `_load_lip_sync_tasks` — L12990
- `_mtv_lip_sync_task_key` — L12997
- `_merged_lip_sync_task_key` — L13001
- `_lip_sync_task_indices` — L13005
- `_find_overlapping_lip_sync_task` — L13026
- `_is_reusable_lip_sync_raw_video` — L13043
- `_find_merged_lip_sync_task` — L13053
- `_save_lip_sync_task` — L13062
- `_remove_lip_sync_task` — L13081
- `_video_visual_motion_qa` — L13088
- `_motion_output_qa` — L13160
- `_has_audio_stream` — L13205
- `_normalize_motion_video` — L13216
- `_motion_poll_and_download` — L13266
- `_validate_enum_field` — L13339
- `_seedance_camera_directive` — L13395
- `_build_motion_video_prompt` — L13415
- `_short_board_text` — L13471
- `_wrap_board_text` — L13478
- `_storyboard_font` — L13509
- `_draw_storyboard_arrow` — L13524
- `_build_annotated_storyboard_reference` — L13538
- `_plain_caption_text` — L13639
- `_werydance_caption_request` — L13647
- `_werydance_caption_instruction` — L13674
- `_werydance_negative_prompt` — L13686
- `_motion_reference_prompt` — L13708
- `_motion_audio_dub_prompt` — L13731
- `_motion_audio_dub_poll_and_download` — L13765
- `_try_motion_audio_dub_video` — L13831
- `_b92_enabled` — L14008
- `_b92_propose_path` — L14012
- `_b92_draw_path` — L14053
- `_b92_trim_lead_frames` — L14082
- `_b92_trajectory_prompt` — L14111
- `_b92_apply_trajectory` — L14126
- `_b92_preplan_paths` — L14147
- `_try_motion_reference_video` — L14171
- `_resume_motion_task` — L14308
- `_motion_one_scene` — L14340
- `_grid_multiref_tasks_file` — L14462
- `_previs_page_tasks_file` — L14466
- `_load_grid_multiref_tasks` — L14470
- `_load_previs_page_tasks` — L14477
- `_save_grid_multiref_task` — L14484
- `_save_previs_page_task` — L14501
- `_remove_grid_multiref_task` — L14518
- `_remove_previs_page_task` — L14525
- `_poll_video_task_download` — L14532
- `_grid_multiref_group_size` — L14581
- `_grid_multiref_adaptive_group_size` — L14591
- `_grid_multiref_duration` — L14615
- `_grid_multiref_tts_buffer_factor` — L14653
- `_grid_multiref_tts_duration_buffered` — L14667
- `_grid_multiref_segment_max_stretch` — L14683
- `_voice_clone_emotion_style` — L14717
- `_grid_multiref_prompt` — L14740
- `_write_grid_multiref_motion_qa` — L14820
- `_write_previs_page_motion_qa` — L14830
- `_write_storyboard_trailer_qa` — L14840
- `_write_character_trailer_qa` — L14850
- `_write_grid_multiref_segment_qa` — L14860
- `_motion_compare_record` — L14870
- `_write_storyboard_motion_compare_qa` — L14892
- `_scene_segment_duration` — L14928
- `_apply_grid_multiref_segments` — L14947
- `_previs_page_duration` — L15152
- `_previs_page_group_prompt` — L15163
- `_previs_page_groups` — L15189
- `_storyboard_trailer_duration` — L15204
- `_storyboard_trailer_prompt` — L15214
- `_character_trailer_max_shots` — L15242
- `_character_trailer_shot_duration` — L15250
- `_character_trailer_prompt` — L15266
- `_concat_character_trailer_segments` — L15281
- `_generate_character_trailer_motion` — L15320
- `_multi_trailer_prompt_for_group` — L15428
- `_generate_multi_trailer_segments` — L15451
- `_generate_storyboard_trailer_motion` — L15562
- `_generate_previs_page_motion_segments` — L15637
- `_generate_grid_multiref_motion_segments` — L15755
- `_grid_multiref_concat_groups` — L16083
- `_grid_multiref_concat_groups_partial` — L16100
- `_grid_multiref_concat_paths` — L16118
- `_lip_sync_slot_duration` — L16160
- `_adsd_lip_sync_prompt` — L16167
- `_adsd_broll_motion_prompt` — L16213
- `_adsd_action_b_motion_prompt` — L16261
- `_adsd_silent_b_motion_prompt` — L16307
- `_adsd_narrated_b_audio_dub_prompt` — L16348
- `_adsd_almighty_audio_dub_prompt` — L16392
- `_postprocess_lip_sync_segment` — L16433
- `_detect_audio_leading_silence` — L16505
- `_concat_audio_files_for_group` — L16530
- `_split_lip_sync_raw_by_durations` — L16553
- `_postprocess_audio_dub_segment` — L16588
- `_lips_change_repair_segment` — L16716
- `_load_lips_change_requested_turns` — L16801
- `_parse_turn_set` — L16818
- `_load_motion_voice_repair_turns` — L16840
- `_voice_assets_file` — L16852
- `_load_voice_assets` — L16859
- `_build_combined_voice_reference` — L16878
- `_select_voice_asset_reference` — L16920
- `_lip_sync_poll_download_and_process` — L16996
- `_resume_lip_sync_task` — L17072
- `_lip_sync_one_group` — L17101
- `_lip_sync_one_scene` — L17436
- `step66_adsd_lip_sync` — L17789
- `step65_motion` — L18142
- `step65_grid_multiref_motion_qa` — L18299
- `_sanitize_scene_for_state` — L18328
- `_save_pipeline_state` — L18347
- `_retime_after_audio_dub` — L18371
- `_build_voice_clone_hybrid_audio` — L18409
- `_build_dynamic_bgm` — L18548

---

### 第七步：拼接视频轨
Range: **L18592 – L18927** (336 lines)

**Functions:**
- `_rescue_motion_image_to_video` — L18593
- `_rescue_motion_text_to_video` — L18628
- `step7_concat` — L18659

---

### 第八步：生成 ASS 字幕
Range: **L18928 – L19886** (959 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L19207-19886 (680 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L18929
- `_word_timings_for_subtitle_align` — L18955
- `_align_segments_via_asr` — L18996
- `_b61_1_asr_turn_boundaries` — L19039
- `step8_subtitles` — L19101
- `_read_output_json` — L19607
- `_qa_file_pass` — L19618
- `_ass_has_dialogue` — L19625
- `_write_adsd_delivery_qa` — L19635
- `_write_bgm_only_qa` — L19775

---

### 第九步：最终合成
Range: **L19887 – L20177** (291 lines)

**Functions:**
- `step9_render` — L19888

---

### 第十步：推送 Telegram
Range: **L20178 – L22060** (1883 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L21284-21393 (110 lines)
- _B70 (2026-05-30) TG oversize policy helpers_ — L21394-21865 (472 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L21866-21870 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L21871-21935 (65 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L21936-21982 (47 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L21983-22060 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L20547
- `PANTONE_FALLBACK` — L20574
- `FESTIVAL_DATE_TAG` — L20688

**Functions:**
- `_generate_caption` — L20179
- `_overlay_title_on_cover` — L20417
- `_prepare_tg_photo` — L20527
- `_get_pantone_for_date` — L20577
- `_llm_bottom_note` — L20602
- `_get_bottom_note` — L20632
- `_get_date_tag` — L20710
- `_shrink_to_b64` — L20732
- `_llm_check_scenes_anomalies` — L20748
- `_llm_check_cover_unique` — L20801
- `_llm_check_cover_quality` — L20831
- `_try_almanac_cover` — L20873
- `_generate_cover_image` — L21044
- `_async_kickoff_cover_caption` — L21291
- `_await_async_cover_caption` — L21367
- `_b70_env_float` — L21397
- `_b70_split_and_deliver` — L21412
- `_b70_send_document_first` — L21525
- `step10_deliver` — L21562

---

### 主流程
Range: **L22061 – L22315** (255 lines)

**Functions:**
- `_print_execution_plan` — L22062
- `_write_run_timings` — L22121
- `main` — L22150

---
