# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (17840 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-2077 (1956 lines · 60 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L2078-4370 (2293 lines · 30 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L4371-5502 (1132 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L5503-6054 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L6055-9837 (3783 lines · 82 fn · 6 sub)
- [`第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）`](#第-6-5-步-动态化-hads-vads-默认-on---no-motion-关) — L9838-14654 (4817 lines · 103 fn · 5 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L14655-14914 (260 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L14915-15717 (803 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L15718-15993 (276 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L15994-17655 (1662 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L17656-17840 (185 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L2077** (1956 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L324-453 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L454-1185 (732 lines)
- _工具函数_ — L1186-1535 (350 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1536-2077 (542 lines)

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
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1465
- `_LLM_TIER` — L1713
- `_TOPIC_MODIFIERS` — L1909
- `_TONE_PANTONE_OVERRIDE` — L1926

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
- `_inject_image2_quality_suffix` — L1473
- `submit_text_to_image` — L1487
- `req_post` — L1517
- `req_get` — L1531
- `_tg_probe_send` — L1539
- `_tg_probe_delete` — L1559
- `_tg_upload_with_probe_gap` — L1572
- `poll` — L1612
- `poll_podcast` — L1637
- `poll_task_status` — L1659
- `poll_storyboard_task` — L1681
- `tier_chat` — L1721
- `chat` — L1727
- `pick_image_model` — L1755
- `detect_topic_meta` — L1780
- `_topic_culture_guard` — L1830
- `_write_cultural_visual_qa` — L1856
- `is_1919_global_topic` — L1903
- `_strip_topic_modifiers` — L1914
- `apply_1919_global_guardrails` — L1932
- `build_1919_global_cover_prompt` — L1961
- `build_shot_blueprint` — L1990
- `ffprobe_duration` — L2016
- `ffprobe_video_size` — L2027
- `_video_decode_probe` — L2048
- `ffmpeg` — L2066

---

### 第一步：双导演生成剧本
Range: **L2078 – L4370** (2293 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L3542-4370 (829 lines)

**Top-level constants:**
- `_ENSEMBLE_CAP_BY_ROUTE` — L2226

**Functions:**
- `_extract_json_array` — L2079
- `_extract_json_object` — L2089
- `_voice_for_speaker` — L2099
- `_adsd_gender_from_voice` — L2135
- `_adsd_infer_gender_from_speaker` — L2143
- `_adsd_gender_lock_phrase` — L2152
- `_adsd_visual_subject_has_gender_conflict` — L2167
- `_adsd_default_roles` — L2179
- `_adsd_allows_media_role` — L2184
- `_adsd_role_candidates` — L2192
- `_adsd_dialogue_shape` — L2215
- `_ensemble_speaker_cap` — L2237
- `_finalize_adsd_turns` — L2250
- `_parse_adsd_override_turns` — L2284
- `_parse_timecode_seconds` — L2377
- `_clean_override_line_text` — L2386
- `_parse_override_script_text` — L2392
- `_adsd_pov_contract` — L2426
- `_load_audit_blacklist_block` — L2439
- `_generate_adsd_dialogue_turns` — L2477
- `_broll_rhythm_reviewer` — L2904
- `_sweep_speaker_field` — L3011
- `_should_run_immersion_qa` — L3071
- `_adsd_immersion_qa_rewrite_turns` — L3094
- `_adsd_visual_contract` — L3158
- `_parse_risk_score` — L3210
- `_check_high_risk_hard_abort` — L3239
- `_maybe_neutralize_topic` — L3266
- `step1_script` — L3305
- `_write_ads_retention_qa` — L4314

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L4371 – L5502** (1132 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L4446
- `_ADSD_POLICY_REWRITE_TERMS` — L4452
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L4543

**Functions:**
- `_openai_tts_fallback` — L4372
- `_edge_tts_fallback` — L4418
- `_sanitize_for_external_api` — L4461
- `_is_content_policy_error` — L4470
- `_rewrite_adsd_tts_text_for_policy` — L4484
- `_record_adsd_tts_rewrite` — L4524
- `_build_silence_mp3` — L4549
- `_audio_duration_seconds` — L4562
- `_text_to_audio_master_voice_timed` — L4574
- `_text_to_audio_master_voice` — L4699
- `step2_master_voice` — L4812
- `_tts_turn_to_audio` — L4940
- `_asr_verify_dialogue_audio` — L5004
- `_asr_verify_dialogue_turns` — L5066
- `_normalize_cn_number_token` — L5108
- `_compact_zh_text` — L5130
- `_write_adsd_asr_text_qa` — L5137
- `_write_adsd_speaker_focus_qa` — L5176
- `_write_adsd_gender_voice_qa` — L5236
- `step2_dialogue_voice` — L5289

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L5503 – L6054** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L5510-5632 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L5633-5667 (35 lines)
- _第二层：字符数插值_ — L5668-5692 (25 lines)
- _第三层：silencedetect 物理校准_ — L5693-6054 (362 lines)

**Functions:**
- `_detect_silences` — L5511
- `_calibrate_boundaries` — L5546
- `_enforce_monotonic` — L5580
- `_manual_override_segments` — L5592
- `_calc_sentence_boundaries` — L5613
- `step345_timeline` — L5724
- `_analyze_bgm_energy_cuts` — L5783
- `_snap_bgm_only_boundaries` — L5846
- `step345_bgm_only_timeline` — L5906

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L6055 – L9837** (3783 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L7256-7306 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L7307-7447 (141 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L7448-7882 (435 lines)
- _Speaker IP Card (2026-05-21)_ — L7883-9670 (1788 lines)
- _审批流程_ — L9671-9727 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L9728-9837 (110 lines)

**Top-level constants:**
- `_CORE_TERMS_STOP_WORDS` — L6450
- `CHARACTER_META_GRID_COSTUMES` — L7262
- `CHARACTER_META_GRID_POSES` — L7263
- `CHARACTER_META_GRID_SCENES` — L7264
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L7267

**Functions:**
- `_extract_img_url` — L6056
- `_extract_img_urls` — L6078
- `_extract_video_url` — L6111
- `_count_bands` — L6136
- `_detect_contact_sheet_like_image` — L6148
- `_file_sha256` — L6209
- `_load_upload_cache` — L6222
- `_save_upload_cache` — L6231
- `_cached_upload_url` — L6239
- `_store_upload_url` — L6256
- `_guess_upload_mime` — L6266
- `_upload_to_weryai` — L6289
- `_send_for_approval` — L6343
- `_wait_approval` — L6407
- `_render_still_segment` — L6419
- `_extract_core_terms` — L6456
- `_scene_text_visual_alignment` — L6475
- `_write_text_visual_alignment_qa` — L6496
- `_scene_motion_action_plan` — L6519
- `_ensure_motion_action_plan` — L6573
- `_motion_action_block` — L6582
- `_motion_plan_for_qa` — L6610
- `_write_motion_action_plan_qa` — L6620
- `_write_motion_bridge_refs_qa` — L6650
- `_motion_bridge_ref_prompt` — L6657
- `generate_motion_bridge_refs_gpt_image2` — L6690
- `generate_image` — L6805
- `generate_storyboard_images_gpt_image2` — L6852
- `_storyboard_grid_aspect` — L7037
- `_storyboard_grid_cols_rows` — L7044
- `_storyboard_grid_prompt` — L7066
- `_storyboard_grid_prompt_limit` — L7104
- `_is_prompt_limit_response` — L7108
- `_production_storyboard_prompt` — L7114
- `_write_production_storyboard_page_qa` — L7148
- `_character_sheet_prompt` — L7158
- `_is_audit_blocked` — L7284
- `_paraphrase_sensitive_dialogue` — L7297
- `_topic_cache_dir` — L7311
- `_topic_cache_path` — L7317
- `_load_topic_decomposition_cache` — L7330
- `_save_topic_decomposition_cache` — L7348
- `_llm_topic_decomposition` — L7354
- `_director_route_block` — L7501
- `_llm_infer_meta_grid_template` — L7571
- `_resolve_meta_grid_template` — L7628
- `_infer_meta_grid_costume` — L7671
- `_infer_meta_grid_pose` — L7720
- `_adsd_meta_grid_call_prompt` — L7767
- `_meta_grid_panel_index` — L7809
- `_migrate_speaker_ip` — L7889
- `_speaker_ips_dir` — L7914
- `_list_speaker_ips` — L7921
- `_match_speaker_ip` — L7935
- `_build_speaker_ip_context_for_script` — L7955
- `_ip_usage_stats` — L8011
- `_recommend_related_ips` — L8029
- `_save_speaker_ip` — L8054
- `_record_speaker_usage_history` — L8063
- `_format_speaker_usage_history_for_prompt` — L8110
- `_llm_infer_ip_skeleton` — L8128
- `_llm_pick_voice_asset_for_ip` — L8173
- `_auto_incubate_missing_ips` — L8221
- `_character_meta_grid_cache_dir` — L8305
- `_character_meta_grid_cache_path` — L8313
- `_character_meta_grid_cache_legacy_path` — L8321
- `_character_meta_grid_path` — L8328
- `generate_character_meta_grid_gpt_image2` — L8334
- `_generate_all_character_meta_grids` — L8506
- `_write_character_sheet_qa` — L8547
- `generate_character_sheet_gpt_image2` — L8557
- `generate_production_storyboard_page_gpt_image2` — L8657
- `_qa_clean_storyboard_panel` — L8720
- `_crop_storyboard_grid_panels` — L8901
- `generate_storyboard_grid_gpt_image2` — L8948
- `_gpt_image2_direct_annotated_aspect` — L9179
- `_gpt_image2_direct_annotated_prompt` — L9186
- `generate_gpt_image2_direct_annotated_storyboards` — L9216
- `_llm_bgm_description` — L9317
- `_bgm_contains_vocals` — L9356
- `generate_bgm` — L9390
- `step6_parallel` — L9507

---

### 第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）
Range: **L9838 – L14654** (4817 lines)

**Sub-sections:**
- _PR-A (2026-05-27): merged_a 合并跑 helpers_ — L12916-14389 (1474 lines)
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L14390-14432 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L14433-14470 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回时间轴锚定音轨_ — L14471-14609 (139 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L14610-14654 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L9841
- `_motion_tasks_file` — L9908
- `_motion_qa_file` — L9912
- `_append_motion_qa` — L9916
- `_finalize_motion_qa` — L9940
- `_lip_sync_tasks_file` — L10024
- `_load_motion_tasks` — L10028
- `_save_motion_task` — L10038
- `_remove_motion_task` — L10046
- `_load_lip_sync_tasks` — L10053
- `_save_lip_sync_task` — L10063
- `_remove_lip_sync_task` — L10070
- `_video_visual_motion_qa` — L10077
- `_motion_output_qa` — L10149
- `_has_audio_stream` — L10194
- `_normalize_motion_video` — L10205
- `_motion_poll_and_download` — L10255
- `_build_motion_video_prompt` — L10306
- `_short_board_text` — L10336
- `_wrap_board_text` — L10343
- `_storyboard_font` — L10374
- `_draw_storyboard_arrow` — L10389
- `_build_annotated_storyboard_reference` — L10403
- `_plain_caption_text` — L10504
- `_werydance_caption_request` — L10512
- `_werydance_caption_instruction` — L10539
- `_werydance_negative_prompt` — L10551
- `_motion_reference_prompt` — L10569
- `_motion_audio_dub_prompt` — L10592
- `_motion_audio_dub_poll_and_download` — L10626
- `_try_motion_audio_dub_video` — L10691
- `_try_motion_reference_video` — L10854
- `_motion_one_scene` — L10970
- `_grid_multiref_tasks_file` — L11099
- `_previs_page_tasks_file` — L11103
- `_load_grid_multiref_tasks` — L11107
- `_load_previs_page_tasks` — L11117
- `_save_grid_multiref_task` — L11127
- `_save_previs_page_task` — L11134
- `_remove_grid_multiref_task` — L11141
- `_remove_previs_page_task` — L11148
- `_poll_video_task_download` — L11155
- `_grid_multiref_group_size` — L11204
- `_grid_multiref_duration` — L11214
- `_grid_multiref_segment_max_stretch` — L11236
- `_grid_multiref_prompt` — L11244
- `_write_grid_multiref_motion_qa` — L11314
- `_write_previs_page_motion_qa` — L11324
- `_write_storyboard_trailer_qa` — L11334
- `_write_character_trailer_qa` — L11344
- `_write_grid_multiref_segment_qa` — L11354
- `_motion_compare_record` — L11364
- `_write_storyboard_motion_compare_qa` — L11386
- `_scene_segment_duration` — L11422
- `_apply_grid_multiref_segments` — L11441
- `_previs_page_duration` — L11646
- `_previs_page_group_prompt` — L11656
- `_previs_page_groups` — L11682
- `_storyboard_trailer_duration` — L11697
- `_storyboard_trailer_prompt` — L11707
- `_character_trailer_max_shots` — L11735
- `_character_trailer_shot_duration` — L11743
- `_character_trailer_prompt` — L11757
- `_concat_character_trailer_segments` — L11772
- `_generate_character_trailer_motion` — L11811
- `_multi_trailer_prompt_for_group` — L11919
- `_generate_multi_trailer_segments` — L11942
- `_generate_storyboard_trailer_motion` — L12053
- `_generate_previs_page_motion_segments` — L12128
- `_generate_grid_multiref_motion_segments` — L12240
- `_grid_multiref_concat_groups` — L12484
- `_grid_multiref_concat_groups_partial` — L12501
- `_grid_multiref_concat_paths` — L12519
- `_lip_sync_slot_duration` — L12561
- `_adsd_lip_sync_prompt` — L12568
- `_adsd_broll_motion_prompt` — L12614
- `_adsd_action_b_motion_prompt` — L12656
- `_adsd_silent_b_motion_prompt` — L12702
- `_adsd_narrated_b_audio_dub_prompt` — L12737
- `_adsd_almighty_audio_dub_prompt` — L12781
- `_postprocess_lip_sync_segment` — L12822
- `_detect_audio_leading_silence` — L12894
- `_concat_audio_files_for_group` — L12919
- `_split_lip_sync_raw_by_durations` — L12942
- `_postprocess_audio_dub_segment` — L12977
- `_lips_change_repair_segment` — L13092
- `_load_lips_change_requested_turns` — L13177
- `_parse_turn_set` — L13194
- `_load_motion_voice_repair_turns` — L13216
- `_voice_assets_file` — L13228
- `_load_voice_assets` — L13235
- `_select_voice_asset_reference` — L13254
- `_lip_sync_poll_download_and_process` — L13320
- `_lip_sync_one_group` — L13388
- `_lip_sync_one_scene` — L13565
- `step66_adsd_lip_sync` — L13889
- `step65_motion` — L14210
- `step65_grid_multiref_motion_qa` — L14362
- `_sanitize_scene_for_state` — L14391
- `_save_pipeline_state` — L14410
- `_retime_after_audio_dub` — L14434
- `_build_voice_clone_hybrid_audio` — L14472
- `_build_dynamic_bgm` — L14611

---

### 第七步：拼接视频轨
Range: **L14655 – L14914** (260 lines)

**Functions:**
- `step7_concat` — L14656

---

### 第八步：生成 ASS 字幕
Range: **L14915 – L15717** (803 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L15038-15717 (680 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L14916
- `_word_timings_for_subtitle_align` — L14942
- `_align_segments_via_asr` — L14983
- `step8_subtitles` — L15026
- `_read_output_json` — L15438
- `_qa_file_pass` — L15449
- `_ass_has_dialogue` — L15456
- `_write_adsd_delivery_qa` — L15466
- `_write_bgm_only_qa` — L15606

---

### 第九步：最终合成
Range: **L15718 – L15993** (276 lines)

**Functions:**
- `step9_render` — L15719

---

### 第十步：推送 Telegram
Range: **L15994 – L17655** (1662 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L17094-17462 (369 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L17463-17467 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L17468-17531 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L17532-17577 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L17578-17655 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L16363
- `PANTONE_FALLBACK` — L16390
- `FESTIVAL_DATE_TAG` — L16503

**Functions:**
- `_generate_caption` — L15995
- `_overlay_title_on_cover` — L16233
- `_prepare_tg_photo` — L16343
- `_get_pantone_for_date` — L16393
- `_llm_bottom_note` — L16418
- `_get_bottom_note` — L16447
- `_get_date_tag` — L16525
- `_shrink_to_b64` — L16547
- `_llm_check_scenes_anomalies` — L16563
- `_llm_check_cover_unique` — L16616
- `_llm_check_cover_quality` — L16646
- `_try_almanac_cover` — L16688
- `_generate_cover_image` — L16859
- `_async_kickoff_cover_caption` — L17101
- `_await_async_cover_caption` — L17175
- `step10_deliver` — L17202

---

### 主流程
Range: **L17656 – L17840** (185 lines)

**Functions:**
- `_print_execution_plan` — L17657
- `main` — L17705

---
