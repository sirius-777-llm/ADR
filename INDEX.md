# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (22855 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-129 (129 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L130-2605 (2476 lines · 75 fn · 5 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L2606-5257 (2652 lines · 33 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L5258-6490 (1233 lines · 22 fn · 2 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L6491-7042 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L7043-12784 (5742 lines · 131 fn · 8 sub)
- [`第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）`](#第-6-5-步-动态化-hads-vads-默认-on---no-motion-关) — L12785-19131 (6347 lines · 137 fn · 6 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L19132-19467 (336 lines · 3 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L19468-20426 (959 lines · 10 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L20427-20717 (291 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L20718-22600 (1883 lines · 19 fn · 6 sub)
- [`主流程`](#主流程) — L22601-22855 (255 lines · 3 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L129** (129 lines)

**Sub-sections:**
- _老黄历数据模块_ — L37-129 (93 lines)

**Functions:**
- `get_almanac_data` — L65

---

### 配置
Range: **L130 – L2605** (2476 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L372-501 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L502-1245 (744 lines)
- _工具函数_ — L1246-1663 (418 lines)
- _B87 纹理档系统：LLM 提名 + 代码护栏 + 确定性渲染_ — L1664-1926 (263 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1927-2605 (679 lines)

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
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1657
- `_TEXTURE_MODE_ENUM` — L1665
- `_TEXTURE_SUFFIX_MAP` — L1670
- `_TEXTURE_BODY_DIRECTIVE` — L1697
- `_TEXTURE_SCENE_PHRASE` — L1704
- `_TEXTURE_GRID_PHRASE` — L1711
- `_TEXTURE_MOTION_PHRASE` — L1719
- `_LLM_TIER` — L2107
- `_TOPIC_MODIFIERS` — L2358
- `_TONE_PANTONE_OVERRIDE` — L2375

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
- `_is_llm_retryable_server_error` — L1609
- `_era_is_pre_photographic` — L1731
- `_texture_mode_fallback` — L1759
- `_texture_guardrail` — L1780
- `_set_active_texture_profile` — L1819
- `_active_texture_suffix` — L1832
- `_active_texture_body_directive` — L1836
- `_active_texture_scene_phrase` — L1840
- `_active_texture_grid_phrase` — L1844
- `_active_texture_motion_phrase` — L1848
- `_inject_image2_quality_suffix` — L1852
- `submit_text_to_image` — L1872
- `req_post` — L1908
- `req_get` — L1922
- `_tg_probe_send` — L1930
- `_tg_probe_delete` — L1950
- `_tg_upload_with_probe_gap` — L1963
- `poll` — L2003
- `poll_podcast` — L2028
- `poll_task_status` — L2050
- `poll_storyboard_task` — L2072
- `tier_chat` — L2115
- `chat` — L2121
- `pick_image_model` — L2204
- `detect_topic_meta` — L2229
- `_topic_culture_guard` — L2279
- `_write_cultural_visual_qa` — L2305
- `is_1919_global_topic` — L2352
- `_strip_topic_modifiers` — L2363
- `apply_1919_global_guardrails` — L2381
- `build_1919_global_cover_prompt` — L2410
- `_shot_blueprint_enums` — L2442
- `build_shot_blueprint` — L2518
- `ffprobe_duration` — L2544
- `ffprobe_video_size` — L2555
- `_video_decode_probe` — L2576
- `ffmpeg` — L2594

---

### 第一步：双导演生成剧本
Range: **L2606 – L5257** (2652 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L4238-5257 (1020 lines)

**Top-level constants:**
- `_ENSEMBLE_CAP_BY_ROUTE` — L2758

**Functions:**
- `_extract_json_array` — L2607
- `_extract_json_object` — L2617
- `_voice_for_speaker` — L2627
- `_adsd_gender_from_voice` — L2663
- `_adsd_infer_gender_from_speaker` — L2671
- `_adsd_gender_lock_phrase` — L2680
- `_adsd_visual_subject_has_gender_conflict` — L2695
- `_adsd_default_roles` — L2707
- `_adsd_allows_media_role` — L2712
- `_adsd_role_candidates` — L2720
- `_adsd_dialogue_shape` — L2747
- `_ensemble_speaker_cap` — L2769
- `_ip_voice_asset_for_speaker` — L2782
- `_finalize_adsd_turns` — L2806
- `_parse_adsd_override_turns` — L2852
- `_parse_timecode_seconds` — L2945
- `_clean_override_line_text` — L2954
- `_parse_override_script_text` — L2960
- `_adsd_pov_contract` — L2994
- `_load_audit_blacklist_block` — L3007
- `_generate_adsd_dialogue_turns` — L3045
- `_broll_rhythm_reviewer` — L3472
- `_sweep_speaker_field` — L3579
- `_should_run_immersion_qa` — L3639
- `_adsd_immersion_qa_rewrite_turns` — L3662
- `_adsd_visual_contract` — L3726
- `_parse_risk_score` — L3778
- `_check_high_risk_hard_abort` — L3807
- `_maybe_neutralize_topic` — L3834
- `_apply_render_budget_scene_cap` — L3873
- `_apply_llm_mode_decision` — L3900
- `step1_script` — L3955
- `_write_ads_retention_qa` — L5201

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L5258 – L6490** (1233 lines)

**Sub-sections:**
- _B88: 内容审核(1002) → 分级软化 → 中性兜底句 → 静音 backstop，绝不崩管线_ — L5953-5981 (29 lines)
- _非内容审核(网络/transient): 有限退避重试，耗尽才抛_ — L5982-6490 (509 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L5333
- `_ADSD_POLICY_REWRITE_TERMS` — L5339
- `_TTS_SAFE_FALLBACK_LINE` — L5440
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L5508

**Functions:**
- `_openai_tts_fallback` — L5259
- `_edge_tts_fallback` — L5305
- `_sanitize_for_external_api` — L5364
- `_is_content_policy_error` — L5373
- `_rewrite_adsd_tts_text_for_policy` — L5387
- `_tts_safe_fallback_line` — L5449
- `_tts_silent_placeholder` — L5454
- `_record_adsd_tts_rewrite` — L5489
- `_build_silence_mp3` — L5514
- `_audio_duration_seconds` — L5527
- `_text_to_audio_master_voice_timed` — L5539
- `_text_to_audio_master_voice` — L5664
- `step2_master_voice` — L5777
- `_tts_turn_to_audio` — L5905
- `_asr_verify_dialogue_audio` — L5992
- `_asr_verify_dialogue_turns` — L6054
- `_normalize_cn_number_token` — L6096
- `_compact_zh_text` — L6118
- `_write_adsd_asr_text_qa` — L6125
- `_write_adsd_speaker_focus_qa` — L6164
- `_write_adsd_gender_voice_qa` — L6224
- `step2_dialogue_voice` — L6277

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L6491 – L7042** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L6498-6620 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L6621-6655 (35 lines)
- _第二层：字符数插值_ — L6656-6680 (25 lines)
- _第三层：silencedetect 物理校准_ — L6681-7042 (362 lines)

**Functions:**
- `_detect_silences` — L6499
- `_calibrate_boundaries` — L6534
- `_enforce_monotonic` — L6568
- `_manual_override_segments` — L6580
- `_calc_sentence_boundaries` — L6601
- `step345_timeline` — L6712
- `_analyze_bgm_energy_cuts` — L6771
- `_snap_bgm_only_boundaries` — L6834
- `step345_bgm_only_timeline` — L6894

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L7043 – L12784** (5742 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L8272-8322 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L8323-9181 (859 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L9182-9669 (488 lines)
- _Speaker IP Card (2026-05-21)_ — L9670-11314 (1645 lines)
- _MTV：原创歌曲 + 主唱人物库 + WeryDance MV_ — L11315-12384 (1070 lines)
- _B68 (2026-05-30) WERYDANCE 段长合规 gate_ — L12385-12617 (233 lines)
- _审批流程_ — L12618-12674 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L12675-12784 (110 lines)

**Top-level constants:**
- `_CORE_TERMS_STOP_WORDS` — L7445
- `CHARACTER_META_GRID_COSTUMES` — L8278
- `CHARACTER_META_GRID_POSES` — L8279
- `CHARACTER_META_GRID_SCENES` — L8280
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L8283
- `_SFX_TYPE_ENUM` — L8651
- `_SFX_INTENSITY_ENUM` — L8656
- `_SFX_POSITION_ENUM` — L8657
- `_GRAIN_LEVEL_ENUM` — L8802
- `_CUSTOM_STYLE_BANNED_NAMES` — L9237
- `_DUANGE_XING_TEXT` — L11316

**Functions:**
- `_extract_img_url` — L7044
- `_extract_img_urls` — L7066
- `_extract_video_url` — L7099
- `_count_bands` — L7124
- `_detect_contact_sheet_like_image` — L7136
- `_file_sha256` — L7197
- `_load_upload_cache` — L7210
- `_save_upload_cache` — L7219
- `_cached_upload_url` — L7227
- `_store_upload_url` — L7244
- `_guess_upload_mime` — L7254
- `_upload_to_weryai` — L7277
- `_send_for_approval` — L7338
- `_wait_approval` — L7402
- `_render_still_segment` — L7414
- `_extract_core_terms` — L7451
- `_scene_text_visual_alignment` — L7470
- `_write_text_visual_alignment_qa` — L7491
- `_scene_motion_action_plan` — L7514
- `_ensure_motion_action_plan` — L7568
- `_motion_action_block` — L7577
- `_motion_plan_for_qa` — L7605
- `_write_motion_action_plan_qa` — L7615
- `_write_motion_bridge_refs_qa` — L7645
- `_motion_bridge_ref_prompt` — L7652
- `generate_motion_bridge_refs_gpt_image2` — L7685
- `generate_image` — L7800
- `generate_storyboard_images_gpt_image2` — L7847
- `_storyboard_grid_aspect` — L8033
- `_storyboard_grid_cols_rows` — L8040
- `_storyboard_grid_prompt` — L8062
- `_storyboard_grid_prompt_limit` — L8120
- `_is_prompt_limit_response` — L8124
- `_production_storyboard_prompt` — L8130
- `_write_production_storyboard_page_qa` — L8164
- `_character_sheet_prompt` — L8174
- `_is_audit_blocked` — L8300
- `_paraphrase_sensitive_dialogue` — L8313
- `_topic_cache_dir` — L8327
- `_topic_cache_path` — L8333
- `_load_topic_decomposition_cache` — L8346
- `_save_topic_decomposition_cache` — L8364
- `_briefs_dir` — L8401
- `_brief_path` — L8407
- `_empty_brief` — L8412
- `_deep_merge_brief_skeleton` — L8452
- `_load_brief` — L8466
- `_save_brief` — L8490
- `_brief_get` — L8509
- `_brief_field` — L8521
- `_brief_set` — L8532
- `_brief_claim` — L8548
- `_brief_agent_status` — L8591
- `_brief_from_topic_decomposition` — L8604
- `_rule_based_sfx_design` — L8660
- `_validate_sfx_entry` — L8711
- `_audio_director_design` — L8749
- `_hex_color_validate` — L8805
- `_rule_based_art_design` — L8817
- `_validate_art_design` — L8898
- `_art_director_design` — L8936
- `_coordinator_review` — L8958
- `_llm_topic_decomposition` — L9059
- `_validate_custom_visual_style` — L9244
- `_resolve_route_style` — L9266
- `_director_route_block` — L9291
- `_llm_infer_meta_grid_template` — L9358
- `_resolve_meta_grid_template` — L9415
- `_infer_meta_grid_costume` — L9458
- `_infer_meta_grid_pose` — L9507
- `_adsd_meta_grid_call_prompt` — L9554
- `_meta_grid_panel_index` — L9596
- `_migrate_speaker_ip` — L9676
- `_speaker_ips_dir` — L9701
- `_list_speaker_ips` — L9708
- `_match_speaker_ip` — L9722
- `_build_speaker_ip_context_for_script` — L9742
- `_ip_usage_stats` — L9798
- `_recommend_related_ips` — L9816
- `_save_speaker_ip` — L9841
- `_record_speaker_usage_history` — L9850
- `_format_speaker_usage_history_for_prompt` — L9897
- `_llm_infer_ip_skeleton` — L9915
- `_llm_pick_voice_asset_for_ip` — L9960
- `_auto_incubate_missing_ips` — L10009
- `_character_meta_grid_cache_dir` — L10093
- `_character_meta_grid_cache_path` — L10101
- `_character_meta_grid_cache_legacy_path` — L10109
- `_character_meta_grid_path` — L10116
- `generate_character_meta_grid_gpt_image2` — L10122
- `_generate_all_character_meta_grids` — L10294
- `_write_character_sheet_qa` — L10335
- `generate_character_sheet_gpt_image2` — L10345
- `generate_production_storyboard_page_gpt_image2` — L10445
- `_qa_clean_storyboard_panel` — L10508
- `_crop_storyboard_grid_panels` — L10689
- `generate_storyboard_grid_gpt_image2` — L10736
- `_gpt_image2_direct_annotated_aspect` — L10968
- `_gpt_image2_direct_annotated_prompt` — L10975
- `generate_gpt_image2_direct_annotated_storyboards` — L11005
- `_llm_bgm_description` — L11106
- `_bgm_contains_vocals` — L11145
- `generate_bgm` — L11179
- `_arg_value` — L11328
- `_infer_mtv_singer` — L11337
- `_ensure_mtv_singer_ip` — L11351
- `_mtv_source_lyrics` — L11406
- `_mtv_build_plan` — L11418
- `_generate_mtv_song` — L11503
- `_trim_mtv_song` — L11542
- `_mtv_generate_visual_segments` — L11555
- `_mtv_ass_time` — L11790
- `_mtv_ass_escape` — L11799
- `_mtv_wrap_lyric` — L11805
- `_mtv_vocal_span_from_asr` — L11830
- `_mtv_split_lyric_clauses` — L11874
- `_mtv_split_lyric_phrases` — L11886
- `_mtv_norm_zh` — L11899
- `_mtv_best_phrase_offset` — L11903
- `_mtv_asr_phrase_records` — L11923
- `_mtv_alignment_from_script` — L11966
- `_mtv_split_span` — L12019
- `_mtv_song_slice` — L12029
- `_mtv_normalize_segment_duration` — L12037
- `_mtv_static_fallback_segment` — L12073
- `_mtv_lip_sync_segment` — L12095
- `_write_mtv_subtitles` — L12248
- `_mtv_concat_and_render` — L12320
- `run_mtv_pipeline` — L12370
- `_b68_clamp_scene_durations_to_werydance_bounds` — L12393
- `step6_parallel` — L12453

---

### 第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）
Range: **L12785 – L19131** (6347 lines)

**Sub-sections:**
- _B92 (2026-06-05): 轨迹标记运镜 (Seedance 红线技法)_ — L14281-16808 (2528 lines)
- _PR-A (2026-05-27): merged_a 合并跑 helpers_ — L16809-18866 (2058 lines)
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L18867-18909 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L18910-18947 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回时间轴锚定音轨_ — L18948-19086 (139 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L19087-19131 (45 lines)

**Top-level constants:**
- `_PR3B1_SHOT_TYPE_ENUM` — L13601
- `_PR3B1_CAMERA_ANGLE_ENUM` — L13605
- `_PR3B1_LIGHTING_ENUM` — L13610
- `_PR3B1_CAMERA_MOTION_ENUM` — L13615
- `_SEEDANCE_CAMERA_GRAMMAR` — L13639
- `_DOLLY_ZOOM_EMOTIONS` — L13652
- `_GRAND_EMOTIONS` — L13657
- `_SEEDANCE_CAMERA_COMPACT` — L13662
- `_B92_HIDE_NEGATIVES` — L14284
- `_EMOTION_NARRATION_STYLE_MAP` — L14975

**Functions:**
- `_generate_motion_prompts` — L12788
- `_motion_tasks_file` — L12855
- `_motion_qa_file` — L12861
- `_append_motion_qa` — L12865
- `_finalize_motion_qa` — L12889
- `_lip_sync_tasks_file` — L12973
- `_lip_sync_tasks_lock_file` — L12977
- `_lip_sync_tasks_guard` — L12982
- `_normalize_generation_interface` — L12995
- `_generation_task_record` — L13005
- `_normalize_cached_task` — L13023
- `_load_generation_tasks` — L13050
- `_atomic_write_json` — L13067
- `_load_motion_tasks` — L13092
- `_save_motion_task` — L13098
- `_remove_motion_task` — L13118
- `_load_lip_sync_tasks` — L13125
- `_mtv_lip_sync_task_key` — L13132
- `_merged_lip_sync_task_key` — L13136
- `_lip_sync_task_indices` — L13140
- `_find_overlapping_lip_sync_task` — L13168
- `_lip_sync_conflict_info` — L13185
- `_is_reusable_lip_sync_raw_video` — L13196
- `_lip_sync_group_raw_path` — L13206
- `_find_merged_lip_sync_task` — L13211
- `_save_lip_sync_task` — L13220
- `_submit_lip_sync_task_transaction` — L13246
- `_is_lip_sync_submission_reservation` — L13347
- `_remove_lip_sync_task` — L13357
- `_video_visual_motion_qa` — L13370
- `_motion_output_qa` — L13442
- `_has_audio_stream` — L13487
- `_normalize_motion_video` — L13498
- `_motion_poll_and_download` — L13548
- `_validate_enum_field` — L13621
- `_seedance_camera_directive` — L13677
- `_build_motion_video_prompt` — L13697
- `_short_board_text` — L13753
- `_wrap_board_text` — L13760
- `_storyboard_font` — L13791
- `_draw_storyboard_arrow` — L13806
- `_build_annotated_storyboard_reference` — L13820
- `_plain_caption_text` — L13921
- `_werydance_caption_request` — L13929
- `_werydance_caption_instruction` — L13956
- `_werydance_negative_prompt` — L13968
- `_motion_reference_prompt` — L13990
- `_motion_audio_dub_prompt` — L14013
- `_motion_audio_dub_poll_and_download` — L14047
- `_try_motion_audio_dub_video` — L14113
- `_b92_enabled` — L14290
- `_b92_propose_path` — L14294
- `_b92_draw_path` — L14335
- `_b92_trim_lead_frames` — L14364
- `_b92_trajectory_prompt` — L14393
- `_b92_apply_trajectory` — L14408
- `_b92_preplan_paths` — L14429
- `_try_motion_reference_video` — L14453
- `_resume_motion_task` — L14590
- `_motion_one_scene` — L14622
- `_grid_multiref_tasks_file` — L14744
- `_previs_page_tasks_file` — L14748
- `_load_grid_multiref_tasks` — L14752
- `_load_previs_page_tasks` — L14759
- `_save_grid_multiref_task` — L14766
- `_save_previs_page_task` — L14783
- `_remove_grid_multiref_task` — L14800
- `_remove_previs_page_task` — L14807
- `_poll_video_task_download` — L14814
- `_grid_multiref_group_size` — L14863
- `_grid_multiref_adaptive_group_size` — L14873
- `_grid_multiref_duration` — L14897
- `_grid_multiref_tts_buffer_factor` — L14935
- `_grid_multiref_tts_duration_buffered` — L14949
- `_grid_multiref_segment_max_stretch` — L14965
- `_voice_clone_emotion_style` — L14999
- `_grid_multiref_prompt` — L15022
- `_write_grid_multiref_motion_qa` — L15102
- `_write_previs_page_motion_qa` — L15112
- `_write_storyboard_trailer_qa` — L15122
- `_write_character_trailer_qa` — L15132
- `_write_grid_multiref_segment_qa` — L15142
- `_motion_compare_record` — L15152
- `_write_storyboard_motion_compare_qa` — L15174
- `_scene_segment_duration` — L15210
- `_apply_grid_multiref_segments` — L15229
- `_previs_page_duration` — L15434
- `_previs_page_group_prompt` — L15445
- `_previs_page_groups` — L15471
- `_storyboard_trailer_duration` — L15486
- `_storyboard_trailer_prompt` — L15496
- `_character_trailer_max_shots` — L15524
- `_character_trailer_shot_duration` — L15532
- `_character_trailer_prompt` — L15548
- `_concat_character_trailer_segments` — L15563
- `_generate_character_trailer_motion` — L15602
- `_multi_trailer_prompt_for_group` — L15710
- `_generate_multi_trailer_segments` — L15733
- `_generate_storyboard_trailer_motion` — L15844
- `_generate_previs_page_motion_segments` — L15919
- `_generate_grid_multiref_motion_segments` — L16037
- `_grid_multiref_concat_groups` — L16365
- `_grid_multiref_concat_groups_partial` — L16382
- `_grid_multiref_concat_paths` — L16400
- `_lip_sync_slot_duration` — L16442
- `_adsd_lip_sync_prompt` — L16449
- `_adsd_broll_motion_prompt` — L16495
- `_adsd_action_b_motion_prompt` — L16543
- `_adsd_silent_b_motion_prompt` — L16589
- `_adsd_narrated_b_audio_dub_prompt` — L16630
- `_adsd_almighty_audio_dub_prompt` — L16674
- `_postprocess_lip_sync_segment` — L16715
- `_detect_audio_leading_silence` — L16787
- `_concat_audio_files_for_group` — L16812
- `_split_lip_sync_raw_by_durations` — L16835
- `_postprocess_audio_dub_segment` — L16870
- `_lips_change_repair_segment` — L16998
- `_load_lips_change_requested_turns` — L17083
- `_parse_turn_set` — L17100
- `_load_motion_voice_repair_turns` — L17122
- `_voice_assets_file` — L17134
- `_load_voice_assets` — L17141
- `_build_combined_voice_reference` — L17160
- `_select_voice_asset_reference` — L17202
- `_lip_sync_poll_download_and_process` — L17278
- `_resume_lip_sync_task` — L17387
- `_poll_download_and_process_lip_sync_group` — L17416
- `_lip_sync_one_group` — L17580
- `_lip_sync_one_scene` — L17918
- `step66_adsd_lip_sync` — L18329
- `step65_motion` — L18682
- `step65_grid_multiref_motion_qa` — L18839
- `_sanitize_scene_for_state` — L18868
- `_save_pipeline_state` — L18887
- `_retime_after_audio_dub` — L18911
- `_build_voice_clone_hybrid_audio` — L18949
- `_build_dynamic_bgm` — L19088

---

### 第七步：拼接视频轨
Range: **L19132 – L19467** (336 lines)

**Functions:**
- `_rescue_motion_image_to_video` — L19133
- `_rescue_motion_text_to_video` — L19168
- `step7_concat` — L19199

---

### 第八步：生成 ASS 字幕
Range: **L19468 – L20426** (959 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L19747-20426 (680 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L19469
- `_word_timings_for_subtitle_align` — L19495
- `_align_segments_via_asr` — L19536
- `_b61_1_asr_turn_boundaries` — L19579
- `step8_subtitles` — L19641
- `_read_output_json` — L20147
- `_qa_file_pass` — L20158
- `_ass_has_dialogue` — L20165
- `_write_adsd_delivery_qa` — L20175
- `_write_bgm_only_qa` — L20315

---

### 第九步：最终合成
Range: **L20427 – L20717** (291 lines)

**Functions:**
- `step9_render` — L20428

---

### 第十步：推送 Telegram
Range: **L20718 – L22600** (1883 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L21824-21933 (110 lines)
- _B70 (2026-05-30) TG oversize policy helpers_ — L21934-22405 (472 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L22406-22410 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L22411-22475 (65 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L22476-22522 (47 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L22523-22600 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L21087
- `PANTONE_FALLBACK` — L21114
- `FESTIVAL_DATE_TAG` — L21228

**Functions:**
- `_generate_caption` — L20719
- `_overlay_title_on_cover` — L20957
- `_prepare_tg_photo` — L21067
- `_get_pantone_for_date` — L21117
- `_llm_bottom_note` — L21142
- `_get_bottom_note` — L21172
- `_get_date_tag` — L21250
- `_shrink_to_b64` — L21272
- `_llm_check_scenes_anomalies` — L21288
- `_llm_check_cover_unique` — L21341
- `_llm_check_cover_quality` — L21371
- `_try_almanac_cover` — L21413
- `_generate_cover_image` — L21584
- `_async_kickoff_cover_caption` — L21831
- `_await_async_cover_caption` — L21907
- `_b70_env_float` — L21937
- `_b70_split_and_deliver` — L21952
- `_b70_send_document_first` — L22065
- `step10_deliver` — L22102

---

### 主流程
Range: **L22601 – L22855** (255 lines)

**Functions:**
- `_print_execution_plan` — L22602
- `_write_run_timings` — L22661
- `main` — L22690

---
