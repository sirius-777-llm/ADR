# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (19061 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-2208 (2087 lines · 62 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L2209-4695 (2487 lines · 31 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L4696-5827 (1132 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L5828-6379 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L6380-10877 (4498 lines · 101 fn · 6 sub)
- [`第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）`](#第-6-5-步-动态化-hads-vads-默认-on---no-motion-关) — L10878-15875 (4998 lines · 106 fn · 5 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L15876-16135 (260 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L16136-16938 (803 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L16939-17214 (276 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L17215-18876 (1662 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L18877-19061 (185 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L2208** (2087 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L324-453 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L454-1195 (742 lines)
- _工具函数_ — L1196-1572 (377 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1573-2208 (636 lines)

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
- `_TG_DASHBOARD_STAGES` — L1209
- `_TG_NOISY_PATTERNS` — L1224
- `_TG_IMMEDIATE_PATTERNS` — L1242
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1502
- `_LLM_TIER` — L1750
- `_TOPIC_MODIFIERS` — L1961
- `_TONE_PANTONE_OVERRIDE` — L1978

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
- `log` — L1197
- `_tg_send_raw` — L1265
- `_tg_matches` — L1281
- `_tg_summarize` — L1285
- `_tg_dashboard_stage_for` — L1292
- `_tg_progress_bar` — L1300
- `_tg_dashboard_text` — L1306
- `_tg_dashboard_update` — L1324
- `_tg_maybe_digest` — L1361
- `tg` — L1376
- `_wait_image_submit_slot` — L1425
- `_wait_motion_submit_slot` — L1438
- `_is_rate_limited_error` — L1451
- `_is_rate_limited_response` — L1461
- `_is_llm_rate_limited_error` — L1482
- `_inject_image2_quality_suffix` — L1510
- `submit_text_to_image` — L1524
- `req_post` — L1554
- `req_get` — L1568
- `_tg_probe_send` — L1576
- `_tg_probe_delete` — L1596
- `_tg_upload_with_probe_gap` — L1609
- `poll` — L1649
- `poll_podcast` — L1674
- `poll_task_status` — L1696
- `poll_storyboard_task` — L1718
- `tier_chat` — L1758
- `chat` — L1764
- `pick_image_model` — L1807
- `detect_topic_meta` — L1832
- `_topic_culture_guard` — L1882
- `_write_cultural_visual_qa` — L1908
- `is_1919_global_topic` — L1955
- `_strip_topic_modifiers` — L1966
- `apply_1919_global_guardrails` — L1984
- `build_1919_global_cover_prompt` — L2013
- `_shot_blueprint_enums` — L2045
- `build_shot_blueprint` — L2121
- `ffprobe_duration` — L2147
- `ffprobe_video_size` — L2158
- `_video_decode_probe` — L2179
- `ffmpeg` — L2197

---

### 第一步：双导演生成剧本
Range: **L2209 – L4695** (2487 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L3709-4695 (987 lines)

**Top-level constants:**
- `_ENSEMBLE_CAP_BY_ROUTE` — L2357

**Functions:**
- `_extract_json_array` — L2210
- `_extract_json_object` — L2220
- `_voice_for_speaker` — L2230
- `_adsd_gender_from_voice` — L2266
- `_adsd_infer_gender_from_speaker` — L2274
- `_adsd_gender_lock_phrase` — L2283
- `_adsd_visual_subject_has_gender_conflict` — L2298
- `_adsd_default_roles` — L2310
- `_adsd_allows_media_role` — L2315
- `_adsd_role_candidates` — L2323
- `_adsd_dialogue_shape` — L2346
- `_ensemble_speaker_cap` — L2368
- `_ip_voice_asset_for_speaker` — L2381
- `_finalize_adsd_turns` — L2405
- `_parse_adsd_override_turns` — L2451
- `_parse_timecode_seconds` — L2544
- `_clean_override_line_text` — L2553
- `_parse_override_script_text` — L2559
- `_adsd_pov_contract` — L2593
- `_load_audit_blacklist_block` — L2606
- `_generate_adsd_dialogue_turns` — L2644
- `_broll_rhythm_reviewer` — L3071
- `_sweep_speaker_field` — L3178
- `_should_run_immersion_qa` — L3238
- `_adsd_immersion_qa_rewrite_turns` — L3261
- `_adsd_visual_contract` — L3325
- `_parse_risk_score` — L3377
- `_check_high_risk_hard_abort` — L3406
- `_maybe_neutralize_topic` — L3433
- `step1_script` — L3472
- `_write_ads_retention_qa` — L4639

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L4696 – L5827** (1132 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L4771
- `_ADSD_POLICY_REWRITE_TERMS` — L4777
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L4868

**Functions:**
- `_openai_tts_fallback` — L4697
- `_edge_tts_fallback` — L4743
- `_sanitize_for_external_api` — L4786
- `_is_content_policy_error` — L4795
- `_rewrite_adsd_tts_text_for_policy` — L4809
- `_record_adsd_tts_rewrite` — L4849
- `_build_silence_mp3` — L4874
- `_audio_duration_seconds` — L4887
- `_text_to_audio_master_voice_timed` — L4899
- `_text_to_audio_master_voice` — L5024
- `step2_master_voice` — L5137
- `_tts_turn_to_audio` — L5265
- `_asr_verify_dialogue_audio` — L5329
- `_asr_verify_dialogue_turns` — L5391
- `_normalize_cn_number_token` — L5433
- `_compact_zh_text` — L5455
- `_write_adsd_asr_text_qa` — L5462
- `_write_adsd_speaker_focus_qa` — L5501
- `_write_adsd_gender_voice_qa` — L5561
- `step2_dialogue_voice` — L5614

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L5828 – L6379** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L5835-5957 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L5958-5992 (35 lines)
- _第二层：字符数插值_ — L5993-6017 (25 lines)
- _第三层：silencedetect 物理校准_ — L6018-6379 (362 lines)

**Functions:**
- `_detect_silences` — L5836
- `_calibrate_boundaries` — L5871
- `_enforce_monotonic` — L5905
- `_manual_override_segments` — L5917
- `_calc_sentence_boundaries` — L5938
- `step345_timeline` — L6049
- `_analyze_bgm_energy_cuts` — L6108
- `_snap_bgm_only_boundaries` — L6171
- `step345_bgm_only_timeline` — L6231

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L6380 – L10877** (4498 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L7601-7651 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L7652-8487 (836 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L8488-8922 (435 lines)
- _Speaker IP Card (2026-05-21)_ — L8923-10710 (1788 lines)
- _审批流程_ — L10711-10767 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L10768-10877 (110 lines)

**Top-level constants:**
- `_CORE_TERMS_STOP_WORDS` — L6775
- `CHARACTER_META_GRID_COSTUMES` — L7607
- `CHARACTER_META_GRID_POSES` — L7608
- `CHARACTER_META_GRID_SCENES` — L7609
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L7612
- `_SFX_TYPE_ENUM` — L7969
- `_SFX_INTENSITY_ENUM` — L7974
- `_SFX_POSITION_ENUM` — L7975
- `_GRAIN_LEVEL_ENUM` — L8120

**Functions:**
- `_extract_img_url` — L6381
- `_extract_img_urls` — L6403
- `_extract_video_url` — L6436
- `_count_bands` — L6461
- `_detect_contact_sheet_like_image` — L6473
- `_file_sha256` — L6534
- `_load_upload_cache` — L6547
- `_save_upload_cache` — L6556
- `_cached_upload_url` — L6564
- `_store_upload_url` — L6581
- `_guess_upload_mime` — L6591
- `_upload_to_weryai` — L6614
- `_send_for_approval` — L6668
- `_wait_approval` — L6732
- `_render_still_segment` — L6744
- `_extract_core_terms` — L6781
- `_scene_text_visual_alignment` — L6800
- `_write_text_visual_alignment_qa` — L6821
- `_scene_motion_action_plan` — L6844
- `_ensure_motion_action_plan` — L6898
- `_motion_action_block` — L6907
- `_motion_plan_for_qa` — L6935
- `_write_motion_action_plan_qa` — L6945
- `_write_motion_bridge_refs_qa` — L6975
- `_motion_bridge_ref_prompt` — L6982
- `generate_motion_bridge_refs_gpt_image2` — L7015
- `generate_image` — L7130
- `generate_storyboard_images_gpt_image2` — L7177
- `_storyboard_grid_aspect` — L7362
- `_storyboard_grid_cols_rows` — L7369
- `_storyboard_grid_prompt` — L7391
- `_storyboard_grid_prompt_limit` — L7449
- `_is_prompt_limit_response` — L7453
- `_production_storyboard_prompt` — L7459
- `_write_production_storyboard_page_qa` — L7493
- `_character_sheet_prompt` — L7503
- `_is_audit_blocked` — L7629
- `_paraphrase_sensitive_dialogue` — L7642
- `_topic_cache_dir` — L7656
- `_topic_cache_path` — L7662
- `_load_topic_decomposition_cache` — L7675
- `_save_topic_decomposition_cache` — L7693
- `_briefs_dir` — L7730
- `_brief_path` — L7736
- `_empty_brief` — L7741
- `_deep_merge_brief_skeleton` — L7781
- `_load_brief` — L7795
- `_save_brief` — L7819
- `_brief_get` — L7838
- `_brief_set` — L7850
- `_brief_claim` — L7866
- `_brief_agent_status` — L7909
- `_brief_from_topic_decomposition` — L7922
- `_rule_based_sfx_design` — L7978
- `_validate_sfx_entry` — L8029
- `_audio_director_design` — L8067
- `_hex_color_validate` — L8123
- `_rule_based_art_design` — L8135
- `_validate_art_design` — L8216
- `_art_director_design` — L8254
- `_coordinator_review` — L8276
- `_llm_topic_decomposition` — L8377
- `_director_route_block` — L8541
- `_llm_infer_meta_grid_template` — L8611
- `_resolve_meta_grid_template` — L8668
- `_infer_meta_grid_costume` — L8711
- `_infer_meta_grid_pose` — L8760
- `_adsd_meta_grid_call_prompt` — L8807
- `_meta_grid_panel_index` — L8849
- `_migrate_speaker_ip` — L8929
- `_speaker_ips_dir` — L8954
- `_list_speaker_ips` — L8961
- `_match_speaker_ip` — L8975
- `_build_speaker_ip_context_for_script` — L8995
- `_ip_usage_stats` — L9051
- `_recommend_related_ips` — L9069
- `_save_speaker_ip` — L9094
- `_record_speaker_usage_history` — L9103
- `_format_speaker_usage_history_for_prompt` — L9150
- `_llm_infer_ip_skeleton` — L9168
- `_llm_pick_voice_asset_for_ip` — L9213
- `_auto_incubate_missing_ips` — L9261
- `_character_meta_grid_cache_dir` — L9345
- `_character_meta_grid_cache_path` — L9353
- `_character_meta_grid_cache_legacy_path` — L9361
- `_character_meta_grid_path` — L9368
- `generate_character_meta_grid_gpt_image2` — L9374
- `_generate_all_character_meta_grids` — L9546
- `_write_character_sheet_qa` — L9587
- `generate_character_sheet_gpt_image2` — L9597
- `generate_production_storyboard_page_gpt_image2` — L9697
- `_qa_clean_storyboard_panel` — L9760
- `_crop_storyboard_grid_panels` — L9941
- `generate_storyboard_grid_gpt_image2` — L9988
- `_gpt_image2_direct_annotated_aspect` — L10219
- `_gpt_image2_direct_annotated_prompt` — L10226
- `generate_gpt_image2_direct_annotated_storyboards` — L10256
- `_llm_bgm_description` — L10357
- `_bgm_contains_vocals` — L10396
- `generate_bgm` — L10430
- `step6_parallel` — L10547

---

### 第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）
Range: **L10878 – L15875** (4998 lines)

**Sub-sections:**
- _PR-A (2026-05-27): merged_a 合并跑 helpers_ — L14074-15610 (1537 lines)
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L15611-15653 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L15654-15691 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回时间轴锚定音轨_ — L15692-15830 (139 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L15831-15875 (45 lines)

**Top-level constants:**
- `_PR3B1_SHOT_TYPE_ENUM` — L11348
- `_PR3B1_CAMERA_ANGLE_ENUM` — L11352
- `_PR3B1_LIGHTING_ENUM` — L11357
- `_PR3B1_CAMERA_MOTION_ENUM` — L11362

**Functions:**
- `_generate_motion_prompts` — L10881
- `_motion_tasks_file` — L10948
- `_motion_qa_file` — L10952
- `_append_motion_qa` — L10956
- `_finalize_motion_qa` — L10980
- `_lip_sync_tasks_file` — L11064
- `_load_motion_tasks` — L11068
- `_save_motion_task` — L11078
- `_remove_motion_task` — L11086
- `_load_lip_sync_tasks` — L11093
- `_save_lip_sync_task` — L11103
- `_remove_lip_sync_task` — L11110
- `_video_visual_motion_qa` — L11117
- `_motion_output_qa` — L11189
- `_has_audio_stream` — L11234
- `_normalize_motion_video` — L11245
- `_motion_poll_and_download` — L11295
- `_validate_enum_field` — L11368
- `_build_motion_video_prompt` — L11383
- `_short_board_text` — L11433
- `_wrap_board_text` — L11440
- `_storyboard_font` — L11471
- `_draw_storyboard_arrow` — L11486
- `_build_annotated_storyboard_reference` — L11500
- `_plain_caption_text` — L11601
- `_werydance_caption_request` — L11609
- `_werydance_caption_instruction` — L11636
- `_werydance_negative_prompt` — L11648
- `_motion_reference_prompt` — L11666
- `_motion_audio_dub_prompt` — L11689
- `_motion_audio_dub_poll_and_download` — L11723
- `_try_motion_audio_dub_video` — L11788
- `_try_motion_reference_video` — L11951
- `_motion_one_scene` — L12067
- `_grid_multiref_tasks_file` — L12196
- `_previs_page_tasks_file` — L12200
- `_load_grid_multiref_tasks` — L12204
- `_load_previs_page_tasks` — L12214
- `_save_grid_multiref_task` — L12224
- `_save_previs_page_task` — L12231
- `_remove_grid_multiref_task` — L12238
- `_remove_previs_page_task` — L12245
- `_poll_video_task_download` — L12252
- `_grid_multiref_group_size` — L12301
- `_grid_multiref_duration` — L12311
- `_grid_multiref_tts_buffer_factor` — L12349
- `_grid_multiref_tts_duration_buffered` — L12363
- `_grid_multiref_segment_max_stretch` — L12379
- `_grid_multiref_prompt` — L12387
- `_write_grid_multiref_motion_qa` — L12457
- `_write_previs_page_motion_qa` — L12467
- `_write_storyboard_trailer_qa` — L12477
- `_write_character_trailer_qa` — L12487
- `_write_grid_multiref_segment_qa` — L12497
- `_motion_compare_record` — L12507
- `_write_storyboard_motion_compare_qa` — L12529
- `_scene_segment_duration` — L12565
- `_apply_grid_multiref_segments` — L12584
- `_previs_page_duration` — L12789
- `_previs_page_group_prompt` — L12799
- `_previs_page_groups` — L12825
- `_storyboard_trailer_duration` — L12840
- `_storyboard_trailer_prompt` — L12850
- `_character_trailer_max_shots` — L12878
- `_character_trailer_shot_duration` — L12886
- `_character_trailer_prompt` — L12900
- `_concat_character_trailer_segments` — L12915
- `_generate_character_trailer_motion` — L12954
- `_multi_trailer_prompt_for_group` — L13062
- `_generate_multi_trailer_segments` — L13085
- `_generate_storyboard_trailer_motion` — L13196
- `_generate_previs_page_motion_segments` — L13271
- `_generate_grid_multiref_motion_segments` — L13383
- `_grid_multiref_concat_groups` — L13642
- `_grid_multiref_concat_groups_partial` — L13659
- `_grid_multiref_concat_paths` — L13677
- `_lip_sync_slot_duration` — L13719
- `_adsd_lip_sync_prompt` — L13726
- `_adsd_broll_motion_prompt` — L13772
- `_adsd_action_b_motion_prompt` — L13814
- `_adsd_silent_b_motion_prompt` — L13860
- `_adsd_narrated_b_audio_dub_prompt` — L13895
- `_adsd_almighty_audio_dub_prompt` — L13939
- `_postprocess_lip_sync_segment` — L13980
- `_detect_audio_leading_silence` — L14052
- `_concat_audio_files_for_group` — L14077
- `_split_lip_sync_raw_by_durations` — L14100
- `_postprocess_audio_dub_segment` — L14135
- `_lips_change_repair_segment` — L14263
- `_load_lips_change_requested_turns` — L14348
- `_parse_turn_set` — L14365
- `_load_motion_voice_repair_turns` — L14387
- `_voice_assets_file` — L14399
- `_load_voice_assets` — L14406
- `_select_voice_asset_reference` — L14425
- `_lip_sync_poll_download_and_process` — L14491
- `_lip_sync_one_group` — L14559
- `_lip_sync_one_scene` — L14763
- `step66_adsd_lip_sync` — L15087
- `step65_motion` — L15431
- `step65_grid_multiref_motion_qa` — L15583
- `_sanitize_scene_for_state` — L15612
- `_save_pipeline_state` — L15631
- `_retime_after_audio_dub` — L15655
- `_build_voice_clone_hybrid_audio` — L15693
- `_build_dynamic_bgm` — L15832

---

### 第七步：拼接视频轨
Range: **L15876 – L16135** (260 lines)

**Functions:**
- `step7_concat` — L15877

---

### 第八步：生成 ASS 字幕
Range: **L16136 – L16938** (803 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L16259-16938 (680 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L16137
- `_word_timings_for_subtitle_align` — L16163
- `_align_segments_via_asr` — L16204
- `step8_subtitles` — L16247
- `_read_output_json` — L16659
- `_qa_file_pass` — L16670
- `_ass_has_dialogue` — L16677
- `_write_adsd_delivery_qa` — L16687
- `_write_bgm_only_qa` — L16827

---

### 第九步：最终合成
Range: **L16939 – L17214** (276 lines)

**Functions:**
- `step9_render` — L16940

---

### 第十步：推送 Telegram
Range: **L17215 – L18876** (1662 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L18315-18683 (369 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L18684-18688 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L18689-18752 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L18753-18798 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L18799-18876 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L17584
- `PANTONE_FALLBACK` — L17611
- `FESTIVAL_DATE_TAG` — L17724

**Functions:**
- `_generate_caption` — L17216
- `_overlay_title_on_cover` — L17454
- `_prepare_tg_photo` — L17564
- `_get_pantone_for_date` — L17614
- `_llm_bottom_note` — L17639
- `_get_bottom_note` — L17668
- `_get_date_tag` — L17746
- `_shrink_to_b64` — L17768
- `_llm_check_scenes_anomalies` — L17784
- `_llm_check_cover_unique` — L17837
- `_llm_check_cover_quality` — L17867
- `_try_almanac_cover` — L17909
- `_generate_cover_image` — L18080
- `_async_kickoff_cover_caption` — L18322
- `_await_async_cover_caption` — L18396
- `step10_deliver` — L18423

---

### 主流程
Range: **L18877 – L19061** (185 lines)

**Functions:**
- `_print_execution_plan` — L18878
- `main` — L18926

---
