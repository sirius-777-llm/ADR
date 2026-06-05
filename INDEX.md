# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (21156 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-2505 (2384 lines · 73 fn · 5 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L2506-5157 (2652 lines · 33 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L5158-6390 (1233 lines · 22 fn · 2 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L6391-6942 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L6943-11971 (5029 lines · 115 fn · 8 sub)
- [`第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）`](#第-6-5-步-动态化-hads-vads-默认-on---no-motion-关) — L11972-17439 (5468 lines · 117 fn · 6 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L17440-17775 (336 lines · 3 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L17776-18734 (959 lines · 10 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L18735-19025 (291 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L19026-20901 (1876 lines · 19 fn · 6 sub)
- [`主流程`](#主流程) — L20902-21156 (255 lines · 3 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L2505** (2384 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L338-467 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L468-1211 (744 lines)
- _工具函数_ — L1212-1587 (376 lines)
- _B87 纹理档系统：LLM 提名 + 代码护栏 + 确定性渲染_ — L1588-1850 (263 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1851-2505 (655 lines)

**Top-level constants:**
- `HEADERS` — L135
- `VIDEO_FORMAT_RAW` — L143
- `MTV_MODE` — L144
- `VIDEO_FORMAT` — L149
- `ADS_DIALOGUE_MODE_EARLY_CHECK` — L160
- `WITH_MOTION` — L167
- `BGM_ONLY_REQUESTED` — L172
- `ADS_DIALOGUE_MODE` — L179
- `GPT_IMAGE2_STORYBOARD` — L191
- `STORYBOARD_REFERENCE_MOTION` — L195
- `STORYBOARD_ANNOTATED_MOTION` — L199
- `GPT_IMAGE2_DIRECT_ANNOTATED_STORYBOARD` — L203
- `GPT_IMAGE2_STORYBOARD_GRID` — L208
- `ADSD_STORYBOARD_GRID` — L216
- `ADS_CHARACTER_SHEET_REQUESTED` — L222
- `STORYBOARD_GRID_MULTIREF_MOTION` — L226
- `STORYBOARD_GRID_MULTIREF_SEGMENTS` — L230
- `STORYBOARD_GRID_MULTIREF_MAIN` — L236
- `GRID_MULTIREF_PRIMARY` — L246
- `PREVIS_PAGE_MOTION` — L258
- `STORYBOARD_TRAILER_MODE` — L262
- `MOTION_ACTION_STORYBOARD` — L267
- `MOTION_BRIDGE_REFS` — L271
- `CHARACTER_TRAILER_MODE` — L275
- `STORYBOARD_TRAILER_MAIN` — L283
- `ADSD_LIP_SYNC_EXPERIMENT` — L296
- `ADSD_RICH_MOTION_PROMPT` — L304
- `ADSD_LLM_VOICE_ASSIGN` — L312
- `ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT` — L316
- `ADSD_CONSECUTIVE_SPEAKER_BATCHING` — L330
- `ADSD_GENDER_FALLBACK_VOICE_ASSET` — L341
- `SILENT_B_SPEAKERS` — L473
- `_PODCAST_TO_VOICE_ASSET_MAP` — L851
- `_VOICE_ASSET_FORBIDDEN_FLAGS` — L869
- `_GENERIC_NARRATOR_NAMES` — L913
- `VOICE_ASSET_AUDIO_DUB_EXPERIMENT` — L950
- `VOICE_ASSET_AUDIO_DUB_PARTIAL_OK` — L958
- `MOTION_VISUAL_QA` — L962
- `MOTION_VOICE_REPAIR` — L970
- `MOTION_VOICE_STRICT_LOCK` — L975
- `WERYDANCE_CAPTIONS` — L980
- `ADSD_ONSITE_POV_MODE` — L992
- `ADSD_LIPS_CHANGE_REPAIR` — L997
- `ADSD_LIPS_CHANGE_ALL` — L1002
- `ADS_REPORTER_MODE` — L1013
- `ADS_STORYBOARD_FLOW_DEFAULT` — L1030
- `ADS_RETENTION_MODE` — L1044
- `ADSD_MODE_NAME` — L1050
- `EMOTION_STYLE` — L1191
- `EMOTION_STYLE_BRIGHT` — L1203
- `_REDACT_PATTERNS_DEFAULT` — L1217
- `_TG_DASHBOARD_STAGES` — L1269
- `_TG_NOISY_PATTERNS` — L1284
- `_TG_IMMEDIATE_PATTERNS` — L1302
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1581
- `_TEXTURE_MODE_ENUM` — L1589
- `_TEXTURE_SUFFIX_MAP` — L1594
- `_TEXTURE_BODY_DIRECTIVE` — L1621
- `_TEXTURE_SCENE_PHRASE` — L1628
- `_TEXTURE_GRID_PHRASE` — L1635
- `_TEXTURE_MOTION_PHRASE` — L1643
- `_LLM_TIER` — L2031
- `_TOPIC_MODIFIERS` — L2258
- `_TONE_PANTONE_OVERRIDE` — L2275

**Functions:**
- `_is_action_scene` — L350
- `_needs_storyboard_flow_character_sheet` — L361
- `_wuxia_action_panel_prompt` — L390
- `_action_motion_fragment` — L412
- `_infer_emotion_from_text` — L427
- `_emotion_expression_phrase` — L442
- `_infer_needs_lip_sync` — L449
- `_infer_turn_type` — L476
- `_is_action_shout` — L501
- `_resolve_turn_type` — L527
- `_is_silent_b` — L542
- `_is_narrated_b` — L546
- `_is_a_roll` — L550
- `_is_action_b` — L554
- `_voice_asset_id_for_speaker` — L558
- `_llm_assign_voice_assets` — L586
- `_apply_llm_voice_assignment` — L715
- `_voice_asset_is_speech_safe` — L876
- `_podcast_id_to_voice_asset` — L882
- `_resolve_voice_asset_for_ads_speaker` — L916
- `_redact_for_stdout` — L1232
- `log` — L1257
- `_tg_send_raw` — L1325
- `_tg_matches` — L1341
- `_tg_summarize` — L1345
- `_tg_dashboard_stage_for` — L1352
- `_tg_progress_bar` — L1360
- `_tg_dashboard_text` — L1366
- `_tg_dashboard_update` — L1384
- `_tg_maybe_digest` — L1421
- `tg` — L1436
- `_wait_image_submit_slot` — L1485
- `_wait_motion_submit_slot` — L1498
- `_is_rate_limited_error` — L1511
- `_is_rate_limited_response` — L1521
- `_is_transient_workflow_error` — L1533
- `_is_llm_rate_limited_error` — L1557
- `_era_is_pre_photographic` — L1655
- `_texture_mode_fallback` — L1683
- `_texture_guardrail` — L1704
- `_set_active_texture_profile` — L1743
- `_active_texture_suffix` — L1756
- `_active_texture_body_directive` — L1760
- `_active_texture_scene_phrase` — L1764
- `_active_texture_grid_phrase` — L1768
- `_active_texture_motion_phrase` — L1772
- `_inject_image2_quality_suffix` — L1776
- `submit_text_to_image` — L1796
- `req_post` — L1832
- `req_get` — L1846
- `_tg_probe_send` — L1854
- `_tg_probe_delete` — L1874
- `_tg_upload_with_probe_gap` — L1887
- `poll` — L1927
- `poll_podcast` — L1952
- `poll_task_status` — L1974
- `poll_storyboard_task` — L1996
- `tier_chat` — L2039
- `chat` — L2045
- `pick_image_model` — L2104
- `detect_topic_meta` — L2129
- `_topic_culture_guard` — L2179
- `_write_cultural_visual_qa` — L2205
- `is_1919_global_topic` — L2252
- `_strip_topic_modifiers` — L2263
- `apply_1919_global_guardrails` — L2281
- `build_1919_global_cover_prompt` — L2310
- `_shot_blueprint_enums` — L2342
- `build_shot_blueprint` — L2418
- `ffprobe_duration` — L2444
- `ffprobe_video_size` — L2455
- `_video_decode_probe` — L2476
- `ffmpeg` — L2494

---

### 第一步：双导演生成剧本
Range: **L2506 – L5157** (2652 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L4138-5157 (1020 lines)

**Top-level constants:**
- `_ENSEMBLE_CAP_BY_ROUTE` — L2658

**Functions:**
- `_extract_json_array` — L2507
- `_extract_json_object` — L2517
- `_voice_for_speaker` — L2527
- `_adsd_gender_from_voice` — L2563
- `_adsd_infer_gender_from_speaker` — L2571
- `_adsd_gender_lock_phrase` — L2580
- `_adsd_visual_subject_has_gender_conflict` — L2595
- `_adsd_default_roles` — L2607
- `_adsd_allows_media_role` — L2612
- `_adsd_role_candidates` — L2620
- `_adsd_dialogue_shape` — L2647
- `_ensemble_speaker_cap` — L2669
- `_ip_voice_asset_for_speaker` — L2682
- `_finalize_adsd_turns` — L2706
- `_parse_adsd_override_turns` — L2752
- `_parse_timecode_seconds` — L2845
- `_clean_override_line_text` — L2854
- `_parse_override_script_text` — L2860
- `_adsd_pov_contract` — L2894
- `_load_audit_blacklist_block` — L2907
- `_generate_adsd_dialogue_turns` — L2945
- `_broll_rhythm_reviewer` — L3372
- `_sweep_speaker_field` — L3479
- `_should_run_immersion_qa` — L3539
- `_adsd_immersion_qa_rewrite_turns` — L3562
- `_adsd_visual_contract` — L3626
- `_parse_risk_score` — L3678
- `_check_high_risk_hard_abort` — L3707
- `_maybe_neutralize_topic` — L3734
- `_apply_render_budget_scene_cap` — L3773
- `_apply_llm_mode_decision` — L3800
- `step1_script` — L3855
- `_write_ads_retention_qa` — L5101

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L5158 – L6390** (1233 lines)

**Sub-sections:**
- _B88: 内容审核(1002) → 分级软化 → 中性兜底句 → 静音 backstop，绝不崩管线_ — L5853-5881 (29 lines)
- _非内容审核(网络/transient): 有限退避重试，耗尽才抛_ — L5882-6390 (509 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L5233
- `_ADSD_POLICY_REWRITE_TERMS` — L5239
- `_TTS_SAFE_FALLBACK_LINE` — L5340
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L5408

**Functions:**
- `_openai_tts_fallback` — L5159
- `_edge_tts_fallback` — L5205
- `_sanitize_for_external_api` — L5264
- `_is_content_policy_error` — L5273
- `_rewrite_adsd_tts_text_for_policy` — L5287
- `_tts_safe_fallback_line` — L5349
- `_tts_silent_placeholder` — L5354
- `_record_adsd_tts_rewrite` — L5389
- `_build_silence_mp3` — L5414
- `_audio_duration_seconds` — L5427
- `_text_to_audio_master_voice_timed` — L5439
- `_text_to_audio_master_voice` — L5564
- `step2_master_voice` — L5677
- `_tts_turn_to_audio` — L5805
- `_asr_verify_dialogue_audio` — L5892
- `_asr_verify_dialogue_turns` — L5954
- `_normalize_cn_number_token` — L5996
- `_compact_zh_text` — L6018
- `_write_adsd_asr_text_qa` — L6025
- `_write_adsd_speaker_focus_qa` — L6064
- `_write_adsd_gender_voice_qa` — L6124
- `step2_dialogue_voice` — L6177

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L6391 – L6942** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L6398-6520 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L6521-6555 (35 lines)
- _第二层：字符数插值_ — L6556-6580 (25 lines)
- _第三层：silencedetect 物理校准_ — L6581-6942 (362 lines)

**Functions:**
- `_detect_silences` — L6399
- `_calibrate_boundaries` — L6434
- `_enforce_monotonic` — L6468
- `_manual_override_segments` — L6480
- `_calc_sentence_boundaries` — L6501
- `step345_timeline` — L6612
- `_analyze_bgm_energy_cuts` — L6671
- `_snap_bgm_only_boundaries` — L6734
- `step345_bgm_only_timeline` — L6794

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L6943 – L11971** (5029 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L8172-8222 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L8223-9081 (859 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L9082-9569 (488 lines)
- _Speaker IP Card (2026-05-21)_ — L9570-11214 (1645 lines)
- _MTV：原创歌曲 + 主唱人物库 + WeryDance MV_ — L11215-11571 (357 lines)
- _B68 (2026-05-30) WERYDANCE 段长合规 gate_ — L11572-11804 (233 lines)
- _审批流程_ — L11805-11861 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L11862-11971 (110 lines)

**Top-level constants:**
- `_CORE_TERMS_STOP_WORDS` — L7345
- `CHARACTER_META_GRID_COSTUMES` — L8178
- `CHARACTER_META_GRID_POSES` — L8179
- `CHARACTER_META_GRID_SCENES` — L8180
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L8183
- `_SFX_TYPE_ENUM` — L8551
- `_SFX_INTENSITY_ENUM` — L8556
- `_SFX_POSITION_ENUM` — L8557
- `_GRAIN_LEVEL_ENUM` — L8702
- `_CUSTOM_STYLE_BANNED_NAMES` — L9137
- `_DUANGE_XING_TEXT` — L11216

**Functions:**
- `_extract_img_url` — L6944
- `_extract_img_urls` — L6966
- `_extract_video_url` — L6999
- `_count_bands` — L7024
- `_detect_contact_sheet_like_image` — L7036
- `_file_sha256` — L7097
- `_load_upload_cache` — L7110
- `_save_upload_cache` — L7119
- `_cached_upload_url` — L7127
- `_store_upload_url` — L7144
- `_guess_upload_mime` — L7154
- `_upload_to_weryai` — L7177
- `_send_for_approval` — L7238
- `_wait_approval` — L7302
- `_render_still_segment` — L7314
- `_extract_core_terms` — L7351
- `_scene_text_visual_alignment` — L7370
- `_write_text_visual_alignment_qa` — L7391
- `_scene_motion_action_plan` — L7414
- `_ensure_motion_action_plan` — L7468
- `_motion_action_block` — L7477
- `_motion_plan_for_qa` — L7505
- `_write_motion_action_plan_qa` — L7515
- `_write_motion_bridge_refs_qa` — L7545
- `_motion_bridge_ref_prompt` — L7552
- `generate_motion_bridge_refs_gpt_image2` — L7585
- `generate_image` — L7700
- `generate_storyboard_images_gpt_image2` — L7747
- `_storyboard_grid_aspect` — L7933
- `_storyboard_grid_cols_rows` — L7940
- `_storyboard_grid_prompt` — L7962
- `_storyboard_grid_prompt_limit` — L8020
- `_is_prompt_limit_response` — L8024
- `_production_storyboard_prompt` — L8030
- `_write_production_storyboard_page_qa` — L8064
- `_character_sheet_prompt` — L8074
- `_is_audit_blocked` — L8200
- `_paraphrase_sensitive_dialogue` — L8213
- `_topic_cache_dir` — L8227
- `_topic_cache_path` — L8233
- `_load_topic_decomposition_cache` — L8246
- `_save_topic_decomposition_cache` — L8264
- `_briefs_dir` — L8301
- `_brief_path` — L8307
- `_empty_brief` — L8312
- `_deep_merge_brief_skeleton` — L8352
- `_load_brief` — L8366
- `_save_brief` — L8390
- `_brief_get` — L8409
- `_brief_field` — L8421
- `_brief_set` — L8432
- `_brief_claim` — L8448
- `_brief_agent_status` — L8491
- `_brief_from_topic_decomposition` — L8504
- `_rule_based_sfx_design` — L8560
- `_validate_sfx_entry` — L8611
- `_audio_director_design` — L8649
- `_hex_color_validate` — L8705
- `_rule_based_art_design` — L8717
- `_validate_art_design` — L8798
- `_art_director_design` — L8836
- `_coordinator_review` — L8858
- `_llm_topic_decomposition` — L8959
- `_validate_custom_visual_style` — L9144
- `_resolve_route_style` — L9166
- `_director_route_block` — L9191
- `_llm_infer_meta_grid_template` — L9258
- `_resolve_meta_grid_template` — L9315
- `_infer_meta_grid_costume` — L9358
- `_infer_meta_grid_pose` — L9407
- `_adsd_meta_grid_call_prompt` — L9454
- `_meta_grid_panel_index` — L9496
- `_migrate_speaker_ip` — L9576
- `_speaker_ips_dir` — L9601
- `_list_speaker_ips` — L9608
- `_match_speaker_ip` — L9622
- `_build_speaker_ip_context_for_script` — L9642
- `_ip_usage_stats` — L9698
- `_recommend_related_ips` — L9716
- `_save_speaker_ip` — L9741
- `_record_speaker_usage_history` — L9750
- `_format_speaker_usage_history_for_prompt` — L9797
- `_llm_infer_ip_skeleton` — L9815
- `_llm_pick_voice_asset_for_ip` — L9860
- `_auto_incubate_missing_ips` — L9909
- `_character_meta_grid_cache_dir` — L9993
- `_character_meta_grid_cache_path` — L10001
- `_character_meta_grid_cache_legacy_path` — L10009
- `_character_meta_grid_path` — L10016
- `generate_character_meta_grid_gpt_image2` — L10022
- `_generate_all_character_meta_grids` — L10194
- `_write_character_sheet_qa` — L10235
- `generate_character_sheet_gpt_image2` — L10245
- `generate_production_storyboard_page_gpt_image2` — L10345
- `_qa_clean_storyboard_panel` — L10408
- `_crop_storyboard_grid_panels` — L10589
- `generate_storyboard_grid_gpt_image2` — L10636
- `_gpt_image2_direct_annotated_aspect` — L10868
- `_gpt_image2_direct_annotated_prompt` — L10875
- `generate_gpt_image2_direct_annotated_storyboards` — L10905
- `_llm_bgm_description` — L11006
- `_bgm_contains_vocals` — L11045
- `generate_bgm` — L11079
- `_arg_value` — L11228
- `_infer_mtv_singer` — L11237
- `_ensure_mtv_singer_ip` — L11251
- `_mtv_source_lyrics` — L11306
- `_mtv_build_plan` — L11318
- `_generate_mtv_song` — L11403
- `_trim_mtv_song` — L11442
- `_mtv_generate_visual_segments` — L11455
- `_mtv_concat_and_render` — L11515
- `run_mtv_pipeline` — L11557
- `_b68_clamp_scene_durations_to_werydance_bounds` — L11580
- `step6_parallel` — L11640

---

### 第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）
Range: **L11972 – L17439** (5468 lines)

**Sub-sections:**
- _B92 (2026-06-05): 轨迹标记运镜 (Seedance 红线技法)_ — L13116-15575 (2460 lines)
- _PR-A (2026-05-27): merged_a 合并跑 helpers_ — L15576-17174 (1599 lines)
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L17175-17217 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L17218-17255 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回时间轴锚定音轨_ — L17256-17394 (139 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L17395-17439 (45 lines)

**Top-level constants:**
- `_PR3B1_SHOT_TYPE_ENUM` — L12442
- `_PR3B1_CAMERA_ANGLE_ENUM` — L12446
- `_PR3B1_LIGHTING_ENUM` — L12451
- `_PR3B1_CAMERA_MOTION_ENUM` — L12456
- `_SEEDANCE_CAMERA_GRAMMAR` — L12480
- `_DOLLY_ZOOM_EMOTIONS` — L12493
- `_GRAND_EMOTIONS` — L12498
- `_SEEDANCE_CAMERA_COMPACT` — L12503
- `_B92_HIDE_NEGATIVES` — L13119
- `_EMOTION_NARRATION_STYLE_MAP` — L13766

**Functions:**
- `_generate_motion_prompts` — L11975
- `_motion_tasks_file` — L12042
- `_motion_qa_file` — L12046
- `_append_motion_qa` — L12050
- `_finalize_motion_qa` — L12074
- `_lip_sync_tasks_file` — L12158
- `_load_motion_tasks` — L12162
- `_save_motion_task` — L12172
- `_remove_motion_task` — L12180
- `_load_lip_sync_tasks` — L12187
- `_save_lip_sync_task` — L12197
- `_remove_lip_sync_task` — L12204
- `_video_visual_motion_qa` — L12211
- `_motion_output_qa` — L12283
- `_has_audio_stream` — L12328
- `_normalize_motion_video` — L12339
- `_motion_poll_and_download` — L12389
- `_validate_enum_field` — L12462
- `_seedance_camera_directive` — L12518
- `_build_motion_video_prompt` — L12538
- `_short_board_text` — L12594
- `_wrap_board_text` — L12601
- `_storyboard_font` — L12632
- `_draw_storyboard_arrow` — L12647
- `_build_annotated_storyboard_reference` — L12661
- `_plain_caption_text` — L12762
- `_werydance_caption_request` — L12770
- `_werydance_caption_instruction` — L12797
- `_werydance_negative_prompt` — L12809
- `_motion_reference_prompt` — L12831
- `_motion_audio_dub_prompt` — L12854
- `_motion_audio_dub_poll_and_download` — L12888
- `_try_motion_audio_dub_video` — L12953
- `_b92_enabled` — L13125
- `_b92_propose_path` — L13129
- `_b92_draw_path` — L13170
- `_b92_trim_lead_frames` — L13199
- `_b92_trajectory_prompt` — L13228
- `_b92_apply_trajectory` — L13243
- `_b92_preplan_paths` — L13264
- `_try_motion_reference_video` — L13288
- `_motion_one_scene` — L13419
- `_grid_multiref_tasks_file` — L13549
- `_previs_page_tasks_file` — L13553
- `_load_grid_multiref_tasks` — L13557
- `_load_previs_page_tasks` — L13567
- `_save_grid_multiref_task` — L13577
- `_save_previs_page_task` — L13584
- `_remove_grid_multiref_task` — L13591
- `_remove_previs_page_task` — L13598
- `_poll_video_task_download` — L13605
- `_grid_multiref_group_size` — L13654
- `_grid_multiref_adaptive_group_size` — L13664
- `_grid_multiref_duration` — L13688
- `_grid_multiref_tts_buffer_factor` — L13726
- `_grid_multiref_tts_duration_buffered` — L13740
- `_grid_multiref_segment_max_stretch` — L13756
- `_voice_clone_emotion_style` — L13790
- `_grid_multiref_prompt` — L13813
- `_write_grid_multiref_motion_qa` — L13893
- `_write_previs_page_motion_qa` — L13903
- `_write_storyboard_trailer_qa` — L13913
- `_write_character_trailer_qa` — L13923
- `_write_grid_multiref_segment_qa` — L13933
- `_motion_compare_record` — L13943
- `_write_storyboard_motion_compare_qa` — L13965
- `_scene_segment_duration` — L14001
- `_apply_grid_multiref_segments` — L14020
- `_previs_page_duration` — L14225
- `_previs_page_group_prompt` — L14236
- `_previs_page_groups` — L14262
- `_storyboard_trailer_duration` — L14277
- `_storyboard_trailer_prompt` — L14287
- `_character_trailer_max_shots` — L14315
- `_character_trailer_shot_duration` — L14323
- `_character_trailer_prompt` — L14339
- `_concat_character_trailer_segments` — L14354
- `_generate_character_trailer_motion` — L14393
- `_multi_trailer_prompt_for_group` — L14501
- `_generate_multi_trailer_segments` — L14524
- `_generate_storyboard_trailer_motion` — L14635
- `_generate_previs_page_motion_segments` — L14710
- `_generate_grid_multiref_motion_segments` — L14822
- `_grid_multiref_concat_groups` — L15132
- `_grid_multiref_concat_groups_partial` — L15149
- `_grid_multiref_concat_paths` — L15167
- `_lip_sync_slot_duration` — L15209
- `_adsd_lip_sync_prompt` — L15216
- `_adsd_broll_motion_prompt` — L15262
- `_adsd_action_b_motion_prompt` — L15310
- `_adsd_silent_b_motion_prompt` — L15356
- `_adsd_narrated_b_audio_dub_prompt` — L15397
- `_adsd_almighty_audio_dub_prompt` — L15441
- `_postprocess_lip_sync_segment` — L15482
- `_detect_audio_leading_silence` — L15554
- `_concat_audio_files_for_group` — L15579
- `_split_lip_sync_raw_by_durations` — L15602
- `_postprocess_audio_dub_segment` — L15637
- `_lips_change_repair_segment` — L15765
- `_load_lips_change_requested_turns` — L15850
- `_parse_turn_set` — L15867
- `_load_motion_voice_repair_turns` — L15889
- `_voice_assets_file` — L15901
- `_load_voice_assets` — L15908
- `_build_combined_voice_reference` — L15927
- `_select_voice_asset_reference` — L15969
- `_lip_sync_poll_download_and_process` — L16045
- `_lip_sync_one_group` — L16113
- `_lip_sync_one_scene` — L16321
- `step66_adsd_lip_sync` — L16648
- `step65_motion` — L16993
- `step65_grid_multiref_motion_qa` — L17147
- `_sanitize_scene_for_state` — L17176
- `_save_pipeline_state` — L17195
- `_retime_after_audio_dub` — L17219
- `_build_voice_clone_hybrid_audio` — L17257
- `_build_dynamic_bgm` — L17396

---

### 第七步：拼接视频轨
Range: **L17440 – L17775** (336 lines)

**Functions:**
- `_rescue_motion_image_to_video` — L17441
- `_rescue_motion_text_to_video` — L17476
- `step7_concat` — L17507

---

### 第八步：生成 ASS 字幕
Range: **L17776 – L18734** (959 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L18055-18734 (680 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L17777
- `_word_timings_for_subtitle_align` — L17803
- `_align_segments_via_asr` — L17844
- `_b61_1_asr_turn_boundaries` — L17887
- `step8_subtitles` — L17949
- `_read_output_json` — L18455
- `_qa_file_pass` — L18466
- `_ass_has_dialogue` — L18473
- `_write_adsd_delivery_qa` — L18483
- `_write_bgm_only_qa` — L18623

---

### 第九步：最终合成
Range: **L18735 – L19025** (291 lines)

**Functions:**
- `step9_render` — L18736

---

### 第十步：推送 Telegram
Range: **L19026 – L20901** (1876 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L20132-20241 (110 lines)
- _B70 (2026-05-30) TG oversize policy helpers_ — L20242-20708 (467 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L20709-20713 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L20714-20777 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L20778-20823 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L20824-20901 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L19395
- `PANTONE_FALLBACK` — L19422
- `FESTIVAL_DATE_TAG` — L19536

**Functions:**
- `_generate_caption` — L19027
- `_overlay_title_on_cover` — L19265
- `_prepare_tg_photo` — L19375
- `_get_pantone_for_date` — L19425
- `_llm_bottom_note` — L19450
- `_get_bottom_note` — L19480
- `_get_date_tag` — L19558
- `_shrink_to_b64` — L19580
- `_llm_check_scenes_anomalies` — L19596
- `_llm_check_cover_unique` — L19649
- `_llm_check_cover_quality` — L19679
- `_try_almanac_cover` — L19721
- `_generate_cover_image` — L19892
- `_async_kickoff_cover_caption` — L20139
- `_await_async_cover_caption` — L20215
- `_b70_env_float` — L20245
- `_b70_split_and_deliver` — L20260
- `_b70_send_document_first` — L20373
- `step10_deliver` — L20410

---

### 主流程
Range: **L20902 – L21156** (255 lines)

**Functions:**
- `_print_execution_plan` — L20903
- `_write_run_timings` — L20962
- `main` — L20991

---
