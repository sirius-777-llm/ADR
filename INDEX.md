# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (17525 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-2030 (1909 lines · 59 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L2031-4288 (2258 lines · 30 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L4289-5420 (1132 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L5421-5972 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L5973-9753 (3781 lines · 82 fn · 6 sub)
- [`第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）`](#第-6-5-步-动态化-hads-vads-默认-on---no-motion-关) — L9754-14444 (4691 lines · 103 fn · 5 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L14445-14676 (232 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L14677-15479 (803 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L15480-15732 (253 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L15733-17347 (1615 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L17348-17525 (178 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L2030** (1909 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L324-453 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L454-1141 (688 lines)
- _工具函数_ — L1142-1491 (350 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1492-2030 (539 lines)

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
- `VOICE_ASSET_AUDIO_DUB_EXPERIMENT` — L883
- `VOICE_ASSET_AUDIO_DUB_PARTIAL_OK` — L891
- `MOTION_VISUAL_QA` — L895
- `MOTION_VOICE_REPAIR` — L903
- `MOTION_VOICE_STRICT_LOCK` — L908
- `WERYDANCE_CAPTIONS` — L913
- `ADSD_ONSITE_POV_MODE` — L925
- `ADSD_LIPS_CHANGE_REPAIR` — L930
- `ADSD_LIPS_CHANGE_ALL` — L935
- `ADS_REPORTER_MODE` — L946
- `ADS_STORYBOARD_FLOW_DEFAULT` — L963
- `ADS_RETENTION_MODE` — L976
- `ADSD_MODE_NAME` — L982
- `EMOTION_STYLE` — L1121
- `EMOTION_STYLE_BRIGHT` — L1133
- `_TG_DASHBOARD_STAGES` — L1155
- `_TG_NOISY_PATTERNS` — L1170
- `_TG_IMMEDIATE_PATTERNS` — L1188
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1421
- `_LLM_TIER` — L1666
- `_TOPIC_MODIFIERS` — L1862
- `_TONE_PANTONE_OVERRIDE` — L1879

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
- `log` — L1143
- `_tg_send_raw` — L1211
- `_tg_matches` — L1227
- `_tg_summarize` — L1231
- `_tg_dashboard_stage_for` — L1238
- `_tg_progress_bar` — L1246
- `_tg_dashboard_text` — L1252
- `_tg_dashboard_update` — L1270
- `_tg_maybe_digest` — L1307
- `tg` — L1322
- `_wait_image_submit_slot` — L1371
- `_wait_motion_submit_slot` — L1384
- `_is_rate_limited_error` — L1397
- `_is_rate_limited_response` — L1407
- `_inject_image2_quality_suffix` — L1429
- `submit_text_to_image` — L1443
- `req_post` — L1473
- `req_get` — L1487
- `_tg_probe_send` — L1495
- `_tg_probe_delete` — L1515
- `_tg_upload_with_probe_gap` — L1528
- `poll` — L1568
- `poll_podcast` — L1593
- `poll_task_status` — L1615
- `poll_storyboard_task` — L1637
- `tier_chat` — L1674
- `chat` — L1680
- `pick_image_model` — L1708
- `detect_topic_meta` — L1733
- `_topic_culture_guard` — L1783
- `_write_cultural_visual_qa` — L1809
- `is_1919_global_topic` — L1856
- `_strip_topic_modifiers` — L1867
- `apply_1919_global_guardrails` — L1885
- `build_1919_global_cover_prompt` — L1914
- `build_shot_blueprint` — L1943
- `ffprobe_duration` — L1969
- `ffprobe_video_size` — L1980
- `_video_decode_probe` — L2001
- `ffmpeg` — L2019

---

### 第一步：双导演生成剧本
Range: **L2031 – L4288** (2258 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L3495-4288 (794 lines)

**Top-level constants:**
- `_ENSEMBLE_CAP_BY_ROUTE` — L2179

**Functions:**
- `_extract_json_array` — L2032
- `_extract_json_object` — L2042
- `_voice_for_speaker` — L2052
- `_adsd_gender_from_voice` — L2088
- `_adsd_infer_gender_from_speaker` — L2096
- `_adsd_gender_lock_phrase` — L2105
- `_adsd_visual_subject_has_gender_conflict` — L2120
- `_adsd_default_roles` — L2132
- `_adsd_allows_media_role` — L2137
- `_adsd_role_candidates` — L2145
- `_adsd_dialogue_shape` — L2168
- `_ensemble_speaker_cap` — L2190
- `_finalize_adsd_turns` — L2203
- `_parse_adsd_override_turns` — L2237
- `_parse_timecode_seconds` — L2330
- `_clean_override_line_text` — L2339
- `_parse_override_script_text` — L2345
- `_adsd_pov_contract` — L2379
- `_load_audit_blacklist_block` — L2392
- `_generate_adsd_dialogue_turns` — L2430
- `_broll_rhythm_reviewer` — L2857
- `_sweep_speaker_field` — L2964
- `_should_run_immersion_qa` — L3024
- `_adsd_immersion_qa_rewrite_turns` — L3047
- `_adsd_visual_contract` — L3111
- `_parse_risk_score` — L3163
- `_check_high_risk_hard_abort` — L3192
- `_maybe_neutralize_topic` — L3219
- `step1_script` — L3258
- `_write_ads_retention_qa` — L4232

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L4289 – L5420** (1132 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L4364
- `_ADSD_POLICY_REWRITE_TERMS` — L4370
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L4461

**Functions:**
- `_openai_tts_fallback` — L4290
- `_edge_tts_fallback` — L4336
- `_sanitize_for_external_api` — L4379
- `_is_content_policy_error` — L4388
- `_rewrite_adsd_tts_text_for_policy` — L4402
- `_record_adsd_tts_rewrite` — L4442
- `_build_silence_mp3` — L4467
- `_audio_duration_seconds` — L4480
- `_text_to_audio_master_voice_timed` — L4492
- `_text_to_audio_master_voice` — L4617
- `step2_master_voice` — L4730
- `_tts_turn_to_audio` — L4858
- `_asr_verify_dialogue_audio` — L4922
- `_asr_verify_dialogue_turns` — L4984
- `_normalize_cn_number_token` — L5026
- `_compact_zh_text` — L5048
- `_write_adsd_asr_text_qa` — L5055
- `_write_adsd_speaker_focus_qa` — L5094
- `_write_adsd_gender_voice_qa` — L5154
- `step2_dialogue_voice` — L5207

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L5421 – L5972** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L5428-5550 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L5551-5585 (35 lines)
- _第二层：字符数插值_ — L5586-5610 (25 lines)
- _第三层：silencedetect 物理校准_ — L5611-5972 (362 lines)

**Functions:**
- `_detect_silences` — L5429
- `_calibrate_boundaries` — L5464
- `_enforce_monotonic` — L5498
- `_manual_override_segments` — L5510
- `_calc_sentence_boundaries` — L5531
- `step345_timeline` — L5642
- `_analyze_bgm_energy_cuts` — L5701
- `_snap_bgm_only_boundaries` — L5764
- `step345_bgm_only_timeline` — L5824

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L5973 – L9753** (3781 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L7172-7222 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L7223-7363 (141 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L7364-7798 (435 lines)
- _Speaker IP Card (2026-05-21)_ — L7799-9586 (1788 lines)
- _审批流程_ — L9587-9643 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L9644-9753 (110 lines)

**Top-level constants:**
- `_CORE_TERMS_STOP_WORDS` — L6368
- `CHARACTER_META_GRID_COSTUMES` — L7178
- `CHARACTER_META_GRID_POSES` — L7179
- `CHARACTER_META_GRID_SCENES` — L7180
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L7183

**Functions:**
- `_extract_img_url` — L5974
- `_extract_img_urls` — L5996
- `_extract_video_url` — L6029
- `_count_bands` — L6054
- `_detect_contact_sheet_like_image` — L6066
- `_file_sha256` — L6127
- `_load_upload_cache` — L6140
- `_save_upload_cache` — L6149
- `_cached_upload_url` — L6157
- `_store_upload_url` — L6174
- `_guess_upload_mime` — L6184
- `_upload_to_weryai` — L6207
- `_send_for_approval` — L6261
- `_wait_approval` — L6325
- `_render_still_segment` — L6337
- `_extract_core_terms` — L6374
- `_scene_text_visual_alignment` — L6393
- `_write_text_visual_alignment_qa` — L6414
- `_scene_motion_action_plan` — L6437
- `_ensure_motion_action_plan` — L6491
- `_motion_action_block` — L6500
- `_motion_plan_for_qa` — L6528
- `_write_motion_action_plan_qa` — L6538
- `_write_motion_bridge_refs_qa` — L6568
- `_motion_bridge_ref_prompt` — L6575
- `generate_motion_bridge_refs_gpt_image2` — L6608
- `generate_image` — L6721
- `generate_storyboard_images_gpt_image2` — L6768
- `_storyboard_grid_aspect` — L6953
- `_storyboard_grid_cols_rows` — L6960
- `_storyboard_grid_prompt` — L6982
- `_storyboard_grid_prompt_limit` — L7020
- `_is_prompt_limit_response` — L7024
- `_production_storyboard_prompt` — L7030
- `_write_production_storyboard_page_qa` — L7064
- `_character_sheet_prompt` — L7074
- `_is_audit_blocked` — L7200
- `_paraphrase_sensitive_dialogue` — L7213
- `_topic_cache_dir` — L7227
- `_topic_cache_path` — L7233
- `_load_topic_decomposition_cache` — L7246
- `_save_topic_decomposition_cache` — L7264
- `_llm_topic_decomposition` — L7270
- `_director_route_block` — L7417
- `_llm_infer_meta_grid_template` — L7487
- `_resolve_meta_grid_template` — L7544
- `_infer_meta_grid_costume` — L7587
- `_infer_meta_grid_pose` — L7636
- `_adsd_meta_grid_call_prompt` — L7683
- `_meta_grid_panel_index` — L7725
- `_migrate_speaker_ip` — L7805
- `_speaker_ips_dir` — L7830
- `_list_speaker_ips` — L7837
- `_match_speaker_ip` — L7851
- `_build_speaker_ip_context_for_script` — L7871
- `_ip_usage_stats` — L7927
- `_recommend_related_ips` — L7945
- `_save_speaker_ip` — L7970
- `_record_speaker_usage_history` — L7979
- `_format_speaker_usage_history_for_prompt` — L8026
- `_llm_infer_ip_skeleton` — L8044
- `_llm_pick_voice_asset_for_ip` — L8089
- `_auto_incubate_missing_ips` — L8137
- `_character_meta_grid_cache_dir` — L8221
- `_character_meta_grid_cache_path` — L8229
- `_character_meta_grid_cache_legacy_path` — L8237
- `_character_meta_grid_path` — L8244
- `generate_character_meta_grid_gpt_image2` — L8250
- `_generate_all_character_meta_grids` — L8422
- `_write_character_sheet_qa` — L8463
- `generate_character_sheet_gpt_image2` — L8473
- `generate_production_storyboard_page_gpt_image2` — L8573
- `_qa_clean_storyboard_panel` — L8636
- `_crop_storyboard_grid_panels` — L8817
- `generate_storyboard_grid_gpt_image2` — L8864
- `_gpt_image2_direct_annotated_aspect` — L9095
- `_gpt_image2_direct_annotated_prompt` — L9102
- `generate_gpt_image2_direct_annotated_storyboards` — L9132
- `_llm_bgm_description` — L9233
- `_bgm_contains_vocals` — L9272
- `generate_bgm` — L9306
- `step6_parallel` — L9423

---

### 第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）
Range: **L9754 – L14444** (4691 lines)

**Sub-sections:**
- _PR-A (2026-05-27): merged_a 合并跑 helpers_ — L12706-14179 (1474 lines)
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L14180-14222 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L14223-14260 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回时间轴锚定音轨_ — L14261-14399 (139 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L14400-14444 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L9757
- `_motion_tasks_file` — L9824
- `_motion_qa_file` — L9828
- `_append_motion_qa` — L9832
- `_finalize_motion_qa` — L9856
- `_lip_sync_tasks_file` — L9940
- `_load_motion_tasks` — L9944
- `_save_motion_task` — L9954
- `_remove_motion_task` — L9962
- `_load_lip_sync_tasks` — L9969
- `_save_lip_sync_task` — L9979
- `_remove_lip_sync_task` — L9986
- `_video_visual_motion_qa` — L9993
- `_motion_output_qa` — L10065
- `_has_audio_stream` — L10110
- `_normalize_motion_video` — L10121
- `_motion_poll_and_download` — L10171
- `_build_motion_video_prompt` — L10222
- `_short_board_text` — L10252
- `_wrap_board_text` — L10259
- `_storyboard_font` — L10290
- `_draw_storyboard_arrow` — L10305
- `_build_annotated_storyboard_reference` — L10319
- `_plain_caption_text` — L10420
- `_werydance_caption_request` — L10428
- `_werydance_caption_instruction` — L10455
- `_werydance_negative_prompt` — L10467
- `_motion_reference_prompt` — L10485
- `_motion_audio_dub_prompt` — L10508
- `_motion_audio_dub_poll_and_download` — L10542
- `_try_motion_audio_dub_video` — L10607
- `_try_motion_reference_video` — L10770
- `_motion_one_scene` — L10886
- `_grid_multiref_tasks_file` — L11015
- `_previs_page_tasks_file` — L11019
- `_load_grid_multiref_tasks` — L11023
- `_load_previs_page_tasks` — L11033
- `_save_grid_multiref_task` — L11043
- `_save_previs_page_task` — L11050
- `_remove_grid_multiref_task` — L11057
- `_remove_previs_page_task` — L11064
- `_poll_video_task_download` — L11071
- `_grid_multiref_group_size` — L11120
- `_grid_multiref_duration` — L11128
- `_grid_multiref_segment_max_stretch` — L11144
- `_grid_multiref_prompt` — L11152
- `_write_grid_multiref_motion_qa` — L11200
- `_write_previs_page_motion_qa` — L11210
- `_write_storyboard_trailer_qa` — L11220
- `_write_character_trailer_qa` — L11230
- `_write_grid_multiref_segment_qa` — L11240
- `_motion_compare_record` — L11250
- `_write_storyboard_motion_compare_qa` — L11272
- `_scene_segment_duration` — L11308
- `_apply_grid_multiref_segments` — L11327
- `_previs_page_duration` — L11521
- `_previs_page_group_prompt` — L11531
- `_previs_page_groups` — L11557
- `_storyboard_trailer_duration` — L11572
- `_storyboard_trailer_prompt` — L11582
- `_character_trailer_max_shots` — L11610
- `_character_trailer_shot_duration` — L11618
- `_character_trailer_prompt` — L11632
- `_concat_character_trailer_segments` — L11647
- `_generate_character_trailer_motion` — L11686
- `_multi_trailer_prompt_for_group` — L11794
- `_generate_multi_trailer_segments` — L11817
- `_generate_storyboard_trailer_motion` — L11928
- `_generate_previs_page_motion_segments` — L12003
- `_generate_grid_multiref_motion_segments` — L12115
- `_grid_multiref_concat_groups` — L12285
- `_grid_multiref_concat_groups_partial` — L12302
- `_grid_multiref_concat_paths` — L12320
- `_lip_sync_slot_duration` — L12351
- `_adsd_lip_sync_prompt` — L12358
- `_adsd_broll_motion_prompt` — L12404
- `_adsd_action_b_motion_prompt` — L12446
- `_adsd_silent_b_motion_prompt` — L12492
- `_adsd_narrated_b_audio_dub_prompt` — L12527
- `_adsd_almighty_audio_dub_prompt` — L12571
- `_postprocess_lip_sync_segment` — L12612
- `_detect_audio_leading_silence` — L12684
- `_concat_audio_files_for_group` — L12709
- `_split_lip_sync_raw_by_durations` — L12732
- `_postprocess_audio_dub_segment` — L12767
- `_lips_change_repair_segment` — L12882
- `_load_lips_change_requested_turns` — L12967
- `_parse_turn_set` — L12984
- `_load_motion_voice_repair_turns` — L13006
- `_voice_assets_file` — L13018
- `_load_voice_assets` — L13025
- `_select_voice_asset_reference` — L13044
- `_lip_sync_poll_download_and_process` — L13110
- `_lip_sync_one_group` — L13178
- `_lip_sync_one_scene` — L13355
- `step66_adsd_lip_sync` — L13679
- `step65_motion` — L14000
- `step65_grid_multiref_motion_qa` — L14152
- `_sanitize_scene_for_state` — L14181
- `_save_pipeline_state` — L14200
- `_retime_after_audio_dub` — L14224
- `_build_voice_clone_hybrid_audio` — L14262
- `_build_dynamic_bgm` — L14401

---

### 第七步：拼接视频轨
Range: **L14445 – L14676** (232 lines)

**Functions:**
- `step7_concat` — L14446

---

### 第八步：生成 ASS 字幕
Range: **L14677 – L15479** (803 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L14800-15479 (680 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L14678
- `_word_timings_for_subtitle_align` — L14704
- `_align_segments_via_asr` — L14745
- `step8_subtitles` — L14788
- `_read_output_json` — L15200
- `_qa_file_pass` — L15211
- `_ass_has_dialogue` — L15218
- `_write_adsd_delivery_qa` — L15228
- `_write_bgm_only_qa` — L15368

---

### 第九步：最终合成
Range: **L15480 – L15732** (253 lines)

**Functions:**
- `step9_render` — L15481

---

### 第十步：推送 Telegram
Range: **L15733 – L17347** (1615 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L16833-17154 (322 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L17155-17159 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L17160-17223 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L17224-17269 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L17270-17347 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L16102
- `PANTONE_FALLBACK` — L16129
- `FESTIVAL_DATE_TAG` — L16242

**Functions:**
- `_generate_caption` — L15734
- `_overlay_title_on_cover` — L15972
- `_prepare_tg_photo` — L16082
- `_get_pantone_for_date` — L16132
- `_llm_bottom_note` — L16157
- `_get_bottom_note` — L16186
- `_get_date_tag` — L16264
- `_shrink_to_b64` — L16286
- `_llm_check_scenes_anomalies` — L16302
- `_llm_check_cover_unique` — L16355
- `_llm_check_cover_quality` — L16385
- `_try_almanac_cover` — L16427
- `_generate_cover_image` — L16598
- `_async_kickoff_cover_caption` — L16840
- `_await_async_cover_caption` — L16870
- `step10_deliver` — L16894

---

### 主流程
Range: **L17348 – L17525** (178 lines)

**Functions:**
- `_print_execution_plan` — L17349
- `main` — L17397

---
