# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (19898 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-2273 (2152 lines · 64 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L2274-4862 (2589 lines · 33 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L4863-5994 (1132 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L5995-6546 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L6547-11109 (4563 lines · 103 fn · 7 sub)
- [`第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）`](#第-6-5-步-动态化-hads-vads-默认-on---no-motion-关) — L11110-16297 (5188 lines · 109 fn · 5 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L16298-16557 (260 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L16558-17516 (959 lines · 10 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L17517-17807 (291 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L17808-19670 (1863 lines · 19 fn · 6 sub)
- [`主流程`](#主流程) — L19671-19898 (228 lines · 3 fn · 0 sub)

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
Range: **L2274 – L4862** (2589 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L3861-4862 (1002 lines)

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
- `_apply_render_budget_scene_cap` — L3537
- `_apply_llm_mode_decision` — L3562
- `step1_script` — L3617
- `_write_ads_retention_qa` — L4806

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L4863 – L5994** (1132 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L4938
- `_ADSD_POLICY_REWRITE_TERMS` — L4944
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L5035

**Functions:**
- `_openai_tts_fallback` — L4864
- `_edge_tts_fallback` — L4910
- `_sanitize_for_external_api` — L4953
- `_is_content_policy_error` — L4962
- `_rewrite_adsd_tts_text_for_policy` — L4976
- `_record_adsd_tts_rewrite` — L5016
- `_build_silence_mp3` — L5041
- `_audio_duration_seconds` — L5054
- `_text_to_audio_master_voice_timed` — L5066
- `_text_to_audio_master_voice` — L5191
- `step2_master_voice` — L5304
- `_tts_turn_to_audio` — L5432
- `_asr_verify_dialogue_audio` — L5496
- `_asr_verify_dialogue_turns` — L5558
- `_normalize_cn_number_token` — L5600
- `_compact_zh_text` — L5622
- `_write_adsd_asr_text_qa` — L5629
- `_write_adsd_speaker_focus_qa` — L5668
- `_write_adsd_gender_voice_qa` — L5728
- `step2_dialogue_voice` — L5781

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L5995 – L6546** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L6002-6124 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L6125-6159 (35 lines)
- _第二层：字符数插值_ — L6160-6184 (25 lines)
- _第三层：silencedetect 物理校准_ — L6185-6546 (362 lines)

**Functions:**
- `_detect_silences` — L6003
- `_calibrate_boundaries` — L6038
- `_enforce_monotonic` — L6072
- `_manual_override_segments` — L6084
- `_calc_sentence_boundaries` — L6105
- `step345_timeline` — L6216
- `_analyze_bgm_energy_cuts` — L6275
- `_snap_bgm_only_boundaries` — L6338
- `step345_bgm_only_timeline` — L6398

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L6547 – L11109** (4563 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L7769-7819 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L7820-8668 (849 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L8669-9103 (435 lines)
- _Speaker IP Card (2026-05-21)_ — L9104-10729 (1626 lines)
- _B68 (2026-05-30) WERYDANCE 段长合规 gate_ — L10730-10942 (213 lines)
- _审批流程_ — L10943-10999 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L11000-11109 (110 lines)

**Top-level constants:**
- `_CORE_TERMS_STOP_WORDS` — L6942
- `CHARACTER_META_GRID_COSTUMES` — L7775
- `CHARACTER_META_GRID_POSES` — L7776
- `CHARACTER_META_GRID_SCENES` — L7777
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L7780
- `_SFX_TYPE_ENUM` — L8148
- `_SFX_INTENSITY_ENUM` — L8153
- `_SFX_POSITION_ENUM` — L8154
- `_GRAIN_LEVEL_ENUM` — L8299

**Functions:**
- `_extract_img_url` — L6548
- `_extract_img_urls` — L6570
- `_extract_video_url` — L6603
- `_count_bands` — L6628
- `_detect_contact_sheet_like_image` — L6640
- `_file_sha256` — L6701
- `_load_upload_cache` — L6714
- `_save_upload_cache` — L6723
- `_cached_upload_url` — L6731
- `_store_upload_url` — L6748
- `_guess_upload_mime` — L6758
- `_upload_to_weryai` — L6781
- `_send_for_approval` — L6835
- `_wait_approval` — L6899
- `_render_still_segment` — L6911
- `_extract_core_terms` — L6948
- `_scene_text_visual_alignment` — L6967
- `_write_text_visual_alignment_qa` — L6988
- `_scene_motion_action_plan` — L7011
- `_ensure_motion_action_plan` — L7065
- `_motion_action_block` — L7074
- `_motion_plan_for_qa` — L7102
- `_write_motion_action_plan_qa` — L7112
- `_write_motion_bridge_refs_qa` — L7142
- `_motion_bridge_ref_prompt` — L7149
- `generate_motion_bridge_refs_gpt_image2` — L7182
- `generate_image` — L7297
- `generate_storyboard_images_gpt_image2` — L7344
- `_storyboard_grid_aspect` — L7530
- `_storyboard_grid_cols_rows` — L7537
- `_storyboard_grid_prompt` — L7559
- `_storyboard_grid_prompt_limit` — L7617
- `_is_prompt_limit_response` — L7621
- `_production_storyboard_prompt` — L7627
- `_write_production_storyboard_page_qa` — L7661
- `_character_sheet_prompt` — L7671
- `_is_audit_blocked` — L7797
- `_paraphrase_sensitive_dialogue` — L7810
- `_topic_cache_dir` — L7824
- `_topic_cache_path` — L7830
- `_load_topic_decomposition_cache` — L7843
- `_save_topic_decomposition_cache` — L7861
- `_briefs_dir` — L7898
- `_brief_path` — L7904
- `_empty_brief` — L7909
- `_deep_merge_brief_skeleton` — L7949
- `_load_brief` — L7963
- `_save_brief` — L7987
- `_brief_get` — L8006
- `_brief_field` — L8018
- `_brief_set` — L8029
- `_brief_claim` — L8045
- `_brief_agent_status` — L8088
- `_brief_from_topic_decomposition` — L8101
- `_rule_based_sfx_design` — L8157
- `_validate_sfx_entry` — L8208
- `_audio_director_design` — L8246
- `_hex_color_validate` — L8302
- `_rule_based_art_design` — L8314
- `_validate_art_design` — L8395
- `_art_director_design` — L8433
- `_coordinator_review` — L8455
- `_llm_topic_decomposition` — L8556
- `_director_route_block` — L8722
- `_llm_infer_meta_grid_template` — L8792
- `_resolve_meta_grid_template` — L8849
- `_infer_meta_grid_costume` — L8892
- `_infer_meta_grid_pose` — L8941
- `_adsd_meta_grid_call_prompt` — L8988
- `_meta_grid_panel_index` — L9030
- `_migrate_speaker_ip` — L9110
- `_speaker_ips_dir` — L9135
- `_list_speaker_ips` — L9142
- `_match_speaker_ip` — L9156
- `_build_speaker_ip_context_for_script` — L9176
- `_ip_usage_stats` — L9232
- `_recommend_related_ips` — L9250
- `_save_speaker_ip` — L9275
- `_record_speaker_usage_history` — L9284
- `_format_speaker_usage_history_for_prompt` — L9331
- `_llm_infer_ip_skeleton` — L9349
- `_llm_pick_voice_asset_for_ip` — L9394
- `_auto_incubate_missing_ips` — L9443
- `_character_meta_grid_cache_dir` — L9527
- `_character_meta_grid_cache_path` — L9535
- `_character_meta_grid_cache_legacy_path` — L9543
- `_character_meta_grid_path` — L9550
- `generate_character_meta_grid_gpt_image2` — L9556
- `_generate_all_character_meta_grids` — L9728
- `_write_character_sheet_qa` — L9769
- `generate_character_sheet_gpt_image2` — L9779
- `generate_production_storyboard_page_gpt_image2` — L9879
- `_qa_clean_storyboard_panel` — L9942
- `_crop_storyboard_grid_panels` — L10123
- `generate_storyboard_grid_gpt_image2` — L10170
- `_gpt_image2_direct_annotated_aspect` — L10402
- `_gpt_image2_direct_annotated_prompt` — L10409
- `generate_gpt_image2_direct_annotated_storyboards` — L10439
- `_llm_bgm_description` — L10540
- `_bgm_contains_vocals` — L10579
- `generate_bgm` — L10613
- `_b68_clamp_scene_durations_to_werydance_bounds` — L10738
- `step6_parallel` — L10778

---

### 第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）
Range: **L11110 – L16297** (5188 lines)

**Sub-sections:**
- _PR-A (2026-05-27): merged_a 合并跑 helpers_ — L14438-16032 (1595 lines)
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L16033-16075 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L16076-16113 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回时间轴锚定音轨_ — L16114-16252 (139 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L16253-16297 (45 lines)

**Top-level constants:**
- `_PR3B1_SHOT_TYPE_ENUM` — L11580
- `_PR3B1_CAMERA_ANGLE_ENUM` — L11584
- `_PR3B1_LIGHTING_ENUM` — L11589
- `_PR3B1_CAMERA_MOTION_ENUM` — L11594
- `_EMOTION_NARRATION_STYLE_MAP` — L12646

**Functions:**
- `_generate_motion_prompts` — L11113
- `_motion_tasks_file` — L11180
- `_motion_qa_file` — L11184
- `_append_motion_qa` — L11188
- `_finalize_motion_qa` — L11212
- `_lip_sync_tasks_file` — L11296
- `_load_motion_tasks` — L11300
- `_save_motion_task` — L11310
- `_remove_motion_task` — L11318
- `_load_lip_sync_tasks` — L11325
- `_save_lip_sync_task` — L11335
- `_remove_lip_sync_task` — L11342
- `_video_visual_motion_qa` — L11349
- `_motion_output_qa` — L11421
- `_has_audio_stream` — L11466
- `_normalize_motion_video` — L11477
- `_motion_poll_and_download` — L11527
- `_validate_enum_field` — L11600
- `_build_motion_video_prompt` — L11615
- `_short_board_text` — L11665
- `_wrap_board_text` — L11672
- `_storyboard_font` — L11703
- `_draw_storyboard_arrow` — L11718
- `_build_annotated_storyboard_reference` — L11732
- `_plain_caption_text` — L11833
- `_werydance_caption_request` — L11841
- `_werydance_caption_instruction` — L11868
- `_werydance_negative_prompt` — L11880
- `_motion_reference_prompt` — L11898
- `_motion_audio_dub_prompt` — L11921
- `_motion_audio_dub_poll_and_download` — L11955
- `_try_motion_audio_dub_video` — L12020
- `_try_motion_reference_video` — L12183
- `_motion_one_scene` — L12299
- `_grid_multiref_tasks_file` — L12429
- `_previs_page_tasks_file` — L12433
- `_load_grid_multiref_tasks` — L12437
- `_load_previs_page_tasks` — L12447
- `_save_grid_multiref_task` — L12457
- `_save_previs_page_task` — L12464
- `_remove_grid_multiref_task` — L12471
- `_remove_previs_page_task` — L12478
- `_poll_video_task_download` — L12485
- `_grid_multiref_group_size` — L12534
- `_grid_multiref_adaptive_group_size` — L12544
- `_grid_multiref_duration` — L12568
- `_grid_multiref_tts_buffer_factor` — L12606
- `_grid_multiref_tts_duration_buffered` — L12620
- `_grid_multiref_segment_max_stretch` — L12636
- `_voice_clone_emotion_style` — L12670
- `_grid_multiref_prompt` — L12693
- `_write_grid_multiref_motion_qa` — L12767
- `_write_previs_page_motion_qa` — L12777
- `_write_storyboard_trailer_qa` — L12787
- `_write_character_trailer_qa` — L12797
- `_write_grid_multiref_segment_qa` — L12807
- `_motion_compare_record` — L12817
- `_write_storyboard_motion_compare_qa` — L12839
- `_scene_segment_duration` — L12875
- `_apply_grid_multiref_segments` — L12894
- `_previs_page_duration` — L13099
- `_previs_page_group_prompt` — L13110
- `_previs_page_groups` — L13136
- `_storyboard_trailer_duration` — L13151
- `_storyboard_trailer_prompt` — L13161
- `_character_trailer_max_shots` — L13189
- `_character_trailer_shot_duration` — L13197
- `_character_trailer_prompt` — L13213
- `_concat_character_trailer_segments` — L13228
- `_generate_character_trailer_motion` — L13267
- `_multi_trailer_prompt_for_group` — L13375
- `_generate_multi_trailer_segments` — L13398
- `_generate_storyboard_trailer_motion` — L13509
- `_generate_previs_page_motion_segments` — L13584
- `_generate_grid_multiref_motion_segments` — L13696
- `_grid_multiref_concat_groups` — L14006
- `_grid_multiref_concat_groups_partial` — L14023
- `_grid_multiref_concat_paths` — L14041
- `_lip_sync_slot_duration` — L14083
- `_adsd_lip_sync_prompt` — L14090
- `_adsd_broll_motion_prompt` — L14136
- `_adsd_action_b_motion_prompt` — L14178
- `_adsd_silent_b_motion_prompt` — L14224
- `_adsd_narrated_b_audio_dub_prompt` — L14259
- `_adsd_almighty_audio_dub_prompt` — L14303
- `_postprocess_lip_sync_segment` — L14344
- `_detect_audio_leading_silence` — L14416
- `_concat_audio_files_for_group` — L14441
- `_split_lip_sync_raw_by_durations` — L14464
- `_postprocess_audio_dub_segment` — L14499
- `_lips_change_repair_segment` — L14627
- `_load_lips_change_requested_turns` — L14712
- `_parse_turn_set` — L14729
- `_load_motion_voice_repair_turns` — L14751
- `_voice_assets_file` — L14763
- `_load_voice_assets` — L14770
- `_build_combined_voice_reference` — L14789
- `_select_voice_asset_reference` — L14831
- `_lip_sync_poll_download_and_process` — L14907
- `_lip_sync_one_group` — L14975
- `_lip_sync_one_scene` — L15183
- `step66_adsd_lip_sync` — L15507
- `step65_motion` — L15852
- `step65_grid_multiref_motion_qa` — L16005
- `_sanitize_scene_for_state` — L16034
- `_save_pipeline_state` — L16053
- `_retime_after_audio_dub` — L16077
- `_build_voice_clone_hybrid_audio` — L16115
- `_build_dynamic_bgm` — L16254

---

### 第七步：拼接视频轨
Range: **L16298 – L16557** (260 lines)

**Functions:**
- `step7_concat` — L16299

---

### 第八步：生成 ASS 字幕
Range: **L16558 – L17516** (959 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L16837-17516 (680 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L16559
- `_word_timings_for_subtitle_align` — L16585
- `_align_segments_via_asr` — L16626
- `_b61_1_asr_turn_boundaries` — L16669
- `step8_subtitles` — L16731
- `_read_output_json` — L17237
- `_qa_file_pass` — L17248
- `_ass_has_dialogue` — L17255
- `_write_adsd_delivery_qa` — L17265
- `_write_bgm_only_qa` — L17405

---

### 第九步：最终合成
Range: **L17517 – L17807** (291 lines)

**Functions:**
- `step9_render` — L17518

---

### 第十步：推送 Telegram
Range: **L17808 – L19670** (1863 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L18914-19023 (110 lines)
- _B70 (2026-05-30) TG oversize policy helpers_ — L19024-19477 (454 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L19478-19482 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L19483-19546 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L19547-19592 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L19593-19670 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L18177
- `PANTONE_FALLBACK` — L18204
- `FESTIVAL_DATE_TAG` — L18318

**Functions:**
- `_generate_caption` — L17809
- `_overlay_title_on_cover` — L18047
- `_prepare_tg_photo` — L18157
- `_get_pantone_for_date` — L18207
- `_llm_bottom_note` — L18232
- `_get_bottom_note` — L18262
- `_get_date_tag` — L18340
- `_shrink_to_b64` — L18362
- `_llm_check_scenes_anomalies` — L18378
- `_llm_check_cover_unique` — L18431
- `_llm_check_cover_quality` — L18461
- `_try_almanac_cover` — L18503
- `_generate_cover_image` — L18674
- `_async_kickoff_cover_caption` — L18921
- `_await_async_cover_caption` — L18997
- `_b70_env_float` — L19027
- `_b70_split_and_deliver` — L19042
- `_b70_send_document_first` — L19142
- `step10_deliver` — L19179

---

### 主流程
Range: **L19671 – L19898** (228 lines)

**Functions:**
- `_print_execution_plan` — L19672
- `_write_run_timings` — L19720
- `main` — L19749

---
