# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (19537 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-2252 (2131 lines · 63 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L2253-4739 (2487 lines · 31 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L4740-5871 (1132 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L5872-6423 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L6424-10921 (4498 lines · 101 fn · 6 sub)
- [`第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）`](#第-6-5-步-动态化-hads-vads-默认-on---no-motion-关) — L10922-16018 (5097 lines · 108 fn · 5 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L16019-16278 (260 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L16279-17212 (934 lines · 10 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L17213-17497 (285 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L17498-19352 (1855 lines · 19 fn · 6 sub)
- [`主流程`](#主流程) — L19353-19537 (185 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L2252** (2131 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L324-453 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L454-1195 (742 lines)
- _工具函数_ — L1196-1616 (421 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1617-2252 (636 lines)

**Top-level constants:**
- `HEADERS` — L135
- `VIDEO_FORMAT` — L143
- `ADS_DIALOGUE_MODE_EARLY_CHECK` — L150
- `WITH_MOTION` — L157
- `BGM_ONLY_REQUESTED` — L161
- `ADS_DIALOGUE_MODE` — L168
- `GPT_IMAGE2_STORYBOARD` — L177
- `STORYBOARD_REFERENCE_MOTION` — L181
- `STORYBOARD_ANNOTATED_MOTION` — L185
- `GPT_IMAGE2_DIRECT_ANNOTATED_STORYBOARD` — L189
- `GPT_IMAGE2_STORYBOARD_GRID` — L194
- `ADSD_STORYBOARD_GRID` — L202
- `ADS_CHARACTER_SHEET_REQUESTED` — L208
- `STORYBOARD_GRID_MULTIREF_MOTION` — L212
- `STORYBOARD_GRID_MULTIREF_SEGMENTS` — L216
- `STORYBOARD_GRID_MULTIREF_MAIN` — L222
- `GRID_MULTIREF_PRIMARY` — L232
- `PREVIS_PAGE_MOTION` — L244
- `STORYBOARD_TRAILER_MODE` — L248
- `MOTION_ACTION_STORYBOARD` — L253
- `MOTION_BRIDGE_REFS` — L257
- `CHARACTER_TRAILER_MODE` — L261
- `STORYBOARD_TRAILER_MAIN` — L269
- `ADSD_LIP_SYNC_EXPERIMENT` — L282
- `ADSD_RICH_MOTION_PROMPT` — L290
- `ADSD_LLM_VOICE_ASSIGN` — L298
- `ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT` — L302
- `ADSD_CONSECUTIVE_SPEAKER_BATCHING` — L316
- `ADSD_GENDER_FALLBACK_VOICE_ASSET` — L327
- `SILENT_B_SPEAKERS` — L459
- `_PODCAST_TO_VOICE_ASSET_MAP` — L837
- `_VOICE_ASSET_FORBIDDEN_FLAGS` — L855
- `_GENERIC_NARRATOR_NAMES` — L899
- `VOICE_ASSET_AUDIO_DUB_EXPERIMENT` — L936
- `VOICE_ASSET_AUDIO_DUB_PARTIAL_OK` — L944
- `MOTION_VISUAL_QA` — L948
- `MOTION_VOICE_REPAIR` — L956
- `MOTION_VOICE_STRICT_LOCK` — L961
- `WERYDANCE_CAPTIONS` — L966
- `ADSD_ONSITE_POV_MODE` — L978
- `ADSD_LIPS_CHANGE_REPAIR` — L983
- `ADSD_LIPS_CHANGE_ALL` — L988
- `ADS_REPORTER_MODE` — L999
- `ADS_STORYBOARD_FLOW_DEFAULT` — L1016
- `ADS_RETENTION_MODE` — L1030
- `ADSD_MODE_NAME` — L1036
- `EMOTION_STYLE` — L1175
- `EMOTION_STYLE_BRIGHT` — L1187
- `_REDACT_PATTERNS_DEFAULT` — L1201
- `_TG_DASHBOARD_STAGES` — L1253
- `_TG_NOISY_PATTERNS` — L1268
- `_TG_IMMEDIATE_PATTERNS` — L1286
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1546
- `_LLM_TIER` — L1794
- `_TOPIC_MODIFIERS` — L2005
- `_TONE_PANTONE_OVERRIDE` — L2022

**Functions:**
- `_is_action_scene` — L336
- `_needs_storyboard_flow_character_sheet` — L347
- `_wuxia_action_panel_prompt` — L376
- `_action_motion_fragment` — L398
- `_infer_emotion_from_text` — L413
- `_emotion_expression_phrase` — L428
- `_infer_needs_lip_sync` — L435
- `_infer_turn_type` — L462
- `_is_action_shout` — L487
- `_resolve_turn_type` — L513
- `_is_silent_b` — L528
- `_is_narrated_b` — L532
- `_is_a_roll` — L536
- `_is_action_b` — L540
- `_voice_asset_id_for_speaker` — L544
- `_llm_assign_voice_assets` — L572
- `_apply_llm_voice_assignment` — L701
- `_voice_asset_is_speech_safe` — L862
- `_podcast_id_to_voice_asset` — L868
- `_resolve_voice_asset_for_ads_speaker` — L902
- `_redact_for_stdout` — L1216
- `log` — L1241
- `_tg_send_raw` — L1309
- `_tg_matches` — L1325
- `_tg_summarize` — L1329
- `_tg_dashboard_stage_for` — L1336
- `_tg_progress_bar` — L1344
- `_tg_dashboard_text` — L1350
- `_tg_dashboard_update` — L1368
- `_tg_maybe_digest` — L1405
- `tg` — L1420
- `_wait_image_submit_slot` — L1469
- `_wait_motion_submit_slot` — L1482
- `_is_rate_limited_error` — L1495
- `_is_rate_limited_response` — L1505
- `_is_llm_rate_limited_error` — L1526
- `_inject_image2_quality_suffix` — L1554
- `submit_text_to_image` — L1568
- `req_post` — L1598
- `req_get` — L1612
- `_tg_probe_send` — L1620
- `_tg_probe_delete` — L1640
- `_tg_upload_with_probe_gap` — L1653
- `poll` — L1693
- `poll_podcast` — L1718
- `poll_task_status` — L1740
- `poll_storyboard_task` — L1762
- `tier_chat` — L1802
- `chat` — L1808
- `pick_image_model` — L1851
- `detect_topic_meta` — L1876
- `_topic_culture_guard` — L1926
- `_write_cultural_visual_qa` — L1952
- `is_1919_global_topic` — L1999
- `_strip_topic_modifiers` — L2010
- `apply_1919_global_guardrails` — L2028
- `build_1919_global_cover_prompt` — L2057
- `_shot_blueprint_enums` — L2089
- `build_shot_blueprint` — L2165
- `ffprobe_duration` — L2191
- `ffprobe_video_size` — L2202
- `_video_decode_probe` — L2223
- `ffmpeg` — L2241

---

### 第一步：双导演生成剧本
Range: **L2253 – L4739** (2487 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L3753-4739 (987 lines)

**Top-level constants:**
- `_ENSEMBLE_CAP_BY_ROUTE` — L2401

**Functions:**
- `_extract_json_array` — L2254
- `_extract_json_object` — L2264
- `_voice_for_speaker` — L2274
- `_adsd_gender_from_voice` — L2310
- `_adsd_infer_gender_from_speaker` — L2318
- `_adsd_gender_lock_phrase` — L2327
- `_adsd_visual_subject_has_gender_conflict` — L2342
- `_adsd_default_roles` — L2354
- `_adsd_allows_media_role` — L2359
- `_adsd_role_candidates` — L2367
- `_adsd_dialogue_shape` — L2390
- `_ensemble_speaker_cap` — L2412
- `_ip_voice_asset_for_speaker` — L2425
- `_finalize_adsd_turns` — L2449
- `_parse_adsd_override_turns` — L2495
- `_parse_timecode_seconds` — L2588
- `_clean_override_line_text` — L2597
- `_parse_override_script_text` — L2603
- `_adsd_pov_contract` — L2637
- `_load_audit_blacklist_block` — L2650
- `_generate_adsd_dialogue_turns` — L2688
- `_broll_rhythm_reviewer` — L3115
- `_sweep_speaker_field` — L3222
- `_should_run_immersion_qa` — L3282
- `_adsd_immersion_qa_rewrite_turns` — L3305
- `_adsd_visual_contract` — L3369
- `_parse_risk_score` — L3421
- `_check_high_risk_hard_abort` — L3450
- `_maybe_neutralize_topic` — L3477
- `step1_script` — L3516
- `_write_ads_retention_qa` — L4683

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L4740 – L5871** (1132 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L4815
- `_ADSD_POLICY_REWRITE_TERMS` — L4821
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L4912

**Functions:**
- `_openai_tts_fallback` — L4741
- `_edge_tts_fallback` — L4787
- `_sanitize_for_external_api` — L4830
- `_is_content_policy_error` — L4839
- `_rewrite_adsd_tts_text_for_policy` — L4853
- `_record_adsd_tts_rewrite` — L4893
- `_build_silence_mp3` — L4918
- `_audio_duration_seconds` — L4931
- `_text_to_audio_master_voice_timed` — L4943
- `_text_to_audio_master_voice` — L5068
- `step2_master_voice` — L5181
- `_tts_turn_to_audio` — L5309
- `_asr_verify_dialogue_audio` — L5373
- `_asr_verify_dialogue_turns` — L5435
- `_normalize_cn_number_token` — L5477
- `_compact_zh_text` — L5499
- `_write_adsd_asr_text_qa` — L5506
- `_write_adsd_speaker_focus_qa` — L5545
- `_write_adsd_gender_voice_qa` — L5605
- `step2_dialogue_voice` — L5658

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L5872 – L6423** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L5879-6001 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L6002-6036 (35 lines)
- _第二层：字符数插值_ — L6037-6061 (25 lines)
- _第三层：silencedetect 物理校准_ — L6062-6423 (362 lines)

**Functions:**
- `_detect_silences` — L5880
- `_calibrate_boundaries` — L5915
- `_enforce_monotonic` — L5949
- `_manual_override_segments` — L5961
- `_calc_sentence_boundaries` — L5982
- `step345_timeline` — L6093
- `_analyze_bgm_energy_cuts` — L6152
- `_snap_bgm_only_boundaries` — L6215
- `step345_bgm_only_timeline` — L6275

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L6424 – L10921** (4498 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L7645-7695 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L7696-8531 (836 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L8532-8966 (435 lines)
- _Speaker IP Card (2026-05-21)_ — L8967-10754 (1788 lines)
- _审批流程_ — L10755-10811 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L10812-10921 (110 lines)

**Top-level constants:**
- `_CORE_TERMS_STOP_WORDS` — L6819
- `CHARACTER_META_GRID_COSTUMES` — L7651
- `CHARACTER_META_GRID_POSES` — L7652
- `CHARACTER_META_GRID_SCENES` — L7653
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L7656
- `_SFX_TYPE_ENUM` — L8013
- `_SFX_INTENSITY_ENUM` — L8018
- `_SFX_POSITION_ENUM` — L8019
- `_GRAIN_LEVEL_ENUM` — L8164

**Functions:**
- `_extract_img_url` — L6425
- `_extract_img_urls` — L6447
- `_extract_video_url` — L6480
- `_count_bands` — L6505
- `_detect_contact_sheet_like_image` — L6517
- `_file_sha256` — L6578
- `_load_upload_cache` — L6591
- `_save_upload_cache` — L6600
- `_cached_upload_url` — L6608
- `_store_upload_url` — L6625
- `_guess_upload_mime` — L6635
- `_upload_to_weryai` — L6658
- `_send_for_approval` — L6712
- `_wait_approval` — L6776
- `_render_still_segment` — L6788
- `_extract_core_terms` — L6825
- `_scene_text_visual_alignment` — L6844
- `_write_text_visual_alignment_qa` — L6865
- `_scene_motion_action_plan` — L6888
- `_ensure_motion_action_plan` — L6942
- `_motion_action_block` — L6951
- `_motion_plan_for_qa` — L6979
- `_write_motion_action_plan_qa` — L6989
- `_write_motion_bridge_refs_qa` — L7019
- `_motion_bridge_ref_prompt` — L7026
- `generate_motion_bridge_refs_gpt_image2` — L7059
- `generate_image` — L7174
- `generate_storyboard_images_gpt_image2` — L7221
- `_storyboard_grid_aspect` — L7406
- `_storyboard_grid_cols_rows` — L7413
- `_storyboard_grid_prompt` — L7435
- `_storyboard_grid_prompt_limit` — L7493
- `_is_prompt_limit_response` — L7497
- `_production_storyboard_prompt` — L7503
- `_write_production_storyboard_page_qa` — L7537
- `_character_sheet_prompt` — L7547
- `_is_audit_blocked` — L7673
- `_paraphrase_sensitive_dialogue` — L7686
- `_topic_cache_dir` — L7700
- `_topic_cache_path` — L7706
- `_load_topic_decomposition_cache` — L7719
- `_save_topic_decomposition_cache` — L7737
- `_briefs_dir` — L7774
- `_brief_path` — L7780
- `_empty_brief` — L7785
- `_deep_merge_brief_skeleton` — L7825
- `_load_brief` — L7839
- `_save_brief` — L7863
- `_brief_get` — L7882
- `_brief_set` — L7894
- `_brief_claim` — L7910
- `_brief_agent_status` — L7953
- `_brief_from_topic_decomposition` — L7966
- `_rule_based_sfx_design` — L8022
- `_validate_sfx_entry` — L8073
- `_audio_director_design` — L8111
- `_hex_color_validate` — L8167
- `_rule_based_art_design` — L8179
- `_validate_art_design` — L8260
- `_art_director_design` — L8298
- `_coordinator_review` — L8320
- `_llm_topic_decomposition` — L8421
- `_director_route_block` — L8585
- `_llm_infer_meta_grid_template` — L8655
- `_resolve_meta_grid_template` — L8712
- `_infer_meta_grid_costume` — L8755
- `_infer_meta_grid_pose` — L8804
- `_adsd_meta_grid_call_prompt` — L8851
- `_meta_grid_panel_index` — L8893
- `_migrate_speaker_ip` — L8973
- `_speaker_ips_dir` — L8998
- `_list_speaker_ips` — L9005
- `_match_speaker_ip` — L9019
- `_build_speaker_ip_context_for_script` — L9039
- `_ip_usage_stats` — L9095
- `_recommend_related_ips` — L9113
- `_save_speaker_ip` — L9138
- `_record_speaker_usage_history` — L9147
- `_format_speaker_usage_history_for_prompt` — L9194
- `_llm_infer_ip_skeleton` — L9212
- `_llm_pick_voice_asset_for_ip` — L9257
- `_auto_incubate_missing_ips` — L9305
- `_character_meta_grid_cache_dir` — L9389
- `_character_meta_grid_cache_path` — L9397
- `_character_meta_grid_cache_legacy_path` — L9405
- `_character_meta_grid_path` — L9412
- `generate_character_meta_grid_gpt_image2` — L9418
- `_generate_all_character_meta_grids` — L9590
- `_write_character_sheet_qa` — L9631
- `generate_character_sheet_gpt_image2` — L9641
- `generate_production_storyboard_page_gpt_image2` — L9741
- `_qa_clean_storyboard_panel` — L9804
- `_crop_storyboard_grid_panels` — L9985
- `generate_storyboard_grid_gpt_image2` — L10032
- `_gpt_image2_direct_annotated_aspect` — L10263
- `_gpt_image2_direct_annotated_prompt` — L10270
- `generate_gpt_image2_direct_annotated_storyboards` — L10300
- `_llm_bgm_description` — L10401
- `_bgm_contains_vocals` — L10440
- `generate_bgm` — L10474
- `step6_parallel` — L10591

---

### 第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）
Range: **L10922 – L16018** (5097 lines)

**Sub-sections:**
- _PR-A (2026-05-27): merged_a 合并跑 helpers_ — L14213-15753 (1541 lines)
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L15754-15796 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L15797-15834 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回时间轴锚定音轨_ — L15835-15973 (139 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L15974-16018 (45 lines)

**Top-level constants:**
- `_PR3B1_SHOT_TYPE_ENUM` — L11392
- `_PR3B1_CAMERA_ANGLE_ENUM` — L11396
- `_PR3B1_LIGHTING_ENUM` — L11401
- `_PR3B1_CAMERA_MOTION_ENUM` — L11406
- `_EMOTION_NARRATION_STYLE_MAP` — L12457

**Functions:**
- `_generate_motion_prompts` — L10925
- `_motion_tasks_file` — L10992
- `_motion_qa_file` — L10996
- `_append_motion_qa` — L11000
- `_finalize_motion_qa` — L11024
- `_lip_sync_tasks_file` — L11108
- `_load_motion_tasks` — L11112
- `_save_motion_task` — L11122
- `_remove_motion_task` — L11130
- `_load_lip_sync_tasks` — L11137
- `_save_lip_sync_task` — L11147
- `_remove_lip_sync_task` — L11154
- `_video_visual_motion_qa` — L11161
- `_motion_output_qa` — L11233
- `_has_audio_stream` — L11278
- `_normalize_motion_video` — L11289
- `_motion_poll_and_download` — L11339
- `_validate_enum_field` — L11412
- `_build_motion_video_prompt` — L11427
- `_short_board_text` — L11477
- `_wrap_board_text` — L11484
- `_storyboard_font` — L11515
- `_draw_storyboard_arrow` — L11530
- `_build_annotated_storyboard_reference` — L11544
- `_plain_caption_text` — L11645
- `_werydance_caption_request` — L11653
- `_werydance_caption_instruction` — L11680
- `_werydance_negative_prompt` — L11692
- `_motion_reference_prompt` — L11710
- `_motion_audio_dub_prompt` — L11733
- `_motion_audio_dub_poll_and_download` — L11767
- `_try_motion_audio_dub_video` — L11832
- `_try_motion_reference_video` — L11995
- `_motion_one_scene` — L12111
- `_grid_multiref_tasks_file` — L12240
- `_previs_page_tasks_file` — L12244
- `_load_grid_multiref_tasks` — L12248
- `_load_previs_page_tasks` — L12258
- `_save_grid_multiref_task` — L12268
- `_save_previs_page_task` — L12275
- `_remove_grid_multiref_task` — L12282
- `_remove_previs_page_task` — L12289
- `_poll_video_task_download` — L12296
- `_grid_multiref_group_size` — L12345
- `_grid_multiref_adaptive_group_size` — L12355
- `_grid_multiref_duration` — L12379
- `_grid_multiref_tts_buffer_factor` — L12417
- `_grid_multiref_tts_duration_buffered` — L12431
- `_grid_multiref_segment_max_stretch` — L12447
- `_voice_clone_emotion_style` — L12481
- `_grid_multiref_prompt` — L12504
- `_write_grid_multiref_motion_qa` — L12578
- `_write_previs_page_motion_qa` — L12588
- `_write_storyboard_trailer_qa` — L12598
- `_write_character_trailer_qa` — L12608
- `_write_grid_multiref_segment_qa` — L12618
- `_motion_compare_record` — L12628
- `_write_storyboard_motion_compare_qa` — L12650
- `_scene_segment_duration` — L12686
- `_apply_grid_multiref_segments` — L12705
- `_previs_page_duration` — L12910
- `_previs_page_group_prompt` — L12920
- `_previs_page_groups` — L12946
- `_storyboard_trailer_duration` — L12961
- `_storyboard_trailer_prompt` — L12971
- `_character_trailer_max_shots` — L12999
- `_character_trailer_shot_duration` — L13007
- `_character_trailer_prompt` — L13021
- `_concat_character_trailer_segments` — L13036
- `_generate_character_trailer_motion` — L13075
- `_multi_trailer_prompt_for_group` — L13183
- `_generate_multi_trailer_segments` — L13206
- `_generate_storyboard_trailer_motion` — L13317
- `_generate_previs_page_motion_segments` — L13392
- `_generate_grid_multiref_motion_segments` — L13504
- `_grid_multiref_concat_groups` — L13781
- `_grid_multiref_concat_groups_partial` — L13798
- `_grid_multiref_concat_paths` — L13816
- `_lip_sync_slot_duration` — L13858
- `_adsd_lip_sync_prompt` — L13865
- `_adsd_broll_motion_prompt` — L13911
- `_adsd_action_b_motion_prompt` — L13953
- `_adsd_silent_b_motion_prompt` — L13999
- `_adsd_narrated_b_audio_dub_prompt` — L14034
- `_adsd_almighty_audio_dub_prompt` — L14078
- `_postprocess_lip_sync_segment` — L14119
- `_detect_audio_leading_silence` — L14191
- `_concat_audio_files_for_group` — L14216
- `_split_lip_sync_raw_by_durations` — L14239
- `_postprocess_audio_dub_segment` — L14274
- `_lips_change_repair_segment` — L14402
- `_load_lips_change_requested_turns` — L14487
- `_parse_turn_set` — L14504
- `_load_motion_voice_repair_turns` — L14526
- `_voice_assets_file` — L14538
- `_load_voice_assets` — L14545
- `_select_voice_asset_reference` — L14564
- `_lip_sync_poll_download_and_process` — L14630
- `_lip_sync_one_group` — L14698
- `_lip_sync_one_scene` — L14906
- `step66_adsd_lip_sync` — L15230
- `step65_motion` — L15574
- `step65_grid_multiref_motion_qa` — L15726
- `_sanitize_scene_for_state` — L15755
- `_save_pipeline_state` — L15774
- `_retime_after_audio_dub` — L15798
- `_build_voice_clone_hybrid_audio` — L15836
- `_build_dynamic_bgm` — L15975

---

### 第七步：拼接视频轨
Range: **L16019 – L16278** (260 lines)

**Functions:**
- `step7_concat` — L16020

---

### 第八步：生成 ASS 字幕
Range: **L16279 – L17212** (934 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L16533-17212 (680 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L16280
- `_word_timings_for_subtitle_align` — L16306
- `_align_segments_via_asr` — L16347
- `_b61_1_asr_turn_boundaries` — L16390
- `step8_subtitles` — L16435
- `_read_output_json` — L16933
- `_qa_file_pass` — L16944
- `_ass_has_dialogue` — L16951
- `_write_adsd_delivery_qa` — L16961
- `_write_bgm_only_qa` — L17101

---

### 第九步：最终合成
Range: **L17213 – L17497** (285 lines)

**Functions:**
- `step9_render` — L17214

---

### 第十步：推送 Telegram
Range: **L17498 – L19352** (1855 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L18598-18705 (108 lines)
- _B70 (2026-05-30) TG oversize policy helpers_ — L18706-19159 (454 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L19160-19164 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L19165-19228 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L19229-19274 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L19275-19352 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L17867
- `PANTONE_FALLBACK` — L17894
- `FESTIVAL_DATE_TAG` — L18007

**Functions:**
- `_generate_caption` — L17499
- `_overlay_title_on_cover` — L17737
- `_prepare_tg_photo` — L17847
- `_get_pantone_for_date` — L17897
- `_llm_bottom_note` — L17922
- `_get_bottom_note` — L17951
- `_get_date_tag` — L18029
- `_shrink_to_b64` — L18051
- `_llm_check_scenes_anomalies` — L18067
- `_llm_check_cover_unique` — L18120
- `_llm_check_cover_quality` — L18150
- `_try_almanac_cover` — L18192
- `_generate_cover_image` — L18363
- `_async_kickoff_cover_caption` — L18605
- `_await_async_cover_caption` — L18679
- `_b70_env_float` — L18709
- `_b70_split_and_deliver` — L18724
- `_b70_send_document_first` — L18824
- `step10_deliver` — L18861

---

### 主流程
Range: **L19353 – L19537** (185 lines)

**Functions:**
- `_print_execution_plan` — L19354
- `main` — L19402

---
