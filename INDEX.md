# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (19957 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-2292 (2171 lines · 64 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L2293-4895 (2603 lines · 33 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L4896-6027 (1132 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L6028-6579 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L6580-11168 (4589 lines · 103 fn · 7 sub)
- [`第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）`](#第-6-5-步-动态化-hads-vads-默认-on---no-motion-关) — L11169-16356 (5188 lines · 109 fn · 5 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L16357-16616 (260 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L16617-17575 (959 lines · 10 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L17576-17866 (291 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L17867-19729 (1863 lines · 19 fn · 6 sub)
- [`主流程`](#主流程) — L19730-19957 (228 lines · 3 fn · 0 sub)

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
Range: **L2293 – L4895** (2603 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L3889-4895 (1007 lines)

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
- `_write_ads_retention_qa` — L4839

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L4896 – L6027** (1132 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L4971
- `_ADSD_POLICY_REWRITE_TERMS` — L4977
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L5068

**Functions:**
- `_openai_tts_fallback` — L4897
- `_edge_tts_fallback` — L4943
- `_sanitize_for_external_api` — L4986
- `_is_content_policy_error` — L4995
- `_rewrite_adsd_tts_text_for_policy` — L5009
- `_record_adsd_tts_rewrite` — L5049
- `_build_silence_mp3` — L5074
- `_audio_duration_seconds` — L5087
- `_text_to_audio_master_voice_timed` — L5099
- `_text_to_audio_master_voice` — L5224
- `step2_master_voice` — L5337
- `_tts_turn_to_audio` — L5465
- `_asr_verify_dialogue_audio` — L5529
- `_asr_verify_dialogue_turns` — L5591
- `_normalize_cn_number_token` — L5633
- `_compact_zh_text` — L5655
- `_write_adsd_asr_text_qa` — L5662
- `_write_adsd_speaker_focus_qa` — L5701
- `_write_adsd_gender_voice_qa` — L5761
- `step2_dialogue_voice` — L5814

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L6028 – L6579** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L6035-6157 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L6158-6192 (35 lines)
- _第二层：字符数插值_ — L6193-6217 (25 lines)
- _第三层：silencedetect 物理校准_ — L6218-6579 (362 lines)

**Functions:**
- `_detect_silences` — L6036
- `_calibrate_boundaries` — L6071
- `_enforce_monotonic` — L6105
- `_manual_override_segments` — L6117
- `_calc_sentence_boundaries` — L6138
- `step345_timeline` — L6249
- `_analyze_bgm_energy_cuts` — L6308
- `_snap_bgm_only_boundaries` — L6371
- `step345_bgm_only_timeline` — L6431

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L6580 – L11168** (4589 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L7802-7852 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L7853-8701 (849 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L8702-9136 (435 lines)
- _Speaker IP Card (2026-05-21)_ — L9137-10768 (1632 lines)
- _B68 (2026-05-30) WERYDANCE 段长合规 gate_ — L10769-11001 (233 lines)
- _审批流程_ — L11002-11058 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L11059-11168 (110 lines)

**Top-level constants:**
- `_CORE_TERMS_STOP_WORDS` — L6975
- `CHARACTER_META_GRID_COSTUMES` — L7808
- `CHARACTER_META_GRID_POSES` — L7809
- `CHARACTER_META_GRID_SCENES` — L7810
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L7813
- `_SFX_TYPE_ENUM` — L8181
- `_SFX_INTENSITY_ENUM` — L8186
- `_SFX_POSITION_ENUM` — L8187
- `_GRAIN_LEVEL_ENUM` — L8332

**Functions:**
- `_extract_img_url` — L6581
- `_extract_img_urls` — L6603
- `_extract_video_url` — L6636
- `_count_bands` — L6661
- `_detect_contact_sheet_like_image` — L6673
- `_file_sha256` — L6734
- `_load_upload_cache` — L6747
- `_save_upload_cache` — L6756
- `_cached_upload_url` — L6764
- `_store_upload_url` — L6781
- `_guess_upload_mime` — L6791
- `_upload_to_weryai` — L6814
- `_send_for_approval` — L6868
- `_wait_approval` — L6932
- `_render_still_segment` — L6944
- `_extract_core_terms` — L6981
- `_scene_text_visual_alignment` — L7000
- `_write_text_visual_alignment_qa` — L7021
- `_scene_motion_action_plan` — L7044
- `_ensure_motion_action_plan` — L7098
- `_motion_action_block` — L7107
- `_motion_plan_for_qa` — L7135
- `_write_motion_action_plan_qa` — L7145
- `_write_motion_bridge_refs_qa` — L7175
- `_motion_bridge_ref_prompt` — L7182
- `generate_motion_bridge_refs_gpt_image2` — L7215
- `generate_image` — L7330
- `generate_storyboard_images_gpt_image2` — L7377
- `_storyboard_grid_aspect` — L7563
- `_storyboard_grid_cols_rows` — L7570
- `_storyboard_grid_prompt` — L7592
- `_storyboard_grid_prompt_limit` — L7650
- `_is_prompt_limit_response` — L7654
- `_production_storyboard_prompt` — L7660
- `_write_production_storyboard_page_qa` — L7694
- `_character_sheet_prompt` — L7704
- `_is_audit_blocked` — L7830
- `_paraphrase_sensitive_dialogue` — L7843
- `_topic_cache_dir` — L7857
- `_topic_cache_path` — L7863
- `_load_topic_decomposition_cache` — L7876
- `_save_topic_decomposition_cache` — L7894
- `_briefs_dir` — L7931
- `_brief_path` — L7937
- `_empty_brief` — L7942
- `_deep_merge_brief_skeleton` — L7982
- `_load_brief` — L7996
- `_save_brief` — L8020
- `_brief_get` — L8039
- `_brief_field` — L8051
- `_brief_set` — L8062
- `_brief_claim` — L8078
- `_brief_agent_status` — L8121
- `_brief_from_topic_decomposition` — L8134
- `_rule_based_sfx_design` — L8190
- `_validate_sfx_entry` — L8241
- `_audio_director_design` — L8279
- `_hex_color_validate` — L8335
- `_rule_based_art_design` — L8347
- `_validate_art_design` — L8428
- `_art_director_design` — L8466
- `_coordinator_review` — L8488
- `_llm_topic_decomposition` — L8589
- `_director_route_block` — L8755
- `_llm_infer_meta_grid_template` — L8825
- `_resolve_meta_grid_template` — L8882
- `_infer_meta_grid_costume` — L8925
- `_infer_meta_grid_pose` — L8974
- `_adsd_meta_grid_call_prompt` — L9021
- `_meta_grid_panel_index` — L9063
- `_migrate_speaker_ip` — L9143
- `_speaker_ips_dir` — L9168
- `_list_speaker_ips` — L9175
- `_match_speaker_ip` — L9189
- `_build_speaker_ip_context_for_script` — L9209
- `_ip_usage_stats` — L9265
- `_recommend_related_ips` — L9283
- `_save_speaker_ip` — L9308
- `_record_speaker_usage_history` — L9317
- `_format_speaker_usage_history_for_prompt` — L9364
- `_llm_infer_ip_skeleton` — L9382
- `_llm_pick_voice_asset_for_ip` — L9427
- `_auto_incubate_missing_ips` — L9476
- `_character_meta_grid_cache_dir` — L9560
- `_character_meta_grid_cache_path` — L9568
- `_character_meta_grid_cache_legacy_path` — L9576
- `_character_meta_grid_path` — L9583
- `generate_character_meta_grid_gpt_image2` — L9589
- `_generate_all_character_meta_grids` — L9761
- `_write_character_sheet_qa` — L9802
- `generate_character_sheet_gpt_image2` — L9812
- `generate_production_storyboard_page_gpt_image2` — L9912
- `_qa_clean_storyboard_panel` — L9975
- `_crop_storyboard_grid_panels` — L10156
- `generate_storyboard_grid_gpt_image2` — L10203
- `_gpt_image2_direct_annotated_aspect` — L10435
- `_gpt_image2_direct_annotated_prompt` — L10442
- `generate_gpt_image2_direct_annotated_storyboards` — L10472
- `_llm_bgm_description` — L10573
- `_bgm_contains_vocals` — L10612
- `generate_bgm` — L10646
- `_b68_clamp_scene_durations_to_werydance_bounds` — L10777
- `step6_parallel` — L10837

---

### 第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）
Range: **L11169 – L16356** (5188 lines)

**Sub-sections:**
- _PR-A (2026-05-27): merged_a 合并跑 helpers_ — L14497-16091 (1595 lines)
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L16092-16134 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L16135-16172 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回时间轴锚定音轨_ — L16173-16311 (139 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L16312-16356 (45 lines)

**Top-level constants:**
- `_PR3B1_SHOT_TYPE_ENUM` — L11639
- `_PR3B1_CAMERA_ANGLE_ENUM` — L11643
- `_PR3B1_LIGHTING_ENUM` — L11648
- `_PR3B1_CAMERA_MOTION_ENUM` — L11653
- `_EMOTION_NARRATION_STYLE_MAP` — L12705

**Functions:**
- `_generate_motion_prompts` — L11172
- `_motion_tasks_file` — L11239
- `_motion_qa_file` — L11243
- `_append_motion_qa` — L11247
- `_finalize_motion_qa` — L11271
- `_lip_sync_tasks_file` — L11355
- `_load_motion_tasks` — L11359
- `_save_motion_task` — L11369
- `_remove_motion_task` — L11377
- `_load_lip_sync_tasks` — L11384
- `_save_lip_sync_task` — L11394
- `_remove_lip_sync_task` — L11401
- `_video_visual_motion_qa` — L11408
- `_motion_output_qa` — L11480
- `_has_audio_stream` — L11525
- `_normalize_motion_video` — L11536
- `_motion_poll_and_download` — L11586
- `_validate_enum_field` — L11659
- `_build_motion_video_prompt` — L11674
- `_short_board_text` — L11724
- `_wrap_board_text` — L11731
- `_storyboard_font` — L11762
- `_draw_storyboard_arrow` — L11777
- `_build_annotated_storyboard_reference` — L11791
- `_plain_caption_text` — L11892
- `_werydance_caption_request` — L11900
- `_werydance_caption_instruction` — L11927
- `_werydance_negative_prompt` — L11939
- `_motion_reference_prompt` — L11957
- `_motion_audio_dub_prompt` — L11980
- `_motion_audio_dub_poll_and_download` — L12014
- `_try_motion_audio_dub_video` — L12079
- `_try_motion_reference_video` — L12242
- `_motion_one_scene` — L12358
- `_grid_multiref_tasks_file` — L12488
- `_previs_page_tasks_file` — L12492
- `_load_grid_multiref_tasks` — L12496
- `_load_previs_page_tasks` — L12506
- `_save_grid_multiref_task` — L12516
- `_save_previs_page_task` — L12523
- `_remove_grid_multiref_task` — L12530
- `_remove_previs_page_task` — L12537
- `_poll_video_task_download` — L12544
- `_grid_multiref_group_size` — L12593
- `_grid_multiref_adaptive_group_size` — L12603
- `_grid_multiref_duration` — L12627
- `_grid_multiref_tts_buffer_factor` — L12665
- `_grid_multiref_tts_duration_buffered` — L12679
- `_grid_multiref_segment_max_stretch` — L12695
- `_voice_clone_emotion_style` — L12729
- `_grid_multiref_prompt` — L12752
- `_write_grid_multiref_motion_qa` — L12826
- `_write_previs_page_motion_qa` — L12836
- `_write_storyboard_trailer_qa` — L12846
- `_write_character_trailer_qa` — L12856
- `_write_grid_multiref_segment_qa` — L12866
- `_motion_compare_record` — L12876
- `_write_storyboard_motion_compare_qa` — L12898
- `_scene_segment_duration` — L12934
- `_apply_grid_multiref_segments` — L12953
- `_previs_page_duration` — L13158
- `_previs_page_group_prompt` — L13169
- `_previs_page_groups` — L13195
- `_storyboard_trailer_duration` — L13210
- `_storyboard_trailer_prompt` — L13220
- `_character_trailer_max_shots` — L13248
- `_character_trailer_shot_duration` — L13256
- `_character_trailer_prompt` — L13272
- `_concat_character_trailer_segments` — L13287
- `_generate_character_trailer_motion` — L13326
- `_multi_trailer_prompt_for_group` — L13434
- `_generate_multi_trailer_segments` — L13457
- `_generate_storyboard_trailer_motion` — L13568
- `_generate_previs_page_motion_segments` — L13643
- `_generate_grid_multiref_motion_segments` — L13755
- `_grid_multiref_concat_groups` — L14065
- `_grid_multiref_concat_groups_partial` — L14082
- `_grid_multiref_concat_paths` — L14100
- `_lip_sync_slot_duration` — L14142
- `_adsd_lip_sync_prompt` — L14149
- `_adsd_broll_motion_prompt` — L14195
- `_adsd_action_b_motion_prompt` — L14237
- `_adsd_silent_b_motion_prompt` — L14283
- `_adsd_narrated_b_audio_dub_prompt` — L14318
- `_adsd_almighty_audio_dub_prompt` — L14362
- `_postprocess_lip_sync_segment` — L14403
- `_detect_audio_leading_silence` — L14475
- `_concat_audio_files_for_group` — L14500
- `_split_lip_sync_raw_by_durations` — L14523
- `_postprocess_audio_dub_segment` — L14558
- `_lips_change_repair_segment` — L14686
- `_load_lips_change_requested_turns` — L14771
- `_parse_turn_set` — L14788
- `_load_motion_voice_repair_turns` — L14810
- `_voice_assets_file` — L14822
- `_load_voice_assets` — L14829
- `_build_combined_voice_reference` — L14848
- `_select_voice_asset_reference` — L14890
- `_lip_sync_poll_download_and_process` — L14966
- `_lip_sync_one_group` — L15034
- `_lip_sync_one_scene` — L15242
- `step66_adsd_lip_sync` — L15566
- `step65_motion` — L15911
- `step65_grid_multiref_motion_qa` — L16064
- `_sanitize_scene_for_state` — L16093
- `_save_pipeline_state` — L16112
- `_retime_after_audio_dub` — L16136
- `_build_voice_clone_hybrid_audio` — L16174
- `_build_dynamic_bgm` — L16313

---

### 第七步：拼接视频轨
Range: **L16357 – L16616** (260 lines)

**Functions:**
- `step7_concat` — L16358

---

### 第八步：生成 ASS 字幕
Range: **L16617 – L17575** (959 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L16896-17575 (680 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L16618
- `_word_timings_for_subtitle_align` — L16644
- `_align_segments_via_asr` — L16685
- `_b61_1_asr_turn_boundaries` — L16728
- `step8_subtitles` — L16790
- `_read_output_json` — L17296
- `_qa_file_pass` — L17307
- `_ass_has_dialogue` — L17314
- `_write_adsd_delivery_qa` — L17324
- `_write_bgm_only_qa` — L17464

---

### 第九步：最终合成
Range: **L17576 – L17866** (291 lines)

**Functions:**
- `step9_render` — L17577

---

### 第十步：推送 Telegram
Range: **L17867 – L19729** (1863 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L18973-19082 (110 lines)
- _B70 (2026-05-30) TG oversize policy helpers_ — L19083-19536 (454 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L19537-19541 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L19542-19605 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L19606-19651 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L19652-19729 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L18236
- `PANTONE_FALLBACK` — L18263
- `FESTIVAL_DATE_TAG` — L18377

**Functions:**
- `_generate_caption` — L17868
- `_overlay_title_on_cover` — L18106
- `_prepare_tg_photo` — L18216
- `_get_pantone_for_date` — L18266
- `_llm_bottom_note` — L18291
- `_get_bottom_note` — L18321
- `_get_date_tag` — L18399
- `_shrink_to_b64` — L18421
- `_llm_check_scenes_anomalies` — L18437
- `_llm_check_cover_unique` — L18490
- `_llm_check_cover_quality` — L18520
- `_try_almanac_cover` — L18562
- `_generate_cover_image` — L18733
- `_async_kickoff_cover_caption` — L18980
- `_await_async_cover_caption` — L19056
- `_b70_env_float` — L19086
- `_b70_split_and_deliver` — L19101
- `_b70_send_document_first` — L19201
- `step10_deliver` — L19238

---

### 主流程
Range: **L19730 – L19957** (228 lines)

**Functions:**
- `_print_execution_plan` — L19731
- `_write_run_timings` — L19779
- `main` — L19808

---
