# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (22685 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-129 (129 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L130-2539 (2410 lines · 74 fn · 5 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L2540-5191 (2652 lines · 33 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L5192-6424 (1233 lines · 22 fn · 2 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L6425-6976 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L6977-12697 (5721 lines · 131 fn · 8 sub)
- [`第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）`](#第-6-5-步-动态化-hads-vads-默认-on---no-motion-关) — L12698-18961 (6264 lines · 137 fn · 6 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L18962-19297 (336 lines · 3 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L19298-20256 (959 lines · 10 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L20257-20547 (291 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L20548-22430 (1883 lines · 19 fn · 6 sub)
- [`主流程`](#主流程) — L22431-22685 (255 lines · 3 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L129** (129 lines)

**Sub-sections:**
- _老黄历数据模块_ — L37-129 (93 lines)

**Functions:**
- `get_almanac_data` — L65

---

### 配置
Range: **L130 – L2539** (2410 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L372-501 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L502-1245 (744 lines)
- _工具函数_ — L1246-1621 (376 lines)
- _B87 纹理档系统：LLM 提名 + 代码护栏 + 确定性渲染_ — L1622-1884 (263 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1885-2539 (655 lines)

**Top-level constants:**
- `HEADERS` — L169
- `VIDEO_FORMAT_RAW` — L177
- `MTV_MODE` — L178
- `VIDEO_FORMAT` — L183
- `ADS_DIALOGUE_MODE_EARLY_CHECK` — L194
- `WITH_MOTION` — L201
- `BGM_ONLY_REQUESTED` — L206
- `ADS_DIALOGUE_MODE` — L213
- `GPT_IMAGE2_STORYBOARD` — L225
- `STORYBOARD_REFERENCE_MOTION` — L229
- `STORYBOARD_ANNOTATED_MOTION` — L233
- `GPT_IMAGE2_DIRECT_ANNOTATED_STORYBOARD` — L237
- `GPT_IMAGE2_STORYBOARD_GRID` — L242
- `ADSD_STORYBOARD_GRID` — L250
- `ADS_CHARACTER_SHEET_REQUESTED` — L256
- `STORYBOARD_GRID_MULTIREF_MOTION` — L260
- `STORYBOARD_GRID_MULTIREF_SEGMENTS` — L264
- `STORYBOARD_GRID_MULTIREF_MAIN` — L270
- `GRID_MULTIREF_PRIMARY` — L280
- `PREVIS_PAGE_MOTION` — L292
- `STORYBOARD_TRAILER_MODE` — L296
- `MOTION_ACTION_STORYBOARD` — L301
- `MOTION_BRIDGE_REFS` — L305
- `CHARACTER_TRAILER_MODE` — L309
- `STORYBOARD_TRAILER_MAIN` — L317
- `ADSD_LIP_SYNC_EXPERIMENT` — L330
- `ADSD_RICH_MOTION_PROMPT` — L338
- `ADSD_LLM_VOICE_ASSIGN` — L346
- `ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT` — L350
- `ADSD_CONSECUTIVE_SPEAKER_BATCHING` — L364
- `ADSD_GENDER_FALLBACK_VOICE_ASSET` — L375
- `SILENT_B_SPEAKERS` — L507
- `_PODCAST_TO_VOICE_ASSET_MAP` — L885
- `_VOICE_ASSET_FORBIDDEN_FLAGS` — L903
- `_GENERIC_NARRATOR_NAMES` — L947
- `VOICE_ASSET_AUDIO_DUB_EXPERIMENT` — L984
- `VOICE_ASSET_AUDIO_DUB_PARTIAL_OK` — L992
- `MOTION_VISUAL_QA` — L996
- `MOTION_VOICE_REPAIR` — L1004
- `MOTION_VOICE_STRICT_LOCK` — L1009
- `WERYDANCE_CAPTIONS` — L1014
- `ADSD_ONSITE_POV_MODE` — L1026
- `ADSD_LIPS_CHANGE_REPAIR` — L1031
- `ADSD_LIPS_CHANGE_ALL` — L1036
- `ADS_REPORTER_MODE` — L1047
- `ADS_STORYBOARD_FLOW_DEFAULT` — L1064
- `ADS_RETENTION_MODE` — L1078
- `ADSD_MODE_NAME` — L1084
- `EMOTION_STYLE` — L1225
- `EMOTION_STYLE_BRIGHT` — L1237
- `_REDACT_PATTERNS_DEFAULT` — L1251
- `_TG_DASHBOARD_STAGES` — L1303
- `_TG_NOISY_PATTERNS` — L1318
- `_TG_IMMEDIATE_PATTERNS` — L1336
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1615
- `_TEXTURE_MODE_ENUM` — L1623
- `_TEXTURE_SUFFIX_MAP` — L1628
- `_TEXTURE_BODY_DIRECTIVE` — L1655
- `_TEXTURE_SCENE_PHRASE` — L1662
- `_TEXTURE_GRID_PHRASE` — L1669
- `_TEXTURE_MOTION_PHRASE` — L1677
- `_LLM_TIER` — L2065
- `_TOPIC_MODIFIERS` — L2292
- `_TONE_PANTONE_OVERRIDE` — L2309

**Functions:**
- `_read_almighty_model` — L149
- `_is_action_scene` — L384
- `_needs_storyboard_flow_character_sheet` — L395
- `_wuxia_action_panel_prompt` — L424
- `_action_motion_fragment` — L446
- `_infer_emotion_from_text` — L461
- `_emotion_expression_phrase` — L476
- `_infer_needs_lip_sync` — L483
- `_infer_turn_type` — L510
- `_is_action_shout` — L535
- `_resolve_turn_type` — L561
- `_is_silent_b` — L576
- `_is_narrated_b` — L580
- `_is_a_roll` — L584
- `_is_action_b` — L588
- `_voice_asset_id_for_speaker` — L592
- `_llm_assign_voice_assets` — L620
- `_apply_llm_voice_assignment` — L749
- `_voice_asset_is_speech_safe` — L910
- `_podcast_id_to_voice_asset` — L916
- `_resolve_voice_asset_for_ads_speaker` — L950
- `_redact_for_stdout` — L1266
- `log` — L1291
- `_tg_send_raw` — L1359
- `_tg_matches` — L1375
- `_tg_summarize` — L1379
- `_tg_dashboard_stage_for` — L1386
- `_tg_progress_bar` — L1394
- `_tg_dashboard_text` — L1400
- `_tg_dashboard_update` — L1418
- `_tg_maybe_digest` — L1455
- `tg` — L1470
- `_wait_image_submit_slot` — L1519
- `_wait_motion_submit_slot` — L1532
- `_is_rate_limited_error` — L1545
- `_is_rate_limited_response` — L1555
- `_is_transient_workflow_error` — L1567
- `_is_llm_rate_limited_error` — L1591
- `_era_is_pre_photographic` — L1689
- `_texture_mode_fallback` — L1717
- `_texture_guardrail` — L1738
- `_set_active_texture_profile` — L1777
- `_active_texture_suffix` — L1790
- `_active_texture_body_directive` — L1794
- `_active_texture_scene_phrase` — L1798
- `_active_texture_grid_phrase` — L1802
- `_active_texture_motion_phrase` — L1806
- `_inject_image2_quality_suffix` — L1810
- `submit_text_to_image` — L1830
- `req_post` — L1866
- `req_get` — L1880
- `_tg_probe_send` — L1888
- `_tg_probe_delete` — L1908
- `_tg_upload_with_probe_gap` — L1921
- `poll` — L1961
- `poll_podcast` — L1986
- `poll_task_status` — L2008
- `poll_storyboard_task` — L2030
- `tier_chat` — L2073
- `chat` — L2079
- `pick_image_model` — L2138
- `detect_topic_meta` — L2163
- `_topic_culture_guard` — L2213
- `_write_cultural_visual_qa` — L2239
- `is_1919_global_topic` — L2286
- `_strip_topic_modifiers` — L2297
- `apply_1919_global_guardrails` — L2315
- `build_1919_global_cover_prompt` — L2344
- `_shot_blueprint_enums` — L2376
- `build_shot_blueprint` — L2452
- `ffprobe_duration` — L2478
- `ffprobe_video_size` — L2489
- `_video_decode_probe` — L2510
- `ffmpeg` — L2528

---

### 第一步：双导演生成剧本
Range: **L2540 – L5191** (2652 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L4172-5191 (1020 lines)

**Top-level constants:**
- `_ENSEMBLE_CAP_BY_ROUTE` — L2692

**Functions:**
- `_extract_json_array` — L2541
- `_extract_json_object` — L2551
- `_voice_for_speaker` — L2561
- `_adsd_gender_from_voice` — L2597
- `_adsd_infer_gender_from_speaker` — L2605
- `_adsd_gender_lock_phrase` — L2614
- `_adsd_visual_subject_has_gender_conflict` — L2629
- `_adsd_default_roles` — L2641
- `_adsd_allows_media_role` — L2646
- `_adsd_role_candidates` — L2654
- `_adsd_dialogue_shape` — L2681
- `_ensemble_speaker_cap` — L2703
- `_ip_voice_asset_for_speaker` — L2716
- `_finalize_adsd_turns` — L2740
- `_parse_adsd_override_turns` — L2786
- `_parse_timecode_seconds` — L2879
- `_clean_override_line_text` — L2888
- `_parse_override_script_text` — L2894
- `_adsd_pov_contract` — L2928
- `_load_audit_blacklist_block` — L2941
- `_generate_adsd_dialogue_turns` — L2979
- `_broll_rhythm_reviewer` — L3406
- `_sweep_speaker_field` — L3513
- `_should_run_immersion_qa` — L3573
- `_adsd_immersion_qa_rewrite_turns` — L3596
- `_adsd_visual_contract` — L3660
- `_parse_risk_score` — L3712
- `_check_high_risk_hard_abort` — L3741
- `_maybe_neutralize_topic` — L3768
- `_apply_render_budget_scene_cap` — L3807
- `_apply_llm_mode_decision` — L3834
- `step1_script` — L3889
- `_write_ads_retention_qa` — L5135

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L5192 – L6424** (1233 lines)

**Sub-sections:**
- _B88: 内容审核(1002) → 分级软化 → 中性兜底句 → 静音 backstop，绝不崩管线_ — L5887-5915 (29 lines)
- _非内容审核(网络/transient): 有限退避重试，耗尽才抛_ — L5916-6424 (509 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L5267
- `_ADSD_POLICY_REWRITE_TERMS` — L5273
- `_TTS_SAFE_FALLBACK_LINE` — L5374
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L5442

**Functions:**
- `_openai_tts_fallback` — L5193
- `_edge_tts_fallback` — L5239
- `_sanitize_for_external_api` — L5298
- `_is_content_policy_error` — L5307
- `_rewrite_adsd_tts_text_for_policy` — L5321
- `_tts_safe_fallback_line` — L5383
- `_tts_silent_placeholder` — L5388
- `_record_adsd_tts_rewrite` — L5423
- `_build_silence_mp3` — L5448
- `_audio_duration_seconds` — L5461
- `_text_to_audio_master_voice_timed` — L5473
- `_text_to_audio_master_voice` — L5598
- `step2_master_voice` — L5711
- `_tts_turn_to_audio` — L5839
- `_asr_verify_dialogue_audio` — L5926
- `_asr_verify_dialogue_turns` — L5988
- `_normalize_cn_number_token` — L6030
- `_compact_zh_text` — L6052
- `_write_adsd_asr_text_qa` — L6059
- `_write_adsd_speaker_focus_qa` — L6098
- `_write_adsd_gender_voice_qa` — L6158
- `step2_dialogue_voice` — L6211

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L6425 – L6976** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L6432-6554 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L6555-6589 (35 lines)
- _第二层：字符数插值_ — L6590-6614 (25 lines)
- _第三层：silencedetect 物理校准_ — L6615-6976 (362 lines)

**Functions:**
- `_detect_silences` — L6433
- `_calibrate_boundaries` — L6468
- `_enforce_monotonic` — L6502
- `_manual_override_segments` — L6514
- `_calc_sentence_boundaries` — L6535
- `step345_timeline` — L6646
- `_analyze_bgm_energy_cuts` — L6705
- `_snap_bgm_only_boundaries` — L6768
- `step345_bgm_only_timeline` — L6828

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L6977 – L12697** (5721 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L8206-8256 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L8257-9115 (859 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L9116-9603 (488 lines)
- _Speaker IP Card (2026-05-21)_ — L9604-11248 (1645 lines)
- _MTV：原创歌曲 + 主唱人物库 + WeryDance MV_ — L11249-12297 (1049 lines)
- _B68 (2026-05-30) WERYDANCE 段长合规 gate_ — L12298-12530 (233 lines)
- _审批流程_ — L12531-12587 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L12588-12697 (110 lines)

**Top-level constants:**
- `_CORE_TERMS_STOP_WORDS` — L7379
- `CHARACTER_META_GRID_COSTUMES` — L8212
- `CHARACTER_META_GRID_POSES` — L8213
- `CHARACTER_META_GRID_SCENES` — L8214
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L8217
- `_SFX_TYPE_ENUM` — L8585
- `_SFX_INTENSITY_ENUM` — L8590
- `_SFX_POSITION_ENUM` — L8591
- `_GRAIN_LEVEL_ENUM` — L8736
- `_CUSTOM_STYLE_BANNED_NAMES` — L9171
- `_DUANGE_XING_TEXT` — L11250

**Functions:**
- `_extract_img_url` — L6978
- `_extract_img_urls` — L7000
- `_extract_video_url` — L7033
- `_count_bands` — L7058
- `_detect_contact_sheet_like_image` — L7070
- `_file_sha256` — L7131
- `_load_upload_cache` — L7144
- `_save_upload_cache` — L7153
- `_cached_upload_url` — L7161
- `_store_upload_url` — L7178
- `_guess_upload_mime` — L7188
- `_upload_to_weryai` — L7211
- `_send_for_approval` — L7272
- `_wait_approval` — L7336
- `_render_still_segment` — L7348
- `_extract_core_terms` — L7385
- `_scene_text_visual_alignment` — L7404
- `_write_text_visual_alignment_qa` — L7425
- `_scene_motion_action_plan` — L7448
- `_ensure_motion_action_plan` — L7502
- `_motion_action_block` — L7511
- `_motion_plan_for_qa` — L7539
- `_write_motion_action_plan_qa` — L7549
- `_write_motion_bridge_refs_qa` — L7579
- `_motion_bridge_ref_prompt` — L7586
- `generate_motion_bridge_refs_gpt_image2` — L7619
- `generate_image` — L7734
- `generate_storyboard_images_gpt_image2` — L7781
- `_storyboard_grid_aspect` — L7967
- `_storyboard_grid_cols_rows` — L7974
- `_storyboard_grid_prompt` — L7996
- `_storyboard_grid_prompt_limit` — L8054
- `_is_prompt_limit_response` — L8058
- `_production_storyboard_prompt` — L8064
- `_write_production_storyboard_page_qa` — L8098
- `_character_sheet_prompt` — L8108
- `_is_audit_blocked` — L8234
- `_paraphrase_sensitive_dialogue` — L8247
- `_topic_cache_dir` — L8261
- `_topic_cache_path` — L8267
- `_load_topic_decomposition_cache` — L8280
- `_save_topic_decomposition_cache` — L8298
- `_briefs_dir` — L8335
- `_brief_path` — L8341
- `_empty_brief` — L8346
- `_deep_merge_brief_skeleton` — L8386
- `_load_brief` — L8400
- `_save_brief` — L8424
- `_brief_get` — L8443
- `_brief_field` — L8455
- `_brief_set` — L8466
- `_brief_claim` — L8482
- `_brief_agent_status` — L8525
- `_brief_from_topic_decomposition` — L8538
- `_rule_based_sfx_design` — L8594
- `_validate_sfx_entry` — L8645
- `_audio_director_design` — L8683
- `_hex_color_validate` — L8739
- `_rule_based_art_design` — L8751
- `_validate_art_design` — L8832
- `_art_director_design` — L8870
- `_coordinator_review` — L8892
- `_llm_topic_decomposition` — L8993
- `_validate_custom_visual_style` — L9178
- `_resolve_route_style` — L9200
- `_director_route_block` — L9225
- `_llm_infer_meta_grid_template` — L9292
- `_resolve_meta_grid_template` — L9349
- `_infer_meta_grid_costume` — L9392
- `_infer_meta_grid_pose` — L9441
- `_adsd_meta_grid_call_prompt` — L9488
- `_meta_grid_panel_index` — L9530
- `_migrate_speaker_ip` — L9610
- `_speaker_ips_dir` — L9635
- `_list_speaker_ips` — L9642
- `_match_speaker_ip` — L9656
- `_build_speaker_ip_context_for_script` — L9676
- `_ip_usage_stats` — L9732
- `_recommend_related_ips` — L9750
- `_save_speaker_ip` — L9775
- `_record_speaker_usage_history` — L9784
- `_format_speaker_usage_history_for_prompt` — L9831
- `_llm_infer_ip_skeleton` — L9849
- `_llm_pick_voice_asset_for_ip` — L9894
- `_auto_incubate_missing_ips` — L9943
- `_character_meta_grid_cache_dir` — L10027
- `_character_meta_grid_cache_path` — L10035
- `_character_meta_grid_cache_legacy_path` — L10043
- `_character_meta_grid_path` — L10050
- `generate_character_meta_grid_gpt_image2` — L10056
- `_generate_all_character_meta_grids` — L10228
- `_write_character_sheet_qa` — L10269
- `generate_character_sheet_gpt_image2` — L10279
- `generate_production_storyboard_page_gpt_image2` — L10379
- `_qa_clean_storyboard_panel` — L10442
- `_crop_storyboard_grid_panels` — L10623
- `generate_storyboard_grid_gpt_image2` — L10670
- `_gpt_image2_direct_annotated_aspect` — L10902
- `_gpt_image2_direct_annotated_prompt` — L10909
- `generate_gpt_image2_direct_annotated_storyboards` — L10939
- `_llm_bgm_description` — L11040
- `_bgm_contains_vocals` — L11079
- `generate_bgm` — L11113
- `_arg_value` — L11262
- `_infer_mtv_singer` — L11271
- `_ensure_mtv_singer_ip` — L11285
- `_mtv_source_lyrics` — L11340
- `_mtv_build_plan` — L11352
- `_generate_mtv_song` — L11437
- `_trim_mtv_song` — L11476
- `_mtv_generate_visual_segments` — L11489
- `_mtv_ass_time` — L11715
- `_mtv_ass_escape` — L11724
- `_mtv_wrap_lyric` — L11730
- `_mtv_vocal_span_from_asr` — L11755
- `_mtv_split_lyric_clauses` — L11799
- `_mtv_split_lyric_phrases` — L11811
- `_mtv_norm_zh` — L11824
- `_mtv_best_phrase_offset` — L11828
- `_mtv_asr_phrase_records` — L11848
- `_mtv_alignment_from_script` — L11891
- `_mtv_split_span` — L11944
- `_mtv_song_slice` — L11954
- `_mtv_normalize_segment_duration` — L11962
- `_mtv_static_fallback_segment` — L11998
- `_mtv_lip_sync_segment` — L12020
- `_write_mtv_subtitles` — L12161
- `_mtv_concat_and_render` — L12233
- `run_mtv_pipeline` — L12283
- `_b68_clamp_scene_durations_to_werydance_bounds` — L12306
- `step6_parallel` — L12366

---

### 第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）
Range: **L12698 – L18961** (6264 lines)

**Sub-sections:**
- _B92 (2026-06-05): 轨迹标记运镜 (Seedance 红线技法)_ — L14168-16695 (2528 lines)
- _PR-A (2026-05-27): merged_a 合并跑 helpers_ — L16696-18696 (2001 lines)
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L18697-18739 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L18740-18777 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回时间轴锚定音轨_ — L18778-18916 (139 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L18917-18961 (45 lines)

**Top-level constants:**
- `_PR3B1_SHOT_TYPE_ENUM` — L13488
- `_PR3B1_CAMERA_ANGLE_ENUM` — L13492
- `_PR3B1_LIGHTING_ENUM` — L13497
- `_PR3B1_CAMERA_MOTION_ENUM` — L13502
- `_SEEDANCE_CAMERA_GRAMMAR` — L13526
- `_DOLLY_ZOOM_EMOTIONS` — L13539
- `_GRAND_EMOTIONS` — L13544
- `_SEEDANCE_CAMERA_COMPACT` — L13549
- `_B92_HIDE_NEGATIVES` — L14171
- `_EMOTION_NARRATION_STYLE_MAP` — L14862

**Functions:**
- `_generate_motion_prompts` — L12701
- `_motion_tasks_file` — L12768
- `_motion_qa_file` — L12774
- `_append_motion_qa` — L12778
- `_finalize_motion_qa` — L12802
- `_lip_sync_tasks_file` — L12886
- `_lip_sync_tasks_lock_file` — L12890
- `_lip_sync_tasks_guard` — L12895
- `_normalize_generation_interface` — L12908
- `_generation_task_record` — L12918
- `_normalize_cached_task` — L12936
- `_load_generation_tasks` — L12963
- `_atomic_write_json` — L12980
- `_load_motion_tasks` — L13005
- `_save_motion_task` — L13011
- `_remove_motion_task` — L13031
- `_load_lip_sync_tasks` — L13038
- `_mtv_lip_sync_task_key` — L13045
- `_merged_lip_sync_task_key` — L13049
- `_lip_sync_task_indices` — L13053
- `_find_overlapping_lip_sync_task` — L13074
- `_lip_sync_conflict_info` — L13091
- `_is_reusable_lip_sync_raw_video` — L13102
- `_lip_sync_group_raw_path` — L13112
- `_find_merged_lip_sync_task` — L13117
- `_save_lip_sync_task` — L13126
- `_submit_lip_sync_task_transaction` — L13152
- `_is_lip_sync_submission_reservation` — L13234
- `_remove_lip_sync_task` — L13244
- `_video_visual_motion_qa` — L13257
- `_motion_output_qa` — L13329
- `_has_audio_stream` — L13374
- `_normalize_motion_video` — L13385
- `_motion_poll_and_download` — L13435
- `_validate_enum_field` — L13508
- `_seedance_camera_directive` — L13564
- `_build_motion_video_prompt` — L13584
- `_short_board_text` — L13640
- `_wrap_board_text` — L13647
- `_storyboard_font` — L13678
- `_draw_storyboard_arrow` — L13693
- `_build_annotated_storyboard_reference` — L13707
- `_plain_caption_text` — L13808
- `_werydance_caption_request` — L13816
- `_werydance_caption_instruction` — L13843
- `_werydance_negative_prompt` — L13855
- `_motion_reference_prompt` — L13877
- `_motion_audio_dub_prompt` — L13900
- `_motion_audio_dub_poll_and_download` — L13934
- `_try_motion_audio_dub_video` — L14000
- `_b92_enabled` — L14177
- `_b92_propose_path` — L14181
- `_b92_draw_path` — L14222
- `_b92_trim_lead_frames` — L14251
- `_b92_trajectory_prompt` — L14280
- `_b92_apply_trajectory` — L14295
- `_b92_preplan_paths` — L14316
- `_try_motion_reference_video` — L14340
- `_resume_motion_task` — L14477
- `_motion_one_scene` — L14509
- `_grid_multiref_tasks_file` — L14631
- `_previs_page_tasks_file` — L14635
- `_load_grid_multiref_tasks` — L14639
- `_load_previs_page_tasks` — L14646
- `_save_grid_multiref_task` — L14653
- `_save_previs_page_task` — L14670
- `_remove_grid_multiref_task` — L14687
- `_remove_previs_page_task` — L14694
- `_poll_video_task_download` — L14701
- `_grid_multiref_group_size` — L14750
- `_grid_multiref_adaptive_group_size` — L14760
- `_grid_multiref_duration` — L14784
- `_grid_multiref_tts_buffer_factor` — L14822
- `_grid_multiref_tts_duration_buffered` — L14836
- `_grid_multiref_segment_max_stretch` — L14852
- `_voice_clone_emotion_style` — L14886
- `_grid_multiref_prompt` — L14909
- `_write_grid_multiref_motion_qa` — L14989
- `_write_previs_page_motion_qa` — L14999
- `_write_storyboard_trailer_qa` — L15009
- `_write_character_trailer_qa` — L15019
- `_write_grid_multiref_segment_qa` — L15029
- `_motion_compare_record` — L15039
- `_write_storyboard_motion_compare_qa` — L15061
- `_scene_segment_duration` — L15097
- `_apply_grid_multiref_segments` — L15116
- `_previs_page_duration` — L15321
- `_previs_page_group_prompt` — L15332
- `_previs_page_groups` — L15358
- `_storyboard_trailer_duration` — L15373
- `_storyboard_trailer_prompt` — L15383
- `_character_trailer_max_shots` — L15411
- `_character_trailer_shot_duration` — L15419
- `_character_trailer_prompt` — L15435
- `_concat_character_trailer_segments` — L15450
- `_generate_character_trailer_motion` — L15489
- `_multi_trailer_prompt_for_group` — L15597
- `_generate_multi_trailer_segments` — L15620
- `_generate_storyboard_trailer_motion` — L15731
- `_generate_previs_page_motion_segments` — L15806
- `_generate_grid_multiref_motion_segments` — L15924
- `_grid_multiref_concat_groups` — L16252
- `_grid_multiref_concat_groups_partial` — L16269
- `_grid_multiref_concat_paths` — L16287
- `_lip_sync_slot_duration` — L16329
- `_adsd_lip_sync_prompt` — L16336
- `_adsd_broll_motion_prompt` — L16382
- `_adsd_action_b_motion_prompt` — L16430
- `_adsd_silent_b_motion_prompt` — L16476
- `_adsd_narrated_b_audio_dub_prompt` — L16517
- `_adsd_almighty_audio_dub_prompt` — L16561
- `_postprocess_lip_sync_segment` — L16602
- `_detect_audio_leading_silence` — L16674
- `_concat_audio_files_for_group` — L16699
- `_split_lip_sync_raw_by_durations` — L16722
- `_postprocess_audio_dub_segment` — L16757
- `_lips_change_repair_segment` — L16885
- `_load_lips_change_requested_turns` — L16970
- `_parse_turn_set` — L16987
- `_load_motion_voice_repair_turns` — L17009
- `_voice_assets_file` — L17021
- `_load_voice_assets` — L17028
- `_build_combined_voice_reference` — L17047
- `_select_voice_asset_reference` — L17089
- `_lip_sync_poll_download_and_process` — L17165
- `_resume_lip_sync_task` — L17241
- `_poll_download_and_process_lip_sync_group` — L17270
- `_lip_sync_one_group` — L17434
- `_lip_sync_one_scene` — L17760
- `step66_adsd_lip_sync` — L18159
- `step65_motion` — L18512
- `step65_grid_multiref_motion_qa` — L18669
- `_sanitize_scene_for_state` — L18698
- `_save_pipeline_state` — L18717
- `_retime_after_audio_dub` — L18741
- `_build_voice_clone_hybrid_audio` — L18779
- `_build_dynamic_bgm` — L18918

---

### 第七步：拼接视频轨
Range: **L18962 – L19297** (336 lines)

**Functions:**
- `_rescue_motion_image_to_video` — L18963
- `_rescue_motion_text_to_video` — L18998
- `step7_concat` — L19029

---

### 第八步：生成 ASS 字幕
Range: **L19298 – L20256** (959 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L19577-20256 (680 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L19299
- `_word_timings_for_subtitle_align` — L19325
- `_align_segments_via_asr` — L19366
- `_b61_1_asr_turn_boundaries` — L19409
- `step8_subtitles` — L19471
- `_read_output_json` — L19977
- `_qa_file_pass` — L19988
- `_ass_has_dialogue` — L19995
- `_write_adsd_delivery_qa` — L20005
- `_write_bgm_only_qa` — L20145

---

### 第九步：最终合成
Range: **L20257 – L20547** (291 lines)

**Functions:**
- `step9_render` — L20258

---

### 第十步：推送 Telegram
Range: **L20548 – L22430** (1883 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L21654-21763 (110 lines)
- _B70 (2026-05-30) TG oversize policy helpers_ — L21764-22235 (472 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L22236-22240 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L22241-22305 (65 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L22306-22352 (47 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L22353-22430 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L20917
- `PANTONE_FALLBACK` — L20944
- `FESTIVAL_DATE_TAG` — L21058

**Functions:**
- `_generate_caption` — L20549
- `_overlay_title_on_cover` — L20787
- `_prepare_tg_photo` — L20897
- `_get_pantone_for_date` — L20947
- `_llm_bottom_note` — L20972
- `_get_bottom_note` — L21002
- `_get_date_tag` — L21080
- `_shrink_to_b64` — L21102
- `_llm_check_scenes_anomalies` — L21118
- `_llm_check_cover_unique` — L21171
- `_llm_check_cover_quality` — L21201
- `_try_almanac_cover` — L21243
- `_generate_cover_image` — L21414
- `_async_kickoff_cover_caption` — L21661
- `_await_async_cover_caption` — L21737
- `_b70_env_float` — L21767
- `_b70_split_and_deliver` — L21782
- `_b70_send_document_first` — L21895
- `step10_deliver` — L21932

---

### 主流程
Range: **L22431 – L22685** (255 lines)

**Functions:**
- `_print_execution_plan` — L22432
- `_write_run_timings` — L22491
- `main` — L22520

---
