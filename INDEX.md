# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (18134 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-2119 (1998 lines · 61 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L2120-4412 (2293 lines · 30 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L4413-5544 (1132 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L5545-6096 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L6097-10131 (4035 lines · 92 fn · 6 sub)
- [`第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）`](#第-6-5-步-动态化-hads-vads-默认-on---no-motion-关) — L10132-14948 (4817 lines · 103 fn · 5 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L14949-15208 (260 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L15209-16011 (803 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L16012-16287 (276 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L16288-17949 (1662 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L17950-18134 (185 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L2119** (1998 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L324-453 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L454-1185 (732 lines)
- _工具函数_ — L1186-1562 (377 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1563-2119 (557 lines)

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
- `build_shot_blueprint` — L2032
- `ffprobe_duration` — L2058
- `ffprobe_video_size` — L2069
- `_video_decode_probe` — L2090
- `ffmpeg` — L2108

---

### 第一步：双导演生成剧本
Range: **L2120 – L4412** (2293 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L3584-4412 (829 lines)

**Top-level constants:**
- `_ENSEMBLE_CAP_BY_ROUTE` — L2268

**Functions:**
- `_extract_json_array` — L2121
- `_extract_json_object` — L2131
- `_voice_for_speaker` — L2141
- `_adsd_gender_from_voice` — L2177
- `_adsd_infer_gender_from_speaker` — L2185
- `_adsd_gender_lock_phrase` — L2194
- `_adsd_visual_subject_has_gender_conflict` — L2209
- `_adsd_default_roles` — L2221
- `_adsd_allows_media_role` — L2226
- `_adsd_role_candidates` — L2234
- `_adsd_dialogue_shape` — L2257
- `_ensemble_speaker_cap` — L2279
- `_finalize_adsd_turns` — L2292
- `_parse_adsd_override_turns` — L2326
- `_parse_timecode_seconds` — L2419
- `_clean_override_line_text` — L2428
- `_parse_override_script_text` — L2434
- `_adsd_pov_contract` — L2468
- `_load_audit_blacklist_block` — L2481
- `_generate_adsd_dialogue_turns` — L2519
- `_broll_rhythm_reviewer` — L2946
- `_sweep_speaker_field` — L3053
- `_should_run_immersion_qa` — L3113
- `_adsd_immersion_qa_rewrite_turns` — L3136
- `_adsd_visual_contract` — L3200
- `_parse_risk_score` — L3252
- `_check_high_risk_hard_abort` — L3281
- `_maybe_neutralize_topic` — L3308
- `step1_script` — L3347
- `_write_ads_retention_qa` — L4356

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L4413 – L5544** (1132 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L4488
- `_ADSD_POLICY_REWRITE_TERMS` — L4494
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L4585

**Functions:**
- `_openai_tts_fallback` — L4414
- `_edge_tts_fallback` — L4460
- `_sanitize_for_external_api` — L4503
- `_is_content_policy_error` — L4512
- `_rewrite_adsd_tts_text_for_policy` — L4526
- `_record_adsd_tts_rewrite` — L4566
- `_build_silence_mp3` — L4591
- `_audio_duration_seconds` — L4604
- `_text_to_audio_master_voice_timed` — L4616
- `_text_to_audio_master_voice` — L4741
- `step2_master_voice` — L4854
- `_tts_turn_to_audio` — L4982
- `_asr_verify_dialogue_audio` — L5046
- `_asr_verify_dialogue_turns` — L5108
- `_normalize_cn_number_token` — L5150
- `_compact_zh_text` — L5172
- `_write_adsd_asr_text_qa` — L5179
- `_write_adsd_speaker_focus_qa` — L5218
- `_write_adsd_gender_voice_qa` — L5278
- `step2_dialogue_voice` — L5331

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L5545 – L6096** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L5552-5674 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L5675-5709 (35 lines)
- _第二层：字符数插值_ — L5710-5734 (25 lines)
- _第三层：silencedetect 物理校准_ — L5735-6096 (362 lines)

**Functions:**
- `_detect_silences` — L5553
- `_calibrate_boundaries` — L5588
- `_enforce_monotonic` — L5622
- `_manual_override_segments` — L5634
- `_calc_sentence_boundaries` — L5655
- `step345_timeline` — L5766
- `_analyze_bgm_energy_cuts` — L5825
- `_snap_bgm_only_boundaries` — L5888
- `step345_bgm_only_timeline` — L5948

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L6097 – L10131** (4035 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L7298-7348 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L7349-7741 (393 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L7742-8176 (435 lines)
- _Speaker IP Card (2026-05-21)_ — L8177-9964 (1788 lines)
- _审批流程_ — L9965-10021 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L10022-10131 (110 lines)

**Top-level constants:**
- `_CORE_TERMS_STOP_WORDS` — L6492
- `CHARACTER_META_GRID_COSTUMES` — L7304
- `CHARACTER_META_GRID_POSES` — L7305
- `CHARACTER_META_GRID_SCENES` — L7306
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L7309

**Functions:**
- `_extract_img_url` — L6098
- `_extract_img_urls` — L6120
- `_extract_video_url` — L6153
- `_count_bands` — L6178
- `_detect_contact_sheet_like_image` — L6190
- `_file_sha256` — L6251
- `_load_upload_cache` — L6264
- `_save_upload_cache` — L6273
- `_cached_upload_url` — L6281
- `_store_upload_url` — L6298
- `_guess_upload_mime` — L6308
- `_upload_to_weryai` — L6331
- `_send_for_approval` — L6385
- `_wait_approval` — L6449
- `_render_still_segment` — L6461
- `_extract_core_terms` — L6498
- `_scene_text_visual_alignment` — L6517
- `_write_text_visual_alignment_qa` — L6538
- `_scene_motion_action_plan` — L6561
- `_ensure_motion_action_plan` — L6615
- `_motion_action_block` — L6624
- `_motion_plan_for_qa` — L6652
- `_write_motion_action_plan_qa` — L6662
- `_write_motion_bridge_refs_qa` — L6692
- `_motion_bridge_ref_prompt` — L6699
- `generate_motion_bridge_refs_gpt_image2` — L6732
- `generate_image` — L6847
- `generate_storyboard_images_gpt_image2` — L6894
- `_storyboard_grid_aspect` — L7079
- `_storyboard_grid_cols_rows` — L7086
- `_storyboard_grid_prompt` — L7108
- `_storyboard_grid_prompt_limit` — L7146
- `_is_prompt_limit_response` — L7150
- `_production_storyboard_prompt` — L7156
- `_write_production_storyboard_page_qa` — L7190
- `_character_sheet_prompt` — L7200
- `_is_audit_blocked` — L7326
- `_paraphrase_sensitive_dialogue` — L7339
- `_topic_cache_dir` — L7353
- `_topic_cache_path` — L7359
- `_load_topic_decomposition_cache` — L7372
- `_save_topic_decomposition_cache` — L7390
- `_briefs_dir` — L7427
- `_brief_path` — L7433
- `_empty_brief` — L7438
- `_load_brief` — L7476
- `_save_brief` — L7498
- `_brief_get` — L7517
- `_brief_set` — L7529
- `_brief_claim` — L7545
- `_brief_agent_status` — L7588
- `_brief_from_topic_decomposition` — L7601
- `_llm_topic_decomposition` — L7640
- `_director_route_block` — L7795
- `_llm_infer_meta_grid_template` — L7865
- `_resolve_meta_grid_template` — L7922
- `_infer_meta_grid_costume` — L7965
- `_infer_meta_grid_pose` — L8014
- `_adsd_meta_grid_call_prompt` — L8061
- `_meta_grid_panel_index` — L8103
- `_migrate_speaker_ip` — L8183
- `_speaker_ips_dir` — L8208
- `_list_speaker_ips` — L8215
- `_match_speaker_ip` — L8229
- `_build_speaker_ip_context_for_script` — L8249
- `_ip_usage_stats` — L8305
- `_recommend_related_ips` — L8323
- `_save_speaker_ip` — L8348
- `_record_speaker_usage_history` — L8357
- `_format_speaker_usage_history_for_prompt` — L8404
- `_llm_infer_ip_skeleton` — L8422
- `_llm_pick_voice_asset_for_ip` — L8467
- `_auto_incubate_missing_ips` — L8515
- `_character_meta_grid_cache_dir` — L8599
- `_character_meta_grid_cache_path` — L8607
- `_character_meta_grid_cache_legacy_path` — L8615
- `_character_meta_grid_path` — L8622
- `generate_character_meta_grid_gpt_image2` — L8628
- `_generate_all_character_meta_grids` — L8800
- `_write_character_sheet_qa` — L8841
- `generate_character_sheet_gpt_image2` — L8851
- `generate_production_storyboard_page_gpt_image2` — L8951
- `_qa_clean_storyboard_panel` — L9014
- `_crop_storyboard_grid_panels` — L9195
- `generate_storyboard_grid_gpt_image2` — L9242
- `_gpt_image2_direct_annotated_aspect` — L9473
- `_gpt_image2_direct_annotated_prompt` — L9480
- `generate_gpt_image2_direct_annotated_storyboards` — L9510
- `_llm_bgm_description` — L9611
- `_bgm_contains_vocals` — L9650
- `generate_bgm` — L9684
- `step6_parallel` — L9801

---

### 第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）
Range: **L10132 – L14948** (4817 lines)

**Sub-sections:**
- _PR-A (2026-05-27): merged_a 合并跑 helpers_ — L13210-14683 (1474 lines)
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L14684-14726 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L14727-14764 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回时间轴锚定音轨_ — L14765-14903 (139 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L14904-14948 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L10135
- `_motion_tasks_file` — L10202
- `_motion_qa_file` — L10206
- `_append_motion_qa` — L10210
- `_finalize_motion_qa` — L10234
- `_lip_sync_tasks_file` — L10318
- `_load_motion_tasks` — L10322
- `_save_motion_task` — L10332
- `_remove_motion_task` — L10340
- `_load_lip_sync_tasks` — L10347
- `_save_lip_sync_task` — L10357
- `_remove_lip_sync_task` — L10364
- `_video_visual_motion_qa` — L10371
- `_motion_output_qa` — L10443
- `_has_audio_stream` — L10488
- `_normalize_motion_video` — L10499
- `_motion_poll_and_download` — L10549
- `_build_motion_video_prompt` — L10600
- `_short_board_text` — L10630
- `_wrap_board_text` — L10637
- `_storyboard_font` — L10668
- `_draw_storyboard_arrow` — L10683
- `_build_annotated_storyboard_reference` — L10697
- `_plain_caption_text` — L10798
- `_werydance_caption_request` — L10806
- `_werydance_caption_instruction` — L10833
- `_werydance_negative_prompt` — L10845
- `_motion_reference_prompt` — L10863
- `_motion_audio_dub_prompt` — L10886
- `_motion_audio_dub_poll_and_download` — L10920
- `_try_motion_audio_dub_video` — L10985
- `_try_motion_reference_video` — L11148
- `_motion_one_scene` — L11264
- `_grid_multiref_tasks_file` — L11393
- `_previs_page_tasks_file` — L11397
- `_load_grid_multiref_tasks` — L11401
- `_load_previs_page_tasks` — L11411
- `_save_grid_multiref_task` — L11421
- `_save_previs_page_task` — L11428
- `_remove_grid_multiref_task` — L11435
- `_remove_previs_page_task` — L11442
- `_poll_video_task_download` — L11449
- `_grid_multiref_group_size` — L11498
- `_grid_multiref_duration` — L11508
- `_grid_multiref_segment_max_stretch` — L11530
- `_grid_multiref_prompt` — L11538
- `_write_grid_multiref_motion_qa` — L11608
- `_write_previs_page_motion_qa` — L11618
- `_write_storyboard_trailer_qa` — L11628
- `_write_character_trailer_qa` — L11638
- `_write_grid_multiref_segment_qa` — L11648
- `_motion_compare_record` — L11658
- `_write_storyboard_motion_compare_qa` — L11680
- `_scene_segment_duration` — L11716
- `_apply_grid_multiref_segments` — L11735
- `_previs_page_duration` — L11940
- `_previs_page_group_prompt` — L11950
- `_previs_page_groups` — L11976
- `_storyboard_trailer_duration` — L11991
- `_storyboard_trailer_prompt` — L12001
- `_character_trailer_max_shots` — L12029
- `_character_trailer_shot_duration` — L12037
- `_character_trailer_prompt` — L12051
- `_concat_character_trailer_segments` — L12066
- `_generate_character_trailer_motion` — L12105
- `_multi_trailer_prompt_for_group` — L12213
- `_generate_multi_trailer_segments` — L12236
- `_generate_storyboard_trailer_motion` — L12347
- `_generate_previs_page_motion_segments` — L12422
- `_generate_grid_multiref_motion_segments` — L12534
- `_grid_multiref_concat_groups` — L12778
- `_grid_multiref_concat_groups_partial` — L12795
- `_grid_multiref_concat_paths` — L12813
- `_lip_sync_slot_duration` — L12855
- `_adsd_lip_sync_prompt` — L12862
- `_adsd_broll_motion_prompt` — L12908
- `_adsd_action_b_motion_prompt` — L12950
- `_adsd_silent_b_motion_prompt` — L12996
- `_adsd_narrated_b_audio_dub_prompt` — L13031
- `_adsd_almighty_audio_dub_prompt` — L13075
- `_postprocess_lip_sync_segment` — L13116
- `_detect_audio_leading_silence` — L13188
- `_concat_audio_files_for_group` — L13213
- `_split_lip_sync_raw_by_durations` — L13236
- `_postprocess_audio_dub_segment` — L13271
- `_lips_change_repair_segment` — L13386
- `_load_lips_change_requested_turns` — L13471
- `_parse_turn_set` — L13488
- `_load_motion_voice_repair_turns` — L13510
- `_voice_assets_file` — L13522
- `_load_voice_assets` — L13529
- `_select_voice_asset_reference` — L13548
- `_lip_sync_poll_download_and_process` — L13614
- `_lip_sync_one_group` — L13682
- `_lip_sync_one_scene` — L13859
- `step66_adsd_lip_sync` — L14183
- `step65_motion` — L14504
- `step65_grid_multiref_motion_qa` — L14656
- `_sanitize_scene_for_state` — L14685
- `_save_pipeline_state` — L14704
- `_retime_after_audio_dub` — L14728
- `_build_voice_clone_hybrid_audio` — L14766
- `_build_dynamic_bgm` — L14905

---

### 第七步：拼接视频轨
Range: **L14949 – L15208** (260 lines)

**Functions:**
- `step7_concat` — L14950

---

### 第八步：生成 ASS 字幕
Range: **L15209 – L16011** (803 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L15332-16011 (680 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L15210
- `_word_timings_for_subtitle_align` — L15236
- `_align_segments_via_asr` — L15277
- `step8_subtitles` — L15320
- `_read_output_json` — L15732
- `_qa_file_pass` — L15743
- `_ass_has_dialogue` — L15750
- `_write_adsd_delivery_qa` — L15760
- `_write_bgm_only_qa` — L15900

---

### 第九步：最终合成
Range: **L16012 – L16287** (276 lines)

**Functions:**
- `step9_render` — L16013

---

### 第十步：推送 Telegram
Range: **L16288 – L17949** (1662 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L17388-17756 (369 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L17757-17761 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L17762-17825 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L17826-17871 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L17872-17949 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L16657
- `PANTONE_FALLBACK` — L16684
- `FESTIVAL_DATE_TAG` — L16797

**Functions:**
- `_generate_caption` — L16289
- `_overlay_title_on_cover` — L16527
- `_prepare_tg_photo` — L16637
- `_get_pantone_for_date` — L16687
- `_llm_bottom_note` — L16712
- `_get_bottom_note` — L16741
- `_get_date_tag` — L16819
- `_shrink_to_b64` — L16841
- `_llm_check_scenes_anomalies` — L16857
- `_llm_check_cover_unique` — L16910
- `_llm_check_cover_quality` — L16940
- `_try_almanac_cover` — L16982
- `_generate_cover_image` — L17153
- `_async_kickoff_cover_caption` — L17395
- `_await_async_cover_caption` — L17469
- `step10_deliver` — L17496

---

### 主流程
Range: **L17950 – L18134** (185 lines)

**Functions:**
- `_print_execution_plan` — L17951
- `main` — L17999

---
