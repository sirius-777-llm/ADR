# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (22015 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-124 (124 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L125-2534 (2410 lines · 74 fn · 5 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L2535-5186 (2652 lines · 33 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L5187-6419 (1233 lines · 22 fn · 2 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L6420-6971 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L6972-12611 (5640 lines · 131 fn · 8 sub)
- [`第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）`](#第-6-5-步-动态化-hads-vads-默认-on---no-motion-关) — L12612-18291 (5680 lines · 123 fn · 6 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L18292-18627 (336 lines · 3 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L18628-19586 (959 lines · 10 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L19587-19877 (291 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L19878-21760 (1883 lines · 19 fn · 6 sub)
- [`主流程`](#主流程) — L21761-22015 (255 lines · 3 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L124** (124 lines)

**Sub-sections:**
- _老黄历数据模块_ — L32-124 (93 lines)

**Functions:**
- `get_almanac_data` — L60

---

### 配置
Range: **L125 – L2534** (2410 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L367-496 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L497-1240 (744 lines)
- _工具函数_ — L1241-1616 (376 lines)
- _B87 纹理档系统：LLM 提名 + 代码护栏 + 确定性渲染_ — L1617-1879 (263 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1880-2534 (655 lines)

**Top-level constants:**
- `HEADERS` — L164
- `VIDEO_FORMAT_RAW` — L172
- `MTV_MODE` — L173
- `VIDEO_FORMAT` — L178
- `ADS_DIALOGUE_MODE_EARLY_CHECK` — L189
- `WITH_MOTION` — L196
- `BGM_ONLY_REQUESTED` — L201
- `ADS_DIALOGUE_MODE` — L208
- `GPT_IMAGE2_STORYBOARD` — L220
- `STORYBOARD_REFERENCE_MOTION` — L224
- `STORYBOARD_ANNOTATED_MOTION` — L228
- `GPT_IMAGE2_DIRECT_ANNOTATED_STORYBOARD` — L232
- `GPT_IMAGE2_STORYBOARD_GRID` — L237
- `ADSD_STORYBOARD_GRID` — L245
- `ADS_CHARACTER_SHEET_REQUESTED` — L251
- `STORYBOARD_GRID_MULTIREF_MOTION` — L255
- `STORYBOARD_GRID_MULTIREF_SEGMENTS` — L259
- `STORYBOARD_GRID_MULTIREF_MAIN` — L265
- `GRID_MULTIREF_PRIMARY` — L275
- `PREVIS_PAGE_MOTION` — L287
- `STORYBOARD_TRAILER_MODE` — L291
- `MOTION_ACTION_STORYBOARD` — L296
- `MOTION_BRIDGE_REFS` — L300
- `CHARACTER_TRAILER_MODE` — L304
- `STORYBOARD_TRAILER_MAIN` — L312
- `ADSD_LIP_SYNC_EXPERIMENT` — L325
- `ADSD_RICH_MOTION_PROMPT` — L333
- `ADSD_LLM_VOICE_ASSIGN` — L341
- `ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT` — L345
- `ADSD_CONSECUTIVE_SPEAKER_BATCHING` — L359
- `ADSD_GENDER_FALLBACK_VOICE_ASSET` — L370
- `SILENT_B_SPEAKERS` — L502
- `_PODCAST_TO_VOICE_ASSET_MAP` — L880
- `_VOICE_ASSET_FORBIDDEN_FLAGS` — L898
- `_GENERIC_NARRATOR_NAMES` — L942
- `VOICE_ASSET_AUDIO_DUB_EXPERIMENT` — L979
- `VOICE_ASSET_AUDIO_DUB_PARTIAL_OK` — L987
- `MOTION_VISUAL_QA` — L991
- `MOTION_VOICE_REPAIR` — L999
- `MOTION_VOICE_STRICT_LOCK` — L1004
- `WERYDANCE_CAPTIONS` — L1009
- `ADSD_ONSITE_POV_MODE` — L1021
- `ADSD_LIPS_CHANGE_REPAIR` — L1026
- `ADSD_LIPS_CHANGE_ALL` — L1031
- `ADS_REPORTER_MODE` — L1042
- `ADS_STORYBOARD_FLOW_DEFAULT` — L1059
- `ADS_RETENTION_MODE` — L1073
- `ADSD_MODE_NAME` — L1079
- `EMOTION_STYLE` — L1220
- `EMOTION_STYLE_BRIGHT` — L1232
- `_REDACT_PATTERNS_DEFAULT` — L1246
- `_TG_DASHBOARD_STAGES` — L1298
- `_TG_NOISY_PATTERNS` — L1313
- `_TG_IMMEDIATE_PATTERNS` — L1331
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1610
- `_TEXTURE_MODE_ENUM` — L1618
- `_TEXTURE_SUFFIX_MAP` — L1623
- `_TEXTURE_BODY_DIRECTIVE` — L1650
- `_TEXTURE_SCENE_PHRASE` — L1657
- `_TEXTURE_GRID_PHRASE` — L1664
- `_TEXTURE_MOTION_PHRASE` — L1672
- `_LLM_TIER` — L2060
- `_TOPIC_MODIFIERS` — L2287
- `_TONE_PANTONE_OVERRIDE` — L2304

**Functions:**
- `_read_almighty_model` — L144
- `_is_action_scene` — L379
- `_needs_storyboard_flow_character_sheet` — L390
- `_wuxia_action_panel_prompt` — L419
- `_action_motion_fragment` — L441
- `_infer_emotion_from_text` — L456
- `_emotion_expression_phrase` — L471
- `_infer_needs_lip_sync` — L478
- `_infer_turn_type` — L505
- `_is_action_shout` — L530
- `_resolve_turn_type` — L556
- `_is_silent_b` — L571
- `_is_narrated_b` — L575
- `_is_a_roll` — L579
- `_is_action_b` — L583
- `_voice_asset_id_for_speaker` — L587
- `_llm_assign_voice_assets` — L615
- `_apply_llm_voice_assignment` — L744
- `_voice_asset_is_speech_safe` — L905
- `_podcast_id_to_voice_asset` — L911
- `_resolve_voice_asset_for_ads_speaker` — L945
- `_redact_for_stdout` — L1261
- `log` — L1286
- `_tg_send_raw` — L1354
- `_tg_matches` — L1370
- `_tg_summarize` — L1374
- `_tg_dashboard_stage_for` — L1381
- `_tg_progress_bar` — L1389
- `_tg_dashboard_text` — L1395
- `_tg_dashboard_update` — L1413
- `_tg_maybe_digest` — L1450
- `tg` — L1465
- `_wait_image_submit_slot` — L1514
- `_wait_motion_submit_slot` — L1527
- `_is_rate_limited_error` — L1540
- `_is_rate_limited_response` — L1550
- `_is_transient_workflow_error` — L1562
- `_is_llm_rate_limited_error` — L1586
- `_era_is_pre_photographic` — L1684
- `_texture_mode_fallback` — L1712
- `_texture_guardrail` — L1733
- `_set_active_texture_profile` — L1772
- `_active_texture_suffix` — L1785
- `_active_texture_body_directive` — L1789
- `_active_texture_scene_phrase` — L1793
- `_active_texture_grid_phrase` — L1797
- `_active_texture_motion_phrase` — L1801
- `_inject_image2_quality_suffix` — L1805
- `submit_text_to_image` — L1825
- `req_post` — L1861
- `req_get` — L1875
- `_tg_probe_send` — L1883
- `_tg_probe_delete` — L1903
- `_tg_upload_with_probe_gap` — L1916
- `poll` — L1956
- `poll_podcast` — L1981
- `poll_task_status` — L2003
- `poll_storyboard_task` — L2025
- `tier_chat` — L2068
- `chat` — L2074
- `pick_image_model` — L2133
- `detect_topic_meta` — L2158
- `_topic_culture_guard` — L2208
- `_write_cultural_visual_qa` — L2234
- `is_1919_global_topic` — L2281
- `_strip_topic_modifiers` — L2292
- `apply_1919_global_guardrails` — L2310
- `build_1919_global_cover_prompt` — L2339
- `_shot_blueprint_enums` — L2371
- `build_shot_blueprint` — L2447
- `ffprobe_duration` — L2473
- `ffprobe_video_size` — L2484
- `_video_decode_probe` — L2505
- `ffmpeg` — L2523

---

### 第一步：双导演生成剧本
Range: **L2535 – L5186** (2652 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L4167-5186 (1020 lines)

**Top-level constants:**
- `_ENSEMBLE_CAP_BY_ROUTE` — L2687

**Functions:**
- `_extract_json_array` — L2536
- `_extract_json_object` — L2546
- `_voice_for_speaker` — L2556
- `_adsd_gender_from_voice` — L2592
- `_adsd_infer_gender_from_speaker` — L2600
- `_adsd_gender_lock_phrase` — L2609
- `_adsd_visual_subject_has_gender_conflict` — L2624
- `_adsd_default_roles` — L2636
- `_adsd_allows_media_role` — L2641
- `_adsd_role_candidates` — L2649
- `_adsd_dialogue_shape` — L2676
- `_ensemble_speaker_cap` — L2698
- `_ip_voice_asset_for_speaker` — L2711
- `_finalize_adsd_turns` — L2735
- `_parse_adsd_override_turns` — L2781
- `_parse_timecode_seconds` — L2874
- `_clean_override_line_text` — L2883
- `_parse_override_script_text` — L2889
- `_adsd_pov_contract` — L2923
- `_load_audit_blacklist_block` — L2936
- `_generate_adsd_dialogue_turns` — L2974
- `_broll_rhythm_reviewer` — L3401
- `_sweep_speaker_field` — L3508
- `_should_run_immersion_qa` — L3568
- `_adsd_immersion_qa_rewrite_turns` — L3591
- `_adsd_visual_contract` — L3655
- `_parse_risk_score` — L3707
- `_check_high_risk_hard_abort` — L3736
- `_maybe_neutralize_topic` — L3763
- `_apply_render_budget_scene_cap` — L3802
- `_apply_llm_mode_decision` — L3829
- `step1_script` — L3884
- `_write_ads_retention_qa` — L5130

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L5187 – L6419** (1233 lines)

**Sub-sections:**
- _B88: 内容审核(1002) → 分级软化 → 中性兜底句 → 静音 backstop，绝不崩管线_ — L5882-5910 (29 lines)
- _非内容审核(网络/transient): 有限退避重试，耗尽才抛_ — L5911-6419 (509 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L5262
- `_ADSD_POLICY_REWRITE_TERMS` — L5268
- `_TTS_SAFE_FALLBACK_LINE` — L5369
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L5437

**Functions:**
- `_openai_tts_fallback` — L5188
- `_edge_tts_fallback` — L5234
- `_sanitize_for_external_api` — L5293
- `_is_content_policy_error` — L5302
- `_rewrite_adsd_tts_text_for_policy` — L5316
- `_tts_safe_fallback_line` — L5378
- `_tts_silent_placeholder` — L5383
- `_record_adsd_tts_rewrite` — L5418
- `_build_silence_mp3` — L5443
- `_audio_duration_seconds` — L5456
- `_text_to_audio_master_voice_timed` — L5468
- `_text_to_audio_master_voice` — L5593
- `step2_master_voice` — L5706
- `_tts_turn_to_audio` — L5834
- `_asr_verify_dialogue_audio` — L5921
- `_asr_verify_dialogue_turns` — L5983
- `_normalize_cn_number_token` — L6025
- `_compact_zh_text` — L6047
- `_write_adsd_asr_text_qa` — L6054
- `_write_adsd_speaker_focus_qa` — L6093
- `_write_adsd_gender_voice_qa` — L6153
- `step2_dialogue_voice` — L6206

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L6420 – L6971** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L6427-6549 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L6550-6584 (35 lines)
- _第二层：字符数插值_ — L6585-6609 (25 lines)
- _第三层：silencedetect 物理校准_ — L6610-6971 (362 lines)

**Functions:**
- `_detect_silences` — L6428
- `_calibrate_boundaries` — L6463
- `_enforce_monotonic` — L6497
- `_manual_override_segments` — L6509
- `_calc_sentence_boundaries` — L6530
- `step345_timeline` — L6641
- `_analyze_bgm_energy_cuts` — L6700
- `_snap_bgm_only_boundaries` — L6763
- `step345_bgm_only_timeline` — L6823

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L6972 – L12611** (5640 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L8201-8251 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L8252-9110 (859 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L9111-9598 (488 lines)
- _Speaker IP Card (2026-05-21)_ — L9599-11243 (1645 lines)
- _MTV：原创歌曲 + 主唱人物库 + WeryDance MV_ — L11244-12211 (968 lines)
- _B68 (2026-05-30) WERYDANCE 段长合规 gate_ — L12212-12444 (233 lines)
- _审批流程_ — L12445-12501 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L12502-12611 (110 lines)

**Top-level constants:**
- `_CORE_TERMS_STOP_WORDS` — L7374
- `CHARACTER_META_GRID_COSTUMES` — L8207
- `CHARACTER_META_GRID_POSES` — L8208
- `CHARACTER_META_GRID_SCENES` — L8209
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L8212
- `_SFX_TYPE_ENUM` — L8580
- `_SFX_INTENSITY_ENUM` — L8585
- `_SFX_POSITION_ENUM` — L8586
- `_GRAIN_LEVEL_ENUM` — L8731
- `_CUSTOM_STYLE_BANNED_NAMES` — L9166
- `_DUANGE_XING_TEXT` — L11245

**Functions:**
- `_extract_img_url` — L6973
- `_extract_img_urls` — L6995
- `_extract_video_url` — L7028
- `_count_bands` — L7053
- `_detect_contact_sheet_like_image` — L7065
- `_file_sha256` — L7126
- `_load_upload_cache` — L7139
- `_save_upload_cache` — L7148
- `_cached_upload_url` — L7156
- `_store_upload_url` — L7173
- `_guess_upload_mime` — L7183
- `_upload_to_weryai` — L7206
- `_send_for_approval` — L7267
- `_wait_approval` — L7331
- `_render_still_segment` — L7343
- `_extract_core_terms` — L7380
- `_scene_text_visual_alignment` — L7399
- `_write_text_visual_alignment_qa` — L7420
- `_scene_motion_action_plan` — L7443
- `_ensure_motion_action_plan` — L7497
- `_motion_action_block` — L7506
- `_motion_plan_for_qa` — L7534
- `_write_motion_action_plan_qa` — L7544
- `_write_motion_bridge_refs_qa` — L7574
- `_motion_bridge_ref_prompt` — L7581
- `generate_motion_bridge_refs_gpt_image2` — L7614
- `generate_image` — L7729
- `generate_storyboard_images_gpt_image2` — L7776
- `_storyboard_grid_aspect` — L7962
- `_storyboard_grid_cols_rows` — L7969
- `_storyboard_grid_prompt` — L7991
- `_storyboard_grid_prompt_limit` — L8049
- `_is_prompt_limit_response` — L8053
- `_production_storyboard_prompt` — L8059
- `_write_production_storyboard_page_qa` — L8093
- `_character_sheet_prompt` — L8103
- `_is_audit_blocked` — L8229
- `_paraphrase_sensitive_dialogue` — L8242
- `_topic_cache_dir` — L8256
- `_topic_cache_path` — L8262
- `_load_topic_decomposition_cache` — L8275
- `_save_topic_decomposition_cache` — L8293
- `_briefs_dir` — L8330
- `_brief_path` — L8336
- `_empty_brief` — L8341
- `_deep_merge_brief_skeleton` — L8381
- `_load_brief` — L8395
- `_save_brief` — L8419
- `_brief_get` — L8438
- `_brief_field` — L8450
- `_brief_set` — L8461
- `_brief_claim` — L8477
- `_brief_agent_status` — L8520
- `_brief_from_topic_decomposition` — L8533
- `_rule_based_sfx_design` — L8589
- `_validate_sfx_entry` — L8640
- `_audio_director_design` — L8678
- `_hex_color_validate` — L8734
- `_rule_based_art_design` — L8746
- `_validate_art_design` — L8827
- `_art_director_design` — L8865
- `_coordinator_review` — L8887
- `_llm_topic_decomposition` — L8988
- `_validate_custom_visual_style` — L9173
- `_resolve_route_style` — L9195
- `_director_route_block` — L9220
- `_llm_infer_meta_grid_template` — L9287
- `_resolve_meta_grid_template` — L9344
- `_infer_meta_grid_costume` — L9387
- `_infer_meta_grid_pose` — L9436
- `_adsd_meta_grid_call_prompt` — L9483
- `_meta_grid_panel_index` — L9525
- `_migrate_speaker_ip` — L9605
- `_speaker_ips_dir` — L9630
- `_list_speaker_ips` — L9637
- `_match_speaker_ip` — L9651
- `_build_speaker_ip_context_for_script` — L9671
- `_ip_usage_stats` — L9727
- `_recommend_related_ips` — L9745
- `_save_speaker_ip` — L9770
- `_record_speaker_usage_history` — L9779
- `_format_speaker_usage_history_for_prompt` — L9826
- `_llm_infer_ip_skeleton` — L9844
- `_llm_pick_voice_asset_for_ip` — L9889
- `_auto_incubate_missing_ips` — L9938
- `_character_meta_grid_cache_dir` — L10022
- `_character_meta_grid_cache_path` — L10030
- `_character_meta_grid_cache_legacy_path` — L10038
- `_character_meta_grid_path` — L10045
- `generate_character_meta_grid_gpt_image2` — L10051
- `_generate_all_character_meta_grids` — L10223
- `_write_character_sheet_qa` — L10264
- `generate_character_sheet_gpt_image2` — L10274
- `generate_production_storyboard_page_gpt_image2` — L10374
- `_qa_clean_storyboard_panel` — L10437
- `_crop_storyboard_grid_panels` — L10618
- `generate_storyboard_grid_gpt_image2` — L10665
- `_gpt_image2_direct_annotated_aspect` — L10897
- `_gpt_image2_direct_annotated_prompt` — L10904
- `generate_gpt_image2_direct_annotated_storyboards` — L10934
- `_llm_bgm_description` — L11035
- `_bgm_contains_vocals` — L11074
- `generate_bgm` — L11108
- `_arg_value` — L11257
- `_infer_mtv_singer` — L11266
- `_ensure_mtv_singer_ip` — L11280
- `_mtv_source_lyrics` — L11335
- `_mtv_build_plan` — L11347
- `_generate_mtv_song` — L11432
- `_trim_mtv_song` — L11471
- `_mtv_generate_visual_segments` — L11484
- `_mtv_ass_time` — L11698
- `_mtv_ass_escape` — L11707
- `_mtv_wrap_lyric` — L11713
- `_mtv_vocal_span_from_asr` — L11738
- `_mtv_split_lyric_clauses` — L11782
- `_mtv_split_lyric_phrases` — L11794
- `_mtv_norm_zh` — L11807
- `_mtv_best_phrase_offset` — L11811
- `_mtv_asr_phrase_records` — L11831
- `_mtv_alignment_from_script` — L11874
- `_mtv_split_span` — L11927
- `_mtv_song_slice` — L11937
- `_mtv_normalize_segment_duration` — L11945
- `_mtv_static_fallback_segment` — L11981
- `_mtv_lip_sync_segment` — L12003
- `_write_mtv_subtitles` — L12075
- `_mtv_concat_and_render` — L12147
- `run_mtv_pipeline` — L12197
- `_b68_clamp_scene_durations_to_werydance_bounds` — L12220
- `step6_parallel` — L12280

---

### 第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）
Range: **L12612 – L18291** (5680 lines)

**Sub-sections:**
- _B92 (2026-06-05): 轨迹标记运镜 (Seedance 红线技法)_ — L13853-16380 (2528 lines)
- _PR-A (2026-05-27): merged_a 合并跑 helpers_ — L16381-18026 (1646 lines)
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L18027-18069 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L18070-18107 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回时间轴锚定音轨_ — L18108-18246 (139 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L18247-18291 (45 lines)

**Top-level constants:**
- `_PR3B1_SHOT_TYPE_ENUM` — L13173
- `_PR3B1_CAMERA_ANGLE_ENUM` — L13177
- `_PR3B1_LIGHTING_ENUM` — L13182
- `_PR3B1_CAMERA_MOTION_ENUM` — L13187
- `_SEEDANCE_CAMERA_GRAMMAR` — L13211
- `_DOLLY_ZOOM_EMOTIONS` — L13224
- `_GRAND_EMOTIONS` — L13229
- `_SEEDANCE_CAMERA_COMPACT` — L13234
- `_B92_HIDE_NEGATIVES` — L13856
- `_EMOTION_NARRATION_STYLE_MAP` — L14547

**Functions:**
- `_generate_motion_prompts` — L12615
- `_motion_tasks_file` — L12682
- `_motion_qa_file` — L12688
- `_append_motion_qa` — L12692
- `_finalize_motion_qa` — L12716
- `_lip_sync_tasks_file` — L12800
- `_normalize_generation_interface` — L12804
- `_generation_task_record` — L12814
- `_normalize_cached_task` — L12832
- `_load_generation_tasks` — L12859
- `_load_motion_tasks` — L12876
- `_save_motion_task` — L12882
- `_remove_motion_task` — L12902
- `_load_lip_sync_tasks` — L12909
- `_save_lip_sync_task` — L12916
- `_remove_lip_sync_task` — L12935
- `_video_visual_motion_qa` — L12942
- `_motion_output_qa` — L13014
- `_has_audio_stream` — L13059
- `_normalize_motion_video` — L13070
- `_motion_poll_and_download` — L13120
- `_validate_enum_field` — L13193
- `_seedance_camera_directive` — L13249
- `_build_motion_video_prompt` — L13269
- `_short_board_text` — L13325
- `_wrap_board_text` — L13332
- `_storyboard_font` — L13363
- `_draw_storyboard_arrow` — L13378
- `_build_annotated_storyboard_reference` — L13392
- `_plain_caption_text` — L13493
- `_werydance_caption_request` — L13501
- `_werydance_caption_instruction` — L13528
- `_werydance_negative_prompt` — L13540
- `_motion_reference_prompt` — L13562
- `_motion_audio_dub_prompt` — L13585
- `_motion_audio_dub_poll_and_download` — L13619
- `_try_motion_audio_dub_video` — L13685
- `_b92_enabled` — L13862
- `_b92_propose_path` — L13866
- `_b92_draw_path` — L13907
- `_b92_trim_lead_frames` — L13936
- `_b92_trajectory_prompt` — L13965
- `_b92_apply_trajectory` — L13980
- `_b92_preplan_paths` — L14001
- `_try_motion_reference_video` — L14025
- `_resume_motion_task` — L14162
- `_motion_one_scene` — L14194
- `_grid_multiref_tasks_file` — L14316
- `_previs_page_tasks_file` — L14320
- `_load_grid_multiref_tasks` — L14324
- `_load_previs_page_tasks` — L14331
- `_save_grid_multiref_task` — L14338
- `_save_previs_page_task` — L14355
- `_remove_grid_multiref_task` — L14372
- `_remove_previs_page_task` — L14379
- `_poll_video_task_download` — L14386
- `_grid_multiref_group_size` — L14435
- `_grid_multiref_adaptive_group_size` — L14445
- `_grid_multiref_duration` — L14469
- `_grid_multiref_tts_buffer_factor` — L14507
- `_grid_multiref_tts_duration_buffered` — L14521
- `_grid_multiref_segment_max_stretch` — L14537
- `_voice_clone_emotion_style` — L14571
- `_grid_multiref_prompt` — L14594
- `_write_grid_multiref_motion_qa` — L14674
- `_write_previs_page_motion_qa` — L14684
- `_write_storyboard_trailer_qa` — L14694
- `_write_character_trailer_qa` — L14704
- `_write_grid_multiref_segment_qa` — L14714
- `_motion_compare_record` — L14724
- `_write_storyboard_motion_compare_qa` — L14746
- `_scene_segment_duration` — L14782
- `_apply_grid_multiref_segments` — L14801
- `_previs_page_duration` — L15006
- `_previs_page_group_prompt` — L15017
- `_previs_page_groups` — L15043
- `_storyboard_trailer_duration` — L15058
- `_storyboard_trailer_prompt` — L15068
- `_character_trailer_max_shots` — L15096
- `_character_trailer_shot_duration` — L15104
- `_character_trailer_prompt` — L15120
- `_concat_character_trailer_segments` — L15135
- `_generate_character_trailer_motion` — L15174
- `_multi_trailer_prompt_for_group` — L15282
- `_generate_multi_trailer_segments` — L15305
- `_generate_storyboard_trailer_motion` — L15416
- `_generate_previs_page_motion_segments` — L15491
- `_generate_grid_multiref_motion_segments` — L15609
- `_grid_multiref_concat_groups` — L15937
- `_grid_multiref_concat_groups_partial` — L15954
- `_grid_multiref_concat_paths` — L15972
- `_lip_sync_slot_duration` — L16014
- `_adsd_lip_sync_prompt` — L16021
- `_adsd_broll_motion_prompt` — L16067
- `_adsd_action_b_motion_prompt` — L16115
- `_adsd_silent_b_motion_prompt` — L16161
- `_adsd_narrated_b_audio_dub_prompt` — L16202
- `_adsd_almighty_audio_dub_prompt` — L16246
- `_postprocess_lip_sync_segment` — L16287
- `_detect_audio_leading_silence` — L16359
- `_concat_audio_files_for_group` — L16384
- `_split_lip_sync_raw_by_durations` — L16407
- `_postprocess_audio_dub_segment` — L16442
- `_lips_change_repair_segment` — L16570
- `_load_lips_change_requested_turns` — L16655
- `_parse_turn_set` — L16672
- `_load_motion_voice_repair_turns` — L16694
- `_voice_assets_file` — L16706
- `_load_voice_assets` — L16713
- `_build_combined_voice_reference` — L16732
- `_select_voice_asset_reference` — L16774
- `_lip_sync_poll_download_and_process` — L16850
- `_resume_lip_sync_task` — L16918
- `_lip_sync_one_group` — L16947
- `_lip_sync_one_scene` — L17155
- `step66_adsd_lip_sync` — L17496
- `step65_motion` — L17842
- `step65_grid_multiref_motion_qa` — L17999
- `_sanitize_scene_for_state` — L18028
- `_save_pipeline_state` — L18047
- `_retime_after_audio_dub` — L18071
- `_build_voice_clone_hybrid_audio` — L18109
- `_build_dynamic_bgm` — L18248

---

### 第七步：拼接视频轨
Range: **L18292 – L18627** (336 lines)

**Functions:**
- `_rescue_motion_image_to_video` — L18293
- `_rescue_motion_text_to_video` — L18328
- `step7_concat` — L18359

---

### 第八步：生成 ASS 字幕
Range: **L18628 – L19586** (959 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L18907-19586 (680 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L18629
- `_word_timings_for_subtitle_align` — L18655
- `_align_segments_via_asr` — L18696
- `_b61_1_asr_turn_boundaries` — L18739
- `step8_subtitles` — L18801
- `_read_output_json` — L19307
- `_qa_file_pass` — L19318
- `_ass_has_dialogue` — L19325
- `_write_adsd_delivery_qa` — L19335
- `_write_bgm_only_qa` — L19475

---

### 第九步：最终合成
Range: **L19587 – L19877** (291 lines)

**Functions:**
- `step9_render` — L19588

---

### 第十步：推送 Telegram
Range: **L19878 – L21760** (1883 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L20984-21093 (110 lines)
- _B70 (2026-05-30) TG oversize policy helpers_ — L21094-21565 (472 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L21566-21570 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L21571-21635 (65 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L21636-21682 (47 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L21683-21760 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L20247
- `PANTONE_FALLBACK` — L20274
- `FESTIVAL_DATE_TAG` — L20388

**Functions:**
- `_generate_caption` — L19879
- `_overlay_title_on_cover` — L20117
- `_prepare_tg_photo` — L20227
- `_get_pantone_for_date` — L20277
- `_llm_bottom_note` — L20302
- `_get_bottom_note` — L20332
- `_get_date_tag` — L20410
- `_shrink_to_b64` — L20432
- `_llm_check_scenes_anomalies` — L20448
- `_llm_check_cover_unique` — L20501
- `_llm_check_cover_quality` — L20531
- `_try_almanac_cover` — L20573
- `_generate_cover_image` — L20744
- `_async_kickoff_cover_caption` — L20991
- `_await_async_cover_caption` — L21067
- `_b70_env_float` — L21097
- `_b70_split_and_deliver` — L21112
- `_b70_send_document_first` — L21225
- `step10_deliver` — L21262

---

### 主流程
Range: **L21761 – L22015** (255 lines)

**Functions:**
- `_print_execution_plan` — L21762
- `_write_run_timings` — L21821
- `main` — L21850

---
