# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (18653 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-2198 (2077 lines · 62 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L2199-4615 (2417 lines · 30 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L4616-5747 (1132 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L5748-6299 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L6300-10532 (4233 lines · 96 fn · 6 sub)
- [`第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）`](#第-6-5-步-动态化-hads-vads-默认-on---no-motion-关) — L10533-15467 (4935 lines · 106 fn · 5 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L15468-15727 (260 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L15728-16530 (803 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L16531-16806 (276 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L16807-18468 (1662 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L18469-18653 (185 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L2198** (2077 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L324-453 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L454-1185 (732 lines)
- _工具函数_ — L1186-1562 (377 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1563-2198 (636 lines)

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
- `_GENERIC_NARRATOR_NAMES` — L889
- `VOICE_ASSET_AUDIO_DUB_EXPERIMENT` — L926
- `VOICE_ASSET_AUDIO_DUB_PARTIAL_OK` — L934
- `MOTION_VISUAL_QA` — L938
- `MOTION_VOICE_REPAIR` — L946
- `MOTION_VOICE_STRICT_LOCK` — L951
- `WERYDANCE_CAPTIONS` — L956
- `ADSD_ONSITE_POV_MODE` — L968
- `ADSD_LIPS_CHANGE_REPAIR` — L973
- `ADSD_LIPS_CHANGE_ALL` — L978
- `ADS_REPORTER_MODE` — L989
- `ADS_STORYBOARD_FLOW_DEFAULT` — L1006
- `ADS_RETENTION_MODE` — L1020
- `ADSD_MODE_NAME` — L1026
- `EMOTION_STYLE` — L1165
- `EMOTION_STYLE_BRIGHT` — L1177
- `_TG_DASHBOARD_STAGES` — L1199
- `_TG_NOISY_PATTERNS` — L1214
- `_TG_IMMEDIATE_PATTERNS` — L1232
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1492
- `_LLM_TIER` — L1740
- `_TOPIC_MODIFIERS` — L1951
- `_TONE_PANTONE_OVERRIDE` — L1968

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
- `_resolve_voice_asset_for_ads_speaker` — L892
- `log` — L1187
- `_tg_send_raw` — L1255
- `_tg_matches` — L1271
- `_tg_summarize` — L1275
- `_tg_dashboard_stage_for` — L1282
- `_tg_progress_bar` — L1290
- `_tg_dashboard_text` — L1296
- `_tg_dashboard_update` — L1314
- `_tg_maybe_digest` — L1351
- `tg` — L1366
- `_wait_image_submit_slot` — L1415
- `_wait_motion_submit_slot` — L1428
- `_is_rate_limited_error` — L1441
- `_is_rate_limited_response` — L1451
- `_is_llm_rate_limited_error` — L1472
- `_inject_image2_quality_suffix` — L1500
- `submit_text_to_image` — L1514
- `req_post` — L1544
- `req_get` — L1558
- `_tg_probe_send` — L1566
- `_tg_probe_delete` — L1586
- `_tg_upload_with_probe_gap` — L1599
- `poll` — L1639
- `poll_podcast` — L1664
- `poll_task_status` — L1686
- `poll_storyboard_task` — L1708
- `tier_chat` — L1748
- `chat` — L1754
- `pick_image_model` — L1797
- `detect_topic_meta` — L1822
- `_topic_culture_guard` — L1872
- `_write_cultural_visual_qa` — L1898
- `is_1919_global_topic` — L1945
- `_strip_topic_modifiers` — L1956
- `apply_1919_global_guardrails` — L1974
- `build_1919_global_cover_prompt` — L2003
- `_shot_blueprint_enums` — L2035
- `build_shot_blueprint` — L2111
- `ffprobe_duration` — L2137
- `ffprobe_video_size` — L2148
- `_video_decode_probe` — L2169
- `ffmpeg` — L2187

---

### 第一步：双导演生成剧本
Range: **L2199 – L4615** (2417 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L3663-4615 (953 lines)

**Top-level constants:**
- `_ENSEMBLE_CAP_BY_ROUTE` — L2347

**Functions:**
- `_extract_json_array` — L2200
- `_extract_json_object` — L2210
- `_voice_for_speaker` — L2220
- `_adsd_gender_from_voice` — L2256
- `_adsd_infer_gender_from_speaker` — L2264
- `_adsd_gender_lock_phrase` — L2273
- `_adsd_visual_subject_has_gender_conflict` — L2288
- `_adsd_default_roles` — L2300
- `_adsd_allows_media_role` — L2305
- `_adsd_role_candidates` — L2313
- `_adsd_dialogue_shape` — L2336
- `_ensemble_speaker_cap` — L2358
- `_finalize_adsd_turns` — L2371
- `_parse_adsd_override_turns` — L2405
- `_parse_timecode_seconds` — L2498
- `_clean_override_line_text` — L2507
- `_parse_override_script_text` — L2513
- `_adsd_pov_contract` — L2547
- `_load_audit_blacklist_block` — L2560
- `_generate_adsd_dialogue_turns` — L2598
- `_broll_rhythm_reviewer` — L3025
- `_sweep_speaker_field` — L3132
- `_should_run_immersion_qa` — L3192
- `_adsd_immersion_qa_rewrite_turns` — L3215
- `_adsd_visual_contract` — L3279
- `_parse_risk_score` — L3331
- `_check_high_risk_hard_abort` — L3360
- `_maybe_neutralize_topic` — L3387
- `step1_script` — L3426
- `_write_ads_retention_qa` — L4559

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L4616 – L5747** (1132 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L4691
- `_ADSD_POLICY_REWRITE_TERMS` — L4697
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L4788

**Functions:**
- `_openai_tts_fallback` — L4617
- `_edge_tts_fallback` — L4663
- `_sanitize_for_external_api` — L4706
- `_is_content_policy_error` — L4715
- `_rewrite_adsd_tts_text_for_policy` — L4729
- `_record_adsd_tts_rewrite` — L4769
- `_build_silence_mp3` — L4794
- `_audio_duration_seconds` — L4807
- `_text_to_audio_master_voice_timed` — L4819
- `_text_to_audio_master_voice` — L4944
- `step2_master_voice` — L5057
- `_tts_turn_to_audio` — L5185
- `_asr_verify_dialogue_audio` — L5249
- `_asr_verify_dialogue_turns` — L5311
- `_normalize_cn_number_token` — L5353
- `_compact_zh_text` — L5375
- `_write_adsd_asr_text_qa` — L5382
- `_write_adsd_speaker_focus_qa` — L5421
- `_write_adsd_gender_voice_qa` — L5481
- `step2_dialogue_voice` — L5534

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L5748 – L6299** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L5755-5877 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L5878-5912 (35 lines)
- _第二层：字符数插值_ — L5913-5937 (25 lines)
- _第三层：silencedetect 物理校准_ — L5938-6299 (362 lines)

**Functions:**
- `_detect_silences` — L5756
- `_calibrate_boundaries` — L5791
- `_enforce_monotonic` — L5825
- `_manual_override_segments` — L5837
- `_calc_sentence_boundaries` — L5858
- `step345_timeline` — L5969
- `_analyze_bgm_energy_cuts` — L6028
- `_snap_bgm_only_boundaries` — L6091
- `step345_bgm_only_timeline` — L6151

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L6300 – L10532** (4233 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L7521-7571 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L7572-8142 (571 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L8143-8577 (435 lines)
- _Speaker IP Card (2026-05-21)_ — L8578-10365 (1788 lines)
- _审批流程_ — L10366-10422 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L10423-10532 (110 lines)

**Top-level constants:**
- `_CORE_TERMS_STOP_WORDS` — L6695
- `CHARACTER_META_GRID_COSTUMES` — L7527
- `CHARACTER_META_GRID_POSES` — L7528
- `CHARACTER_META_GRID_SCENES` — L7529
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L7532
- `_SFX_TYPE_ENUM` — L7887
- `_SFX_INTENSITY_ENUM` — L7892
- `_SFX_POSITION_ENUM` — L7893

**Functions:**
- `_extract_img_url` — L6301
- `_extract_img_urls` — L6323
- `_extract_video_url` — L6356
- `_count_bands` — L6381
- `_detect_contact_sheet_like_image` — L6393
- `_file_sha256` — L6454
- `_load_upload_cache` — L6467
- `_save_upload_cache` — L6476
- `_cached_upload_url` — L6484
- `_store_upload_url` — L6501
- `_guess_upload_mime` — L6511
- `_upload_to_weryai` — L6534
- `_send_for_approval` — L6588
- `_wait_approval` — L6652
- `_render_still_segment` — L6664
- `_extract_core_terms` — L6701
- `_scene_text_visual_alignment` — L6720
- `_write_text_visual_alignment_qa` — L6741
- `_scene_motion_action_plan` — L6764
- `_ensure_motion_action_plan` — L6818
- `_motion_action_block` — L6827
- `_motion_plan_for_qa` — L6855
- `_write_motion_action_plan_qa` — L6865
- `_write_motion_bridge_refs_qa` — L6895
- `_motion_bridge_ref_prompt` — L6902
- `generate_motion_bridge_refs_gpt_image2` — L6935
- `generate_image` — L7050
- `generate_storyboard_images_gpt_image2` — L7097
- `_storyboard_grid_aspect` — L7282
- `_storyboard_grid_cols_rows` — L7289
- `_storyboard_grid_prompt` — L7311
- `_storyboard_grid_prompt_limit` — L7369
- `_is_prompt_limit_response` — L7373
- `_production_storyboard_prompt` — L7379
- `_write_production_storyboard_page_qa` — L7413
- `_character_sheet_prompt` — L7423
- `_is_audit_blocked` — L7549
- `_paraphrase_sensitive_dialogue` — L7562
- `_topic_cache_dir` — L7576
- `_topic_cache_path` — L7582
- `_load_topic_decomposition_cache` — L7595
- `_save_topic_decomposition_cache` — L7613
- `_briefs_dir` — L7650
- `_brief_path` — L7656
- `_empty_brief` — L7661
- `_deep_merge_brief_skeleton` — L7699
- `_load_brief` — L7713
- `_save_brief` — L7737
- `_brief_get` — L7756
- `_brief_set` — L7768
- `_brief_claim` — L7784
- `_brief_agent_status` — L7827
- `_brief_from_topic_decomposition` — L7840
- `_rule_based_sfx_design` — L7896
- `_validate_sfx_entry` — L7947
- `_audio_director_design` — L7985
- `_llm_topic_decomposition` — L8032
- `_director_route_block` — L8196
- `_llm_infer_meta_grid_template` — L8266
- `_resolve_meta_grid_template` — L8323
- `_infer_meta_grid_costume` — L8366
- `_infer_meta_grid_pose` — L8415
- `_adsd_meta_grid_call_prompt` — L8462
- `_meta_grid_panel_index` — L8504
- `_migrate_speaker_ip` — L8584
- `_speaker_ips_dir` — L8609
- `_list_speaker_ips` — L8616
- `_match_speaker_ip` — L8630
- `_build_speaker_ip_context_for_script` — L8650
- `_ip_usage_stats` — L8706
- `_recommend_related_ips` — L8724
- `_save_speaker_ip` — L8749
- `_record_speaker_usage_history` — L8758
- `_format_speaker_usage_history_for_prompt` — L8805
- `_llm_infer_ip_skeleton` — L8823
- `_llm_pick_voice_asset_for_ip` — L8868
- `_auto_incubate_missing_ips` — L8916
- `_character_meta_grid_cache_dir` — L9000
- `_character_meta_grid_cache_path` — L9008
- `_character_meta_grid_cache_legacy_path` — L9016
- `_character_meta_grid_path` — L9023
- `generate_character_meta_grid_gpt_image2` — L9029
- `_generate_all_character_meta_grids` — L9201
- `_write_character_sheet_qa` — L9242
- `generate_character_sheet_gpt_image2` — L9252
- `generate_production_storyboard_page_gpt_image2` — L9352
- `_qa_clean_storyboard_panel` — L9415
- `_crop_storyboard_grid_panels` — L9596
- `generate_storyboard_grid_gpt_image2` — L9643
- `_gpt_image2_direct_annotated_aspect` — L9874
- `_gpt_image2_direct_annotated_prompt` — L9881
- `generate_gpt_image2_direct_annotated_storyboards` — L9911
- `_llm_bgm_description` — L10012
- `_bgm_contains_vocals` — L10051
- `generate_bgm` — L10085
- `step6_parallel` — L10202

---

### 第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）
Range: **L10533 – L15467** (4935 lines)

**Sub-sections:**
- _PR-A (2026-05-27): merged_a 合并跑 helpers_ — L13729-15202 (1474 lines)
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L15203-15245 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L15246-15283 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回时间轴锚定音轨_ — L15284-15422 (139 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L15423-15467 (45 lines)

**Top-level constants:**
- `_PR3B1_SHOT_TYPE_ENUM` — L11003
- `_PR3B1_CAMERA_ANGLE_ENUM` — L11007
- `_PR3B1_LIGHTING_ENUM` — L11012
- `_PR3B1_CAMERA_MOTION_ENUM` — L11017

**Functions:**
- `_generate_motion_prompts` — L10536
- `_motion_tasks_file` — L10603
- `_motion_qa_file` — L10607
- `_append_motion_qa` — L10611
- `_finalize_motion_qa` — L10635
- `_lip_sync_tasks_file` — L10719
- `_load_motion_tasks` — L10723
- `_save_motion_task` — L10733
- `_remove_motion_task` — L10741
- `_load_lip_sync_tasks` — L10748
- `_save_lip_sync_task` — L10758
- `_remove_lip_sync_task` — L10765
- `_video_visual_motion_qa` — L10772
- `_motion_output_qa` — L10844
- `_has_audio_stream` — L10889
- `_normalize_motion_video` — L10900
- `_motion_poll_and_download` — L10950
- `_validate_enum_field` — L11023
- `_build_motion_video_prompt` — L11038
- `_short_board_text` — L11088
- `_wrap_board_text` — L11095
- `_storyboard_font` — L11126
- `_draw_storyboard_arrow` — L11141
- `_build_annotated_storyboard_reference` — L11155
- `_plain_caption_text` — L11256
- `_werydance_caption_request` — L11264
- `_werydance_caption_instruction` — L11291
- `_werydance_negative_prompt` — L11303
- `_motion_reference_prompt` — L11321
- `_motion_audio_dub_prompt` — L11344
- `_motion_audio_dub_poll_and_download` — L11378
- `_try_motion_audio_dub_video` — L11443
- `_try_motion_reference_video` — L11606
- `_motion_one_scene` — L11722
- `_grid_multiref_tasks_file` — L11851
- `_previs_page_tasks_file` — L11855
- `_load_grid_multiref_tasks` — L11859
- `_load_previs_page_tasks` — L11869
- `_save_grid_multiref_task` — L11879
- `_save_previs_page_task` — L11886
- `_remove_grid_multiref_task` — L11893
- `_remove_previs_page_task` — L11900
- `_poll_video_task_download` — L11907
- `_grid_multiref_group_size` — L11956
- `_grid_multiref_duration` — L11966
- `_grid_multiref_tts_buffer_factor` — L12004
- `_grid_multiref_tts_duration_buffered` — L12018
- `_grid_multiref_segment_max_stretch` — L12034
- `_grid_multiref_prompt` — L12042
- `_write_grid_multiref_motion_qa` — L12112
- `_write_previs_page_motion_qa` — L12122
- `_write_storyboard_trailer_qa` — L12132
- `_write_character_trailer_qa` — L12142
- `_write_grid_multiref_segment_qa` — L12152
- `_motion_compare_record` — L12162
- `_write_storyboard_motion_compare_qa` — L12184
- `_scene_segment_duration` — L12220
- `_apply_grid_multiref_segments` — L12239
- `_previs_page_duration` — L12444
- `_previs_page_group_prompt` — L12454
- `_previs_page_groups` — L12480
- `_storyboard_trailer_duration` — L12495
- `_storyboard_trailer_prompt` — L12505
- `_character_trailer_max_shots` — L12533
- `_character_trailer_shot_duration` — L12541
- `_character_trailer_prompt` — L12555
- `_concat_character_trailer_segments` — L12570
- `_generate_character_trailer_motion` — L12609
- `_multi_trailer_prompt_for_group` — L12717
- `_generate_multi_trailer_segments` — L12740
- `_generate_storyboard_trailer_motion` — L12851
- `_generate_previs_page_motion_segments` — L12926
- `_generate_grid_multiref_motion_segments` — L13038
- `_grid_multiref_concat_groups` — L13297
- `_grid_multiref_concat_groups_partial` — L13314
- `_grid_multiref_concat_paths` — L13332
- `_lip_sync_slot_duration` — L13374
- `_adsd_lip_sync_prompt` — L13381
- `_adsd_broll_motion_prompt` — L13427
- `_adsd_action_b_motion_prompt` — L13469
- `_adsd_silent_b_motion_prompt` — L13515
- `_adsd_narrated_b_audio_dub_prompt` — L13550
- `_adsd_almighty_audio_dub_prompt` — L13594
- `_postprocess_lip_sync_segment` — L13635
- `_detect_audio_leading_silence` — L13707
- `_concat_audio_files_for_group` — L13732
- `_split_lip_sync_raw_by_durations` — L13755
- `_postprocess_audio_dub_segment` — L13790
- `_lips_change_repair_segment` — L13905
- `_load_lips_change_requested_turns` — L13990
- `_parse_turn_set` — L14007
- `_load_motion_voice_repair_turns` — L14029
- `_voice_assets_file` — L14041
- `_load_voice_assets` — L14048
- `_select_voice_asset_reference` — L14067
- `_lip_sync_poll_download_and_process` — L14133
- `_lip_sync_one_group` — L14201
- `_lip_sync_one_scene` — L14378
- `step66_adsd_lip_sync` — L14702
- `step65_motion` — L15023
- `step65_grid_multiref_motion_qa` — L15175
- `_sanitize_scene_for_state` — L15204
- `_save_pipeline_state` — L15223
- `_retime_after_audio_dub` — L15247
- `_build_voice_clone_hybrid_audio` — L15285
- `_build_dynamic_bgm` — L15424

---

### 第七步：拼接视频轨
Range: **L15468 – L15727** (260 lines)

**Functions:**
- `step7_concat` — L15469

---

### 第八步：生成 ASS 字幕
Range: **L15728 – L16530** (803 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L15851-16530 (680 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L15729
- `_word_timings_for_subtitle_align` — L15755
- `_align_segments_via_asr` — L15796
- `step8_subtitles` — L15839
- `_read_output_json` — L16251
- `_qa_file_pass` — L16262
- `_ass_has_dialogue` — L16269
- `_write_adsd_delivery_qa` — L16279
- `_write_bgm_only_qa` — L16419

---

### 第九步：最终合成
Range: **L16531 – L16806** (276 lines)

**Functions:**
- `step9_render` — L16532

---

### 第十步：推送 Telegram
Range: **L16807 – L18468** (1662 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L17907-18275 (369 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L18276-18280 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L18281-18344 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L18345-18390 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L18391-18468 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L17176
- `PANTONE_FALLBACK` — L17203
- `FESTIVAL_DATE_TAG` — L17316

**Functions:**
- `_generate_caption` — L16808
- `_overlay_title_on_cover` — L17046
- `_prepare_tg_photo` — L17156
- `_get_pantone_for_date` — L17206
- `_llm_bottom_note` — L17231
- `_get_bottom_note` — L17260
- `_get_date_tag` — L17338
- `_shrink_to_b64` — L17360
- `_llm_check_scenes_anomalies` — L17376
- `_llm_check_cover_unique` — L17429
- `_llm_check_cover_quality` — L17459
- `_try_almanac_cover` — L17501
- `_generate_cover_image` — L17672
- `_async_kickoff_cover_caption` — L17914
- `_await_async_cover_caption` — L17988
- `step10_deliver` — L18015

---

### 主流程
Range: **L18469 – L18653** (185 lines)

**Functions:**
- `_print_execution_plan` — L18470
- `main` — L18518

---
