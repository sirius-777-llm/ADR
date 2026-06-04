# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (20463 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-2489 (2368 lines · 73 fn · 5 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L2490-5141 (2652 lines · 33 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L5142-6374 (1233 lines · 22 fn · 2 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L6375-6926 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L6927-11598 (4672 lines · 105 fn · 7 sub)
- [`第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）`](#第-6-5-步-动态化-hads-vads-默认-on---no-motion-关) — L11599-16786 (5188 lines · 109 fn · 5 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L16787-17122 (336 lines · 3 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L17123-18081 (959 lines · 10 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L18082-18372 (291 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L18373-20235 (1863 lines · 19 fn · 6 sub)
- [`主流程`](#主流程) — L20236-20463 (228 lines · 3 fn · 0 sub)

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
Range: **L2490 – L5141** (2652 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L4122-5141 (1020 lines)

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
- `_write_ads_retention_qa` — L5085

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L5142 – L6374** (1233 lines)

**Sub-sections:**
- _B88: 内容审核(1002) → 分级软化 → 中性兜底句 → 静音 backstop，绝不崩管线_ — L5837-5865 (29 lines)
- _非内容审核(网络/transient): 有限退避重试，耗尽才抛_ — L5866-6374 (509 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L5217
- `_ADSD_POLICY_REWRITE_TERMS` — L5223
- `_TTS_SAFE_FALLBACK_LINE` — L5324
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L5392

**Functions:**
- `_openai_tts_fallback` — L5143
- `_edge_tts_fallback` — L5189
- `_sanitize_for_external_api` — L5248
- `_is_content_policy_error` — L5257
- `_rewrite_adsd_tts_text_for_policy` — L5271
- `_tts_safe_fallback_line` — L5333
- `_tts_silent_placeholder` — L5338
- `_record_adsd_tts_rewrite` — L5373
- `_build_silence_mp3` — L5398
- `_audio_duration_seconds` — L5411
- `_text_to_audio_master_voice_timed` — L5423
- `_text_to_audio_master_voice` — L5548
- `step2_master_voice` — L5661
- `_tts_turn_to_audio` — L5789
- `_asr_verify_dialogue_audio` — L5876
- `_asr_verify_dialogue_turns` — L5938
- `_normalize_cn_number_token` — L5980
- `_compact_zh_text` — L6002
- `_write_adsd_asr_text_qa` — L6009
- `_write_adsd_speaker_focus_qa` — L6048
- `_write_adsd_gender_voice_qa` — L6108
- `step2_dialogue_voice` — L6161

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L6375 – L6926** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L6382-6504 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L6505-6539 (35 lines)
- _第二层：字符数插值_ — L6540-6564 (25 lines)
- _第三层：silencedetect 物理校准_ — L6565-6926 (362 lines)

**Functions:**
- `_detect_silences` — L6383
- `_calibrate_boundaries` — L6418
- `_enforce_monotonic` — L6452
- `_manual_override_segments` — L6464
- `_calc_sentence_boundaries` — L6485
- `step345_timeline` — L6596
- `_analyze_bgm_energy_cuts` — L6655
- `_snap_bgm_only_boundaries` — L6718
- `step345_bgm_only_timeline` — L6778

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L6927 – L11598** (4672 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L8156-8206 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L8207-9065 (859 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L9066-9553 (488 lines)
- _Speaker IP Card (2026-05-21)_ — L9554-11198 (1645 lines)
- _B68 (2026-05-30) WERYDANCE 段长合规 gate_ — L11199-11431 (233 lines)
- _审批流程_ — L11432-11488 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L11489-11598 (110 lines)

**Top-level constants:**
- `_CORE_TERMS_STOP_WORDS` — L7329
- `CHARACTER_META_GRID_COSTUMES` — L8162
- `CHARACTER_META_GRID_POSES` — L8163
- `CHARACTER_META_GRID_SCENES` — L8164
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L8167
- `_SFX_TYPE_ENUM` — L8535
- `_SFX_INTENSITY_ENUM` — L8540
- `_SFX_POSITION_ENUM` — L8541
- `_GRAIN_LEVEL_ENUM` — L8686
- `_CUSTOM_STYLE_BANNED_NAMES` — L9121

**Functions:**
- `_extract_img_url` — L6928
- `_extract_img_urls` — L6950
- `_extract_video_url` — L6983
- `_count_bands` — L7008
- `_detect_contact_sheet_like_image` — L7020
- `_file_sha256` — L7081
- `_load_upload_cache` — L7094
- `_save_upload_cache` — L7103
- `_cached_upload_url` — L7111
- `_store_upload_url` — L7128
- `_guess_upload_mime` — L7138
- `_upload_to_weryai` — L7161
- `_send_for_approval` — L7222
- `_wait_approval` — L7286
- `_render_still_segment` — L7298
- `_extract_core_terms` — L7335
- `_scene_text_visual_alignment` — L7354
- `_write_text_visual_alignment_qa` — L7375
- `_scene_motion_action_plan` — L7398
- `_ensure_motion_action_plan` — L7452
- `_motion_action_block` — L7461
- `_motion_plan_for_qa` — L7489
- `_write_motion_action_plan_qa` — L7499
- `_write_motion_bridge_refs_qa` — L7529
- `_motion_bridge_ref_prompt` — L7536
- `generate_motion_bridge_refs_gpt_image2` — L7569
- `generate_image` — L7684
- `generate_storyboard_images_gpt_image2` — L7731
- `_storyboard_grid_aspect` — L7917
- `_storyboard_grid_cols_rows` — L7924
- `_storyboard_grid_prompt` — L7946
- `_storyboard_grid_prompt_limit` — L8004
- `_is_prompt_limit_response` — L8008
- `_production_storyboard_prompt` — L8014
- `_write_production_storyboard_page_qa` — L8048
- `_character_sheet_prompt` — L8058
- `_is_audit_blocked` — L8184
- `_paraphrase_sensitive_dialogue` — L8197
- `_topic_cache_dir` — L8211
- `_topic_cache_path` — L8217
- `_load_topic_decomposition_cache` — L8230
- `_save_topic_decomposition_cache` — L8248
- `_briefs_dir` — L8285
- `_brief_path` — L8291
- `_empty_brief` — L8296
- `_deep_merge_brief_skeleton` — L8336
- `_load_brief` — L8350
- `_save_brief` — L8374
- `_brief_get` — L8393
- `_brief_field` — L8405
- `_brief_set` — L8416
- `_brief_claim` — L8432
- `_brief_agent_status` — L8475
- `_brief_from_topic_decomposition` — L8488
- `_rule_based_sfx_design` — L8544
- `_validate_sfx_entry` — L8595
- `_audio_director_design` — L8633
- `_hex_color_validate` — L8689
- `_rule_based_art_design` — L8701
- `_validate_art_design` — L8782
- `_art_director_design` — L8820
- `_coordinator_review` — L8842
- `_llm_topic_decomposition` — L8943
- `_validate_custom_visual_style` — L9128
- `_resolve_route_style` — L9150
- `_director_route_block` — L9175
- `_llm_infer_meta_grid_template` — L9242
- `_resolve_meta_grid_template` — L9299
- `_infer_meta_grid_costume` — L9342
- `_infer_meta_grid_pose` — L9391
- `_adsd_meta_grid_call_prompt` — L9438
- `_meta_grid_panel_index` — L9480
- `_migrate_speaker_ip` — L9560
- `_speaker_ips_dir` — L9585
- `_list_speaker_ips` — L9592
- `_match_speaker_ip` — L9606
- `_build_speaker_ip_context_for_script` — L9626
- `_ip_usage_stats` — L9682
- `_recommend_related_ips` — L9700
- `_save_speaker_ip` — L9725
- `_record_speaker_usage_history` — L9734
- `_format_speaker_usage_history_for_prompt` — L9781
- `_llm_infer_ip_skeleton` — L9799
- `_llm_pick_voice_asset_for_ip` — L9844
- `_auto_incubate_missing_ips` — L9893
- `_character_meta_grid_cache_dir` — L9977
- `_character_meta_grid_cache_path` — L9985
- `_character_meta_grid_cache_legacy_path` — L9993
- `_character_meta_grid_path` — L10000
- `generate_character_meta_grid_gpt_image2` — L10006
- `_generate_all_character_meta_grids` — L10178
- `_write_character_sheet_qa` — L10219
- `generate_character_sheet_gpt_image2` — L10229
- `generate_production_storyboard_page_gpt_image2` — L10329
- `_qa_clean_storyboard_panel` — L10392
- `_crop_storyboard_grid_panels` — L10573
- `generate_storyboard_grid_gpt_image2` — L10620
- `_gpt_image2_direct_annotated_aspect` — L10852
- `_gpt_image2_direct_annotated_prompt` — L10859
- `generate_gpt_image2_direct_annotated_storyboards` — L10889
- `_llm_bgm_description` — L10990
- `_bgm_contains_vocals` — L11029
- `generate_bgm` — L11063
- `_b68_clamp_scene_durations_to_werydance_bounds` — L11207
- `step6_parallel` — L11267

---

### 第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）
Range: **L11599 – L16786** (5188 lines)

**Sub-sections:**
- _PR-A (2026-05-27): merged_a 合并跑 helpers_ — L14927-16521 (1595 lines)
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L16522-16564 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L16565-16602 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回时间轴锚定音轨_ — L16603-16741 (139 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L16742-16786 (45 lines)

**Top-level constants:**
- `_PR3B1_SHOT_TYPE_ENUM` — L12069
- `_PR3B1_CAMERA_ANGLE_ENUM` — L12073
- `_PR3B1_LIGHTING_ENUM` — L12078
- `_PR3B1_CAMERA_MOTION_ENUM` — L12083
- `_EMOTION_NARRATION_STYLE_MAP` — L13135

**Functions:**
- `_generate_motion_prompts` — L11602
- `_motion_tasks_file` — L11669
- `_motion_qa_file` — L11673
- `_append_motion_qa` — L11677
- `_finalize_motion_qa` — L11701
- `_lip_sync_tasks_file` — L11785
- `_load_motion_tasks` — L11789
- `_save_motion_task` — L11799
- `_remove_motion_task` — L11807
- `_load_lip_sync_tasks` — L11814
- `_save_lip_sync_task` — L11824
- `_remove_lip_sync_task` — L11831
- `_video_visual_motion_qa` — L11838
- `_motion_output_qa` — L11910
- `_has_audio_stream` — L11955
- `_normalize_motion_video` — L11966
- `_motion_poll_and_download` — L12016
- `_validate_enum_field` — L12089
- `_build_motion_video_prompt` — L12104
- `_short_board_text` — L12154
- `_wrap_board_text` — L12161
- `_storyboard_font` — L12192
- `_draw_storyboard_arrow` — L12207
- `_build_annotated_storyboard_reference` — L12221
- `_plain_caption_text` — L12322
- `_werydance_caption_request` — L12330
- `_werydance_caption_instruction` — L12357
- `_werydance_negative_prompt` — L12369
- `_motion_reference_prompt` — L12387
- `_motion_audio_dub_prompt` — L12410
- `_motion_audio_dub_poll_and_download` — L12444
- `_try_motion_audio_dub_video` — L12509
- `_try_motion_reference_video` — L12672
- `_motion_one_scene` — L12788
- `_grid_multiref_tasks_file` — L12918
- `_previs_page_tasks_file` — L12922
- `_load_grid_multiref_tasks` — L12926
- `_load_previs_page_tasks` — L12936
- `_save_grid_multiref_task` — L12946
- `_save_previs_page_task` — L12953
- `_remove_grid_multiref_task` — L12960
- `_remove_previs_page_task` — L12967
- `_poll_video_task_download` — L12974
- `_grid_multiref_group_size` — L13023
- `_grid_multiref_adaptive_group_size` — L13033
- `_grid_multiref_duration` — L13057
- `_grid_multiref_tts_buffer_factor` — L13095
- `_grid_multiref_tts_duration_buffered` — L13109
- `_grid_multiref_segment_max_stretch` — L13125
- `_voice_clone_emotion_style` — L13159
- `_grid_multiref_prompt` — L13182
- `_write_grid_multiref_motion_qa` — L13256
- `_write_previs_page_motion_qa` — L13266
- `_write_storyboard_trailer_qa` — L13276
- `_write_character_trailer_qa` — L13286
- `_write_grid_multiref_segment_qa` — L13296
- `_motion_compare_record` — L13306
- `_write_storyboard_motion_compare_qa` — L13328
- `_scene_segment_duration` — L13364
- `_apply_grid_multiref_segments` — L13383
- `_previs_page_duration` — L13588
- `_previs_page_group_prompt` — L13599
- `_previs_page_groups` — L13625
- `_storyboard_trailer_duration` — L13640
- `_storyboard_trailer_prompt` — L13650
- `_character_trailer_max_shots` — L13678
- `_character_trailer_shot_duration` — L13686
- `_character_trailer_prompt` — L13702
- `_concat_character_trailer_segments` — L13717
- `_generate_character_trailer_motion` — L13756
- `_multi_trailer_prompt_for_group` — L13864
- `_generate_multi_trailer_segments` — L13887
- `_generate_storyboard_trailer_motion` — L13998
- `_generate_previs_page_motion_segments` — L14073
- `_generate_grid_multiref_motion_segments` — L14185
- `_grid_multiref_concat_groups` — L14495
- `_grid_multiref_concat_groups_partial` — L14512
- `_grid_multiref_concat_paths` — L14530
- `_lip_sync_slot_duration` — L14572
- `_adsd_lip_sync_prompt` — L14579
- `_adsd_broll_motion_prompt` — L14625
- `_adsd_action_b_motion_prompt` — L14667
- `_adsd_silent_b_motion_prompt` — L14713
- `_adsd_narrated_b_audio_dub_prompt` — L14748
- `_adsd_almighty_audio_dub_prompt` — L14792
- `_postprocess_lip_sync_segment` — L14833
- `_detect_audio_leading_silence` — L14905
- `_concat_audio_files_for_group` — L14930
- `_split_lip_sync_raw_by_durations` — L14953
- `_postprocess_audio_dub_segment` — L14988
- `_lips_change_repair_segment` — L15116
- `_load_lips_change_requested_turns` — L15201
- `_parse_turn_set` — L15218
- `_load_motion_voice_repair_turns` — L15240
- `_voice_assets_file` — L15252
- `_load_voice_assets` — L15259
- `_build_combined_voice_reference` — L15278
- `_select_voice_asset_reference` — L15320
- `_lip_sync_poll_download_and_process` — L15396
- `_lip_sync_one_group` — L15464
- `_lip_sync_one_scene` — L15672
- `step66_adsd_lip_sync` — L15996
- `step65_motion` — L16341
- `step65_grid_multiref_motion_qa` — L16494
- `_sanitize_scene_for_state` — L16523
- `_save_pipeline_state` — L16542
- `_retime_after_audio_dub` — L16566
- `_build_voice_clone_hybrid_audio` — L16604
- `_build_dynamic_bgm` — L16743

---

### 第七步：拼接视频轨
Range: **L16787 – L17122** (336 lines)

**Functions:**
- `_rescue_motion_image_to_video` — L16788
- `_rescue_motion_text_to_video` — L16823
- `step7_concat` — L16854

---

### 第八步：生成 ASS 字幕
Range: **L17123 – L18081** (959 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L17402-18081 (680 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L17124
- `_word_timings_for_subtitle_align` — L17150
- `_align_segments_via_asr` — L17191
- `_b61_1_asr_turn_boundaries` — L17234
- `step8_subtitles` — L17296
- `_read_output_json` — L17802
- `_qa_file_pass` — L17813
- `_ass_has_dialogue` — L17820
- `_write_adsd_delivery_qa` — L17830
- `_write_bgm_only_qa` — L17970

---

### 第九步：最终合成
Range: **L18082 – L18372** (291 lines)

**Functions:**
- `step9_render` — L18083

---

### 第十步：推送 Telegram
Range: **L18373 – L20235** (1863 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L19479-19588 (110 lines)
- _B70 (2026-05-30) TG oversize policy helpers_ — L19589-20042 (454 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L20043-20047 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L20048-20111 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L20112-20157 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L20158-20235 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L18742
- `PANTONE_FALLBACK` — L18769
- `FESTIVAL_DATE_TAG` — L18883

**Functions:**
- `_generate_caption` — L18374
- `_overlay_title_on_cover` — L18612
- `_prepare_tg_photo` — L18722
- `_get_pantone_for_date` — L18772
- `_llm_bottom_note` — L18797
- `_get_bottom_note` — L18827
- `_get_date_tag` — L18905
- `_shrink_to_b64` — L18927
- `_llm_check_scenes_anomalies` — L18943
- `_llm_check_cover_unique` — L18996
- `_llm_check_cover_quality` — L19026
- `_try_almanac_cover` — L19068
- `_generate_cover_image` — L19239
- `_async_kickoff_cover_caption` — L19486
- `_await_async_cover_caption` — L19562
- `_b70_env_float` — L19592
- `_b70_split_and_deliver` — L19607
- `_b70_send_document_first` — L19707
- `step10_deliver` — L19744

---

### 主流程
Range: **L20236 – L20463** (228 lines)

**Functions:**
- `_print_execution_plan` — L20237
- `_write_run_timings` — L20285
- `main` — L20314

---
