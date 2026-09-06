# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (23033 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-132 (132 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L133-2777 (2645 lines · 78 fn · 5 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L2778-5430 (2653 lines · 33 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L5431-6664 (1234 lines · 22 fn · 2 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L6665-7216 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L7217-12959 (5743 lines · 131 fn · 8 sub)
- [`第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）`](#第-6-5-步-动态化-hads-vads-默认-on---no-motion-关) — L12960-19307 (6348 lines · 137 fn · 6 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L19308-19643 (336 lines · 3 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L19644-20602 (959 lines · 10 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L20603-20893 (291 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L20894-22778 (1885 lines · 19 fn · 6 sub)
- [`主流程`](#主流程) — L22779-23033 (255 lines · 3 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L132** (132 lines)

**Sub-sections:**
- _老黄历数据模块_ — L40-132 (93 lines)

**Functions:**
- `get_almanac_data` — L68

---

### 配置
Range: **L133 – L2777** (2645 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L375-504 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L505-1249 (745 lines)
- _工具函数_ — L1250-1713 (464 lines)
- _B87 纹理档系统：LLM 提名 + 代码护栏 + 确定性渲染_ — L1714-1976 (263 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1977-2777 (801 lines)

**Top-level constants:**
- `HEADERS` — L172
- `VIDEO_FORMAT_RAW` — L180
- `MTV_MODE` — L181
- `VIDEO_FORMAT` — L186
- `ADS_DIALOGUE_MODE_EARLY_CHECK` — L197
- `WITH_MOTION` — L204
- `BGM_ONLY_REQUESTED` — L209
- `ADS_DIALOGUE_MODE` — L216
- `GPT_IMAGE2_STORYBOARD` — L228
- `STORYBOARD_REFERENCE_MOTION` — L232
- `STORYBOARD_ANNOTATED_MOTION` — L236
- `GPT_IMAGE2_DIRECT_ANNOTATED_STORYBOARD` — L240
- `GPT_IMAGE2_STORYBOARD_GRID` — L245
- `ADSD_STORYBOARD_GRID` — L253
- `ADS_CHARACTER_SHEET_REQUESTED` — L259
- `STORYBOARD_GRID_MULTIREF_MOTION` — L263
- `STORYBOARD_GRID_MULTIREF_SEGMENTS` — L267
- `STORYBOARD_GRID_MULTIREF_MAIN` — L273
- `GRID_MULTIREF_PRIMARY` — L283
- `PREVIS_PAGE_MOTION` — L295
- `STORYBOARD_TRAILER_MODE` — L299
- `MOTION_ACTION_STORYBOARD` — L304
- `MOTION_BRIDGE_REFS` — L308
- `CHARACTER_TRAILER_MODE` — L312
- `STORYBOARD_TRAILER_MAIN` — L320
- `ADSD_LIP_SYNC_EXPERIMENT` — L333
- `ADSD_RICH_MOTION_PROMPT` — L341
- `ADSD_LLM_VOICE_ASSIGN` — L349
- `ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT` — L353
- `ADSD_CONSECUTIVE_SPEAKER_BATCHING` — L367
- `ADSD_GENDER_FALLBACK_VOICE_ASSET` — L378
- `SILENT_B_SPEAKERS` — L510
- `_PODCAST_TO_VOICE_ASSET_MAP` — L889
- `_VOICE_ASSET_FORBIDDEN_FLAGS` — L907
- `_GENERIC_NARRATOR_NAMES` — L951
- `VOICE_ASSET_AUDIO_DUB_EXPERIMENT` — L988
- `VOICE_ASSET_AUDIO_DUB_PARTIAL_OK` — L996
- `MOTION_VISUAL_QA` — L1000
- `MOTION_VOICE_REPAIR` — L1008
- `MOTION_VOICE_STRICT_LOCK` — L1013
- `WERYDANCE_CAPTIONS` — L1018
- `ADSD_ONSITE_POV_MODE` — L1030
- `ADSD_LIPS_CHANGE_REPAIR` — L1035
- `ADSD_LIPS_CHANGE_ALL` — L1040
- `ADS_REPORTER_MODE` — L1051
- `ADS_STORYBOARD_FLOW_DEFAULT` — L1068
- `ADS_RETENTION_MODE` — L1082
- `ADSD_MODE_NAME` — L1088
- `EMOTION_STYLE` — L1229
- `EMOTION_STYLE_BRIGHT` — L1241
- `_REDACT_PATTERNS_DEFAULT` — L1255
- `_TG_DASHBOARD_STAGES` — L1307
- `_TG_NOISY_PATTERNS` — L1322
- `_TG_IMMEDIATE_PATTERNS` — L1340
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1707
- `_TEXTURE_MODE_ENUM` — L1715
- `_TEXTURE_SUFFIX_MAP` — L1720
- `_TEXTURE_BODY_DIRECTIVE` — L1747
- `_TEXTURE_SCENE_PHRASE` — L1754
- `_TEXTURE_GRID_PHRASE` — L1761
- `_TEXTURE_MOTION_PHRASE` — L1769
- `_LLM_TIER` — L2184
- `_TOPIC_MODIFIERS` — L2530
- `_TONE_PANTONE_OVERRIDE` — L2547

**Functions:**
- `_read_almighty_model` — L152
- `_is_action_scene` — L387
- `_needs_storyboard_flow_character_sheet` — L398
- `_wuxia_action_panel_prompt` — L427
- `_action_motion_fragment` — L449
- `_infer_emotion_from_text` — L464
- `_emotion_expression_phrase` — L479
- `_infer_needs_lip_sync` — L486
- `_infer_turn_type` — L513
- `_is_action_shout` — L538
- `_resolve_turn_type` — L564
- `_is_silent_b` — L579
- `_is_narrated_b` — L583
- `_is_a_roll` — L587
- `_is_action_b` — L591
- `_voice_asset_id_for_speaker` — L595
- `_llm_assign_voice_assets` — L623
- `_apply_llm_voice_assignment` — L753
- `_voice_asset_is_speech_safe` — L914
- `_podcast_id_to_voice_asset` — L920
- `_resolve_voice_asset_for_ads_speaker` — L954
- `_redact_for_stdout` — L1270
- `log` — L1295
- `_tg_send_raw` — L1363
- `_tg_matches` — L1379
- `_tg_summarize` — L1383
- `_tg_dashboard_stage_for` — L1390
- `_tg_progress_bar` — L1398
- `_tg_dashboard_text` — L1404
- `_tg_dashboard_update` — L1422
- `_tg_maybe_digest` — L1459
- `tg` — L1474
- `_wait_image_submit_slot` — L1523
- `_wait_motion_submit_slot` — L1536
- `_is_rate_limited_error` — L1549
- `_is_rate_limited_response` — L1559
- `_is_transient_workflow_error` — L1571
- `_is_llm_rate_limited_error` — L1595
- `_is_llm_retryable_server_error` — L1613
- `_is_llm_model_missing_error` — L1655
- `_era_is_pre_photographic` — L1781
- `_texture_mode_fallback` — L1809
- `_texture_guardrail` — L1830
- `_set_active_texture_profile` — L1869
- `_active_texture_suffix` — L1882
- `_active_texture_body_directive` — L1886
- `_active_texture_scene_phrase` — L1890
- `_active_texture_grid_phrase` — L1894
- `_active_texture_motion_phrase` — L1898
- `_inject_image2_quality_suffix` — L1902
- `submit_text_to_image` — L1922
- `req_post` — L1958
- `req_get` — L1972
- `_tg_probe_send` — L1980
- `_tg_probe_delete` — L2000
- `_tg_upload_with_probe_gap` — L2013
- `poll` — L2053
- `poll_podcast` — L2078
- `poll_task_status` — L2100
- `poll_storyboard_task` — L2122
- `_read_model_list` — L2156
- `tier_chat` — L2192
- `chat` — L2206
- `_vision_chat_completion` — L2326
- `pick_image_model` — L2376
- `detect_topic_meta` — L2401
- `_topic_culture_guard` — L2451
- `_write_cultural_visual_qa` — L2477
- `is_1919_global_topic` — L2524
- `_strip_topic_modifiers` — L2535
- `apply_1919_global_guardrails` — L2553
- `build_1919_global_cover_prompt` — L2582
- `_shot_blueprint_enums` — L2614
- `build_shot_blueprint` — L2690
- `ffprobe_duration` — L2716
- `ffprobe_video_size` — L2727
- `_video_decode_probe` — L2748
- `ffmpeg` — L2766

---

### 第一步：双导演生成剧本
Range: **L2778 – L5430** (2653 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L4410-5430 (1021 lines)

**Top-level constants:**
- `_ENSEMBLE_CAP_BY_ROUTE` — L2930

**Functions:**
- `_extract_json_array` — L2779
- `_extract_json_object` — L2789
- `_voice_for_speaker` — L2799
- `_adsd_gender_from_voice` — L2835
- `_adsd_infer_gender_from_speaker` — L2843
- `_adsd_gender_lock_phrase` — L2852
- `_adsd_visual_subject_has_gender_conflict` — L2867
- `_adsd_default_roles` — L2879
- `_adsd_allows_media_role` — L2884
- `_adsd_role_candidates` — L2892
- `_adsd_dialogue_shape` — L2919
- `_ensemble_speaker_cap` — L2941
- `_ip_voice_asset_for_speaker` — L2954
- `_finalize_adsd_turns` — L2978
- `_parse_adsd_override_turns` — L3024
- `_parse_timecode_seconds` — L3117
- `_clean_override_line_text` — L3126
- `_parse_override_script_text` — L3132
- `_adsd_pov_contract` — L3166
- `_load_audit_blacklist_block` — L3179
- `_generate_adsd_dialogue_turns` — L3217
- `_broll_rhythm_reviewer` — L3644
- `_sweep_speaker_field` — L3751
- `_should_run_immersion_qa` — L3811
- `_adsd_immersion_qa_rewrite_turns` — L3834
- `_adsd_visual_contract` — L3898
- `_parse_risk_score` — L3950
- `_check_high_risk_hard_abort` — L3979
- `_maybe_neutralize_topic` — L4006
- `_apply_render_budget_scene_cap` — L4045
- `_apply_llm_mode_decision` — L4072
- `step1_script` — L4127
- `_write_ads_retention_qa` — L5374

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L5431 – L6664** (1234 lines)

**Sub-sections:**
- _B88: 内容审核(1002) → 分级软化 → 中性兜底句 → 静音 backstop，绝不崩管线_ — L6127-6155 (29 lines)
- _非内容审核(网络/transient): 有限退避重试，耗尽才抛_ — L6156-6664 (509 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L5506
- `_ADSD_POLICY_REWRITE_TERMS` — L5512
- `_TTS_SAFE_FALLBACK_LINE` — L5614
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L5682

**Functions:**
- `_openai_tts_fallback` — L5432
- `_edge_tts_fallback` — L5478
- `_sanitize_for_external_api` — L5537
- `_is_content_policy_error` — L5546
- `_rewrite_adsd_tts_text_for_policy` — L5560
- `_tts_safe_fallback_line` — L5623
- `_tts_silent_placeholder` — L5628
- `_record_adsd_tts_rewrite` — L5663
- `_build_silence_mp3` — L5688
- `_audio_duration_seconds` — L5701
- `_text_to_audio_master_voice_timed` — L5713
- `_text_to_audio_master_voice` — L5838
- `step2_master_voice` — L5951
- `_tts_turn_to_audio` — L6079
- `_asr_verify_dialogue_audio` — L6166
- `_asr_verify_dialogue_turns` — L6228
- `_normalize_cn_number_token` — L6270
- `_compact_zh_text` — L6292
- `_write_adsd_asr_text_qa` — L6299
- `_write_adsd_speaker_focus_qa` — L6338
- `_write_adsd_gender_voice_qa` — L6398
- `step2_dialogue_voice` — L6451

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L6665 – L7216** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L6672-6794 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L6795-6829 (35 lines)
- _第二层：字符数插值_ — L6830-6854 (25 lines)
- _第三层：silencedetect 物理校准_ — L6855-7216 (362 lines)

**Functions:**
- `_detect_silences` — L6673
- `_calibrate_boundaries` — L6708
- `_enforce_monotonic` — L6742
- `_manual_override_segments` — L6754
- `_calc_sentence_boundaries` — L6775
- `step345_timeline` — L6886
- `_analyze_bgm_energy_cuts` — L6945
- `_snap_bgm_only_boundaries` — L7008
- `step345_bgm_only_timeline` — L7068

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L7217 – L12959** (5743 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L8446-8496 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L8497-9355 (859 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L9356-9843 (488 lines)
- _Speaker IP Card (2026-05-21)_ — L9844-11488 (1645 lines)
- _MTV：原创歌曲 + 主唱人物库 + WeryDance MV_ — L11489-12558 (1070 lines)
- _B68 (2026-05-30) WERYDANCE 段长合规 gate_ — L12559-12791 (233 lines)
- _审批流程_ — L12792-12848 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L12849-12959 (111 lines)

**Top-level constants:**
- `_CORE_TERMS_STOP_WORDS` — L7619
- `CHARACTER_META_GRID_COSTUMES` — L8452
- `CHARACTER_META_GRID_POSES` — L8453
- `CHARACTER_META_GRID_SCENES` — L8454
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L8457
- `_SFX_TYPE_ENUM` — L8825
- `_SFX_INTENSITY_ENUM` — L8830
- `_SFX_POSITION_ENUM` — L8831
- `_GRAIN_LEVEL_ENUM` — L8976
- `_CUSTOM_STYLE_BANNED_NAMES` — L9411
- `_DUANGE_XING_TEXT` — L11490

**Functions:**
- `_extract_img_url` — L7218
- `_extract_img_urls` — L7240
- `_extract_video_url` — L7273
- `_count_bands` — L7298
- `_detect_contact_sheet_like_image` — L7310
- `_file_sha256` — L7371
- `_load_upload_cache` — L7384
- `_save_upload_cache` — L7393
- `_cached_upload_url` — L7401
- `_store_upload_url` — L7418
- `_guess_upload_mime` — L7428
- `_upload_to_weryai` — L7451
- `_send_for_approval` — L7512
- `_wait_approval` — L7576
- `_render_still_segment` — L7588
- `_extract_core_terms` — L7625
- `_scene_text_visual_alignment` — L7644
- `_write_text_visual_alignment_qa` — L7665
- `_scene_motion_action_plan` — L7688
- `_ensure_motion_action_plan` — L7742
- `_motion_action_block` — L7751
- `_motion_plan_for_qa` — L7779
- `_write_motion_action_plan_qa` — L7789
- `_write_motion_bridge_refs_qa` — L7819
- `_motion_bridge_ref_prompt` — L7826
- `generate_motion_bridge_refs_gpt_image2` — L7859
- `generate_image` — L7974
- `generate_storyboard_images_gpt_image2` — L8021
- `_storyboard_grid_aspect` — L8207
- `_storyboard_grid_cols_rows` — L8214
- `_storyboard_grid_prompt` — L8236
- `_storyboard_grid_prompt_limit` — L8294
- `_is_prompt_limit_response` — L8298
- `_production_storyboard_prompt` — L8304
- `_write_production_storyboard_page_qa` — L8338
- `_character_sheet_prompt` — L8348
- `_is_audit_blocked` — L8474
- `_paraphrase_sensitive_dialogue` — L8487
- `_topic_cache_dir` — L8501
- `_topic_cache_path` — L8507
- `_load_topic_decomposition_cache` — L8520
- `_save_topic_decomposition_cache` — L8538
- `_briefs_dir` — L8575
- `_brief_path` — L8581
- `_empty_brief` — L8586
- `_deep_merge_brief_skeleton` — L8626
- `_load_brief` — L8640
- `_save_brief` — L8664
- `_brief_get` — L8683
- `_brief_field` — L8695
- `_brief_set` — L8706
- `_brief_claim` — L8722
- `_brief_agent_status` — L8765
- `_brief_from_topic_decomposition` — L8778
- `_rule_based_sfx_design` — L8834
- `_validate_sfx_entry` — L8885
- `_audio_director_design` — L8923
- `_hex_color_validate` — L8979
- `_rule_based_art_design` — L8991
- `_validate_art_design` — L9072
- `_art_director_design` — L9110
- `_coordinator_review` — L9132
- `_llm_topic_decomposition` — L9233
- `_validate_custom_visual_style` — L9418
- `_resolve_route_style` — L9440
- `_director_route_block` — L9465
- `_llm_infer_meta_grid_template` — L9532
- `_resolve_meta_grid_template` — L9589
- `_infer_meta_grid_costume` — L9632
- `_infer_meta_grid_pose` — L9681
- `_adsd_meta_grid_call_prompt` — L9728
- `_meta_grid_panel_index` — L9770
- `_migrate_speaker_ip` — L9850
- `_speaker_ips_dir` — L9875
- `_list_speaker_ips` — L9882
- `_match_speaker_ip` — L9896
- `_build_speaker_ip_context_for_script` — L9916
- `_ip_usage_stats` — L9972
- `_recommend_related_ips` — L9990
- `_save_speaker_ip` — L10015
- `_record_speaker_usage_history` — L10024
- `_format_speaker_usage_history_for_prompt` — L10071
- `_llm_infer_ip_skeleton` — L10089
- `_llm_pick_voice_asset_for_ip` — L10134
- `_auto_incubate_missing_ips` — L10183
- `_character_meta_grid_cache_dir` — L10267
- `_character_meta_grid_cache_path` — L10275
- `_character_meta_grid_cache_legacy_path` — L10283
- `_character_meta_grid_path` — L10290
- `generate_character_meta_grid_gpt_image2` — L10296
- `_generate_all_character_meta_grids` — L10468
- `_write_character_sheet_qa` — L10509
- `generate_character_sheet_gpt_image2` — L10519
- `generate_production_storyboard_page_gpt_image2` — L10619
- `_qa_clean_storyboard_panel` — L10682
- `_crop_storyboard_grid_panels` — L10863
- `generate_storyboard_grid_gpt_image2` — L10910
- `_gpt_image2_direct_annotated_aspect` — L11142
- `_gpt_image2_direct_annotated_prompt` — L11149
- `generate_gpt_image2_direct_annotated_storyboards` — L11179
- `_llm_bgm_description` — L11280
- `_bgm_contains_vocals` — L11319
- `generate_bgm` — L11353
- `_arg_value` — L11502
- `_infer_mtv_singer` — L11511
- `_ensure_mtv_singer_ip` — L11525
- `_mtv_source_lyrics` — L11580
- `_mtv_build_plan` — L11592
- `_generate_mtv_song` — L11677
- `_trim_mtv_song` — L11716
- `_mtv_generate_visual_segments` — L11729
- `_mtv_ass_time` — L11964
- `_mtv_ass_escape` — L11973
- `_mtv_wrap_lyric` — L11979
- `_mtv_vocal_span_from_asr` — L12004
- `_mtv_split_lyric_clauses` — L12048
- `_mtv_split_lyric_phrases` — L12060
- `_mtv_norm_zh` — L12073
- `_mtv_best_phrase_offset` — L12077
- `_mtv_asr_phrase_records` — L12097
- `_mtv_alignment_from_script` — L12140
- `_mtv_split_span` — L12193
- `_mtv_song_slice` — L12203
- `_mtv_normalize_segment_duration` — L12211
- `_mtv_static_fallback_segment` — L12247
- `_mtv_lip_sync_segment` — L12269
- `_write_mtv_subtitles` — L12422
- `_mtv_concat_and_render` — L12494
- `run_mtv_pipeline` — L12544
- `_b68_clamp_scene_durations_to_werydance_bounds` — L12567
- `step6_parallel` — L12627

---

### 第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）
Range: **L12960 – L19307** (6348 lines)

**Sub-sections:**
- _B92 (2026-06-05): 轨迹标记运镜 (Seedance 红线技法)_ — L14457-16984 (2528 lines)
- _PR-A (2026-05-27): merged_a 合并跑 helpers_ — L16985-19042 (2058 lines)
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L19043-19085 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L19086-19123 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回时间轴锚定音轨_ — L19124-19262 (139 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L19263-19307 (45 lines)

**Top-level constants:**
- `_PR3B1_SHOT_TYPE_ENUM` — L13777
- `_PR3B1_CAMERA_ANGLE_ENUM` — L13781
- `_PR3B1_LIGHTING_ENUM` — L13786
- `_PR3B1_CAMERA_MOTION_ENUM` — L13791
- `_SEEDANCE_CAMERA_GRAMMAR` — L13815
- `_DOLLY_ZOOM_EMOTIONS` — L13828
- `_GRAND_EMOTIONS` — L13833
- `_SEEDANCE_CAMERA_COMPACT` — L13838
- `_B92_HIDE_NEGATIVES` — L14460
- `_EMOTION_NARRATION_STYLE_MAP` — L15151

**Functions:**
- `_generate_motion_prompts` — L12963
- `_motion_tasks_file` — L13031
- `_motion_qa_file` — L13037
- `_append_motion_qa` — L13041
- `_finalize_motion_qa` — L13065
- `_lip_sync_tasks_file` — L13149
- `_lip_sync_tasks_lock_file` — L13153
- `_lip_sync_tasks_guard` — L13158
- `_normalize_generation_interface` — L13171
- `_generation_task_record` — L13181
- `_normalize_cached_task` — L13199
- `_load_generation_tasks` — L13226
- `_atomic_write_json` — L13243
- `_load_motion_tasks` — L13268
- `_save_motion_task` — L13274
- `_remove_motion_task` — L13294
- `_load_lip_sync_tasks` — L13301
- `_mtv_lip_sync_task_key` — L13308
- `_merged_lip_sync_task_key` — L13312
- `_lip_sync_task_indices` — L13316
- `_find_overlapping_lip_sync_task` — L13344
- `_lip_sync_conflict_info` — L13361
- `_is_reusable_lip_sync_raw_video` — L13372
- `_lip_sync_group_raw_path` — L13382
- `_find_merged_lip_sync_task` — L13387
- `_save_lip_sync_task` — L13396
- `_submit_lip_sync_task_transaction` — L13422
- `_is_lip_sync_submission_reservation` — L13523
- `_remove_lip_sync_task` — L13533
- `_video_visual_motion_qa` — L13546
- `_motion_output_qa` — L13618
- `_has_audio_stream` — L13663
- `_normalize_motion_video` — L13674
- `_motion_poll_and_download` — L13724
- `_validate_enum_field` — L13797
- `_seedance_camera_directive` — L13853
- `_build_motion_video_prompt` — L13873
- `_short_board_text` — L13929
- `_wrap_board_text` — L13936
- `_storyboard_font` — L13967
- `_draw_storyboard_arrow` — L13982
- `_build_annotated_storyboard_reference` — L13996
- `_plain_caption_text` — L14097
- `_werydance_caption_request` — L14105
- `_werydance_caption_instruction` — L14132
- `_werydance_negative_prompt` — L14144
- `_motion_reference_prompt` — L14166
- `_motion_audio_dub_prompt` — L14189
- `_motion_audio_dub_poll_and_download` — L14223
- `_try_motion_audio_dub_video` — L14289
- `_b92_enabled` — L14466
- `_b92_propose_path` — L14470
- `_b92_draw_path` — L14511
- `_b92_trim_lead_frames` — L14540
- `_b92_trajectory_prompt` — L14569
- `_b92_apply_trajectory` — L14584
- `_b92_preplan_paths` — L14605
- `_try_motion_reference_video` — L14629
- `_resume_motion_task` — L14766
- `_motion_one_scene` — L14798
- `_grid_multiref_tasks_file` — L14920
- `_previs_page_tasks_file` — L14924
- `_load_grid_multiref_tasks` — L14928
- `_load_previs_page_tasks` — L14935
- `_save_grid_multiref_task` — L14942
- `_save_previs_page_task` — L14959
- `_remove_grid_multiref_task` — L14976
- `_remove_previs_page_task` — L14983
- `_poll_video_task_download` — L14990
- `_grid_multiref_group_size` — L15039
- `_grid_multiref_adaptive_group_size` — L15049
- `_grid_multiref_duration` — L15073
- `_grid_multiref_tts_buffer_factor` — L15111
- `_grid_multiref_tts_duration_buffered` — L15125
- `_grid_multiref_segment_max_stretch` — L15141
- `_voice_clone_emotion_style` — L15175
- `_grid_multiref_prompt` — L15198
- `_write_grid_multiref_motion_qa` — L15278
- `_write_previs_page_motion_qa` — L15288
- `_write_storyboard_trailer_qa` — L15298
- `_write_character_trailer_qa` — L15308
- `_write_grid_multiref_segment_qa` — L15318
- `_motion_compare_record` — L15328
- `_write_storyboard_motion_compare_qa` — L15350
- `_scene_segment_duration` — L15386
- `_apply_grid_multiref_segments` — L15405
- `_previs_page_duration` — L15610
- `_previs_page_group_prompt` — L15621
- `_previs_page_groups` — L15647
- `_storyboard_trailer_duration` — L15662
- `_storyboard_trailer_prompt` — L15672
- `_character_trailer_max_shots` — L15700
- `_character_trailer_shot_duration` — L15708
- `_character_trailer_prompt` — L15724
- `_concat_character_trailer_segments` — L15739
- `_generate_character_trailer_motion` — L15778
- `_multi_trailer_prompt_for_group` — L15886
- `_generate_multi_trailer_segments` — L15909
- `_generate_storyboard_trailer_motion` — L16020
- `_generate_previs_page_motion_segments` — L16095
- `_generate_grid_multiref_motion_segments` — L16213
- `_grid_multiref_concat_groups` — L16541
- `_grid_multiref_concat_groups_partial` — L16558
- `_grid_multiref_concat_paths` — L16576
- `_lip_sync_slot_duration` — L16618
- `_adsd_lip_sync_prompt` — L16625
- `_adsd_broll_motion_prompt` — L16671
- `_adsd_action_b_motion_prompt` — L16719
- `_adsd_silent_b_motion_prompt` — L16765
- `_adsd_narrated_b_audio_dub_prompt` — L16806
- `_adsd_almighty_audio_dub_prompt` — L16850
- `_postprocess_lip_sync_segment` — L16891
- `_detect_audio_leading_silence` — L16963
- `_concat_audio_files_for_group` — L16988
- `_split_lip_sync_raw_by_durations` — L17011
- `_postprocess_audio_dub_segment` — L17046
- `_lips_change_repair_segment` — L17174
- `_load_lips_change_requested_turns` — L17259
- `_parse_turn_set` — L17276
- `_load_motion_voice_repair_turns` — L17298
- `_voice_assets_file` — L17310
- `_load_voice_assets` — L17317
- `_build_combined_voice_reference` — L17336
- `_select_voice_asset_reference` — L17378
- `_lip_sync_poll_download_and_process` — L17454
- `_resume_lip_sync_task` — L17563
- `_poll_download_and_process_lip_sync_group` — L17592
- `_lip_sync_one_group` — L17756
- `_lip_sync_one_scene` — L18094
- `step66_adsd_lip_sync` — L18505
- `step65_motion` — L18858
- `step65_grid_multiref_motion_qa` — L19015
- `_sanitize_scene_for_state` — L19044
- `_save_pipeline_state` — L19063
- `_retime_after_audio_dub` — L19087
- `_build_voice_clone_hybrid_audio` — L19125
- `_build_dynamic_bgm` — L19264

---

### 第七步：拼接视频轨
Range: **L19308 – L19643** (336 lines)

**Functions:**
- `_rescue_motion_image_to_video` — L19309
- `_rescue_motion_text_to_video` — L19344
- `step7_concat` — L19375

---

### 第八步：生成 ASS 字幕
Range: **L19644 – L20602** (959 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L19923-20602 (680 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L19645
- `_word_timings_for_subtitle_align` — L19671
- `_align_segments_via_asr` — L19712
- `_b61_1_asr_turn_boundaries` — L19755
- `step8_subtitles` — L19817
- `_read_output_json` — L20323
- `_qa_file_pass` — L20334
- `_ass_has_dialogue` — L20341
- `_write_adsd_delivery_qa` — L20351
- `_write_bgm_only_qa` — L20491

---

### 第九步：最终合成
Range: **L20603 – L20893** (291 lines)

**Functions:**
- `step9_render` — L20604

---

### 第十步：推送 Telegram
Range: **L20894 – L22778** (1885 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L22002-22111 (110 lines)
- _B70 (2026-05-30) TG oversize policy helpers_ — L22112-22583 (472 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L22584-22588 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L22589-22653 (65 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L22654-22700 (47 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L22701-22778 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L21264
- `PANTONE_FALLBACK` — L21291
- `FESTIVAL_DATE_TAG` — L21405

**Functions:**
- `_generate_caption` — L20895
- `_overlay_title_on_cover` — L21134
- `_prepare_tg_photo` — L21244
- `_get_pantone_for_date` — L21294
- `_llm_bottom_note` — L21319
- `_get_bottom_note` — L21349
- `_get_date_tag` — L21427
- `_shrink_to_b64` — L21449
- `_llm_check_scenes_anomalies` — L21465
- `_llm_check_cover_unique` — L21518
- `_llm_check_cover_quality` — L21548
- `_try_almanac_cover` — L21590
- `_generate_cover_image` — L21761
- `_async_kickoff_cover_caption` — L22009
- `_await_async_cover_caption` — L22085
- `_b70_env_float` — L22115
- `_b70_split_and_deliver` — L22130
- `_b70_send_document_first` — L22243
- `step10_deliver` — L22280

---

### 主流程
Range: **L22779 – L23033** (255 lines)

**Functions:**
- `_print_execution_plan` — L22780
- `_write_run_timings` — L22839
- `main` — L22868

---
