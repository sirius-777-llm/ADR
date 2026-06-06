# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (21437 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-122 (122 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L123-2506 (2384 lines · 73 fn · 5 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L2507-5158 (2652 lines · 33 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L5159-6391 (1233 lines · 22 fn · 2 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L6392-6943 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L6944-12245 (5302 lines · 125 fn · 8 sub)
- [`第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）`](#第-6-5-步-动态化-hads-vads-默认-on---no-motion-关) — L12246-17713 (5468 lines · 117 fn · 6 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L17714-18049 (336 lines · 3 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L18050-19008 (959 lines · 10 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L19009-19299 (291 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L19300-21182 (1883 lines · 19 fn · 6 sub)
- [`主流程`](#主流程) — L21183-21437 (255 lines · 3 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L122** (122 lines)

**Sub-sections:**
- _老黄历数据模块_ — L30-122 (93 lines)

**Functions:**
- `get_almanac_data` — L58

---

### 配置
Range: **L123 – L2506** (2384 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L339-468 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L469-1212 (744 lines)
- _工具函数_ — L1213-1588 (376 lines)
- _B87 纹理档系统：LLM 提名 + 代码护栏 + 确定性渲染_ — L1589-1851 (263 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1852-2506 (655 lines)

**Top-level constants:**
- `HEADERS` — L136
- `VIDEO_FORMAT_RAW` — L144
- `MTV_MODE` — L145
- `VIDEO_FORMAT` — L150
- `ADS_DIALOGUE_MODE_EARLY_CHECK` — L161
- `WITH_MOTION` — L168
- `BGM_ONLY_REQUESTED` — L173
- `ADS_DIALOGUE_MODE` — L180
- `GPT_IMAGE2_STORYBOARD` — L192
- `STORYBOARD_REFERENCE_MOTION` — L196
- `STORYBOARD_ANNOTATED_MOTION` — L200
- `GPT_IMAGE2_DIRECT_ANNOTATED_STORYBOARD` — L204
- `GPT_IMAGE2_STORYBOARD_GRID` — L209
- `ADSD_STORYBOARD_GRID` — L217
- `ADS_CHARACTER_SHEET_REQUESTED` — L223
- `STORYBOARD_GRID_MULTIREF_MOTION` — L227
- `STORYBOARD_GRID_MULTIREF_SEGMENTS` — L231
- `STORYBOARD_GRID_MULTIREF_MAIN` — L237
- `GRID_MULTIREF_PRIMARY` — L247
- `PREVIS_PAGE_MOTION` — L259
- `STORYBOARD_TRAILER_MODE` — L263
- `MOTION_ACTION_STORYBOARD` — L268
- `MOTION_BRIDGE_REFS` — L272
- `CHARACTER_TRAILER_MODE` — L276
- `STORYBOARD_TRAILER_MAIN` — L284
- `ADSD_LIP_SYNC_EXPERIMENT` — L297
- `ADSD_RICH_MOTION_PROMPT` — L305
- `ADSD_LLM_VOICE_ASSIGN` — L313
- `ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT` — L317
- `ADSD_CONSECUTIVE_SPEAKER_BATCHING` — L331
- `ADSD_GENDER_FALLBACK_VOICE_ASSET` — L342
- `SILENT_B_SPEAKERS` — L474
- `_PODCAST_TO_VOICE_ASSET_MAP` — L852
- `_VOICE_ASSET_FORBIDDEN_FLAGS` — L870
- `_GENERIC_NARRATOR_NAMES` — L914
- `VOICE_ASSET_AUDIO_DUB_EXPERIMENT` — L951
- `VOICE_ASSET_AUDIO_DUB_PARTIAL_OK` — L959
- `MOTION_VISUAL_QA` — L963
- `MOTION_VOICE_REPAIR` — L971
- `MOTION_VOICE_STRICT_LOCK` — L976
- `WERYDANCE_CAPTIONS` — L981
- `ADSD_ONSITE_POV_MODE` — L993
- `ADSD_LIPS_CHANGE_REPAIR` — L998
- `ADSD_LIPS_CHANGE_ALL` — L1003
- `ADS_REPORTER_MODE` — L1014
- `ADS_STORYBOARD_FLOW_DEFAULT` — L1031
- `ADS_RETENTION_MODE` — L1045
- `ADSD_MODE_NAME` — L1051
- `EMOTION_STYLE` — L1192
- `EMOTION_STYLE_BRIGHT` — L1204
- `_REDACT_PATTERNS_DEFAULT` — L1218
- `_TG_DASHBOARD_STAGES` — L1270
- `_TG_NOISY_PATTERNS` — L1285
- `_TG_IMMEDIATE_PATTERNS` — L1303
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1582
- `_TEXTURE_MODE_ENUM` — L1590
- `_TEXTURE_SUFFIX_MAP` — L1595
- `_TEXTURE_BODY_DIRECTIVE` — L1622
- `_TEXTURE_SCENE_PHRASE` — L1629
- `_TEXTURE_GRID_PHRASE` — L1636
- `_TEXTURE_MOTION_PHRASE` — L1644
- `_LLM_TIER` — L2032
- `_TOPIC_MODIFIERS` — L2259
- `_TONE_PANTONE_OVERRIDE` — L2276

**Functions:**
- `_is_action_scene` — L351
- `_needs_storyboard_flow_character_sheet` — L362
- `_wuxia_action_panel_prompt` — L391
- `_action_motion_fragment` — L413
- `_infer_emotion_from_text` — L428
- `_emotion_expression_phrase` — L443
- `_infer_needs_lip_sync` — L450
- `_infer_turn_type` — L477
- `_is_action_shout` — L502
- `_resolve_turn_type` — L528
- `_is_silent_b` — L543
- `_is_narrated_b` — L547
- `_is_a_roll` — L551
- `_is_action_b` — L555
- `_voice_asset_id_for_speaker` — L559
- `_llm_assign_voice_assets` — L587
- `_apply_llm_voice_assignment` — L716
- `_voice_asset_is_speech_safe` — L877
- `_podcast_id_to_voice_asset` — L883
- `_resolve_voice_asset_for_ads_speaker` — L917
- `_redact_for_stdout` — L1233
- `log` — L1258
- `_tg_send_raw` — L1326
- `_tg_matches` — L1342
- `_tg_summarize` — L1346
- `_tg_dashboard_stage_for` — L1353
- `_tg_progress_bar` — L1361
- `_tg_dashboard_text` — L1367
- `_tg_dashboard_update` — L1385
- `_tg_maybe_digest` — L1422
- `tg` — L1437
- `_wait_image_submit_slot` — L1486
- `_wait_motion_submit_slot` — L1499
- `_is_rate_limited_error` — L1512
- `_is_rate_limited_response` — L1522
- `_is_transient_workflow_error` — L1534
- `_is_llm_rate_limited_error` — L1558
- `_era_is_pre_photographic` — L1656
- `_texture_mode_fallback` — L1684
- `_texture_guardrail` — L1705
- `_set_active_texture_profile` — L1744
- `_active_texture_suffix` — L1757
- `_active_texture_body_directive` — L1761
- `_active_texture_scene_phrase` — L1765
- `_active_texture_grid_phrase` — L1769
- `_active_texture_motion_phrase` — L1773
- `_inject_image2_quality_suffix` — L1777
- `submit_text_to_image` — L1797
- `req_post` — L1833
- `req_get` — L1847
- `_tg_probe_send` — L1855
- `_tg_probe_delete` — L1875
- `_tg_upload_with_probe_gap` — L1888
- `poll` — L1928
- `poll_podcast` — L1953
- `poll_task_status` — L1975
- `poll_storyboard_task` — L1997
- `tier_chat` — L2040
- `chat` — L2046
- `pick_image_model` — L2105
- `detect_topic_meta` — L2130
- `_topic_culture_guard` — L2180
- `_write_cultural_visual_qa` — L2206
- `is_1919_global_topic` — L2253
- `_strip_topic_modifiers` — L2264
- `apply_1919_global_guardrails` — L2282
- `build_1919_global_cover_prompt` — L2311
- `_shot_blueprint_enums` — L2343
- `build_shot_blueprint` — L2419
- `ffprobe_duration` — L2445
- `ffprobe_video_size` — L2456
- `_video_decode_probe` — L2477
- `ffmpeg` — L2495

---

### 第一步：双导演生成剧本
Range: **L2507 – L5158** (2652 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L4139-5158 (1020 lines)

**Top-level constants:**
- `_ENSEMBLE_CAP_BY_ROUTE` — L2659

**Functions:**
- `_extract_json_array` — L2508
- `_extract_json_object` — L2518
- `_voice_for_speaker` — L2528
- `_adsd_gender_from_voice` — L2564
- `_adsd_infer_gender_from_speaker` — L2572
- `_adsd_gender_lock_phrase` — L2581
- `_adsd_visual_subject_has_gender_conflict` — L2596
- `_adsd_default_roles` — L2608
- `_adsd_allows_media_role` — L2613
- `_adsd_role_candidates` — L2621
- `_adsd_dialogue_shape` — L2648
- `_ensemble_speaker_cap` — L2670
- `_ip_voice_asset_for_speaker` — L2683
- `_finalize_adsd_turns` — L2707
- `_parse_adsd_override_turns` — L2753
- `_parse_timecode_seconds` — L2846
- `_clean_override_line_text` — L2855
- `_parse_override_script_text` — L2861
- `_adsd_pov_contract` — L2895
- `_load_audit_blacklist_block` — L2908
- `_generate_adsd_dialogue_turns` — L2946
- `_broll_rhythm_reviewer` — L3373
- `_sweep_speaker_field` — L3480
- `_should_run_immersion_qa` — L3540
- `_adsd_immersion_qa_rewrite_turns` — L3563
- `_adsd_visual_contract` — L3627
- `_parse_risk_score` — L3679
- `_check_high_risk_hard_abort` — L3708
- `_maybe_neutralize_topic` — L3735
- `_apply_render_budget_scene_cap` — L3774
- `_apply_llm_mode_decision` — L3801
- `step1_script` — L3856
- `_write_ads_retention_qa` — L5102

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L5159 – L6391** (1233 lines)

**Sub-sections:**
- _B88: 内容审核(1002) → 分级软化 → 中性兜底句 → 静音 backstop，绝不崩管线_ — L5854-5882 (29 lines)
- _非内容审核(网络/transient): 有限退避重试，耗尽才抛_ — L5883-6391 (509 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L5234
- `_ADSD_POLICY_REWRITE_TERMS` — L5240
- `_TTS_SAFE_FALLBACK_LINE` — L5341
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L5409

**Functions:**
- `_openai_tts_fallback` — L5160
- `_edge_tts_fallback` — L5206
- `_sanitize_for_external_api` — L5265
- `_is_content_policy_error` — L5274
- `_rewrite_adsd_tts_text_for_policy` — L5288
- `_tts_safe_fallback_line` — L5350
- `_tts_silent_placeholder` — L5355
- `_record_adsd_tts_rewrite` — L5390
- `_build_silence_mp3` — L5415
- `_audio_duration_seconds` — L5428
- `_text_to_audio_master_voice_timed` — L5440
- `_text_to_audio_master_voice` — L5565
- `step2_master_voice` — L5678
- `_tts_turn_to_audio` — L5806
- `_asr_verify_dialogue_audio` — L5893
- `_asr_verify_dialogue_turns` — L5955
- `_normalize_cn_number_token` — L5997
- `_compact_zh_text` — L6019
- `_write_adsd_asr_text_qa` — L6026
- `_write_adsd_speaker_focus_qa` — L6065
- `_write_adsd_gender_voice_qa` — L6125
- `step2_dialogue_voice` — L6178

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L6392 – L6943** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L6399-6521 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L6522-6556 (35 lines)
- _第二层：字符数插值_ — L6557-6581 (25 lines)
- _第三层：silencedetect 物理校准_ — L6582-6943 (362 lines)

**Functions:**
- `_detect_silences` — L6400
- `_calibrate_boundaries` — L6435
- `_enforce_monotonic` — L6469
- `_manual_override_segments` — L6481
- `_calc_sentence_boundaries` — L6502
- `step345_timeline` — L6613
- `_analyze_bgm_energy_cuts` — L6672
- `_snap_bgm_only_boundaries` — L6735
- `step345_bgm_only_timeline` — L6795

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L6944 – L12245** (5302 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L8173-8223 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L8224-9082 (859 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L9083-9570 (488 lines)
- _Speaker IP Card (2026-05-21)_ — L9571-11215 (1645 lines)
- _MTV：原创歌曲 + 主唱人物库 + WeryDance MV_ — L11216-11845 (630 lines)
- _B68 (2026-05-30) WERYDANCE 段长合规 gate_ — L11846-12078 (233 lines)
- _审批流程_ — L12079-12135 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L12136-12245 (110 lines)

**Top-level constants:**
- `_CORE_TERMS_STOP_WORDS` — L7346
- `CHARACTER_META_GRID_COSTUMES` — L8179
- `CHARACTER_META_GRID_POSES` — L8180
- `CHARACTER_META_GRID_SCENES` — L8181
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L8184
- `_SFX_TYPE_ENUM` — L8552
- `_SFX_INTENSITY_ENUM` — L8557
- `_SFX_POSITION_ENUM` — L8558
- `_GRAIN_LEVEL_ENUM` — L8703
- `_CUSTOM_STYLE_BANNED_NAMES` — L9138
- `_DUANGE_XING_TEXT` — L11217

**Functions:**
- `_extract_img_url` — L6945
- `_extract_img_urls` — L6967
- `_extract_video_url` — L7000
- `_count_bands` — L7025
- `_detect_contact_sheet_like_image` — L7037
- `_file_sha256` — L7098
- `_load_upload_cache` — L7111
- `_save_upload_cache` — L7120
- `_cached_upload_url` — L7128
- `_store_upload_url` — L7145
- `_guess_upload_mime` — L7155
- `_upload_to_weryai` — L7178
- `_send_for_approval` — L7239
- `_wait_approval` — L7303
- `_render_still_segment` — L7315
- `_extract_core_terms` — L7352
- `_scene_text_visual_alignment` — L7371
- `_write_text_visual_alignment_qa` — L7392
- `_scene_motion_action_plan` — L7415
- `_ensure_motion_action_plan` — L7469
- `_motion_action_block` — L7478
- `_motion_plan_for_qa` — L7506
- `_write_motion_action_plan_qa` — L7516
- `_write_motion_bridge_refs_qa` — L7546
- `_motion_bridge_ref_prompt` — L7553
- `generate_motion_bridge_refs_gpt_image2` — L7586
- `generate_image` — L7701
- `generate_storyboard_images_gpt_image2` — L7748
- `_storyboard_grid_aspect` — L7934
- `_storyboard_grid_cols_rows` — L7941
- `_storyboard_grid_prompt` — L7963
- `_storyboard_grid_prompt_limit` — L8021
- `_is_prompt_limit_response` — L8025
- `_production_storyboard_prompt` — L8031
- `_write_production_storyboard_page_qa` — L8065
- `_character_sheet_prompt` — L8075
- `_is_audit_blocked` — L8201
- `_paraphrase_sensitive_dialogue` — L8214
- `_topic_cache_dir` — L8228
- `_topic_cache_path` — L8234
- `_load_topic_decomposition_cache` — L8247
- `_save_topic_decomposition_cache` — L8265
- `_briefs_dir` — L8302
- `_brief_path` — L8308
- `_empty_brief` — L8313
- `_deep_merge_brief_skeleton` — L8353
- `_load_brief` — L8367
- `_save_brief` — L8391
- `_brief_get` — L8410
- `_brief_field` — L8422
- `_brief_set` — L8433
- `_brief_claim` — L8449
- `_brief_agent_status` — L8492
- `_brief_from_topic_decomposition` — L8505
- `_rule_based_sfx_design` — L8561
- `_validate_sfx_entry` — L8612
- `_audio_director_design` — L8650
- `_hex_color_validate` — L8706
- `_rule_based_art_design` — L8718
- `_validate_art_design` — L8799
- `_art_director_design` — L8837
- `_coordinator_review` — L8859
- `_llm_topic_decomposition` — L8960
- `_validate_custom_visual_style` — L9145
- `_resolve_route_style` — L9167
- `_director_route_block` — L9192
- `_llm_infer_meta_grid_template` — L9259
- `_resolve_meta_grid_template` — L9316
- `_infer_meta_grid_costume` — L9359
- `_infer_meta_grid_pose` — L9408
- `_adsd_meta_grid_call_prompt` — L9455
- `_meta_grid_panel_index` — L9497
- `_migrate_speaker_ip` — L9577
- `_speaker_ips_dir` — L9602
- `_list_speaker_ips` — L9609
- `_match_speaker_ip` — L9623
- `_build_speaker_ip_context_for_script` — L9643
- `_ip_usage_stats` — L9699
- `_recommend_related_ips` — L9717
- `_save_speaker_ip` — L9742
- `_record_speaker_usage_history` — L9751
- `_format_speaker_usage_history_for_prompt` — L9798
- `_llm_infer_ip_skeleton` — L9816
- `_llm_pick_voice_asset_for_ip` — L9861
- `_auto_incubate_missing_ips` — L9910
- `_character_meta_grid_cache_dir` — L9994
- `_character_meta_grid_cache_path` — L10002
- `_character_meta_grid_cache_legacy_path` — L10010
- `_character_meta_grid_path` — L10017
- `generate_character_meta_grid_gpt_image2` — L10023
- `_generate_all_character_meta_grids` — L10195
- `_write_character_sheet_qa` — L10236
- `generate_character_sheet_gpt_image2` — L10246
- `generate_production_storyboard_page_gpt_image2` — L10346
- `_qa_clean_storyboard_panel` — L10409
- `_crop_storyboard_grid_panels` — L10590
- `generate_storyboard_grid_gpt_image2` — L10637
- `_gpt_image2_direct_annotated_aspect` — L10869
- `_gpt_image2_direct_annotated_prompt` — L10876
- `generate_gpt_image2_direct_annotated_storyboards` — L10906
- `_llm_bgm_description` — L11007
- `_bgm_contains_vocals` — L11046
- `generate_bgm` — L11080
- `_arg_value` — L11229
- `_infer_mtv_singer` — L11238
- `_ensure_mtv_singer_ip` — L11252
- `_mtv_source_lyrics` — L11307
- `_mtv_build_plan` — L11319
- `_generate_mtv_song` — L11404
- `_trim_mtv_song` — L11443
- `_mtv_generate_visual_segments` — L11456
- `_mtv_ass_time` — L11516
- `_mtv_ass_escape` — L11525
- `_mtv_wrap_lyric` — L11531
- `_mtv_vocal_span_from_asr` — L11556
- `_mtv_split_lyric_clauses` — L11600
- `_mtv_split_lyric_phrases` — L11612
- `_mtv_norm_zh` — L11625
- `_mtv_best_phrase_offset` — L11629
- `_mtv_asr_phrase_records` — L11649
- `_write_mtv_subtitles` — L11692
- `_mtv_concat_and_render` — L11781
- `run_mtv_pipeline` — L11831
- `_b68_clamp_scene_durations_to_werydance_bounds` — L11854
- `step6_parallel` — L11914

---

### 第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）
Range: **L12246 – L17713** (5468 lines)

**Sub-sections:**
- _B92 (2026-06-05): 轨迹标记运镜 (Seedance 红线技法)_ — L13390-15849 (2460 lines)
- _PR-A (2026-05-27): merged_a 合并跑 helpers_ — L15850-17448 (1599 lines)
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L17449-17491 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L17492-17529 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回时间轴锚定音轨_ — L17530-17668 (139 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L17669-17713 (45 lines)

**Top-level constants:**
- `_PR3B1_SHOT_TYPE_ENUM` — L12716
- `_PR3B1_CAMERA_ANGLE_ENUM` — L12720
- `_PR3B1_LIGHTING_ENUM` — L12725
- `_PR3B1_CAMERA_MOTION_ENUM` — L12730
- `_SEEDANCE_CAMERA_GRAMMAR` — L12754
- `_DOLLY_ZOOM_EMOTIONS` — L12767
- `_GRAND_EMOTIONS` — L12772
- `_SEEDANCE_CAMERA_COMPACT` — L12777
- `_B92_HIDE_NEGATIVES` — L13393
- `_EMOTION_NARRATION_STYLE_MAP` — L14040

**Functions:**
- `_generate_motion_prompts` — L12249
- `_motion_tasks_file` — L12316
- `_motion_qa_file` — L12320
- `_append_motion_qa` — L12324
- `_finalize_motion_qa` — L12348
- `_lip_sync_tasks_file` — L12432
- `_load_motion_tasks` — L12436
- `_save_motion_task` — L12446
- `_remove_motion_task` — L12454
- `_load_lip_sync_tasks` — L12461
- `_save_lip_sync_task` — L12471
- `_remove_lip_sync_task` — L12478
- `_video_visual_motion_qa` — L12485
- `_motion_output_qa` — L12557
- `_has_audio_stream` — L12602
- `_normalize_motion_video` — L12613
- `_motion_poll_and_download` — L12663
- `_validate_enum_field` — L12736
- `_seedance_camera_directive` — L12792
- `_build_motion_video_prompt` — L12812
- `_short_board_text` — L12868
- `_wrap_board_text` — L12875
- `_storyboard_font` — L12906
- `_draw_storyboard_arrow` — L12921
- `_build_annotated_storyboard_reference` — L12935
- `_plain_caption_text` — L13036
- `_werydance_caption_request` — L13044
- `_werydance_caption_instruction` — L13071
- `_werydance_negative_prompt` — L13083
- `_motion_reference_prompt` — L13105
- `_motion_audio_dub_prompt` — L13128
- `_motion_audio_dub_poll_and_download` — L13162
- `_try_motion_audio_dub_video` — L13227
- `_b92_enabled` — L13399
- `_b92_propose_path` — L13403
- `_b92_draw_path` — L13444
- `_b92_trim_lead_frames` — L13473
- `_b92_trajectory_prompt` — L13502
- `_b92_apply_trajectory` — L13517
- `_b92_preplan_paths` — L13538
- `_try_motion_reference_video` — L13562
- `_motion_one_scene` — L13693
- `_grid_multiref_tasks_file` — L13823
- `_previs_page_tasks_file` — L13827
- `_load_grid_multiref_tasks` — L13831
- `_load_previs_page_tasks` — L13841
- `_save_grid_multiref_task` — L13851
- `_save_previs_page_task` — L13858
- `_remove_grid_multiref_task` — L13865
- `_remove_previs_page_task` — L13872
- `_poll_video_task_download` — L13879
- `_grid_multiref_group_size` — L13928
- `_grid_multiref_adaptive_group_size` — L13938
- `_grid_multiref_duration` — L13962
- `_grid_multiref_tts_buffer_factor` — L14000
- `_grid_multiref_tts_duration_buffered` — L14014
- `_grid_multiref_segment_max_stretch` — L14030
- `_voice_clone_emotion_style` — L14064
- `_grid_multiref_prompt` — L14087
- `_write_grid_multiref_motion_qa` — L14167
- `_write_previs_page_motion_qa` — L14177
- `_write_storyboard_trailer_qa` — L14187
- `_write_character_trailer_qa` — L14197
- `_write_grid_multiref_segment_qa` — L14207
- `_motion_compare_record` — L14217
- `_write_storyboard_motion_compare_qa` — L14239
- `_scene_segment_duration` — L14275
- `_apply_grid_multiref_segments` — L14294
- `_previs_page_duration` — L14499
- `_previs_page_group_prompt` — L14510
- `_previs_page_groups` — L14536
- `_storyboard_trailer_duration` — L14551
- `_storyboard_trailer_prompt` — L14561
- `_character_trailer_max_shots` — L14589
- `_character_trailer_shot_duration` — L14597
- `_character_trailer_prompt` — L14613
- `_concat_character_trailer_segments` — L14628
- `_generate_character_trailer_motion` — L14667
- `_multi_trailer_prompt_for_group` — L14775
- `_generate_multi_trailer_segments` — L14798
- `_generate_storyboard_trailer_motion` — L14909
- `_generate_previs_page_motion_segments` — L14984
- `_generate_grid_multiref_motion_segments` — L15096
- `_grid_multiref_concat_groups` — L15406
- `_grid_multiref_concat_groups_partial` — L15423
- `_grid_multiref_concat_paths` — L15441
- `_lip_sync_slot_duration` — L15483
- `_adsd_lip_sync_prompt` — L15490
- `_adsd_broll_motion_prompt` — L15536
- `_adsd_action_b_motion_prompt` — L15584
- `_adsd_silent_b_motion_prompt` — L15630
- `_adsd_narrated_b_audio_dub_prompt` — L15671
- `_adsd_almighty_audio_dub_prompt` — L15715
- `_postprocess_lip_sync_segment` — L15756
- `_detect_audio_leading_silence` — L15828
- `_concat_audio_files_for_group` — L15853
- `_split_lip_sync_raw_by_durations` — L15876
- `_postprocess_audio_dub_segment` — L15911
- `_lips_change_repair_segment` — L16039
- `_load_lips_change_requested_turns` — L16124
- `_parse_turn_set` — L16141
- `_load_motion_voice_repair_turns` — L16163
- `_voice_assets_file` — L16175
- `_load_voice_assets` — L16182
- `_build_combined_voice_reference` — L16201
- `_select_voice_asset_reference` — L16243
- `_lip_sync_poll_download_and_process` — L16319
- `_lip_sync_one_group` — L16387
- `_lip_sync_one_scene` — L16595
- `step66_adsd_lip_sync` — L16922
- `step65_motion` — L17267
- `step65_grid_multiref_motion_qa` — L17421
- `_sanitize_scene_for_state` — L17450
- `_save_pipeline_state` — L17469
- `_retime_after_audio_dub` — L17493
- `_build_voice_clone_hybrid_audio` — L17531
- `_build_dynamic_bgm` — L17670

---

### 第七步：拼接视频轨
Range: **L17714 – L18049** (336 lines)

**Functions:**
- `_rescue_motion_image_to_video` — L17715
- `_rescue_motion_text_to_video` — L17750
- `step7_concat` — L17781

---

### 第八步：生成 ASS 字幕
Range: **L18050 – L19008** (959 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L18329-19008 (680 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L18051
- `_word_timings_for_subtitle_align` — L18077
- `_align_segments_via_asr` — L18118
- `_b61_1_asr_turn_boundaries` — L18161
- `step8_subtitles` — L18223
- `_read_output_json` — L18729
- `_qa_file_pass` — L18740
- `_ass_has_dialogue` — L18747
- `_write_adsd_delivery_qa` — L18757
- `_write_bgm_only_qa` — L18897

---

### 第九步：最终合成
Range: **L19009 – L19299** (291 lines)

**Functions:**
- `step9_render` — L19010

---

### 第十步：推送 Telegram
Range: **L19300 – L21182** (1883 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L20406-20515 (110 lines)
- _B70 (2026-05-30) TG oversize policy helpers_ — L20516-20987 (472 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L20988-20992 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L20993-21057 (65 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L21058-21104 (47 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L21105-21182 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L19669
- `PANTONE_FALLBACK` — L19696
- `FESTIVAL_DATE_TAG` — L19810

**Functions:**
- `_generate_caption` — L19301
- `_overlay_title_on_cover` — L19539
- `_prepare_tg_photo` — L19649
- `_get_pantone_for_date` — L19699
- `_llm_bottom_note` — L19724
- `_get_bottom_note` — L19754
- `_get_date_tag` — L19832
- `_shrink_to_b64` — L19854
- `_llm_check_scenes_anomalies` — L19870
- `_llm_check_cover_unique` — L19923
- `_llm_check_cover_quality` — L19953
- `_try_almanac_cover` — L19995
- `_generate_cover_image` — L20166
- `_async_kickoff_cover_caption` — L20413
- `_await_async_cover_caption` — L20489
- `_b70_env_float` — L20519
- `_b70_split_and_deliver` — L20534
- `_b70_send_document_first` — L20647
- `step10_deliver` — L20684

---

### 主流程
Range: **L21183 – L21437** (255 lines)

**Functions:**
- `_print_execution_plan` — L21184
- `_write_run_timings` — L21243
- `main` — L21272

---
