# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (19872 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-2273 (2152 lines · 64 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L2274-4836 (2563 lines · 32 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L4837-5968 (1132 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L5969-6520 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L6521-11083 (4563 lines · 103 fn · 7 sub)
- [`第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）`](#第-6-5-步-动态化-hads-vads-默认-on---no-motion-关) — L11084-16271 (5188 lines · 109 fn · 5 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L16272-16531 (260 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L16532-17490 (959 lines · 10 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L17491-17781 (291 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L17782-19644 (1863 lines · 19 fn · 6 sub)
- [`主流程`](#主流程) — L19645-19872 (228 lines · 3 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L2273** (2152 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L324-453 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L454-1195 (742 lines)
- _工具函数_ — L1196-1637 (442 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1638-2273 (636 lines)

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
- `_LLM_TIER` — L1815
- `_TOPIC_MODIFIERS` — L2026
- `_TONE_PANTONE_OVERRIDE` — L2043

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
- `tier_chat` — L1823
- `chat` — L1829
- `pick_image_model` — L1872
- `detect_topic_meta` — L1897
- `_topic_culture_guard` — L1947
- `_write_cultural_visual_qa` — L1973
- `is_1919_global_topic` — L2020
- `_strip_topic_modifiers` — L2031
- `apply_1919_global_guardrails` — L2049
- `build_1919_global_cover_prompt` — L2078
- `_shot_blueprint_enums` — L2110
- `build_shot_blueprint` — L2186
- `ffprobe_duration` — L2212
- `ffprobe_video_size` — L2223
- `_video_decode_probe` — L2244
- `ffmpeg` — L2262

---

### 第一步：双导演生成剧本
Range: **L2274 – L4836** (2563 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L3835-4836 (1002 lines)

**Top-level constants:**
- `_ENSEMBLE_CAP_BY_ROUTE` — L2422

**Functions:**
- `_extract_json_array` — L2275
- `_extract_json_object` — L2285
- `_voice_for_speaker` — L2295
- `_adsd_gender_from_voice` — L2331
- `_adsd_infer_gender_from_speaker` — L2339
- `_adsd_gender_lock_phrase` — L2348
- `_adsd_visual_subject_has_gender_conflict` — L2363
- `_adsd_default_roles` — L2375
- `_adsd_allows_media_role` — L2380
- `_adsd_role_candidates` — L2388
- `_adsd_dialogue_shape` — L2411
- `_ensemble_speaker_cap` — L2433
- `_ip_voice_asset_for_speaker` — L2446
- `_finalize_adsd_turns` — L2470
- `_parse_adsd_override_turns` — L2516
- `_parse_timecode_seconds` — L2609
- `_clean_override_line_text` — L2618
- `_parse_override_script_text` — L2624
- `_adsd_pov_contract` — L2658
- `_load_audit_blacklist_block` — L2671
- `_generate_adsd_dialogue_turns` — L2709
- `_broll_rhythm_reviewer` — L3136
- `_sweep_speaker_field` — L3243
- `_should_run_immersion_qa` — L3303
- `_adsd_immersion_qa_rewrite_turns` — L3326
- `_adsd_visual_contract` — L3390
- `_parse_risk_score` — L3442
- `_check_high_risk_hard_abort` — L3471
- `_maybe_neutralize_topic` — L3498
- `_apply_llm_mode_decision` — L3537
- `step1_script` — L3592
- `_write_ads_retention_qa` — L4780

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L4837 – L5968** (1132 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L4912
- `_ADSD_POLICY_REWRITE_TERMS` — L4918
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L5009

**Functions:**
- `_openai_tts_fallback` — L4838
- `_edge_tts_fallback` — L4884
- `_sanitize_for_external_api` — L4927
- `_is_content_policy_error` — L4936
- `_rewrite_adsd_tts_text_for_policy` — L4950
- `_record_adsd_tts_rewrite` — L4990
- `_build_silence_mp3` — L5015
- `_audio_duration_seconds` — L5028
- `_text_to_audio_master_voice_timed` — L5040
- `_text_to_audio_master_voice` — L5165
- `step2_master_voice` — L5278
- `_tts_turn_to_audio` — L5406
- `_asr_verify_dialogue_audio` — L5470
- `_asr_verify_dialogue_turns` — L5532
- `_normalize_cn_number_token` — L5574
- `_compact_zh_text` — L5596
- `_write_adsd_asr_text_qa` — L5603
- `_write_adsd_speaker_focus_qa` — L5642
- `_write_adsd_gender_voice_qa` — L5702
- `step2_dialogue_voice` — L5755

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L5969 – L6520** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L5976-6098 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L6099-6133 (35 lines)
- _第二层：字符数插值_ — L6134-6158 (25 lines)
- _第三层：silencedetect 物理校准_ — L6159-6520 (362 lines)

**Functions:**
- `_detect_silences` — L5977
- `_calibrate_boundaries` — L6012
- `_enforce_monotonic` — L6046
- `_manual_override_segments` — L6058
- `_calc_sentence_boundaries` — L6079
- `step345_timeline` — L6190
- `_analyze_bgm_energy_cuts` — L6249
- `_snap_bgm_only_boundaries` — L6312
- `step345_bgm_only_timeline` — L6372

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L6521 – L11083** (4563 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L7743-7793 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L7794-8642 (849 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L8643-9077 (435 lines)
- _Speaker IP Card (2026-05-21)_ — L9078-10703 (1626 lines)
- _B68 (2026-05-30) WERYDANCE 段长合规 gate_ — L10704-10916 (213 lines)
- _审批流程_ — L10917-10973 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L10974-11083 (110 lines)

**Top-level constants:**
- `_CORE_TERMS_STOP_WORDS` — L6916
- `CHARACTER_META_GRID_COSTUMES` — L7749
- `CHARACTER_META_GRID_POSES` — L7750
- `CHARACTER_META_GRID_SCENES` — L7751
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L7754
- `_SFX_TYPE_ENUM` — L8122
- `_SFX_INTENSITY_ENUM` — L8127
- `_SFX_POSITION_ENUM` — L8128
- `_GRAIN_LEVEL_ENUM` — L8273

**Functions:**
- `_extract_img_url` — L6522
- `_extract_img_urls` — L6544
- `_extract_video_url` — L6577
- `_count_bands` — L6602
- `_detect_contact_sheet_like_image` — L6614
- `_file_sha256` — L6675
- `_load_upload_cache` — L6688
- `_save_upload_cache` — L6697
- `_cached_upload_url` — L6705
- `_store_upload_url` — L6722
- `_guess_upload_mime` — L6732
- `_upload_to_weryai` — L6755
- `_send_for_approval` — L6809
- `_wait_approval` — L6873
- `_render_still_segment` — L6885
- `_extract_core_terms` — L6922
- `_scene_text_visual_alignment` — L6941
- `_write_text_visual_alignment_qa` — L6962
- `_scene_motion_action_plan` — L6985
- `_ensure_motion_action_plan` — L7039
- `_motion_action_block` — L7048
- `_motion_plan_for_qa` — L7076
- `_write_motion_action_plan_qa` — L7086
- `_write_motion_bridge_refs_qa` — L7116
- `_motion_bridge_ref_prompt` — L7123
- `generate_motion_bridge_refs_gpt_image2` — L7156
- `generate_image` — L7271
- `generate_storyboard_images_gpt_image2` — L7318
- `_storyboard_grid_aspect` — L7504
- `_storyboard_grid_cols_rows` — L7511
- `_storyboard_grid_prompt` — L7533
- `_storyboard_grid_prompt_limit` — L7591
- `_is_prompt_limit_response` — L7595
- `_production_storyboard_prompt` — L7601
- `_write_production_storyboard_page_qa` — L7635
- `_character_sheet_prompt` — L7645
- `_is_audit_blocked` — L7771
- `_paraphrase_sensitive_dialogue` — L7784
- `_topic_cache_dir` — L7798
- `_topic_cache_path` — L7804
- `_load_topic_decomposition_cache` — L7817
- `_save_topic_decomposition_cache` — L7835
- `_briefs_dir` — L7872
- `_brief_path` — L7878
- `_empty_brief` — L7883
- `_deep_merge_brief_skeleton` — L7923
- `_load_brief` — L7937
- `_save_brief` — L7961
- `_brief_get` — L7980
- `_brief_field` — L7992
- `_brief_set` — L8003
- `_brief_claim` — L8019
- `_brief_agent_status` — L8062
- `_brief_from_topic_decomposition` — L8075
- `_rule_based_sfx_design` — L8131
- `_validate_sfx_entry` — L8182
- `_audio_director_design` — L8220
- `_hex_color_validate` — L8276
- `_rule_based_art_design` — L8288
- `_validate_art_design` — L8369
- `_art_director_design` — L8407
- `_coordinator_review` — L8429
- `_llm_topic_decomposition` — L8530
- `_director_route_block` — L8696
- `_llm_infer_meta_grid_template` — L8766
- `_resolve_meta_grid_template` — L8823
- `_infer_meta_grid_costume` — L8866
- `_infer_meta_grid_pose` — L8915
- `_adsd_meta_grid_call_prompt` — L8962
- `_meta_grid_panel_index` — L9004
- `_migrate_speaker_ip` — L9084
- `_speaker_ips_dir` — L9109
- `_list_speaker_ips` — L9116
- `_match_speaker_ip` — L9130
- `_build_speaker_ip_context_for_script` — L9150
- `_ip_usage_stats` — L9206
- `_recommend_related_ips` — L9224
- `_save_speaker_ip` — L9249
- `_record_speaker_usage_history` — L9258
- `_format_speaker_usage_history_for_prompt` — L9305
- `_llm_infer_ip_skeleton` — L9323
- `_llm_pick_voice_asset_for_ip` — L9368
- `_auto_incubate_missing_ips` — L9417
- `_character_meta_grid_cache_dir` — L9501
- `_character_meta_grid_cache_path` — L9509
- `_character_meta_grid_cache_legacy_path` — L9517
- `_character_meta_grid_path` — L9524
- `generate_character_meta_grid_gpt_image2` — L9530
- `_generate_all_character_meta_grids` — L9702
- `_write_character_sheet_qa` — L9743
- `generate_character_sheet_gpt_image2` — L9753
- `generate_production_storyboard_page_gpt_image2` — L9853
- `_qa_clean_storyboard_panel` — L9916
- `_crop_storyboard_grid_panels` — L10097
- `generate_storyboard_grid_gpt_image2` — L10144
- `_gpt_image2_direct_annotated_aspect` — L10376
- `_gpt_image2_direct_annotated_prompt` — L10383
- `generate_gpt_image2_direct_annotated_storyboards` — L10413
- `_llm_bgm_description` — L10514
- `_bgm_contains_vocals` — L10553
- `generate_bgm` — L10587
- `_b68_clamp_scene_durations_to_werydance_bounds` — L10712
- `step6_parallel` — L10752

---

### 第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）
Range: **L11084 – L16271** (5188 lines)

**Sub-sections:**
- _PR-A (2026-05-27): merged_a 合并跑 helpers_ — L14412-16006 (1595 lines)
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L16007-16049 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L16050-16087 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回时间轴锚定音轨_ — L16088-16226 (139 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L16227-16271 (45 lines)

**Top-level constants:**
- `_PR3B1_SHOT_TYPE_ENUM` — L11554
- `_PR3B1_CAMERA_ANGLE_ENUM` — L11558
- `_PR3B1_LIGHTING_ENUM` — L11563
- `_PR3B1_CAMERA_MOTION_ENUM` — L11568
- `_EMOTION_NARRATION_STYLE_MAP` — L12620

**Functions:**
- `_generate_motion_prompts` — L11087
- `_motion_tasks_file` — L11154
- `_motion_qa_file` — L11158
- `_append_motion_qa` — L11162
- `_finalize_motion_qa` — L11186
- `_lip_sync_tasks_file` — L11270
- `_load_motion_tasks` — L11274
- `_save_motion_task` — L11284
- `_remove_motion_task` — L11292
- `_load_lip_sync_tasks` — L11299
- `_save_lip_sync_task` — L11309
- `_remove_lip_sync_task` — L11316
- `_video_visual_motion_qa` — L11323
- `_motion_output_qa` — L11395
- `_has_audio_stream` — L11440
- `_normalize_motion_video` — L11451
- `_motion_poll_and_download` — L11501
- `_validate_enum_field` — L11574
- `_build_motion_video_prompt` — L11589
- `_short_board_text` — L11639
- `_wrap_board_text` — L11646
- `_storyboard_font` — L11677
- `_draw_storyboard_arrow` — L11692
- `_build_annotated_storyboard_reference` — L11706
- `_plain_caption_text` — L11807
- `_werydance_caption_request` — L11815
- `_werydance_caption_instruction` — L11842
- `_werydance_negative_prompt` — L11854
- `_motion_reference_prompt` — L11872
- `_motion_audio_dub_prompt` — L11895
- `_motion_audio_dub_poll_and_download` — L11929
- `_try_motion_audio_dub_video` — L11994
- `_try_motion_reference_video` — L12157
- `_motion_one_scene` — L12273
- `_grid_multiref_tasks_file` — L12403
- `_previs_page_tasks_file` — L12407
- `_load_grid_multiref_tasks` — L12411
- `_load_previs_page_tasks` — L12421
- `_save_grid_multiref_task` — L12431
- `_save_previs_page_task` — L12438
- `_remove_grid_multiref_task` — L12445
- `_remove_previs_page_task` — L12452
- `_poll_video_task_download` — L12459
- `_grid_multiref_group_size` — L12508
- `_grid_multiref_adaptive_group_size` — L12518
- `_grid_multiref_duration` — L12542
- `_grid_multiref_tts_buffer_factor` — L12580
- `_grid_multiref_tts_duration_buffered` — L12594
- `_grid_multiref_segment_max_stretch` — L12610
- `_voice_clone_emotion_style` — L12644
- `_grid_multiref_prompt` — L12667
- `_write_grid_multiref_motion_qa` — L12741
- `_write_previs_page_motion_qa` — L12751
- `_write_storyboard_trailer_qa` — L12761
- `_write_character_trailer_qa` — L12771
- `_write_grid_multiref_segment_qa` — L12781
- `_motion_compare_record` — L12791
- `_write_storyboard_motion_compare_qa` — L12813
- `_scene_segment_duration` — L12849
- `_apply_grid_multiref_segments` — L12868
- `_previs_page_duration` — L13073
- `_previs_page_group_prompt` — L13084
- `_previs_page_groups` — L13110
- `_storyboard_trailer_duration` — L13125
- `_storyboard_trailer_prompt` — L13135
- `_character_trailer_max_shots` — L13163
- `_character_trailer_shot_duration` — L13171
- `_character_trailer_prompt` — L13187
- `_concat_character_trailer_segments` — L13202
- `_generate_character_trailer_motion` — L13241
- `_multi_trailer_prompt_for_group` — L13349
- `_generate_multi_trailer_segments` — L13372
- `_generate_storyboard_trailer_motion` — L13483
- `_generate_previs_page_motion_segments` — L13558
- `_generate_grid_multiref_motion_segments` — L13670
- `_grid_multiref_concat_groups` — L13980
- `_grid_multiref_concat_groups_partial` — L13997
- `_grid_multiref_concat_paths` — L14015
- `_lip_sync_slot_duration` — L14057
- `_adsd_lip_sync_prompt` — L14064
- `_adsd_broll_motion_prompt` — L14110
- `_adsd_action_b_motion_prompt` — L14152
- `_adsd_silent_b_motion_prompt` — L14198
- `_adsd_narrated_b_audio_dub_prompt` — L14233
- `_adsd_almighty_audio_dub_prompt` — L14277
- `_postprocess_lip_sync_segment` — L14318
- `_detect_audio_leading_silence` — L14390
- `_concat_audio_files_for_group` — L14415
- `_split_lip_sync_raw_by_durations` — L14438
- `_postprocess_audio_dub_segment` — L14473
- `_lips_change_repair_segment` — L14601
- `_load_lips_change_requested_turns` — L14686
- `_parse_turn_set` — L14703
- `_load_motion_voice_repair_turns` — L14725
- `_voice_assets_file` — L14737
- `_load_voice_assets` — L14744
- `_build_combined_voice_reference` — L14763
- `_select_voice_asset_reference` — L14805
- `_lip_sync_poll_download_and_process` — L14881
- `_lip_sync_one_group` — L14949
- `_lip_sync_one_scene` — L15157
- `step66_adsd_lip_sync` — L15481
- `step65_motion` — L15826
- `step65_grid_multiref_motion_qa` — L15979
- `_sanitize_scene_for_state` — L16008
- `_save_pipeline_state` — L16027
- `_retime_after_audio_dub` — L16051
- `_build_voice_clone_hybrid_audio` — L16089
- `_build_dynamic_bgm` — L16228

---

### 第七步：拼接视频轨
Range: **L16272 – L16531** (260 lines)

**Functions:**
- `step7_concat` — L16273

---

### 第八步：生成 ASS 字幕
Range: **L16532 – L17490** (959 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L16811-17490 (680 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L16533
- `_word_timings_for_subtitle_align` — L16559
- `_align_segments_via_asr` — L16600
- `_b61_1_asr_turn_boundaries` — L16643
- `step8_subtitles` — L16705
- `_read_output_json` — L17211
- `_qa_file_pass` — L17222
- `_ass_has_dialogue` — L17229
- `_write_adsd_delivery_qa` — L17239
- `_write_bgm_only_qa` — L17379

---

### 第九步：最终合成
Range: **L17491 – L17781** (291 lines)

**Functions:**
- `step9_render` — L17492

---

### 第十步：推送 Telegram
Range: **L17782 – L19644** (1863 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L18888-18997 (110 lines)
- _B70 (2026-05-30) TG oversize policy helpers_ — L18998-19451 (454 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L19452-19456 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L19457-19520 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L19521-19566 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L19567-19644 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L18151
- `PANTONE_FALLBACK` — L18178
- `FESTIVAL_DATE_TAG` — L18292

**Functions:**
- `_generate_caption` — L17783
- `_overlay_title_on_cover` — L18021
- `_prepare_tg_photo` — L18131
- `_get_pantone_for_date` — L18181
- `_llm_bottom_note` — L18206
- `_get_bottom_note` — L18236
- `_get_date_tag` — L18314
- `_shrink_to_b64` — L18336
- `_llm_check_scenes_anomalies` — L18352
- `_llm_check_cover_unique` — L18405
- `_llm_check_cover_quality` — L18435
- `_try_almanac_cover` — L18477
- `_generate_cover_image` — L18648
- `_async_kickoff_cover_caption` — L18895
- `_await_async_cover_caption` — L18971
- `_b70_env_float` — L19001
- `_b70_split_and_deliver` — L19016
- `_b70_send_document_first` — L19116
- `step10_deliver` — L19153

---

### 主流程
Range: **L19645 – L19872** (228 lines)

**Functions:**
- `_print_execution_plan` — L19646
- `_write_run_timings` — L19694
- `main` — L19723

---
