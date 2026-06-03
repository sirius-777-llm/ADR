# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (19987 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-2292 (2171 lines · 64 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L2293-4912 (2620 lines · 33 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L4913-6044 (1132 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L6045-6596 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L6597-11198 (4602 lines · 103 fn · 7 sub)
- [`第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）`](#第-6-5-步-动态化-hads-vads-默认-on---no-motion-关) — L11199-16386 (5188 lines · 109 fn · 5 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L16387-16646 (260 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L16647-17605 (959 lines · 10 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L17606-17896 (291 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L17897-19759 (1863 lines · 19 fn · 6 sub)
- [`主流程`](#主流程) — L19760-19987 (228 lines · 3 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L2292** (2171 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L324-453 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L454-1195 (742 lines)
- _工具函数_ — L1196-1637 (442 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1638-2292 (655 lines)

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
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1561
- `_LLM_TIER` — L1818
- `_TOPIC_MODIFIERS` — L2045
- `_TONE_PANTONE_OVERRIDE` — L2062

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
- `_is_transient_workflow_error` — L1517
- `_is_llm_rate_limited_error` — L1541
- `_inject_image2_quality_suffix` — L1569
- `submit_text_to_image` — L1583
- `req_post` — L1619
- `req_get` — L1633
- `_tg_probe_send` — L1641
- `_tg_probe_delete` — L1661
- `_tg_upload_with_probe_gap` — L1674
- `poll` — L1714
- `poll_podcast` — L1739
- `poll_task_status` — L1761
- `poll_storyboard_task` — L1783
- `tier_chat` — L1826
- `chat` — L1832
- `pick_image_model` — L1891
- `detect_topic_meta` — L1916
- `_topic_culture_guard` — L1966
- `_write_cultural_visual_qa` — L1992
- `is_1919_global_topic` — L2039
- `_strip_topic_modifiers` — L2050
- `apply_1919_global_guardrails` — L2068
- `build_1919_global_cover_prompt` — L2097
- `_shot_blueprint_enums` — L2129
- `build_shot_blueprint` — L2205
- `ffprobe_duration` — L2231
- `ffprobe_video_size` — L2242
- `_video_decode_probe` — L2263
- `ffmpeg` — L2281

---

### 第一步：双导演生成剧本
Range: **L2293 – L4912** (2620 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L3906-4912 (1007 lines)

**Top-level constants:**
- `_ENSEMBLE_CAP_BY_ROUTE` — L2445

**Functions:**
- `_extract_json_array` — L2294
- `_extract_json_object` — L2304
- `_voice_for_speaker` — L2314
- `_adsd_gender_from_voice` — L2350
- `_adsd_infer_gender_from_speaker` — L2358
- `_adsd_gender_lock_phrase` — L2367
- `_adsd_visual_subject_has_gender_conflict` — L2382
- `_adsd_default_roles` — L2394
- `_adsd_allows_media_role` — L2399
- `_adsd_role_candidates` — L2407
- `_adsd_dialogue_shape` — L2434
- `_ensemble_speaker_cap` — L2456
- `_ip_voice_asset_for_speaker` — L2469
- `_finalize_adsd_turns` — L2493
- `_parse_adsd_override_turns` — L2539
- `_parse_timecode_seconds` — L2632
- `_clean_override_line_text` — L2641
- `_parse_override_script_text` — L2647
- `_adsd_pov_contract` — L2681
- `_load_audit_blacklist_block` — L2694
- `_generate_adsd_dialogue_turns` — L2732
- `_broll_rhythm_reviewer` — L3159
- `_sweep_speaker_field` — L3266
- `_should_run_immersion_qa` — L3326
- `_adsd_immersion_qa_rewrite_turns` — L3349
- `_adsd_visual_contract` — L3413
- `_parse_risk_score` — L3465
- `_check_high_risk_hard_abort` — L3494
- `_maybe_neutralize_topic` — L3521
- `_apply_render_budget_scene_cap` — L3560
- `_apply_llm_mode_decision` — L3587
- `step1_script` — L3642
- `_write_ads_retention_qa` — L4856

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L4913 – L6044** (1132 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L4988
- `_ADSD_POLICY_REWRITE_TERMS` — L4994
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L5085

**Functions:**
- `_openai_tts_fallback` — L4914
- `_edge_tts_fallback` — L4960
- `_sanitize_for_external_api` — L5003
- `_is_content_policy_error` — L5012
- `_rewrite_adsd_tts_text_for_policy` — L5026
- `_record_adsd_tts_rewrite` — L5066
- `_build_silence_mp3` — L5091
- `_audio_duration_seconds` — L5104
- `_text_to_audio_master_voice_timed` — L5116
- `_text_to_audio_master_voice` — L5241
- `step2_master_voice` — L5354
- `_tts_turn_to_audio` — L5482
- `_asr_verify_dialogue_audio` — L5546
- `_asr_verify_dialogue_turns` — L5608
- `_normalize_cn_number_token` — L5650
- `_compact_zh_text` — L5672
- `_write_adsd_asr_text_qa` — L5679
- `_write_adsd_speaker_focus_qa` — L5718
- `_write_adsd_gender_voice_qa` — L5778
- `step2_dialogue_voice` — L5831

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L6045 – L6596** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L6052-6174 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L6175-6209 (35 lines)
- _第二层：字符数插值_ — L6210-6234 (25 lines)
- _第三层：silencedetect 物理校准_ — L6235-6596 (362 lines)

**Functions:**
- `_detect_silences` — L6053
- `_calibrate_boundaries` — L6088
- `_enforce_monotonic` — L6122
- `_manual_override_segments` — L6134
- `_calc_sentence_boundaries` — L6155
- `step345_timeline` — L6266
- `_analyze_bgm_energy_cuts` — L6325
- `_snap_bgm_only_boundaries` — L6388
- `step345_bgm_only_timeline` — L6448

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L6597 – L11198** (4602 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L7819-7869 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L7870-8718 (849 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L8719-9153 (435 lines)
- _Speaker IP Card (2026-05-21)_ — L9154-10798 (1645 lines)
- _B68 (2026-05-30) WERYDANCE 段长合规 gate_ — L10799-11031 (233 lines)
- _审批流程_ — L11032-11088 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L11089-11198 (110 lines)

**Top-level constants:**
- `_CORE_TERMS_STOP_WORDS` — L6992
- `CHARACTER_META_GRID_COSTUMES` — L7825
- `CHARACTER_META_GRID_POSES` — L7826
- `CHARACTER_META_GRID_SCENES` — L7827
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L7830
- `_SFX_TYPE_ENUM` — L8198
- `_SFX_INTENSITY_ENUM` — L8203
- `_SFX_POSITION_ENUM` — L8204
- `_GRAIN_LEVEL_ENUM` — L8349

**Functions:**
- `_extract_img_url` — L6598
- `_extract_img_urls` — L6620
- `_extract_video_url` — L6653
- `_count_bands` — L6678
- `_detect_contact_sheet_like_image` — L6690
- `_file_sha256` — L6751
- `_load_upload_cache` — L6764
- `_save_upload_cache` — L6773
- `_cached_upload_url` — L6781
- `_store_upload_url` — L6798
- `_guess_upload_mime` — L6808
- `_upload_to_weryai` — L6831
- `_send_for_approval` — L6885
- `_wait_approval` — L6949
- `_render_still_segment` — L6961
- `_extract_core_terms` — L6998
- `_scene_text_visual_alignment` — L7017
- `_write_text_visual_alignment_qa` — L7038
- `_scene_motion_action_plan` — L7061
- `_ensure_motion_action_plan` — L7115
- `_motion_action_block` — L7124
- `_motion_plan_for_qa` — L7152
- `_write_motion_action_plan_qa` — L7162
- `_write_motion_bridge_refs_qa` — L7192
- `_motion_bridge_ref_prompt` — L7199
- `generate_motion_bridge_refs_gpt_image2` — L7232
- `generate_image` — L7347
- `generate_storyboard_images_gpt_image2` — L7394
- `_storyboard_grid_aspect` — L7580
- `_storyboard_grid_cols_rows` — L7587
- `_storyboard_grid_prompt` — L7609
- `_storyboard_grid_prompt_limit` — L7667
- `_is_prompt_limit_response` — L7671
- `_production_storyboard_prompt` — L7677
- `_write_production_storyboard_page_qa` — L7711
- `_character_sheet_prompt` — L7721
- `_is_audit_blocked` — L7847
- `_paraphrase_sensitive_dialogue` — L7860
- `_topic_cache_dir` — L7874
- `_topic_cache_path` — L7880
- `_load_topic_decomposition_cache` — L7893
- `_save_topic_decomposition_cache` — L7911
- `_briefs_dir` — L7948
- `_brief_path` — L7954
- `_empty_brief` — L7959
- `_deep_merge_brief_skeleton` — L7999
- `_load_brief` — L8013
- `_save_brief` — L8037
- `_brief_get` — L8056
- `_brief_field` — L8068
- `_brief_set` — L8079
- `_brief_claim` — L8095
- `_brief_agent_status` — L8138
- `_brief_from_topic_decomposition` — L8151
- `_rule_based_sfx_design` — L8207
- `_validate_sfx_entry` — L8258
- `_audio_director_design` — L8296
- `_hex_color_validate` — L8352
- `_rule_based_art_design` — L8364
- `_validate_art_design` — L8445
- `_art_director_design` — L8483
- `_coordinator_review` — L8505
- `_llm_topic_decomposition` — L8606
- `_director_route_block` — L8772
- `_llm_infer_meta_grid_template` — L8842
- `_resolve_meta_grid_template` — L8899
- `_infer_meta_grid_costume` — L8942
- `_infer_meta_grid_pose` — L8991
- `_adsd_meta_grid_call_prompt` — L9038
- `_meta_grid_panel_index` — L9080
- `_migrate_speaker_ip` — L9160
- `_speaker_ips_dir` — L9185
- `_list_speaker_ips` — L9192
- `_match_speaker_ip` — L9206
- `_build_speaker_ip_context_for_script` — L9226
- `_ip_usage_stats` — L9282
- `_recommend_related_ips` — L9300
- `_save_speaker_ip` — L9325
- `_record_speaker_usage_history` — L9334
- `_format_speaker_usage_history_for_prompt` — L9381
- `_llm_infer_ip_skeleton` — L9399
- `_llm_pick_voice_asset_for_ip` — L9444
- `_auto_incubate_missing_ips` — L9493
- `_character_meta_grid_cache_dir` — L9577
- `_character_meta_grid_cache_path` — L9585
- `_character_meta_grid_cache_legacy_path` — L9593
- `_character_meta_grid_path` — L9600
- `generate_character_meta_grid_gpt_image2` — L9606
- `_generate_all_character_meta_grids` — L9778
- `_write_character_sheet_qa` — L9819
- `generate_character_sheet_gpt_image2` — L9829
- `generate_production_storyboard_page_gpt_image2` — L9929
- `_qa_clean_storyboard_panel` — L9992
- `_crop_storyboard_grid_panels` — L10173
- `generate_storyboard_grid_gpt_image2` — L10220
- `_gpt_image2_direct_annotated_aspect` — L10452
- `_gpt_image2_direct_annotated_prompt` — L10459
- `generate_gpt_image2_direct_annotated_storyboards` — L10489
- `_llm_bgm_description` — L10590
- `_bgm_contains_vocals` — L10629
- `generate_bgm` — L10663
- `_b68_clamp_scene_durations_to_werydance_bounds` — L10807
- `step6_parallel` — L10867

---

### 第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）
Range: **L11199 – L16386** (5188 lines)

**Sub-sections:**
- _PR-A (2026-05-27): merged_a 合并跑 helpers_ — L14527-16121 (1595 lines)
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L16122-16164 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L16165-16202 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回时间轴锚定音轨_ — L16203-16341 (139 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L16342-16386 (45 lines)

**Top-level constants:**
- `_PR3B1_SHOT_TYPE_ENUM` — L11669
- `_PR3B1_CAMERA_ANGLE_ENUM` — L11673
- `_PR3B1_LIGHTING_ENUM` — L11678
- `_PR3B1_CAMERA_MOTION_ENUM` — L11683
- `_EMOTION_NARRATION_STYLE_MAP` — L12735

**Functions:**
- `_generate_motion_prompts` — L11202
- `_motion_tasks_file` — L11269
- `_motion_qa_file` — L11273
- `_append_motion_qa` — L11277
- `_finalize_motion_qa` — L11301
- `_lip_sync_tasks_file` — L11385
- `_load_motion_tasks` — L11389
- `_save_motion_task` — L11399
- `_remove_motion_task` — L11407
- `_load_lip_sync_tasks` — L11414
- `_save_lip_sync_task` — L11424
- `_remove_lip_sync_task` — L11431
- `_video_visual_motion_qa` — L11438
- `_motion_output_qa` — L11510
- `_has_audio_stream` — L11555
- `_normalize_motion_video` — L11566
- `_motion_poll_and_download` — L11616
- `_validate_enum_field` — L11689
- `_build_motion_video_prompt` — L11704
- `_short_board_text` — L11754
- `_wrap_board_text` — L11761
- `_storyboard_font` — L11792
- `_draw_storyboard_arrow` — L11807
- `_build_annotated_storyboard_reference` — L11821
- `_plain_caption_text` — L11922
- `_werydance_caption_request` — L11930
- `_werydance_caption_instruction` — L11957
- `_werydance_negative_prompt` — L11969
- `_motion_reference_prompt` — L11987
- `_motion_audio_dub_prompt` — L12010
- `_motion_audio_dub_poll_and_download` — L12044
- `_try_motion_audio_dub_video` — L12109
- `_try_motion_reference_video` — L12272
- `_motion_one_scene` — L12388
- `_grid_multiref_tasks_file` — L12518
- `_previs_page_tasks_file` — L12522
- `_load_grid_multiref_tasks` — L12526
- `_load_previs_page_tasks` — L12536
- `_save_grid_multiref_task` — L12546
- `_save_previs_page_task` — L12553
- `_remove_grid_multiref_task` — L12560
- `_remove_previs_page_task` — L12567
- `_poll_video_task_download` — L12574
- `_grid_multiref_group_size` — L12623
- `_grid_multiref_adaptive_group_size` — L12633
- `_grid_multiref_duration` — L12657
- `_grid_multiref_tts_buffer_factor` — L12695
- `_grid_multiref_tts_duration_buffered` — L12709
- `_grid_multiref_segment_max_stretch` — L12725
- `_voice_clone_emotion_style` — L12759
- `_grid_multiref_prompt` — L12782
- `_write_grid_multiref_motion_qa` — L12856
- `_write_previs_page_motion_qa` — L12866
- `_write_storyboard_trailer_qa` — L12876
- `_write_character_trailer_qa` — L12886
- `_write_grid_multiref_segment_qa` — L12896
- `_motion_compare_record` — L12906
- `_write_storyboard_motion_compare_qa` — L12928
- `_scene_segment_duration` — L12964
- `_apply_grid_multiref_segments` — L12983
- `_previs_page_duration` — L13188
- `_previs_page_group_prompt` — L13199
- `_previs_page_groups` — L13225
- `_storyboard_trailer_duration` — L13240
- `_storyboard_trailer_prompt` — L13250
- `_character_trailer_max_shots` — L13278
- `_character_trailer_shot_duration` — L13286
- `_character_trailer_prompt` — L13302
- `_concat_character_trailer_segments` — L13317
- `_generate_character_trailer_motion` — L13356
- `_multi_trailer_prompt_for_group` — L13464
- `_generate_multi_trailer_segments` — L13487
- `_generate_storyboard_trailer_motion` — L13598
- `_generate_previs_page_motion_segments` — L13673
- `_generate_grid_multiref_motion_segments` — L13785
- `_grid_multiref_concat_groups` — L14095
- `_grid_multiref_concat_groups_partial` — L14112
- `_grid_multiref_concat_paths` — L14130
- `_lip_sync_slot_duration` — L14172
- `_adsd_lip_sync_prompt` — L14179
- `_adsd_broll_motion_prompt` — L14225
- `_adsd_action_b_motion_prompt` — L14267
- `_adsd_silent_b_motion_prompt` — L14313
- `_adsd_narrated_b_audio_dub_prompt` — L14348
- `_adsd_almighty_audio_dub_prompt` — L14392
- `_postprocess_lip_sync_segment` — L14433
- `_detect_audio_leading_silence` — L14505
- `_concat_audio_files_for_group` — L14530
- `_split_lip_sync_raw_by_durations` — L14553
- `_postprocess_audio_dub_segment` — L14588
- `_lips_change_repair_segment` — L14716
- `_load_lips_change_requested_turns` — L14801
- `_parse_turn_set` — L14818
- `_load_motion_voice_repair_turns` — L14840
- `_voice_assets_file` — L14852
- `_load_voice_assets` — L14859
- `_build_combined_voice_reference` — L14878
- `_select_voice_asset_reference` — L14920
- `_lip_sync_poll_download_and_process` — L14996
- `_lip_sync_one_group` — L15064
- `_lip_sync_one_scene` — L15272
- `step66_adsd_lip_sync` — L15596
- `step65_motion` — L15941
- `step65_grid_multiref_motion_qa` — L16094
- `_sanitize_scene_for_state` — L16123
- `_save_pipeline_state` — L16142
- `_retime_after_audio_dub` — L16166
- `_build_voice_clone_hybrid_audio` — L16204
- `_build_dynamic_bgm` — L16343

---

### 第七步：拼接视频轨
Range: **L16387 – L16646** (260 lines)

**Functions:**
- `step7_concat` — L16388

---

### 第八步：生成 ASS 字幕
Range: **L16647 – L17605** (959 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L16926-17605 (680 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L16648
- `_word_timings_for_subtitle_align` — L16674
- `_align_segments_via_asr` — L16715
- `_b61_1_asr_turn_boundaries` — L16758
- `step8_subtitles` — L16820
- `_read_output_json` — L17326
- `_qa_file_pass` — L17337
- `_ass_has_dialogue` — L17344
- `_write_adsd_delivery_qa` — L17354
- `_write_bgm_only_qa` — L17494

---

### 第九步：最终合成
Range: **L17606 – L17896** (291 lines)

**Functions:**
- `step9_render` — L17607

---

### 第十步：推送 Telegram
Range: **L17897 – L19759** (1863 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L19003-19112 (110 lines)
- _B70 (2026-05-30) TG oversize policy helpers_ — L19113-19566 (454 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L19567-19571 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L19572-19635 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L19636-19681 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L19682-19759 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L18266
- `PANTONE_FALLBACK` — L18293
- `FESTIVAL_DATE_TAG` — L18407

**Functions:**
- `_generate_caption` — L17898
- `_overlay_title_on_cover` — L18136
- `_prepare_tg_photo` — L18246
- `_get_pantone_for_date` — L18296
- `_llm_bottom_note` — L18321
- `_get_bottom_note` — L18351
- `_get_date_tag` — L18429
- `_shrink_to_b64` — L18451
- `_llm_check_scenes_anomalies` — L18467
- `_llm_check_cover_unique` — L18520
- `_llm_check_cover_quality` — L18550
- `_try_almanac_cover` — L18592
- `_generate_cover_image` — L18763
- `_async_kickoff_cover_caption` — L19010
- `_await_async_cover_caption` — L19086
- `_b70_env_float` — L19116
- `_b70_split_and_deliver` — L19131
- `_b70_send_document_first` — L19231
- `step10_deliver` — L19268

---

### 主流程
Range: **L19760 – L19987** (228 lines)

**Functions:**
- `_print_execution_plan` — L19761
- `_write_run_timings` — L19809
- `main` — L19838

---
