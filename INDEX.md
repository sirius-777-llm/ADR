# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (20411 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-2489 (2368 lines · 73 fn · 5 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L2490-5142 (2653 lines · 33 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L5143-6375 (1233 lines · 22 fn · 2 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L6376-6927 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L6928-11546 (4619 lines · 103 fn · 7 sub)
- [`第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）`](#第-6-5-步-动态化-hads-vads-默认-on---no-motion-关) — L11547-16734 (5188 lines · 109 fn · 5 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L16735-17070 (336 lines · 3 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L17071-18029 (959 lines · 10 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L18030-18320 (291 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L18321-20183 (1863 lines · 19 fn · 6 sub)
- [`主流程`](#主流程) — L20184-20411 (228 lines · 3 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L2489** (2368 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L324-453 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L454-1195 (742 lines)
- _工具函数_ — L1196-1571 (376 lines)
- _B87 纹理档系统：LLM 提名 + 代码护栏 + 确定性渲染_ — L1572-1834 (263 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1835-2489 (655 lines)

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
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1565
- `_TEXTURE_MODE_ENUM` — L1573
- `_TEXTURE_SUFFIX_MAP` — L1578
- `_TEXTURE_BODY_DIRECTIVE` — L1605
- `_TEXTURE_SCENE_PHRASE` — L1612
- `_TEXTURE_GRID_PHRASE` — L1619
- `_TEXTURE_MOTION_PHRASE` — L1627
- `_LLM_TIER` — L2015
- `_TOPIC_MODIFIERS` — L2242
- `_TONE_PANTONE_OVERRIDE` — L2259

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
- `_era_is_pre_photographic` — L1639
- `_texture_mode_fallback` — L1667
- `_texture_guardrail` — L1688
- `_set_active_texture_profile` — L1727
- `_active_texture_suffix` — L1740
- `_active_texture_body_directive` — L1744
- `_active_texture_scene_phrase` — L1748
- `_active_texture_grid_phrase` — L1752
- `_active_texture_motion_phrase` — L1756
- `_inject_image2_quality_suffix` — L1760
- `submit_text_to_image` — L1780
- `req_post` — L1816
- `req_get` — L1830
- `_tg_probe_send` — L1838
- `_tg_probe_delete` — L1858
- `_tg_upload_with_probe_gap` — L1871
- `poll` — L1911
- `poll_podcast` — L1936
- `poll_task_status` — L1958
- `poll_storyboard_task` — L1980
- `tier_chat` — L2023
- `chat` — L2029
- `pick_image_model` — L2088
- `detect_topic_meta` — L2113
- `_topic_culture_guard` — L2163
- `_write_cultural_visual_qa` — L2189
- `is_1919_global_topic` — L2236
- `_strip_topic_modifiers` — L2247
- `apply_1919_global_guardrails` — L2265
- `build_1919_global_cover_prompt` — L2294
- `_shot_blueprint_enums` — L2326
- `build_shot_blueprint` — L2402
- `ffprobe_duration` — L2428
- `ffprobe_video_size` — L2439
- `_video_decode_probe` — L2460
- `ffmpeg` — L2478

---

### 第一步：双导演生成剧本
Range: **L2490 – L5142** (2653 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L4122-5142 (1021 lines)

**Top-level constants:**
- `_ENSEMBLE_CAP_BY_ROUTE` — L2642

**Functions:**
- `_extract_json_array` — L2491
- `_extract_json_object` — L2501
- `_voice_for_speaker` — L2511
- `_adsd_gender_from_voice` — L2547
- `_adsd_infer_gender_from_speaker` — L2555
- `_adsd_gender_lock_phrase` — L2564
- `_adsd_visual_subject_has_gender_conflict` — L2579
- `_adsd_default_roles` — L2591
- `_adsd_allows_media_role` — L2596
- `_adsd_role_candidates` — L2604
- `_adsd_dialogue_shape` — L2631
- `_ensemble_speaker_cap` — L2653
- `_ip_voice_asset_for_speaker` — L2666
- `_finalize_adsd_turns` — L2690
- `_parse_adsd_override_turns` — L2736
- `_parse_timecode_seconds` — L2829
- `_clean_override_line_text` — L2838
- `_parse_override_script_text` — L2844
- `_adsd_pov_contract` — L2878
- `_load_audit_blacklist_block` — L2891
- `_generate_adsd_dialogue_turns` — L2929
- `_broll_rhythm_reviewer` — L3356
- `_sweep_speaker_field` — L3463
- `_should_run_immersion_qa` — L3523
- `_adsd_immersion_qa_rewrite_turns` — L3546
- `_adsd_visual_contract` — L3610
- `_parse_risk_score` — L3662
- `_check_high_risk_hard_abort` — L3691
- `_maybe_neutralize_topic` — L3718
- `_apply_render_budget_scene_cap` — L3757
- `_apply_llm_mode_decision` — L3784
- `step1_script` — L3839
- `_write_ads_retention_qa` — L5086

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L5143 – L6375** (1233 lines)

**Sub-sections:**
- _B88: 内容审核(1002) → 分级软化 → 中性兜底句 → 静音 backstop，绝不崩管线_ — L5838-5866 (29 lines)
- _非内容审核(网络/transient): 有限退避重试，耗尽才抛_ — L5867-6375 (509 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L5218
- `_ADSD_POLICY_REWRITE_TERMS` — L5224
- `_TTS_SAFE_FALLBACK_LINE` — L5325
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L5393

**Functions:**
- `_openai_tts_fallback` — L5144
- `_edge_tts_fallback` — L5190
- `_sanitize_for_external_api` — L5249
- `_is_content_policy_error` — L5258
- `_rewrite_adsd_tts_text_for_policy` — L5272
- `_tts_safe_fallback_line` — L5334
- `_tts_silent_placeholder` — L5339
- `_record_adsd_tts_rewrite` — L5374
- `_build_silence_mp3` — L5399
- `_audio_duration_seconds` — L5412
- `_text_to_audio_master_voice_timed` — L5424
- `_text_to_audio_master_voice` — L5549
- `step2_master_voice` — L5662
- `_tts_turn_to_audio` — L5790
- `_asr_verify_dialogue_audio` — L5877
- `_asr_verify_dialogue_turns` — L5939
- `_normalize_cn_number_token` — L5981
- `_compact_zh_text` — L6003
- `_write_adsd_asr_text_qa` — L6010
- `_write_adsd_speaker_focus_qa` — L6049
- `_write_adsd_gender_voice_qa` — L6109
- `step2_dialogue_voice` — L6162

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L6376 – L6927** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L6383-6505 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L6506-6540 (35 lines)
- _第二层：字符数插值_ — L6541-6565 (25 lines)
- _第三层：silencedetect 物理校准_ — L6566-6927 (362 lines)

**Functions:**
- `_detect_silences` — L6384
- `_calibrate_boundaries` — L6419
- `_enforce_monotonic` — L6453
- `_manual_override_segments` — L6465
- `_calc_sentence_boundaries` — L6486
- `step345_timeline` — L6597
- `_analyze_bgm_energy_cuts` — L6656
- `_snap_bgm_only_boundaries` — L6719
- `step345_bgm_only_timeline` — L6779

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L6928 – L11546** (4619 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L8157-8207 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L8208-9064 (857 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L9065-9501 (437 lines)
- _Speaker IP Card (2026-05-21)_ — L9502-11146 (1645 lines)
- _B68 (2026-05-30) WERYDANCE 段长合规 gate_ — L11147-11379 (233 lines)
- _审批流程_ — L11380-11436 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L11437-11546 (110 lines)

**Top-level constants:**
- `_CORE_TERMS_STOP_WORDS` — L7330
- `CHARACTER_META_GRID_COSTUMES` — L8163
- `CHARACTER_META_GRID_POSES` — L8164
- `CHARACTER_META_GRID_SCENES` — L8165
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L8168
- `_SFX_TYPE_ENUM` — L8536
- `_SFX_INTENSITY_ENUM` — L8541
- `_SFX_POSITION_ENUM` — L8542
- `_GRAIN_LEVEL_ENUM` — L8687

**Functions:**
- `_extract_img_url` — L6929
- `_extract_img_urls` — L6951
- `_extract_video_url` — L6984
- `_count_bands` — L7009
- `_detect_contact_sheet_like_image` — L7021
- `_file_sha256` — L7082
- `_load_upload_cache` — L7095
- `_save_upload_cache` — L7104
- `_cached_upload_url` — L7112
- `_store_upload_url` — L7129
- `_guess_upload_mime` — L7139
- `_upload_to_weryai` — L7162
- `_send_for_approval` — L7223
- `_wait_approval` — L7287
- `_render_still_segment` — L7299
- `_extract_core_terms` — L7336
- `_scene_text_visual_alignment` — L7355
- `_write_text_visual_alignment_qa` — L7376
- `_scene_motion_action_plan` — L7399
- `_ensure_motion_action_plan` — L7453
- `_motion_action_block` — L7462
- `_motion_plan_for_qa` — L7490
- `_write_motion_action_plan_qa` — L7500
- `_write_motion_bridge_refs_qa` — L7530
- `_motion_bridge_ref_prompt` — L7537
- `generate_motion_bridge_refs_gpt_image2` — L7570
- `generate_image` — L7685
- `generate_storyboard_images_gpt_image2` — L7732
- `_storyboard_grid_aspect` — L7918
- `_storyboard_grid_cols_rows` — L7925
- `_storyboard_grid_prompt` — L7947
- `_storyboard_grid_prompt_limit` — L8005
- `_is_prompt_limit_response` — L8009
- `_production_storyboard_prompt` — L8015
- `_write_production_storyboard_page_qa` — L8049
- `_character_sheet_prompt` — L8059
- `_is_audit_blocked` — L8185
- `_paraphrase_sensitive_dialogue` — L8198
- `_topic_cache_dir` — L8212
- `_topic_cache_path` — L8218
- `_load_topic_decomposition_cache` — L8231
- `_save_topic_decomposition_cache` — L8249
- `_briefs_dir` — L8286
- `_brief_path` — L8292
- `_empty_brief` — L8297
- `_deep_merge_brief_skeleton` — L8337
- `_load_brief` — L8351
- `_save_brief` — L8375
- `_brief_get` — L8394
- `_brief_field` — L8406
- `_brief_set` — L8417
- `_brief_claim` — L8433
- `_brief_agent_status` — L8476
- `_brief_from_topic_decomposition` — L8489
- `_rule_based_sfx_design` — L8545
- `_validate_sfx_entry` — L8596
- `_audio_director_design` — L8634
- `_hex_color_validate` — L8690
- `_rule_based_art_design` — L8702
- `_validate_art_design` — L8783
- `_art_director_design` — L8821
- `_coordinator_review` — L8843
- `_llm_topic_decomposition` — L8944
- `_director_route_block` — L9120
- `_llm_infer_meta_grid_template` — L9190
- `_resolve_meta_grid_template` — L9247
- `_infer_meta_grid_costume` — L9290
- `_infer_meta_grid_pose` — L9339
- `_adsd_meta_grid_call_prompt` — L9386
- `_meta_grid_panel_index` — L9428
- `_migrate_speaker_ip` — L9508
- `_speaker_ips_dir` — L9533
- `_list_speaker_ips` — L9540
- `_match_speaker_ip` — L9554
- `_build_speaker_ip_context_for_script` — L9574
- `_ip_usage_stats` — L9630
- `_recommend_related_ips` — L9648
- `_save_speaker_ip` — L9673
- `_record_speaker_usage_history` — L9682
- `_format_speaker_usage_history_for_prompt` — L9729
- `_llm_infer_ip_skeleton` — L9747
- `_llm_pick_voice_asset_for_ip` — L9792
- `_auto_incubate_missing_ips` — L9841
- `_character_meta_grid_cache_dir` — L9925
- `_character_meta_grid_cache_path` — L9933
- `_character_meta_grid_cache_legacy_path` — L9941
- `_character_meta_grid_path` — L9948
- `generate_character_meta_grid_gpt_image2` — L9954
- `_generate_all_character_meta_grids` — L10126
- `_write_character_sheet_qa` — L10167
- `generate_character_sheet_gpt_image2` — L10177
- `generate_production_storyboard_page_gpt_image2` — L10277
- `_qa_clean_storyboard_panel` — L10340
- `_crop_storyboard_grid_panels` — L10521
- `generate_storyboard_grid_gpt_image2` — L10568
- `_gpt_image2_direct_annotated_aspect` — L10800
- `_gpt_image2_direct_annotated_prompt` — L10807
- `generate_gpt_image2_direct_annotated_storyboards` — L10837
- `_llm_bgm_description` — L10938
- `_bgm_contains_vocals` — L10977
- `generate_bgm` — L11011
- `_b68_clamp_scene_durations_to_werydance_bounds` — L11155
- `step6_parallel` — L11215

---

### 第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）
Range: **L11547 – L16734** (5188 lines)

**Sub-sections:**
- _PR-A (2026-05-27): merged_a 合并跑 helpers_ — L14875-16469 (1595 lines)
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L16470-16512 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L16513-16550 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回时间轴锚定音轨_ — L16551-16689 (139 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L16690-16734 (45 lines)

**Top-level constants:**
- `_PR3B1_SHOT_TYPE_ENUM` — L12017
- `_PR3B1_CAMERA_ANGLE_ENUM` — L12021
- `_PR3B1_LIGHTING_ENUM` — L12026
- `_PR3B1_CAMERA_MOTION_ENUM` — L12031
- `_EMOTION_NARRATION_STYLE_MAP` — L13083

**Functions:**
- `_generate_motion_prompts` — L11550
- `_motion_tasks_file` — L11617
- `_motion_qa_file` — L11621
- `_append_motion_qa` — L11625
- `_finalize_motion_qa` — L11649
- `_lip_sync_tasks_file` — L11733
- `_load_motion_tasks` — L11737
- `_save_motion_task` — L11747
- `_remove_motion_task` — L11755
- `_load_lip_sync_tasks` — L11762
- `_save_lip_sync_task` — L11772
- `_remove_lip_sync_task` — L11779
- `_video_visual_motion_qa` — L11786
- `_motion_output_qa` — L11858
- `_has_audio_stream` — L11903
- `_normalize_motion_video` — L11914
- `_motion_poll_and_download` — L11964
- `_validate_enum_field` — L12037
- `_build_motion_video_prompt` — L12052
- `_short_board_text` — L12102
- `_wrap_board_text` — L12109
- `_storyboard_font` — L12140
- `_draw_storyboard_arrow` — L12155
- `_build_annotated_storyboard_reference` — L12169
- `_plain_caption_text` — L12270
- `_werydance_caption_request` — L12278
- `_werydance_caption_instruction` — L12305
- `_werydance_negative_prompt` — L12317
- `_motion_reference_prompt` — L12335
- `_motion_audio_dub_prompt` — L12358
- `_motion_audio_dub_poll_and_download` — L12392
- `_try_motion_audio_dub_video` — L12457
- `_try_motion_reference_video` — L12620
- `_motion_one_scene` — L12736
- `_grid_multiref_tasks_file` — L12866
- `_previs_page_tasks_file` — L12870
- `_load_grid_multiref_tasks` — L12874
- `_load_previs_page_tasks` — L12884
- `_save_grid_multiref_task` — L12894
- `_save_previs_page_task` — L12901
- `_remove_grid_multiref_task` — L12908
- `_remove_previs_page_task` — L12915
- `_poll_video_task_download` — L12922
- `_grid_multiref_group_size` — L12971
- `_grid_multiref_adaptive_group_size` — L12981
- `_grid_multiref_duration` — L13005
- `_grid_multiref_tts_buffer_factor` — L13043
- `_grid_multiref_tts_duration_buffered` — L13057
- `_grid_multiref_segment_max_stretch` — L13073
- `_voice_clone_emotion_style` — L13107
- `_grid_multiref_prompt` — L13130
- `_write_grid_multiref_motion_qa` — L13204
- `_write_previs_page_motion_qa` — L13214
- `_write_storyboard_trailer_qa` — L13224
- `_write_character_trailer_qa` — L13234
- `_write_grid_multiref_segment_qa` — L13244
- `_motion_compare_record` — L13254
- `_write_storyboard_motion_compare_qa` — L13276
- `_scene_segment_duration` — L13312
- `_apply_grid_multiref_segments` — L13331
- `_previs_page_duration` — L13536
- `_previs_page_group_prompt` — L13547
- `_previs_page_groups` — L13573
- `_storyboard_trailer_duration` — L13588
- `_storyboard_trailer_prompt` — L13598
- `_character_trailer_max_shots` — L13626
- `_character_trailer_shot_duration` — L13634
- `_character_trailer_prompt` — L13650
- `_concat_character_trailer_segments` — L13665
- `_generate_character_trailer_motion` — L13704
- `_multi_trailer_prompt_for_group` — L13812
- `_generate_multi_trailer_segments` — L13835
- `_generate_storyboard_trailer_motion` — L13946
- `_generate_previs_page_motion_segments` — L14021
- `_generate_grid_multiref_motion_segments` — L14133
- `_grid_multiref_concat_groups` — L14443
- `_grid_multiref_concat_groups_partial` — L14460
- `_grid_multiref_concat_paths` — L14478
- `_lip_sync_slot_duration` — L14520
- `_adsd_lip_sync_prompt` — L14527
- `_adsd_broll_motion_prompt` — L14573
- `_adsd_action_b_motion_prompt` — L14615
- `_adsd_silent_b_motion_prompt` — L14661
- `_adsd_narrated_b_audio_dub_prompt` — L14696
- `_adsd_almighty_audio_dub_prompt` — L14740
- `_postprocess_lip_sync_segment` — L14781
- `_detect_audio_leading_silence` — L14853
- `_concat_audio_files_for_group` — L14878
- `_split_lip_sync_raw_by_durations` — L14901
- `_postprocess_audio_dub_segment` — L14936
- `_lips_change_repair_segment` — L15064
- `_load_lips_change_requested_turns` — L15149
- `_parse_turn_set` — L15166
- `_load_motion_voice_repair_turns` — L15188
- `_voice_assets_file` — L15200
- `_load_voice_assets` — L15207
- `_build_combined_voice_reference` — L15226
- `_select_voice_asset_reference` — L15268
- `_lip_sync_poll_download_and_process` — L15344
- `_lip_sync_one_group` — L15412
- `_lip_sync_one_scene` — L15620
- `step66_adsd_lip_sync` — L15944
- `step65_motion` — L16289
- `step65_grid_multiref_motion_qa` — L16442
- `_sanitize_scene_for_state` — L16471
- `_save_pipeline_state` — L16490
- `_retime_after_audio_dub` — L16514
- `_build_voice_clone_hybrid_audio` — L16552
- `_build_dynamic_bgm` — L16691

---

### 第七步：拼接视频轨
Range: **L16735 – L17070** (336 lines)

**Functions:**
- `_rescue_motion_image_to_video` — L16736
- `_rescue_motion_text_to_video` — L16771
- `step7_concat` — L16802

---

### 第八步：生成 ASS 字幕
Range: **L17071 – L18029** (959 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L17350-18029 (680 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L17072
- `_word_timings_for_subtitle_align` — L17098
- `_align_segments_via_asr` — L17139
- `_b61_1_asr_turn_boundaries` — L17182
- `step8_subtitles` — L17244
- `_read_output_json` — L17750
- `_qa_file_pass` — L17761
- `_ass_has_dialogue` — L17768
- `_write_adsd_delivery_qa` — L17778
- `_write_bgm_only_qa` — L17918

---

### 第九步：最终合成
Range: **L18030 – L18320** (291 lines)

**Functions:**
- `step9_render` — L18031

---

### 第十步：推送 Telegram
Range: **L18321 – L20183** (1863 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L19427-19536 (110 lines)
- _B70 (2026-05-30) TG oversize policy helpers_ — L19537-19990 (454 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L19991-19995 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L19996-20059 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L20060-20105 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L20106-20183 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L18690
- `PANTONE_FALLBACK` — L18717
- `FESTIVAL_DATE_TAG` — L18831

**Functions:**
- `_generate_caption` — L18322
- `_overlay_title_on_cover` — L18560
- `_prepare_tg_photo` — L18670
- `_get_pantone_for_date` — L18720
- `_llm_bottom_note` — L18745
- `_get_bottom_note` — L18775
- `_get_date_tag` — L18853
- `_shrink_to_b64` — L18875
- `_llm_check_scenes_anomalies` — L18891
- `_llm_check_cover_unique` — L18944
- `_llm_check_cover_quality` — L18974
- `_try_almanac_cover` — L19016
- `_generate_cover_image` — L19187
- `_async_kickoff_cover_caption` — L19434
- `_await_async_cover_caption` — L19510
- `_b70_env_float` — L19540
- `_b70_split_and_deliver` — L19555
- `_b70_send_document_first` — L19655
- `step10_deliver` — L19692

---

### 主流程
Range: **L20184 – L20411** (228 lines)

**Functions:**
- `_print_execution_plan` — L20185
- `_write_run_timings` — L20233
- `main` — L20262

---
