# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (17695 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-2031 (1910 lines · 59 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L2032-4320 (2289 lines · 30 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L4321-5452 (1132 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L5453-6004 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L6005-9787 (3783 lines · 82 fn · 6 sub)
- [`第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）`](#第-6-5-步-动态化-hads-vads-默认-on---no-motion-关) — L9788-14557 (4770 lines · 103 fn · 5 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L14558-14789 (232 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L14790-15592 (803 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L15593-15848 (256 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L15849-17510 (1662 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L17511-17695 (185 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L2031** (1910 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L324-453 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L454-1142 (689 lines)
- _工具函数_ — L1143-1492 (350 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1493-2031 (539 lines)

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
- `VOICE_ASSET_AUDIO_DUB_EXPERIMENT` — L883
- `VOICE_ASSET_AUDIO_DUB_PARTIAL_OK` — L891
- `MOTION_VISUAL_QA` — L895
- `MOTION_VOICE_REPAIR` — L903
- `MOTION_VOICE_STRICT_LOCK` — L908
- `WERYDANCE_CAPTIONS` — L913
- `ADSD_ONSITE_POV_MODE` — L925
- `ADSD_LIPS_CHANGE_REPAIR` — L930
- `ADSD_LIPS_CHANGE_ALL` — L935
- `ADS_REPORTER_MODE` — L946
- `ADS_STORYBOARD_FLOW_DEFAULT` — L963
- `ADS_RETENTION_MODE` — L977
- `ADSD_MODE_NAME` — L983
- `EMOTION_STYLE` — L1122
- `EMOTION_STYLE_BRIGHT` — L1134
- `_TG_DASHBOARD_STAGES` — L1156
- `_TG_NOISY_PATTERNS` — L1171
- `_TG_IMMEDIATE_PATTERNS` — L1189
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1422
- `_LLM_TIER` — L1667
- `_TOPIC_MODIFIERS` — L1863
- `_TONE_PANTONE_OVERRIDE` — L1880

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
- `log` — L1144
- `_tg_send_raw` — L1212
- `_tg_matches` — L1228
- `_tg_summarize` — L1232
- `_tg_dashboard_stage_for` — L1239
- `_tg_progress_bar` — L1247
- `_tg_dashboard_text` — L1253
- `_tg_dashboard_update` — L1271
- `_tg_maybe_digest` — L1308
- `tg` — L1323
- `_wait_image_submit_slot` — L1372
- `_wait_motion_submit_slot` — L1385
- `_is_rate_limited_error` — L1398
- `_is_rate_limited_response` — L1408
- `_inject_image2_quality_suffix` — L1430
- `submit_text_to_image` — L1444
- `req_post` — L1474
- `req_get` — L1488
- `_tg_probe_send` — L1496
- `_tg_probe_delete` — L1516
- `_tg_upload_with_probe_gap` — L1529
- `poll` — L1569
- `poll_podcast` — L1594
- `poll_task_status` — L1616
- `poll_storyboard_task` — L1638
- `tier_chat` — L1675
- `chat` — L1681
- `pick_image_model` — L1709
- `detect_topic_meta` — L1734
- `_topic_culture_guard` — L1784
- `_write_cultural_visual_qa` — L1810
- `is_1919_global_topic` — L1857
- `_strip_topic_modifiers` — L1868
- `apply_1919_global_guardrails` — L1886
- `build_1919_global_cover_prompt` — L1915
- `build_shot_blueprint` — L1944
- `ffprobe_duration` — L1970
- `ffprobe_video_size` — L1981
- `_video_decode_probe` — L2002
- `ffmpeg` — L2020

---

### 第一步：双导演生成剧本
Range: **L2032 – L4320** (2289 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L3496-4320 (825 lines)

**Top-level constants:**
- `_ENSEMBLE_CAP_BY_ROUTE` — L2180

**Functions:**
- `_extract_json_array` — L2033
- `_extract_json_object` — L2043
- `_voice_for_speaker` — L2053
- `_adsd_gender_from_voice` — L2089
- `_adsd_infer_gender_from_speaker` — L2097
- `_adsd_gender_lock_phrase` — L2106
- `_adsd_visual_subject_has_gender_conflict` — L2121
- `_adsd_default_roles` — L2133
- `_adsd_allows_media_role` — L2138
- `_adsd_role_candidates` — L2146
- `_adsd_dialogue_shape` — L2169
- `_ensemble_speaker_cap` — L2191
- `_finalize_adsd_turns` — L2204
- `_parse_adsd_override_turns` — L2238
- `_parse_timecode_seconds` — L2331
- `_clean_override_line_text` — L2340
- `_parse_override_script_text` — L2346
- `_adsd_pov_contract` — L2380
- `_load_audit_blacklist_block` — L2393
- `_generate_adsd_dialogue_turns` — L2431
- `_broll_rhythm_reviewer` — L2858
- `_sweep_speaker_field` — L2965
- `_should_run_immersion_qa` — L3025
- `_adsd_immersion_qa_rewrite_turns` — L3048
- `_adsd_visual_contract` — L3112
- `_parse_risk_score` — L3164
- `_check_high_risk_hard_abort` — L3193
- `_maybe_neutralize_topic` — L3220
- `step1_script` — L3259
- `_write_ads_retention_qa` — L4264

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L4321 – L5452** (1132 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L4396
- `_ADSD_POLICY_REWRITE_TERMS` — L4402
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L4493

**Functions:**
- `_openai_tts_fallback` — L4322
- `_edge_tts_fallback` — L4368
- `_sanitize_for_external_api` — L4411
- `_is_content_policy_error` — L4420
- `_rewrite_adsd_tts_text_for_policy` — L4434
- `_record_adsd_tts_rewrite` — L4474
- `_build_silence_mp3` — L4499
- `_audio_duration_seconds` — L4512
- `_text_to_audio_master_voice_timed` — L4524
- `_text_to_audio_master_voice` — L4649
- `step2_master_voice` — L4762
- `_tts_turn_to_audio` — L4890
- `_asr_verify_dialogue_audio` — L4954
- `_asr_verify_dialogue_turns` — L5016
- `_normalize_cn_number_token` — L5058
- `_compact_zh_text` — L5080
- `_write_adsd_asr_text_qa` — L5087
- `_write_adsd_speaker_focus_qa` — L5126
- `_write_adsd_gender_voice_qa` — L5186
- `step2_dialogue_voice` — L5239

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L5453 – L6004** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L5460-5582 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L5583-5617 (35 lines)
- _第二层：字符数插值_ — L5618-5642 (25 lines)
- _第三层：silencedetect 物理校准_ — L5643-6004 (362 lines)

**Functions:**
- `_detect_silences` — L5461
- `_calibrate_boundaries` — L5496
- `_enforce_monotonic` — L5530
- `_manual_override_segments` — L5542
- `_calc_sentence_boundaries` — L5563
- `step345_timeline` — L5674
- `_analyze_bgm_energy_cuts` — L5733
- `_snap_bgm_only_boundaries` — L5796
- `step345_bgm_only_timeline` — L5856

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L6005 – L9787** (3783 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L7206-7256 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L7257-7397 (141 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L7398-7832 (435 lines)
- _Speaker IP Card (2026-05-21)_ — L7833-9620 (1788 lines)
- _审批流程_ — L9621-9677 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L9678-9787 (110 lines)

**Top-level constants:**
- `_CORE_TERMS_STOP_WORDS` — L6400
- `CHARACTER_META_GRID_COSTUMES` — L7212
- `CHARACTER_META_GRID_POSES` — L7213
- `CHARACTER_META_GRID_SCENES` — L7214
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L7217

**Functions:**
- `_extract_img_url` — L6006
- `_extract_img_urls` — L6028
- `_extract_video_url` — L6061
- `_count_bands` — L6086
- `_detect_contact_sheet_like_image` — L6098
- `_file_sha256` — L6159
- `_load_upload_cache` — L6172
- `_save_upload_cache` — L6181
- `_cached_upload_url` — L6189
- `_store_upload_url` — L6206
- `_guess_upload_mime` — L6216
- `_upload_to_weryai` — L6239
- `_send_for_approval` — L6293
- `_wait_approval` — L6357
- `_render_still_segment` — L6369
- `_extract_core_terms` — L6406
- `_scene_text_visual_alignment` — L6425
- `_write_text_visual_alignment_qa` — L6446
- `_scene_motion_action_plan` — L6469
- `_ensure_motion_action_plan` — L6523
- `_motion_action_block` — L6532
- `_motion_plan_for_qa` — L6560
- `_write_motion_action_plan_qa` — L6570
- `_write_motion_bridge_refs_qa` — L6600
- `_motion_bridge_ref_prompt` — L6607
- `generate_motion_bridge_refs_gpt_image2` — L6640
- `generate_image` — L6755
- `generate_storyboard_images_gpt_image2` — L6802
- `_storyboard_grid_aspect` — L6987
- `_storyboard_grid_cols_rows` — L6994
- `_storyboard_grid_prompt` — L7016
- `_storyboard_grid_prompt_limit` — L7054
- `_is_prompt_limit_response` — L7058
- `_production_storyboard_prompt` — L7064
- `_write_production_storyboard_page_qa` — L7098
- `_character_sheet_prompt` — L7108
- `_is_audit_blocked` — L7234
- `_paraphrase_sensitive_dialogue` — L7247
- `_topic_cache_dir` — L7261
- `_topic_cache_path` — L7267
- `_load_topic_decomposition_cache` — L7280
- `_save_topic_decomposition_cache` — L7298
- `_llm_topic_decomposition` — L7304
- `_director_route_block` — L7451
- `_llm_infer_meta_grid_template` — L7521
- `_resolve_meta_grid_template` — L7578
- `_infer_meta_grid_costume` — L7621
- `_infer_meta_grid_pose` — L7670
- `_adsd_meta_grid_call_prompt` — L7717
- `_meta_grid_panel_index` — L7759
- `_migrate_speaker_ip` — L7839
- `_speaker_ips_dir` — L7864
- `_list_speaker_ips` — L7871
- `_match_speaker_ip` — L7885
- `_build_speaker_ip_context_for_script` — L7905
- `_ip_usage_stats` — L7961
- `_recommend_related_ips` — L7979
- `_save_speaker_ip` — L8004
- `_record_speaker_usage_history` — L8013
- `_format_speaker_usage_history_for_prompt` — L8060
- `_llm_infer_ip_skeleton` — L8078
- `_llm_pick_voice_asset_for_ip` — L8123
- `_auto_incubate_missing_ips` — L8171
- `_character_meta_grid_cache_dir` — L8255
- `_character_meta_grid_cache_path` — L8263
- `_character_meta_grid_cache_legacy_path` — L8271
- `_character_meta_grid_path` — L8278
- `generate_character_meta_grid_gpt_image2` — L8284
- `_generate_all_character_meta_grids` — L8456
- `_write_character_sheet_qa` — L8497
- `generate_character_sheet_gpt_image2` — L8507
- `generate_production_storyboard_page_gpt_image2` — L8607
- `_qa_clean_storyboard_panel` — L8670
- `_crop_storyboard_grid_panels` — L8851
- `generate_storyboard_grid_gpt_image2` — L8898
- `_gpt_image2_direct_annotated_aspect` — L9129
- `_gpt_image2_direct_annotated_prompt` — L9136
- `generate_gpt_image2_direct_annotated_storyboards` — L9166
- `_llm_bgm_description` — L9267
- `_bgm_contains_vocals` — L9306
- `generate_bgm` — L9340
- `step6_parallel` — L9457

---

### 第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）
Range: **L9788 – L14557** (4770 lines)

**Sub-sections:**
- _PR-A (2026-05-27): merged_a 合并跑 helpers_ — L12819-14292 (1474 lines)
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L14293-14335 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L14336-14373 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回时间轴锚定音轨_ — L14374-14512 (139 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L14513-14557 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L9791
- `_motion_tasks_file` — L9858
- `_motion_qa_file` — L9862
- `_append_motion_qa` — L9866
- `_finalize_motion_qa` — L9890
- `_lip_sync_tasks_file` — L9974
- `_load_motion_tasks` — L9978
- `_save_motion_task` — L9988
- `_remove_motion_task` — L9996
- `_load_lip_sync_tasks` — L10003
- `_save_lip_sync_task` — L10013
- `_remove_lip_sync_task` — L10020
- `_video_visual_motion_qa` — L10027
- `_motion_output_qa` — L10099
- `_has_audio_stream` — L10144
- `_normalize_motion_video` — L10155
- `_motion_poll_and_download` — L10205
- `_build_motion_video_prompt` — L10256
- `_short_board_text` — L10286
- `_wrap_board_text` — L10293
- `_storyboard_font` — L10324
- `_draw_storyboard_arrow` — L10339
- `_build_annotated_storyboard_reference` — L10353
- `_plain_caption_text` — L10454
- `_werydance_caption_request` — L10462
- `_werydance_caption_instruction` — L10489
- `_werydance_negative_prompt` — L10501
- `_motion_reference_prompt` — L10519
- `_motion_audio_dub_prompt` — L10542
- `_motion_audio_dub_poll_and_download` — L10576
- `_try_motion_audio_dub_video` — L10641
- `_try_motion_reference_video` — L10804
- `_motion_one_scene` — L10920
- `_grid_multiref_tasks_file` — L11049
- `_previs_page_tasks_file` — L11053
- `_load_grid_multiref_tasks` — L11057
- `_load_previs_page_tasks` — L11067
- `_save_grid_multiref_task` — L11077
- `_save_previs_page_task` — L11084
- `_remove_grid_multiref_task` — L11091
- `_remove_previs_page_task` — L11098
- `_poll_video_task_download` — L11105
- `_grid_multiref_group_size` — L11154
- `_grid_multiref_duration` — L11164
- `_grid_multiref_segment_max_stretch` — L11186
- `_grid_multiref_prompt` — L11194
- `_write_grid_multiref_motion_qa` — L11247
- `_write_previs_page_motion_qa` — L11257
- `_write_storyboard_trailer_qa` — L11267
- `_write_character_trailer_qa` — L11277
- `_write_grid_multiref_segment_qa` — L11287
- `_motion_compare_record` — L11297
- `_write_storyboard_motion_compare_qa` — L11319
- `_scene_segment_duration` — L11355
- `_apply_grid_multiref_segments` — L11374
- `_previs_page_duration` — L11579
- `_previs_page_group_prompt` — L11589
- `_previs_page_groups` — L11615
- `_storyboard_trailer_duration` — L11630
- `_storyboard_trailer_prompt` — L11640
- `_character_trailer_max_shots` — L11668
- `_character_trailer_shot_duration` — L11676
- `_character_trailer_prompt` — L11690
- `_concat_character_trailer_segments` — L11705
- `_generate_character_trailer_motion` — L11744
- `_multi_trailer_prompt_for_group` — L11852
- `_generate_multi_trailer_segments` — L11875
- `_generate_storyboard_trailer_motion` — L11986
- `_generate_previs_page_motion_segments` — L12061
- `_generate_grid_multiref_motion_segments` — L12173
- `_grid_multiref_concat_groups` — L12387
- `_grid_multiref_concat_groups_partial` — L12404
- `_grid_multiref_concat_paths` — L12422
- `_lip_sync_slot_duration` — L12464
- `_adsd_lip_sync_prompt` — L12471
- `_adsd_broll_motion_prompt` — L12517
- `_adsd_action_b_motion_prompt` — L12559
- `_adsd_silent_b_motion_prompt` — L12605
- `_adsd_narrated_b_audio_dub_prompt` — L12640
- `_adsd_almighty_audio_dub_prompt` — L12684
- `_postprocess_lip_sync_segment` — L12725
- `_detect_audio_leading_silence` — L12797
- `_concat_audio_files_for_group` — L12822
- `_split_lip_sync_raw_by_durations` — L12845
- `_postprocess_audio_dub_segment` — L12880
- `_lips_change_repair_segment` — L12995
- `_load_lips_change_requested_turns` — L13080
- `_parse_turn_set` — L13097
- `_load_motion_voice_repair_turns` — L13119
- `_voice_assets_file` — L13131
- `_load_voice_assets` — L13138
- `_select_voice_asset_reference` — L13157
- `_lip_sync_poll_download_and_process` — L13223
- `_lip_sync_one_group` — L13291
- `_lip_sync_one_scene` — L13468
- `step66_adsd_lip_sync` — L13792
- `step65_motion` — L14113
- `step65_grid_multiref_motion_qa` — L14265
- `_sanitize_scene_for_state` — L14294
- `_save_pipeline_state` — L14313
- `_retime_after_audio_dub` — L14337
- `_build_voice_clone_hybrid_audio` — L14375
- `_build_dynamic_bgm` — L14514

---

### 第七步：拼接视频轨
Range: **L14558 – L14789** (232 lines)

**Functions:**
- `step7_concat` — L14559

---

### 第八步：生成 ASS 字幕
Range: **L14790 – L15592** (803 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L14913-15592 (680 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L14791
- `_word_timings_for_subtitle_align` — L14817
- `_align_segments_via_asr` — L14858
- `step8_subtitles` — L14901
- `_read_output_json` — L15313
- `_qa_file_pass` — L15324
- `_ass_has_dialogue` — L15331
- `_write_adsd_delivery_qa` — L15341
- `_write_bgm_only_qa` — L15481

---

### 第九步：最终合成
Range: **L15593 – L15848** (256 lines)

**Functions:**
- `step9_render` — L15594

---

### 第十步：推送 Telegram
Range: **L15849 – L17510** (1662 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L16949-17317 (369 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L17318-17322 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L17323-17386 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L17387-17432 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L17433-17510 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L16218
- `PANTONE_FALLBACK` — L16245
- `FESTIVAL_DATE_TAG` — L16358

**Functions:**
- `_generate_caption` — L15850
- `_overlay_title_on_cover` — L16088
- `_prepare_tg_photo` — L16198
- `_get_pantone_for_date` — L16248
- `_llm_bottom_note` — L16273
- `_get_bottom_note` — L16302
- `_get_date_tag` — L16380
- `_shrink_to_b64` — L16402
- `_llm_check_scenes_anomalies` — L16418
- `_llm_check_cover_unique` — L16471
- `_llm_check_cover_quality` — L16501
- `_try_almanac_cover` — L16543
- `_generate_cover_image` — L16714
- `_async_kickoff_cover_caption` — L16956
- `_await_async_cover_caption` — L17030
- `step10_deliver` — L17057

---

### 主流程
Range: **L17511 – L17695** (185 lines)

**Functions:**
- `_print_execution_plan` — L17512
- `main` — L17560

---
