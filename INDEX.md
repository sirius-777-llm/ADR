# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (18245 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-2119 (1998 lines · 61 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L2120-4494 (2375 lines · 30 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L4495-5626 (1132 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L5627-6178 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L6179-10242 (4064 lines · 93 fn · 6 sub)
- [`第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）`](#第-6-5-步-动态化-hads-vads-默认-on---no-motion-关) — L10243-15059 (4817 lines · 103 fn · 5 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L15060-15319 (260 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L15320-16122 (803 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L16123-16398 (276 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L16399-18060 (1662 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L18061-18245 (185 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L2119** (1998 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L324-453 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L454-1185 (732 lines)
- _工具函数_ — L1186-1562 (377 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1563-2119 (557 lines)

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
- `_PODCAST_TO_VOICE_ASSET_MAP` — L827
- `_VOICE_ASSET_FORBIDDEN_FLAGS` — L845
- `_GENERIC_NARRATOR_NAMES` — L889
- `VOICE_ASSET_AUDIO_DUB_EXPERIMENT` — L926
- `VOICE_ASSET_AUDIO_DUB_PARTIAL_OK` — L934
- `MOTION_VISUAL_QA` — L938
- `MOTION_VOICE_REPAIR` — L946
- `MOTION_VOICE_STRICT_LOCK` — L951
- `WERYDANCE_CAPTIONS` — L956
- `ADSD_ONSITE_POV_MODE` — L968
- `ADSD_LIPS_CHANGE_REPAIR` — L973
- `ADSD_LIPS_CHANGE_ALL` — L978
- `ADS_REPORTER_MODE` — L989
- `ADS_STORYBOARD_FLOW_DEFAULT` — L1006
- `ADS_RETENTION_MODE` — L1020
- `ADSD_MODE_NAME` — L1026
- `EMOTION_STYLE` — L1165
- `EMOTION_STYLE_BRIGHT` — L1177
- `_TG_DASHBOARD_STAGES` — L1199
- `_TG_NOISY_PATTERNS` — L1214
- `_TG_IMMEDIATE_PATTERNS` — L1232
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1492
- `_LLM_TIER` — L1740
- `_TOPIC_MODIFIERS` — L1951
- `_TONE_PANTONE_OVERRIDE` — L1968

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
- `_voice_asset_is_speech_safe` — L852
- `_podcast_id_to_voice_asset` — L858
- `_resolve_voice_asset_for_ads_speaker` — L892
- `log` — L1187
- `_tg_send_raw` — L1255
- `_tg_matches` — L1271
- `_tg_summarize` — L1275
- `_tg_dashboard_stage_for` — L1282
- `_tg_progress_bar` — L1290
- `_tg_dashboard_text` — L1296
- `_tg_dashboard_update` — L1314
- `_tg_maybe_digest` — L1351
- `tg` — L1366
- `_wait_image_submit_slot` — L1415
- `_wait_motion_submit_slot` — L1428
- `_is_rate_limited_error` — L1441
- `_is_rate_limited_response` — L1451
- `_is_llm_rate_limited_error` — L1472
- `_inject_image2_quality_suffix` — L1500
- `submit_text_to_image` — L1514
- `req_post` — L1544
- `req_get` — L1558
- `_tg_probe_send` — L1566
- `_tg_probe_delete` — L1586
- `_tg_upload_with_probe_gap` — L1599
- `poll` — L1639
- `poll_podcast` — L1664
- `poll_task_status` — L1686
- `poll_storyboard_task` — L1708
- `tier_chat` — L1748
- `chat` — L1754
- `pick_image_model` — L1797
- `detect_topic_meta` — L1822
- `_topic_culture_guard` — L1872
- `_write_cultural_visual_qa` — L1898
- `is_1919_global_topic` — L1945
- `_strip_topic_modifiers` — L1956
- `apply_1919_global_guardrails` — L1974
- `build_1919_global_cover_prompt` — L2003
- `build_shot_blueprint` — L2032
- `ffprobe_duration` — L2058
- `ffprobe_video_size` — L2069
- `_video_decode_probe` — L2090
- `ffmpeg` — L2108

---

### 第一步：双导演生成剧本
Range: **L2120 – L4494** (2375 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L3584-4494 (911 lines)

**Top-level constants:**
- `_ENSEMBLE_CAP_BY_ROUTE` — L2268

**Functions:**
- `_extract_json_array` — L2121
- `_extract_json_object` — L2131
- `_voice_for_speaker` — L2141
- `_adsd_gender_from_voice` — L2177
- `_adsd_infer_gender_from_speaker` — L2185
- `_adsd_gender_lock_phrase` — L2194
- `_adsd_visual_subject_has_gender_conflict` — L2209
- `_adsd_default_roles` — L2221
- `_adsd_allows_media_role` — L2226
- `_adsd_role_candidates` — L2234
- `_adsd_dialogue_shape` — L2257
- `_ensemble_speaker_cap` — L2279
- `_finalize_adsd_turns` — L2292
- `_parse_adsd_override_turns` — L2326
- `_parse_timecode_seconds` — L2419
- `_clean_override_line_text` — L2428
- `_parse_override_script_text` — L2434
- `_adsd_pov_contract` — L2468
- `_load_audit_blacklist_block` — L2481
- `_generate_adsd_dialogue_turns` — L2519
- `_broll_rhythm_reviewer` — L2946
- `_sweep_speaker_field` — L3053
- `_should_run_immersion_qa` — L3113
- `_adsd_immersion_qa_rewrite_turns` — L3136
- `_adsd_visual_contract` — L3200
- `_parse_risk_score` — L3252
- `_check_high_risk_hard_abort` — L3281
- `_maybe_neutralize_topic` — L3308
- `step1_script` — L3347
- `_write_ads_retention_qa` — L4438

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L4495 – L5626** (1132 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L4570
- `_ADSD_POLICY_REWRITE_TERMS` — L4576
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L4667

**Functions:**
- `_openai_tts_fallback` — L4496
- `_edge_tts_fallback` — L4542
- `_sanitize_for_external_api` — L4585
- `_is_content_policy_error` — L4594
- `_rewrite_adsd_tts_text_for_policy` — L4608
- `_record_adsd_tts_rewrite` — L4648
- `_build_silence_mp3` — L4673
- `_audio_duration_seconds` — L4686
- `_text_to_audio_master_voice_timed` — L4698
- `_text_to_audio_master_voice` — L4823
- `step2_master_voice` — L4936
- `_tts_turn_to_audio` — L5064
- `_asr_verify_dialogue_audio` — L5128
- `_asr_verify_dialogue_turns` — L5190
- `_normalize_cn_number_token` — L5232
- `_compact_zh_text` — L5254
- `_write_adsd_asr_text_qa` — L5261
- `_write_adsd_speaker_focus_qa` — L5300
- `_write_adsd_gender_voice_qa` — L5360
- `step2_dialogue_voice` — L5413

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L5627 – L6178** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L5634-5756 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L5757-5791 (35 lines)
- _第二层：字符数插值_ — L5792-5816 (25 lines)
- _第三层：silencedetect 物理校准_ — L5817-6178 (362 lines)

**Functions:**
- `_detect_silences` — L5635
- `_calibrate_boundaries` — L5670
- `_enforce_monotonic` — L5704
- `_manual_override_segments` — L5716
- `_calc_sentence_boundaries` — L5737
- `step345_timeline` — L5848
- `_analyze_bgm_energy_cuts` — L5907
- `_snap_bgm_only_boundaries` — L5970
- `step345_bgm_only_timeline` — L6030

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L6179 – L10242** (4064 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L7380-7430 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L7431-7852 (422 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L7853-8287 (435 lines)
- _Speaker IP Card (2026-05-21)_ — L8288-10075 (1788 lines)
- _审批流程_ — L10076-10132 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L10133-10242 (110 lines)

**Top-level constants:**
- `_CORE_TERMS_STOP_WORDS` — L6574
- `CHARACTER_META_GRID_COSTUMES` — L7386
- `CHARACTER_META_GRID_POSES` — L7387
- `CHARACTER_META_GRID_SCENES` — L7388
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L7391

**Functions:**
- `_extract_img_url` — L6180
- `_extract_img_urls` — L6202
- `_extract_video_url` — L6235
- `_count_bands` — L6260
- `_detect_contact_sheet_like_image` — L6272
- `_file_sha256` — L6333
- `_load_upload_cache` — L6346
- `_save_upload_cache` — L6355
- `_cached_upload_url` — L6363
- `_store_upload_url` — L6380
- `_guess_upload_mime` — L6390
- `_upload_to_weryai` — L6413
- `_send_for_approval` — L6467
- `_wait_approval` — L6531
- `_render_still_segment` — L6543
- `_extract_core_terms` — L6580
- `_scene_text_visual_alignment` — L6599
- `_write_text_visual_alignment_qa` — L6620
- `_scene_motion_action_plan` — L6643
- `_ensure_motion_action_plan` — L6697
- `_motion_action_block` — L6706
- `_motion_plan_for_qa` — L6734
- `_write_motion_action_plan_qa` — L6744
- `_write_motion_bridge_refs_qa` — L6774
- `_motion_bridge_ref_prompt` — L6781
- `generate_motion_bridge_refs_gpt_image2` — L6814
- `generate_image` — L6929
- `generate_storyboard_images_gpt_image2` — L6976
- `_storyboard_grid_aspect` — L7161
- `_storyboard_grid_cols_rows` — L7168
- `_storyboard_grid_prompt` — L7190
- `_storyboard_grid_prompt_limit` — L7228
- `_is_prompt_limit_response` — L7232
- `_production_storyboard_prompt` — L7238
- `_write_production_storyboard_page_qa` — L7272
- `_character_sheet_prompt` — L7282
- `_is_audit_blocked` — L7408
- `_paraphrase_sensitive_dialogue` — L7421
- `_topic_cache_dir` — L7435
- `_topic_cache_path` — L7441
- `_load_topic_decomposition_cache` — L7454
- `_save_topic_decomposition_cache` — L7472
- `_briefs_dir` — L7509
- `_brief_path` — L7515
- `_empty_brief` — L7520
- `_deep_merge_brief_skeleton` — L7558
- `_load_brief` — L7572
- `_save_brief` — L7596
- `_brief_get` — L7615
- `_brief_set` — L7627
- `_brief_claim` — L7643
- `_brief_agent_status` — L7686
- `_brief_from_topic_decomposition` — L7699
- `_llm_topic_decomposition` — L7742
- `_director_route_block` — L7906
- `_llm_infer_meta_grid_template` — L7976
- `_resolve_meta_grid_template` — L8033
- `_infer_meta_grid_costume` — L8076
- `_infer_meta_grid_pose` — L8125
- `_adsd_meta_grid_call_prompt` — L8172
- `_meta_grid_panel_index` — L8214
- `_migrate_speaker_ip` — L8294
- `_speaker_ips_dir` — L8319
- `_list_speaker_ips` — L8326
- `_match_speaker_ip` — L8340
- `_build_speaker_ip_context_for_script` — L8360
- `_ip_usage_stats` — L8416
- `_recommend_related_ips` — L8434
- `_save_speaker_ip` — L8459
- `_record_speaker_usage_history` — L8468
- `_format_speaker_usage_history_for_prompt` — L8515
- `_llm_infer_ip_skeleton` — L8533
- `_llm_pick_voice_asset_for_ip` — L8578
- `_auto_incubate_missing_ips` — L8626
- `_character_meta_grid_cache_dir` — L8710
- `_character_meta_grid_cache_path` — L8718
- `_character_meta_grid_cache_legacy_path` — L8726
- `_character_meta_grid_path` — L8733
- `generate_character_meta_grid_gpt_image2` — L8739
- `_generate_all_character_meta_grids` — L8911
- `_write_character_sheet_qa` — L8952
- `generate_character_sheet_gpt_image2` — L8962
- `generate_production_storyboard_page_gpt_image2` — L9062
- `_qa_clean_storyboard_panel` — L9125
- `_crop_storyboard_grid_panels` — L9306
- `generate_storyboard_grid_gpt_image2` — L9353
- `_gpt_image2_direct_annotated_aspect` — L9584
- `_gpt_image2_direct_annotated_prompt` — L9591
- `generate_gpt_image2_direct_annotated_storyboards` — L9621
- `_llm_bgm_description` — L9722
- `_bgm_contains_vocals` — L9761
- `generate_bgm` — L9795
- `step6_parallel` — L9912

---

### 第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）
Range: **L10243 – L15059** (4817 lines)

**Sub-sections:**
- _PR-A (2026-05-27): merged_a 合并跑 helpers_ — L13321-14794 (1474 lines)
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L14795-14837 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L14838-14875 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回时间轴锚定音轨_ — L14876-15014 (139 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L15015-15059 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L10246
- `_motion_tasks_file` — L10313
- `_motion_qa_file` — L10317
- `_append_motion_qa` — L10321
- `_finalize_motion_qa` — L10345
- `_lip_sync_tasks_file` — L10429
- `_load_motion_tasks` — L10433
- `_save_motion_task` — L10443
- `_remove_motion_task` — L10451
- `_load_lip_sync_tasks` — L10458
- `_save_lip_sync_task` — L10468
- `_remove_lip_sync_task` — L10475
- `_video_visual_motion_qa` — L10482
- `_motion_output_qa` — L10554
- `_has_audio_stream` — L10599
- `_normalize_motion_video` — L10610
- `_motion_poll_and_download` — L10660
- `_build_motion_video_prompt` — L10711
- `_short_board_text` — L10741
- `_wrap_board_text` — L10748
- `_storyboard_font` — L10779
- `_draw_storyboard_arrow` — L10794
- `_build_annotated_storyboard_reference` — L10808
- `_plain_caption_text` — L10909
- `_werydance_caption_request` — L10917
- `_werydance_caption_instruction` — L10944
- `_werydance_negative_prompt` — L10956
- `_motion_reference_prompt` — L10974
- `_motion_audio_dub_prompt` — L10997
- `_motion_audio_dub_poll_and_download` — L11031
- `_try_motion_audio_dub_video` — L11096
- `_try_motion_reference_video` — L11259
- `_motion_one_scene` — L11375
- `_grid_multiref_tasks_file` — L11504
- `_previs_page_tasks_file` — L11508
- `_load_grid_multiref_tasks` — L11512
- `_load_previs_page_tasks` — L11522
- `_save_grid_multiref_task` — L11532
- `_save_previs_page_task` — L11539
- `_remove_grid_multiref_task` — L11546
- `_remove_previs_page_task` — L11553
- `_poll_video_task_download` — L11560
- `_grid_multiref_group_size` — L11609
- `_grid_multiref_duration` — L11619
- `_grid_multiref_segment_max_stretch` — L11641
- `_grid_multiref_prompt` — L11649
- `_write_grid_multiref_motion_qa` — L11719
- `_write_previs_page_motion_qa` — L11729
- `_write_storyboard_trailer_qa` — L11739
- `_write_character_trailer_qa` — L11749
- `_write_grid_multiref_segment_qa` — L11759
- `_motion_compare_record` — L11769
- `_write_storyboard_motion_compare_qa` — L11791
- `_scene_segment_duration` — L11827
- `_apply_grid_multiref_segments` — L11846
- `_previs_page_duration` — L12051
- `_previs_page_group_prompt` — L12061
- `_previs_page_groups` — L12087
- `_storyboard_trailer_duration` — L12102
- `_storyboard_trailer_prompt` — L12112
- `_character_trailer_max_shots` — L12140
- `_character_trailer_shot_duration` — L12148
- `_character_trailer_prompt` — L12162
- `_concat_character_trailer_segments` — L12177
- `_generate_character_trailer_motion` — L12216
- `_multi_trailer_prompt_for_group` — L12324
- `_generate_multi_trailer_segments` — L12347
- `_generate_storyboard_trailer_motion` — L12458
- `_generate_previs_page_motion_segments` — L12533
- `_generate_grid_multiref_motion_segments` — L12645
- `_grid_multiref_concat_groups` — L12889
- `_grid_multiref_concat_groups_partial` — L12906
- `_grid_multiref_concat_paths` — L12924
- `_lip_sync_slot_duration` — L12966
- `_adsd_lip_sync_prompt` — L12973
- `_adsd_broll_motion_prompt` — L13019
- `_adsd_action_b_motion_prompt` — L13061
- `_adsd_silent_b_motion_prompt` — L13107
- `_adsd_narrated_b_audio_dub_prompt` — L13142
- `_adsd_almighty_audio_dub_prompt` — L13186
- `_postprocess_lip_sync_segment` — L13227
- `_detect_audio_leading_silence` — L13299
- `_concat_audio_files_for_group` — L13324
- `_split_lip_sync_raw_by_durations` — L13347
- `_postprocess_audio_dub_segment` — L13382
- `_lips_change_repair_segment` — L13497
- `_load_lips_change_requested_turns` — L13582
- `_parse_turn_set` — L13599
- `_load_motion_voice_repair_turns` — L13621
- `_voice_assets_file` — L13633
- `_load_voice_assets` — L13640
- `_select_voice_asset_reference` — L13659
- `_lip_sync_poll_download_and_process` — L13725
- `_lip_sync_one_group` — L13793
- `_lip_sync_one_scene` — L13970
- `step66_adsd_lip_sync` — L14294
- `step65_motion` — L14615
- `step65_grid_multiref_motion_qa` — L14767
- `_sanitize_scene_for_state` — L14796
- `_save_pipeline_state` — L14815
- `_retime_after_audio_dub` — L14839
- `_build_voice_clone_hybrid_audio` — L14877
- `_build_dynamic_bgm` — L15016

---

### 第七步：拼接视频轨
Range: **L15060 – L15319** (260 lines)

**Functions:**
- `step7_concat` — L15061

---

### 第八步：生成 ASS 字幕
Range: **L15320 – L16122** (803 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L15443-16122 (680 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L15321
- `_word_timings_for_subtitle_align` — L15347
- `_align_segments_via_asr` — L15388
- `step8_subtitles` — L15431
- `_read_output_json` — L15843
- `_qa_file_pass` — L15854
- `_ass_has_dialogue` — L15861
- `_write_adsd_delivery_qa` — L15871
- `_write_bgm_only_qa` — L16011

---

### 第九步：最终合成
Range: **L16123 – L16398** (276 lines)

**Functions:**
- `step9_render` — L16124

---

### 第十步：推送 Telegram
Range: **L16399 – L18060** (1662 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L17499-17867 (369 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L17868-17872 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L17873-17936 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L17937-17982 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L17983-18060 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L16768
- `PANTONE_FALLBACK` — L16795
- `FESTIVAL_DATE_TAG` — L16908

**Functions:**
- `_generate_caption` — L16400
- `_overlay_title_on_cover` — L16638
- `_prepare_tg_photo` — L16748
- `_get_pantone_for_date` — L16798
- `_llm_bottom_note` — L16823
- `_get_bottom_note` — L16852
- `_get_date_tag` — L16930
- `_shrink_to_b64` — L16952
- `_llm_check_scenes_anomalies` — L16968
- `_llm_check_cover_unique` — L17021
- `_llm_check_cover_quality` — L17051
- `_try_almanac_cover` — L17093
- `_generate_cover_image` — L17264
- `_async_kickoff_cover_caption` — L17506
- `_await_async_cover_caption` — L17580
- `step10_deliver` — L17607

---

### 主流程
Range: **L18061 – L18245** (185 lines)

**Functions:**
- `_print_execution_plan` — L18062
- `main` — L18110

---
