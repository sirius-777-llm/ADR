# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (18426 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-2198 (2077 lines · 62 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L2199-4598 (2400 lines · 30 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L4599-5730 (1132 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L5731-6282 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L6283-10366 (4084 lines · 93 fn · 6 sub)
- [`第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）`](#第-6-5-步-动态化-hads-vads-默认-on---no-motion-关) — L10367-15240 (4874 lines · 104 fn · 5 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L15241-15500 (260 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L15501-16303 (803 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L16304-16579 (276 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L16580-18241 (1662 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L18242-18426 (185 lines · 2 fn · 0 sub)

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
Range: **L2199 – L4598** (2400 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L3663-4598 (936 lines)

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
- `_write_ads_retention_qa` — L4542

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L4599 – L5730** (1132 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L4674
- `_ADSD_POLICY_REWRITE_TERMS` — L4680
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L4771

**Functions:**
- `_openai_tts_fallback` — L4600
- `_edge_tts_fallback` — L4646
- `_sanitize_for_external_api` — L4689
- `_is_content_policy_error` — L4698
- `_rewrite_adsd_tts_text_for_policy` — L4712
- `_record_adsd_tts_rewrite` — L4752
- `_build_silence_mp3` — L4777
- `_audio_duration_seconds` — L4790
- `_text_to_audio_master_voice_timed` — L4802
- `_text_to_audio_master_voice` — L4927
- `step2_master_voice` — L5040
- `_tts_turn_to_audio` — L5168
- `_asr_verify_dialogue_audio` — L5232
- `_asr_verify_dialogue_turns` — L5294
- `_normalize_cn_number_token` — L5336
- `_compact_zh_text` — L5358
- `_write_adsd_asr_text_qa` — L5365
- `_write_adsd_speaker_focus_qa` — L5404
- `_write_adsd_gender_voice_qa` — L5464
- `step2_dialogue_voice` — L5517

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L5731 – L6282** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L5738-5860 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L5861-5895 (35 lines)
- _第二层：字符数插值_ — L5896-5920 (25 lines)
- _第三层：silencedetect 物理校准_ — L5921-6282 (362 lines)

**Functions:**
- `_detect_silences` — L5739
- `_calibrate_boundaries` — L5774
- `_enforce_monotonic` — L5808
- `_manual_override_segments` — L5820
- `_calc_sentence_boundaries` — L5841
- `step345_timeline` — L5952
- `_analyze_bgm_energy_cuts` — L6011
- `_snap_bgm_only_boundaries` — L6074
- `step345_bgm_only_timeline` — L6134

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L6283 – L10366** (4084 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L7504-7554 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L7555-7976 (422 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L7977-8411 (435 lines)
- _Speaker IP Card (2026-05-21)_ — L8412-10199 (1788 lines)
- _审批流程_ — L10200-10256 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L10257-10366 (110 lines)

**Top-level constants:**
- `_CORE_TERMS_STOP_WORDS` — L6678
- `CHARACTER_META_GRID_COSTUMES` — L7510
- `CHARACTER_META_GRID_POSES` — L7511
- `CHARACTER_META_GRID_SCENES` — L7512
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L7515

**Functions:**
- `_extract_img_url` — L6284
- `_extract_img_urls` — L6306
- `_extract_video_url` — L6339
- `_count_bands` — L6364
- `_detect_contact_sheet_like_image` — L6376
- `_file_sha256` — L6437
- `_load_upload_cache` — L6450
- `_save_upload_cache` — L6459
- `_cached_upload_url` — L6467
- `_store_upload_url` — L6484
- `_guess_upload_mime` — L6494
- `_upload_to_weryai` — L6517
- `_send_for_approval` — L6571
- `_wait_approval` — L6635
- `_render_still_segment` — L6647
- `_extract_core_terms` — L6684
- `_scene_text_visual_alignment` — L6703
- `_write_text_visual_alignment_qa` — L6724
- `_scene_motion_action_plan` — L6747
- `_ensure_motion_action_plan` — L6801
- `_motion_action_block` — L6810
- `_motion_plan_for_qa` — L6838
- `_write_motion_action_plan_qa` — L6848
- `_write_motion_bridge_refs_qa` — L6878
- `_motion_bridge_ref_prompt` — L6885
- `generate_motion_bridge_refs_gpt_image2` — L6918
- `generate_image` — L7033
- `generate_storyboard_images_gpt_image2` — L7080
- `_storyboard_grid_aspect` — L7265
- `_storyboard_grid_cols_rows` — L7272
- `_storyboard_grid_prompt` — L7294
- `_storyboard_grid_prompt_limit` — L7352
- `_is_prompt_limit_response` — L7356
- `_production_storyboard_prompt` — L7362
- `_write_production_storyboard_page_qa` — L7396
- `_character_sheet_prompt` — L7406
- `_is_audit_blocked` — L7532
- `_paraphrase_sensitive_dialogue` — L7545
- `_topic_cache_dir` — L7559
- `_topic_cache_path` — L7565
- `_load_topic_decomposition_cache` — L7578
- `_save_topic_decomposition_cache` — L7596
- `_briefs_dir` — L7633
- `_brief_path` — L7639
- `_empty_brief` — L7644
- `_deep_merge_brief_skeleton` — L7682
- `_load_brief` — L7696
- `_save_brief` — L7720
- `_brief_get` — L7739
- `_brief_set` — L7751
- `_brief_claim` — L7767
- `_brief_agent_status` — L7810
- `_brief_from_topic_decomposition` — L7823
- `_llm_topic_decomposition` — L7866
- `_director_route_block` — L8030
- `_llm_infer_meta_grid_template` — L8100
- `_resolve_meta_grid_template` — L8157
- `_infer_meta_grid_costume` — L8200
- `_infer_meta_grid_pose` — L8249
- `_adsd_meta_grid_call_prompt` — L8296
- `_meta_grid_panel_index` — L8338
- `_migrate_speaker_ip` — L8418
- `_speaker_ips_dir` — L8443
- `_list_speaker_ips` — L8450
- `_match_speaker_ip` — L8464
- `_build_speaker_ip_context_for_script` — L8484
- `_ip_usage_stats` — L8540
- `_recommend_related_ips` — L8558
- `_save_speaker_ip` — L8583
- `_record_speaker_usage_history` — L8592
- `_format_speaker_usage_history_for_prompt` — L8639
- `_llm_infer_ip_skeleton` — L8657
- `_llm_pick_voice_asset_for_ip` — L8702
- `_auto_incubate_missing_ips` — L8750
- `_character_meta_grid_cache_dir` — L8834
- `_character_meta_grid_cache_path` — L8842
- `_character_meta_grid_cache_legacy_path` — L8850
- `_character_meta_grid_path` — L8857
- `generate_character_meta_grid_gpt_image2` — L8863
- `_generate_all_character_meta_grids` — L9035
- `_write_character_sheet_qa` — L9076
- `generate_character_sheet_gpt_image2` — L9086
- `generate_production_storyboard_page_gpt_image2` — L9186
- `_qa_clean_storyboard_panel` — L9249
- `_crop_storyboard_grid_panels` — L9430
- `generate_storyboard_grid_gpt_image2` — L9477
- `_gpt_image2_direct_annotated_aspect` — L9708
- `_gpt_image2_direct_annotated_prompt` — L9715
- `generate_gpt_image2_direct_annotated_storyboards` — L9745
- `_llm_bgm_description` — L9846
- `_bgm_contains_vocals` — L9885
- `generate_bgm` — L9919
- `step6_parallel` — L10036

---

### 第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）
Range: **L10367 – L15240** (4874 lines)

**Sub-sections:**
- _PR-A (2026-05-27): merged_a 合并跑 helpers_ — L13502-14975 (1474 lines)
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L14976-15018 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L15019-15056 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回时间轴锚定音轨_ — L15057-15195 (139 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L15196-15240 (45 lines)

**Top-level constants:**
- `_PR3B1_SHOT_TYPE_ENUM` — L10837
- `_PR3B1_CAMERA_ANGLE_ENUM` — L10841
- `_PR3B1_LIGHTING_ENUM` — L10846
- `_PR3B1_CAMERA_MOTION_ENUM` — L10851

**Functions:**
- `_generate_motion_prompts` — L10370
- `_motion_tasks_file` — L10437
- `_motion_qa_file` — L10441
- `_append_motion_qa` — L10445
- `_finalize_motion_qa` — L10469
- `_lip_sync_tasks_file` — L10553
- `_load_motion_tasks` — L10557
- `_save_motion_task` — L10567
- `_remove_motion_task` — L10575
- `_load_lip_sync_tasks` — L10582
- `_save_lip_sync_task` — L10592
- `_remove_lip_sync_task` — L10599
- `_video_visual_motion_qa` — L10606
- `_motion_output_qa` — L10678
- `_has_audio_stream` — L10723
- `_normalize_motion_video` — L10734
- `_motion_poll_and_download` — L10784
- `_validate_enum_field` — L10857
- `_build_motion_video_prompt` — L10872
- `_short_board_text` — L10922
- `_wrap_board_text` — L10929
- `_storyboard_font` — L10960
- `_draw_storyboard_arrow` — L10975
- `_build_annotated_storyboard_reference` — L10989
- `_plain_caption_text` — L11090
- `_werydance_caption_request` — L11098
- `_werydance_caption_instruction` — L11125
- `_werydance_negative_prompt` — L11137
- `_motion_reference_prompt` — L11155
- `_motion_audio_dub_prompt` — L11178
- `_motion_audio_dub_poll_and_download` — L11212
- `_try_motion_audio_dub_video` — L11277
- `_try_motion_reference_video` — L11440
- `_motion_one_scene` — L11556
- `_grid_multiref_tasks_file` — L11685
- `_previs_page_tasks_file` — L11689
- `_load_grid_multiref_tasks` — L11693
- `_load_previs_page_tasks` — L11703
- `_save_grid_multiref_task` — L11713
- `_save_previs_page_task` — L11720
- `_remove_grid_multiref_task` — L11727
- `_remove_previs_page_task` — L11734
- `_poll_video_task_download` — L11741
- `_grid_multiref_group_size` — L11790
- `_grid_multiref_duration` — L11800
- `_grid_multiref_segment_max_stretch` — L11822
- `_grid_multiref_prompt` — L11830
- `_write_grid_multiref_motion_qa` — L11900
- `_write_previs_page_motion_qa` — L11910
- `_write_storyboard_trailer_qa` — L11920
- `_write_character_trailer_qa` — L11930
- `_write_grid_multiref_segment_qa` — L11940
- `_motion_compare_record` — L11950
- `_write_storyboard_motion_compare_qa` — L11972
- `_scene_segment_duration` — L12008
- `_apply_grid_multiref_segments` — L12027
- `_previs_page_duration` — L12232
- `_previs_page_group_prompt` — L12242
- `_previs_page_groups` — L12268
- `_storyboard_trailer_duration` — L12283
- `_storyboard_trailer_prompt` — L12293
- `_character_trailer_max_shots` — L12321
- `_character_trailer_shot_duration` — L12329
- `_character_trailer_prompt` — L12343
- `_concat_character_trailer_segments` — L12358
- `_generate_character_trailer_motion` — L12397
- `_multi_trailer_prompt_for_group` — L12505
- `_generate_multi_trailer_segments` — L12528
- `_generate_storyboard_trailer_motion` — L12639
- `_generate_previs_page_motion_segments` — L12714
- `_generate_grid_multiref_motion_segments` — L12826
- `_grid_multiref_concat_groups` — L13070
- `_grid_multiref_concat_groups_partial` — L13087
- `_grid_multiref_concat_paths` — L13105
- `_lip_sync_slot_duration` — L13147
- `_adsd_lip_sync_prompt` — L13154
- `_adsd_broll_motion_prompt` — L13200
- `_adsd_action_b_motion_prompt` — L13242
- `_adsd_silent_b_motion_prompt` — L13288
- `_adsd_narrated_b_audio_dub_prompt` — L13323
- `_adsd_almighty_audio_dub_prompt` — L13367
- `_postprocess_lip_sync_segment` — L13408
- `_detect_audio_leading_silence` — L13480
- `_concat_audio_files_for_group` — L13505
- `_split_lip_sync_raw_by_durations` — L13528
- `_postprocess_audio_dub_segment` — L13563
- `_lips_change_repair_segment` — L13678
- `_load_lips_change_requested_turns` — L13763
- `_parse_turn_set` — L13780
- `_load_motion_voice_repair_turns` — L13802
- `_voice_assets_file` — L13814
- `_load_voice_assets` — L13821
- `_select_voice_asset_reference` — L13840
- `_lip_sync_poll_download_and_process` — L13906
- `_lip_sync_one_group` — L13974
- `_lip_sync_one_scene` — L14151
- `step66_adsd_lip_sync` — L14475
- `step65_motion` — L14796
- `step65_grid_multiref_motion_qa` — L14948
- `_sanitize_scene_for_state` — L14977
- `_save_pipeline_state` — L14996
- `_retime_after_audio_dub` — L15020
- `_build_voice_clone_hybrid_audio` — L15058
- `_build_dynamic_bgm` — L15197

---

### 第七步：拼接视频轨
Range: **L15241 – L15500** (260 lines)

**Functions:**
- `step7_concat` — L15242

---

### 第八步：生成 ASS 字幕
Range: **L15501 – L16303** (803 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L15624-16303 (680 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L15502
- `_word_timings_for_subtitle_align` — L15528
- `_align_segments_via_asr` — L15569
- `step8_subtitles` — L15612
- `_read_output_json` — L16024
- `_qa_file_pass` — L16035
- `_ass_has_dialogue` — L16042
- `_write_adsd_delivery_qa` — L16052
- `_write_bgm_only_qa` — L16192

---

### 第九步：最终合成
Range: **L16304 – L16579** (276 lines)

**Functions:**
- `step9_render` — L16305

---

### 第十步：推送 Telegram
Range: **L16580 – L18241** (1662 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L17680-18048 (369 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L18049-18053 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L18054-18117 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L18118-18163 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L18164-18241 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L16949
- `PANTONE_FALLBACK` — L16976
- `FESTIVAL_DATE_TAG` — L17089

**Functions:**
- `_generate_caption` — L16581
- `_overlay_title_on_cover` — L16819
- `_prepare_tg_photo` — L16929
- `_get_pantone_for_date` — L16979
- `_llm_bottom_note` — L17004
- `_get_bottom_note` — L17033
- `_get_date_tag` — L17111
- `_shrink_to_b64` — L17133
- `_llm_check_scenes_anomalies` — L17149
- `_llm_check_cover_unique` — L17202
- `_llm_check_cover_quality` — L17232
- `_try_almanac_cover` — L17274
- `_generate_cover_image` — L17445
- `_async_kickoff_cover_caption` — L17687
- `_await_async_cover_caption` — L17761
- `step10_deliver` — L17788

---

### 主流程
Range: **L18242 – L18426** (185 lines)

**Functions:**
- `_print_execution_plan` — L18243
- `main` — L18291

---
