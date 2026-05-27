# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (17357 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-2014 (1893 lines · 59 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L2015-4248 (2234 lines · 30 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L4249-5370 (1122 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L5371-5922 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L5923-9693 (3771 lines · 82 fn · 6 sub)
- [`第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）`](#第-6-5-步-动态化-hads-vads-默认-on---no-motion-关) — L9694-14283 (4590 lines · 103 fn · 5 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L14284-14515 (232 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L14516-15318 (803 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L15319-15564 (246 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L15565-17179 (1615 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L17180-17357 (178 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L2014** (1893 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L308-437 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L438-1125 (688 lines)
- _工具函数_ — L1126-1475 (350 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1476-2014 (539 lines)

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
- `PREVIS_PAGE_MOTION` — L228
- `STORYBOARD_TRAILER_MODE` — L232
- `MOTION_ACTION_STORYBOARD` — L237
- `MOTION_BRIDGE_REFS` — L241
- `CHARACTER_TRAILER_MODE` — L245
- `STORYBOARD_TRAILER_MAIN` — L253
- `ADSD_LIP_SYNC_EXPERIMENT` — L266
- `ADSD_RICH_MOTION_PROMPT` — L274
- `ADSD_LLM_VOICE_ASSIGN` — L282
- `ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT` — L286
- `ADSD_CONSECUTIVE_SPEAKER_BATCHING` — L300
- `ADSD_GENDER_FALLBACK_VOICE_ASSET` — L311
- `SILENT_B_SPEAKERS` — L443
- `_PODCAST_TO_VOICE_ASSET_MAP` — L811
- `_VOICE_ASSET_FORBIDDEN_FLAGS` — L829
- `VOICE_ASSET_AUDIO_DUB_EXPERIMENT` — L867
- `VOICE_ASSET_AUDIO_DUB_PARTIAL_OK` — L875
- `MOTION_VISUAL_QA` — L879
- `MOTION_VOICE_REPAIR` — L887
- `MOTION_VOICE_STRICT_LOCK` — L892
- `WERYDANCE_CAPTIONS` — L897
- `ADSD_ONSITE_POV_MODE` — L909
- `ADSD_LIPS_CHANGE_REPAIR` — L914
- `ADSD_LIPS_CHANGE_ALL` — L919
- `ADS_REPORTER_MODE` — L930
- `ADS_STORYBOARD_FLOW_DEFAULT` — L947
- `ADS_RETENTION_MODE` — L960
- `ADSD_MODE_NAME` — L966
- `EMOTION_STYLE` — L1105
- `EMOTION_STYLE_BRIGHT` — L1117
- `_TG_DASHBOARD_STAGES` — L1139
- `_TG_NOISY_PATTERNS` — L1154
- `_TG_IMMEDIATE_PATTERNS` — L1172
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1405
- `_LLM_TIER` — L1650
- `_TOPIC_MODIFIERS` — L1846
- `_TONE_PANTONE_OVERRIDE` — L1863

**Functions:**
- `_is_action_scene` — L320
- `_needs_storyboard_flow_character_sheet` — L331
- `_wuxia_action_panel_prompt` — L360
- `_action_motion_fragment` — L382
- `_infer_emotion_from_text` — L397
- `_emotion_expression_phrase` — L412
- `_infer_needs_lip_sync` — L419
- `_infer_turn_type` — L446
- `_is_action_shout` — L471
- `_resolve_turn_type` — L497
- `_is_silent_b` — L512
- `_is_narrated_b` — L516
- `_is_a_roll` — L520
- `_is_action_b` — L524
- `_voice_asset_id_for_speaker` — L528
- `_llm_assign_voice_assets` — L556
- `_apply_llm_voice_assignment` — L685
- `_voice_asset_is_speech_safe` — L836
- `_podcast_id_to_voice_asset` — L842
- `log` — L1127
- `_tg_send_raw` — L1195
- `_tg_matches` — L1211
- `_tg_summarize` — L1215
- `_tg_dashboard_stage_for` — L1222
- `_tg_progress_bar` — L1230
- `_tg_dashboard_text` — L1236
- `_tg_dashboard_update` — L1254
- `_tg_maybe_digest` — L1291
- `tg` — L1306
- `_wait_image_submit_slot` — L1355
- `_wait_motion_submit_slot` — L1368
- `_is_rate_limited_error` — L1381
- `_is_rate_limited_response` — L1391
- `_inject_image2_quality_suffix` — L1413
- `submit_text_to_image` — L1427
- `req_post` — L1457
- `req_get` — L1471
- `_tg_probe_send` — L1479
- `_tg_probe_delete` — L1499
- `_tg_upload_with_probe_gap` — L1512
- `poll` — L1552
- `poll_podcast` — L1577
- `poll_task_status` — L1599
- `poll_storyboard_task` — L1621
- `tier_chat` — L1658
- `chat` — L1664
- `pick_image_model` — L1692
- `detect_topic_meta` — L1717
- `_topic_culture_guard` — L1767
- `_write_cultural_visual_qa` — L1793
- `is_1919_global_topic` — L1840
- `_strip_topic_modifiers` — L1851
- `apply_1919_global_guardrails` — L1869
- `build_1919_global_cover_prompt` — L1898
- `build_shot_blueprint` — L1927
- `ffprobe_duration` — L1953
- `ffprobe_video_size` — L1964
- `_video_decode_probe` — L1985
- `ffmpeg` — L2003

---

### 第一步：双导演生成剧本
Range: **L2015 – L4248** (2234 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L3477-4248 (772 lines)

**Top-level constants:**
- `_ENSEMBLE_CAP_BY_ROUTE` — L2163

**Functions:**
- `_extract_json_array` — L2016
- `_extract_json_object` — L2026
- `_voice_for_speaker` — L2036
- `_adsd_gender_from_voice` — L2072
- `_adsd_infer_gender_from_speaker` — L2080
- `_adsd_gender_lock_phrase` — L2089
- `_adsd_visual_subject_has_gender_conflict` — L2104
- `_adsd_default_roles` — L2116
- `_adsd_allows_media_role` — L2121
- `_adsd_role_candidates` — L2129
- `_adsd_dialogue_shape` — L2152
- `_ensemble_speaker_cap` — L2174
- `_finalize_adsd_turns` — L2187
- `_parse_adsd_override_turns` — L2221
- `_parse_timecode_seconds` — L2312
- `_clean_override_line_text` — L2321
- `_parse_override_script_text` — L2327
- `_adsd_pov_contract` — L2361
- `_load_audit_blacklist_block` — L2374
- `_generate_adsd_dialogue_turns` — L2412
- `_broll_rhythm_reviewer` — L2839
- `_sweep_speaker_field` — L2946
- `_should_run_immersion_qa` — L3006
- `_adsd_immersion_qa_rewrite_turns` — L3029
- `_adsd_visual_contract` — L3093
- `_parse_risk_score` — L3145
- `_check_high_risk_hard_abort` — L3174
- `_maybe_neutralize_topic` — L3201
- `step1_script` — L3240
- `_write_ads_retention_qa` — L4192

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L4249 – L5370** (1122 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L4324
- `_ADSD_POLICY_REWRITE_TERMS` — L4330
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L4421

**Functions:**
- `_openai_tts_fallback` — L4250
- `_edge_tts_fallback` — L4296
- `_sanitize_for_external_api` — L4339
- `_is_content_policy_error` — L4348
- `_rewrite_adsd_tts_text_for_policy` — L4362
- `_record_adsd_tts_rewrite` — L4402
- `_build_silence_mp3` — L4427
- `_audio_duration_seconds` — L4440
- `_text_to_audio_master_voice_timed` — L4452
- `_text_to_audio_master_voice` — L4577
- `step2_master_voice` — L4680
- `_tts_turn_to_audio` — L4808
- `_asr_verify_dialogue_audio` — L4872
- `_asr_verify_dialogue_turns` — L4934
- `_normalize_cn_number_token` — L4976
- `_compact_zh_text` — L4998
- `_write_adsd_asr_text_qa` — L5005
- `_write_adsd_speaker_focus_qa` — L5044
- `_write_adsd_gender_voice_qa` — L5104
- `step2_dialogue_voice` — L5157

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L5371 – L5922** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L5378-5500 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L5501-5535 (35 lines)
- _第二层：字符数插值_ — L5536-5560 (25 lines)
- _第三层：silencedetect 物理校准_ — L5561-5922 (362 lines)

**Functions:**
- `_detect_silences` — L5379
- `_calibrate_boundaries` — L5414
- `_enforce_monotonic` — L5448
- `_manual_override_segments` — L5460
- `_calc_sentence_boundaries` — L5481
- `step345_timeline` — L5592
- `_analyze_bgm_energy_cuts` — L5651
- `_snap_bgm_only_boundaries` — L5714
- `step345_bgm_only_timeline` — L5774

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L5923 – L9693** (3771 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L7122-7172 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L7173-7313 (141 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L7314-7748 (435 lines)
- _Speaker IP Card (2026-05-21)_ — L7749-9526 (1778 lines)
- _审批流程_ — L9527-9583 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L9584-9693 (110 lines)

**Top-level constants:**
- `_CORE_TERMS_STOP_WORDS` — L6318
- `CHARACTER_META_GRID_COSTUMES` — L7128
- `CHARACTER_META_GRID_POSES` — L7129
- `CHARACTER_META_GRID_SCENES` — L7130
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L7133

**Functions:**
- `_extract_img_url` — L5924
- `_extract_img_urls` — L5946
- `_extract_video_url` — L5979
- `_count_bands` — L6004
- `_detect_contact_sheet_like_image` — L6016
- `_file_sha256` — L6077
- `_load_upload_cache` — L6090
- `_save_upload_cache` — L6099
- `_cached_upload_url` — L6107
- `_store_upload_url` — L6124
- `_guess_upload_mime` — L6134
- `_upload_to_weryai` — L6157
- `_send_for_approval` — L6211
- `_wait_approval` — L6275
- `_render_still_segment` — L6287
- `_extract_core_terms` — L6324
- `_scene_text_visual_alignment` — L6343
- `_write_text_visual_alignment_qa` — L6364
- `_scene_motion_action_plan` — L6387
- `_ensure_motion_action_plan` — L6441
- `_motion_action_block` — L6450
- `_motion_plan_for_qa` — L6478
- `_write_motion_action_plan_qa` — L6488
- `_write_motion_bridge_refs_qa` — L6518
- `_motion_bridge_ref_prompt` — L6525
- `generate_motion_bridge_refs_gpt_image2` — L6558
- `generate_image` — L6671
- `generate_storyboard_images_gpt_image2` — L6718
- `_storyboard_grid_aspect` — L6903
- `_storyboard_grid_cols_rows` — L6910
- `_storyboard_grid_prompt` — L6932
- `_storyboard_grid_prompt_limit` — L6970
- `_is_prompt_limit_response` — L6974
- `_production_storyboard_prompt` — L6980
- `_write_production_storyboard_page_qa` — L7014
- `_character_sheet_prompt` — L7024
- `_is_audit_blocked` — L7150
- `_paraphrase_sensitive_dialogue` — L7163
- `_topic_cache_dir` — L7177
- `_topic_cache_path` — L7183
- `_load_topic_decomposition_cache` — L7196
- `_save_topic_decomposition_cache` — L7214
- `_llm_topic_decomposition` — L7220
- `_director_route_block` — L7367
- `_llm_infer_meta_grid_template` — L7437
- `_resolve_meta_grid_template` — L7494
- `_infer_meta_grid_costume` — L7537
- `_infer_meta_grid_pose` — L7586
- `_adsd_meta_grid_call_prompt` — L7633
- `_meta_grid_panel_index` — L7675
- `_migrate_speaker_ip` — L7755
- `_speaker_ips_dir` — L7780
- `_list_speaker_ips` — L7787
- `_match_speaker_ip` — L7801
- `_build_speaker_ip_context_for_script` — L7821
- `_ip_usage_stats` — L7877
- `_recommend_related_ips` — L7895
- `_save_speaker_ip` — L7920
- `_record_speaker_usage_history` — L7929
- `_format_speaker_usage_history_for_prompt` — L7976
- `_llm_infer_ip_skeleton` — L7994
- `_llm_pick_voice_asset_for_ip` — L8039
- `_auto_incubate_missing_ips` — L8087
- `_character_meta_grid_cache_dir` — L8171
- `_character_meta_grid_cache_path` — L8179
- `_character_meta_grid_cache_legacy_path` — L8187
- `_character_meta_grid_path` — L8194
- `generate_character_meta_grid_gpt_image2` — L8200
- `_generate_all_character_meta_grids` — L8372
- `_write_character_sheet_qa` — L8413
- `generate_character_sheet_gpt_image2` — L8423
- `generate_production_storyboard_page_gpt_image2` — L8523
- `_qa_clean_storyboard_panel` — L8586
- `_crop_storyboard_grid_panels` — L8767
- `generate_storyboard_grid_gpt_image2` — L8814
- `_gpt_image2_direct_annotated_aspect` — L9045
- `_gpt_image2_direct_annotated_prompt` — L9052
- `generate_gpt_image2_direct_annotated_storyboards` — L9082
- `_llm_bgm_description` — L9183
- `_bgm_contains_vocals` — L9222
- `generate_bgm` — L9256
- `step6_parallel` — L9373

---

### 第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）
Range: **L9694 – L14283** (4590 lines)

**Sub-sections:**
- _PR-A (2026-05-27): merged_a 合并跑 helpers_ — L12618-14019 (1402 lines)
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L14020-14062 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L14063-14100 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回主音轨_ — L14101-14238 (138 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L14239-14283 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L9697
- `_motion_tasks_file` — L9764
- `_motion_qa_file` — L9768
- `_append_motion_qa` — L9772
- `_finalize_motion_qa` — L9796
- `_lip_sync_tasks_file` — L9880
- `_load_motion_tasks` — L9884
- `_save_motion_task` — L9894
- `_remove_motion_task` — L9902
- `_load_lip_sync_tasks` — L9909
- `_save_lip_sync_task` — L9919
- `_remove_lip_sync_task` — L9926
- `_video_visual_motion_qa` — L9933
- `_motion_output_qa` — L10005
- `_has_audio_stream` — L10050
- `_normalize_motion_video` — L10061
- `_motion_poll_and_download` — L10111
- `_build_motion_video_prompt` — L10162
- `_short_board_text` — L10192
- `_wrap_board_text` — L10199
- `_storyboard_font` — L10230
- `_draw_storyboard_arrow` — L10245
- `_build_annotated_storyboard_reference` — L10259
- `_plain_caption_text` — L10360
- `_werydance_caption_request` — L10368
- `_werydance_caption_instruction` — L10395
- `_werydance_negative_prompt` — L10407
- `_motion_reference_prompt` — L10425
- `_motion_audio_dub_prompt` — L10448
- `_motion_audio_dub_poll_and_download` — L10482
- `_try_motion_audio_dub_video` — L10547
- `_try_motion_reference_video` — L10682
- `_motion_one_scene` — L10798
- `_grid_multiref_tasks_file` — L10927
- `_previs_page_tasks_file` — L10931
- `_load_grid_multiref_tasks` — L10935
- `_load_previs_page_tasks` — L10945
- `_save_grid_multiref_task` — L10955
- `_save_previs_page_task` — L10962
- `_remove_grid_multiref_task` — L10969
- `_remove_previs_page_task` — L10976
- `_poll_video_task_download` — L10983
- `_grid_multiref_group_size` — L11032
- `_grid_multiref_duration` — L11040
- `_grid_multiref_segment_max_stretch` — L11056
- `_grid_multiref_prompt` — L11064
- `_write_grid_multiref_motion_qa` — L11112
- `_write_previs_page_motion_qa` — L11122
- `_write_storyboard_trailer_qa` — L11132
- `_write_character_trailer_qa` — L11142
- `_write_grid_multiref_segment_qa` — L11152
- `_motion_compare_record` — L11162
- `_write_storyboard_motion_compare_qa` — L11184
- `_scene_segment_duration` — L11220
- `_apply_grid_multiref_segments` — L11239
- `_previs_page_duration` — L11433
- `_previs_page_group_prompt` — L11443
- `_previs_page_groups` — L11469
- `_storyboard_trailer_duration` — L11484
- `_storyboard_trailer_prompt` — L11494
- `_character_trailer_max_shots` — L11522
- `_character_trailer_shot_duration` — L11530
- `_character_trailer_prompt` — L11544
- `_concat_character_trailer_segments` — L11559
- `_generate_character_trailer_motion` — L11598
- `_multi_trailer_prompt_for_group` — L11706
- `_generate_multi_trailer_segments` — L11729
- `_generate_storyboard_trailer_motion` — L11840
- `_generate_previs_page_motion_segments` — L11915
- `_generate_grid_multiref_motion_segments` — L12027
- `_grid_multiref_concat_groups` — L12197
- `_grid_multiref_concat_groups_partial` — L12214
- `_grid_multiref_concat_paths` — L12232
- `_lip_sync_slot_duration` — L12263
- `_adsd_lip_sync_prompt` — L12270
- `_adsd_broll_motion_prompt` — L12316
- `_adsd_action_b_motion_prompt` — L12358
- `_adsd_silent_b_motion_prompt` — L12404
- `_adsd_narrated_b_audio_dub_prompt` — L12439
- `_adsd_almighty_audio_dub_prompt` — L12483
- `_postprocess_lip_sync_segment` — L12524
- `_detect_audio_leading_silence` — L12596
- `_concat_audio_files_for_group` — L12621
- `_split_lip_sync_raw_by_durations` — L12644
- `_postprocess_audio_dub_segment` — L12679
- `_lips_change_repair_segment` — L12794
- `_load_lips_change_requested_turns` — L12879
- `_parse_turn_set` — L12896
- `_load_motion_voice_repair_turns` — L12918
- `_voice_assets_file` — L12930
- `_load_voice_assets` — L12937
- `_select_voice_asset_reference` — L12956
- `_lip_sync_poll_download_and_process` — L13022
- `_lip_sync_one_group` — L13090
- `_lip_sync_one_scene` — L13267
- `step66_adsd_lip_sync` — L13591
- `step65_motion` — L13910
- `step65_grid_multiref_motion_qa` — L13992
- `_sanitize_scene_for_state` — L14021
- `_save_pipeline_state` — L14040
- `_retime_after_audio_dub` — L14064
- `_build_voice_clone_hybrid_audio` — L14102
- `_build_dynamic_bgm` — L14240

---

### 第七步：拼接视频轨
Range: **L14284 – L14515** (232 lines)

**Functions:**
- `step7_concat` — L14285

---

### 第八步：生成 ASS 字幕
Range: **L14516 – L15318** (803 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L14639-15318 (680 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L14517
- `_word_timings_for_subtitle_align` — L14543
- `_align_segments_via_asr` — L14584
- `step8_subtitles` — L14627
- `_read_output_json` — L15039
- `_qa_file_pass` — L15050
- `_ass_has_dialogue` — L15057
- `_write_adsd_delivery_qa` — L15067
- `_write_bgm_only_qa` — L15207

---

### 第九步：最终合成
Range: **L15319 – L15564** (246 lines)

**Functions:**
- `step9_render` — L15320

---

### 第十步：推送 Telegram
Range: **L15565 – L17179** (1615 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L16665-16986 (322 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L16987-16991 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L16992-17055 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L17056-17101 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L17102-17179 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L15934
- `PANTONE_FALLBACK` — L15961
- `FESTIVAL_DATE_TAG` — L16074

**Functions:**
- `_generate_caption` — L15566
- `_overlay_title_on_cover` — L15804
- `_prepare_tg_photo` — L15914
- `_get_pantone_for_date` — L15964
- `_llm_bottom_note` — L15989
- `_get_bottom_note` — L16018
- `_get_date_tag` — L16096
- `_shrink_to_b64` — L16118
- `_llm_check_scenes_anomalies` — L16134
- `_llm_check_cover_unique` — L16187
- `_llm_check_cover_quality` — L16217
- `_try_almanac_cover` — L16259
- `_generate_cover_image` — L16430
- `_async_kickoff_cover_caption` — L16672
- `_await_async_cover_caption` — L16702
- `step10_deliver` — L16726

---

### 主流程
Range: **L17180 – L17357** (178 lines)

**Functions:**
- `_print_execution_plan` — L17181
- `main` — L17229

---
