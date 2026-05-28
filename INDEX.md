# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (17746 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-2034 (1913 lines · 59 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L2035-4323 (2289 lines · 30 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L4324-5455 (1132 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L5456-6007 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L6008-9790 (3783 lines · 82 fn · 6 sub)
- [`第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）`](#第-6-5-步-动态化-hads-vads-默认-on---no-motion-关) — L9791-14560 (4770 lines · 103 fn · 5 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L14561-14820 (260 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L14821-15623 (803 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L15624-15899 (276 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L15900-17561 (1662 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L17562-17746 (185 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L2034** (1913 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L324-453 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L454-1142 (689 lines)
- _工具函数_ — L1143-1492 (350 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1493-2034 (542 lines)

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
- `ADS_RETENTION_MODE` — L977
- `ADSD_MODE_NAME` — L983
- `EMOTION_STYLE` — L1122
- `EMOTION_STYLE_BRIGHT` — L1134
- `_TG_DASHBOARD_STAGES` — L1156
- `_TG_NOISY_PATTERNS` — L1171
- `_TG_IMMEDIATE_PATTERNS` — L1189
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1422
- `_LLM_TIER` — L1670
- `_TOPIC_MODIFIERS` — L1866
- `_TONE_PANTONE_OVERRIDE` — L1883

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
- `log` — L1144
- `_tg_send_raw` — L1212
- `_tg_matches` — L1228
- `_tg_summarize` — L1232
- `_tg_dashboard_stage_for` — L1239
- `_tg_progress_bar` — L1247
- `_tg_dashboard_text` — L1253
- `_tg_dashboard_update` — L1271
- `_tg_maybe_digest` — L1308
- `tg` — L1323
- `_wait_image_submit_slot` — L1372
- `_wait_motion_submit_slot` — L1385
- `_is_rate_limited_error` — L1398
- `_is_rate_limited_response` — L1408
- `_inject_image2_quality_suffix` — L1430
- `submit_text_to_image` — L1444
- `req_post` — L1474
- `req_get` — L1488
- `_tg_probe_send` — L1496
- `_tg_probe_delete` — L1516
- `_tg_upload_with_probe_gap` — L1529
- `poll` — L1569
- `poll_podcast` — L1594
- `poll_task_status` — L1616
- `poll_storyboard_task` — L1638
- `tier_chat` — L1678
- `chat` — L1684
- `pick_image_model` — L1712
- `detect_topic_meta` — L1737
- `_topic_culture_guard` — L1787
- `_write_cultural_visual_qa` — L1813
- `is_1919_global_topic` — L1860
- `_strip_topic_modifiers` — L1871
- `apply_1919_global_guardrails` — L1889
- `build_1919_global_cover_prompt` — L1918
- `build_shot_blueprint` — L1947
- `ffprobe_duration` — L1973
- `ffprobe_video_size` — L1984
- `_video_decode_probe` — L2005
- `ffmpeg` — L2023

---

### 第一步：双导演生成剧本
Range: **L2035 – L4323** (2289 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L3499-4323 (825 lines)

**Top-level constants:**
- `_ENSEMBLE_CAP_BY_ROUTE` — L2183

**Functions:**
- `_extract_json_array` — L2036
- `_extract_json_object` — L2046
- `_voice_for_speaker` — L2056
- `_adsd_gender_from_voice` — L2092
- `_adsd_infer_gender_from_speaker` — L2100
- `_adsd_gender_lock_phrase` — L2109
- `_adsd_visual_subject_has_gender_conflict` — L2124
- `_adsd_default_roles` — L2136
- `_adsd_allows_media_role` — L2141
- `_adsd_role_candidates` — L2149
- `_adsd_dialogue_shape` — L2172
- `_ensemble_speaker_cap` — L2194
- `_finalize_adsd_turns` — L2207
- `_parse_adsd_override_turns` — L2241
- `_parse_timecode_seconds` — L2334
- `_clean_override_line_text` — L2343
- `_parse_override_script_text` — L2349
- `_adsd_pov_contract` — L2383
- `_load_audit_blacklist_block` — L2396
- `_generate_adsd_dialogue_turns` — L2434
- `_broll_rhythm_reviewer` — L2861
- `_sweep_speaker_field` — L2968
- `_should_run_immersion_qa` — L3028
- `_adsd_immersion_qa_rewrite_turns` — L3051
- `_adsd_visual_contract` — L3115
- `_parse_risk_score` — L3167
- `_check_high_risk_hard_abort` — L3196
- `_maybe_neutralize_topic` — L3223
- `step1_script` — L3262
- `_write_ads_retention_qa` — L4267

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L4324 – L5455** (1132 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L4399
- `_ADSD_POLICY_REWRITE_TERMS` — L4405
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L4496

**Functions:**
- `_openai_tts_fallback` — L4325
- `_edge_tts_fallback` — L4371
- `_sanitize_for_external_api` — L4414
- `_is_content_policy_error` — L4423
- `_rewrite_adsd_tts_text_for_policy` — L4437
- `_record_adsd_tts_rewrite` — L4477
- `_build_silence_mp3` — L4502
- `_audio_duration_seconds` — L4515
- `_text_to_audio_master_voice_timed` — L4527
- `_text_to_audio_master_voice` — L4652
- `step2_master_voice` — L4765
- `_tts_turn_to_audio` — L4893
- `_asr_verify_dialogue_audio` — L4957
- `_asr_verify_dialogue_turns` — L5019
- `_normalize_cn_number_token` — L5061
- `_compact_zh_text` — L5083
- `_write_adsd_asr_text_qa` — L5090
- `_write_adsd_speaker_focus_qa` — L5129
- `_write_adsd_gender_voice_qa` — L5189
- `step2_dialogue_voice` — L5242

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L5456 – L6007** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L5463-5585 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L5586-5620 (35 lines)
- _第二层：字符数插值_ — L5621-5645 (25 lines)
- _第三层：silencedetect 物理校准_ — L5646-6007 (362 lines)

**Functions:**
- `_detect_silences` — L5464
- `_calibrate_boundaries` — L5499
- `_enforce_monotonic` — L5533
- `_manual_override_segments` — L5545
- `_calc_sentence_boundaries` — L5566
- `step345_timeline` — L5677
- `_analyze_bgm_energy_cuts` — L5736
- `_snap_bgm_only_boundaries` — L5799
- `step345_bgm_only_timeline` — L5859

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L6008 – L9790** (3783 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L7209-7259 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L7260-7400 (141 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L7401-7835 (435 lines)
- _Speaker IP Card (2026-05-21)_ — L7836-9623 (1788 lines)
- _审批流程_ — L9624-9680 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L9681-9790 (110 lines)

**Top-level constants:**
- `_CORE_TERMS_STOP_WORDS` — L6403
- `CHARACTER_META_GRID_COSTUMES` — L7215
- `CHARACTER_META_GRID_POSES` — L7216
- `CHARACTER_META_GRID_SCENES` — L7217
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L7220

**Functions:**
- `_extract_img_url` — L6009
- `_extract_img_urls` — L6031
- `_extract_video_url` — L6064
- `_count_bands` — L6089
- `_detect_contact_sheet_like_image` — L6101
- `_file_sha256` — L6162
- `_load_upload_cache` — L6175
- `_save_upload_cache` — L6184
- `_cached_upload_url` — L6192
- `_store_upload_url` — L6209
- `_guess_upload_mime` — L6219
- `_upload_to_weryai` — L6242
- `_send_for_approval` — L6296
- `_wait_approval` — L6360
- `_render_still_segment` — L6372
- `_extract_core_terms` — L6409
- `_scene_text_visual_alignment` — L6428
- `_write_text_visual_alignment_qa` — L6449
- `_scene_motion_action_plan` — L6472
- `_ensure_motion_action_plan` — L6526
- `_motion_action_block` — L6535
- `_motion_plan_for_qa` — L6563
- `_write_motion_action_plan_qa` — L6573
- `_write_motion_bridge_refs_qa` — L6603
- `_motion_bridge_ref_prompt` — L6610
- `generate_motion_bridge_refs_gpt_image2` — L6643
- `generate_image` — L6758
- `generate_storyboard_images_gpt_image2` — L6805
- `_storyboard_grid_aspect` — L6990
- `_storyboard_grid_cols_rows` — L6997
- `_storyboard_grid_prompt` — L7019
- `_storyboard_grid_prompt_limit` — L7057
- `_is_prompt_limit_response` — L7061
- `_production_storyboard_prompt` — L7067
- `_write_production_storyboard_page_qa` — L7101
- `_character_sheet_prompt` — L7111
- `_is_audit_blocked` — L7237
- `_paraphrase_sensitive_dialogue` — L7250
- `_topic_cache_dir` — L7264
- `_topic_cache_path` — L7270
- `_load_topic_decomposition_cache` — L7283
- `_save_topic_decomposition_cache` — L7301
- `_llm_topic_decomposition` — L7307
- `_director_route_block` — L7454
- `_llm_infer_meta_grid_template` — L7524
- `_resolve_meta_grid_template` — L7581
- `_infer_meta_grid_costume` — L7624
- `_infer_meta_grid_pose` — L7673
- `_adsd_meta_grid_call_prompt` — L7720
- `_meta_grid_panel_index` — L7762
- `_migrate_speaker_ip` — L7842
- `_speaker_ips_dir` — L7867
- `_list_speaker_ips` — L7874
- `_match_speaker_ip` — L7888
- `_build_speaker_ip_context_for_script` — L7908
- `_ip_usage_stats` — L7964
- `_recommend_related_ips` — L7982
- `_save_speaker_ip` — L8007
- `_record_speaker_usage_history` — L8016
- `_format_speaker_usage_history_for_prompt` — L8063
- `_llm_infer_ip_skeleton` — L8081
- `_llm_pick_voice_asset_for_ip` — L8126
- `_auto_incubate_missing_ips` — L8174
- `_character_meta_grid_cache_dir` — L8258
- `_character_meta_grid_cache_path` — L8266
- `_character_meta_grid_cache_legacy_path` — L8274
- `_character_meta_grid_path` — L8281
- `generate_character_meta_grid_gpt_image2` — L8287
- `_generate_all_character_meta_grids` — L8459
- `_write_character_sheet_qa` — L8500
- `generate_character_sheet_gpt_image2` — L8510
- `generate_production_storyboard_page_gpt_image2` — L8610
- `_qa_clean_storyboard_panel` — L8673
- `_crop_storyboard_grid_panels` — L8854
- `generate_storyboard_grid_gpt_image2` — L8901
- `_gpt_image2_direct_annotated_aspect` — L9132
- `_gpt_image2_direct_annotated_prompt` — L9139
- `generate_gpt_image2_direct_annotated_storyboards` — L9169
- `_llm_bgm_description` — L9270
- `_bgm_contains_vocals` — L9309
- `generate_bgm` — L9343
- `step6_parallel` — L9460

---

### 第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）
Range: **L9791 – L14560** (4770 lines)

**Sub-sections:**
- _PR-A (2026-05-27): merged_a 合并跑 helpers_ — L12822-14295 (1474 lines)
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L14296-14338 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L14339-14376 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回时间轴锚定音轨_ — L14377-14515 (139 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L14516-14560 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L9794
- `_motion_tasks_file` — L9861
- `_motion_qa_file` — L9865
- `_append_motion_qa` — L9869
- `_finalize_motion_qa` — L9893
- `_lip_sync_tasks_file` — L9977
- `_load_motion_tasks` — L9981
- `_save_motion_task` — L9991
- `_remove_motion_task` — L9999
- `_load_lip_sync_tasks` — L10006
- `_save_lip_sync_task` — L10016
- `_remove_lip_sync_task` — L10023
- `_video_visual_motion_qa` — L10030
- `_motion_output_qa` — L10102
- `_has_audio_stream` — L10147
- `_normalize_motion_video` — L10158
- `_motion_poll_and_download` — L10208
- `_build_motion_video_prompt` — L10259
- `_short_board_text` — L10289
- `_wrap_board_text` — L10296
- `_storyboard_font` — L10327
- `_draw_storyboard_arrow` — L10342
- `_build_annotated_storyboard_reference` — L10356
- `_plain_caption_text` — L10457
- `_werydance_caption_request` — L10465
- `_werydance_caption_instruction` — L10492
- `_werydance_negative_prompt` — L10504
- `_motion_reference_prompt` — L10522
- `_motion_audio_dub_prompt` — L10545
- `_motion_audio_dub_poll_and_download` — L10579
- `_try_motion_audio_dub_video` — L10644
- `_try_motion_reference_video` — L10807
- `_motion_one_scene` — L10923
- `_grid_multiref_tasks_file` — L11052
- `_previs_page_tasks_file` — L11056
- `_load_grid_multiref_tasks` — L11060
- `_load_previs_page_tasks` — L11070
- `_save_grid_multiref_task` — L11080
- `_save_previs_page_task` — L11087
- `_remove_grid_multiref_task` — L11094
- `_remove_previs_page_task` — L11101
- `_poll_video_task_download` — L11108
- `_grid_multiref_group_size` — L11157
- `_grid_multiref_duration` — L11167
- `_grid_multiref_segment_max_stretch` — L11189
- `_grid_multiref_prompt` — L11197
- `_write_grid_multiref_motion_qa` — L11250
- `_write_previs_page_motion_qa` — L11260
- `_write_storyboard_trailer_qa` — L11270
- `_write_character_trailer_qa` — L11280
- `_write_grid_multiref_segment_qa` — L11290
- `_motion_compare_record` — L11300
- `_write_storyboard_motion_compare_qa` — L11322
- `_scene_segment_duration` — L11358
- `_apply_grid_multiref_segments` — L11377
- `_previs_page_duration` — L11582
- `_previs_page_group_prompt` — L11592
- `_previs_page_groups` — L11618
- `_storyboard_trailer_duration` — L11633
- `_storyboard_trailer_prompt` — L11643
- `_character_trailer_max_shots` — L11671
- `_character_trailer_shot_duration` — L11679
- `_character_trailer_prompt` — L11693
- `_concat_character_trailer_segments` — L11708
- `_generate_character_trailer_motion` — L11747
- `_multi_trailer_prompt_for_group` — L11855
- `_generate_multi_trailer_segments` — L11878
- `_generate_storyboard_trailer_motion` — L11989
- `_generate_previs_page_motion_segments` — L12064
- `_generate_grid_multiref_motion_segments` — L12176
- `_grid_multiref_concat_groups` — L12390
- `_grid_multiref_concat_groups_partial` — L12407
- `_grid_multiref_concat_paths` — L12425
- `_lip_sync_slot_duration` — L12467
- `_adsd_lip_sync_prompt` — L12474
- `_adsd_broll_motion_prompt` — L12520
- `_adsd_action_b_motion_prompt` — L12562
- `_adsd_silent_b_motion_prompt` — L12608
- `_adsd_narrated_b_audio_dub_prompt` — L12643
- `_adsd_almighty_audio_dub_prompt` — L12687
- `_postprocess_lip_sync_segment` — L12728
- `_detect_audio_leading_silence` — L12800
- `_concat_audio_files_for_group` — L12825
- `_split_lip_sync_raw_by_durations` — L12848
- `_postprocess_audio_dub_segment` — L12883
- `_lips_change_repair_segment` — L12998
- `_load_lips_change_requested_turns` — L13083
- `_parse_turn_set` — L13100
- `_load_motion_voice_repair_turns` — L13122
- `_voice_assets_file` — L13134
- `_load_voice_assets` — L13141
- `_select_voice_asset_reference` — L13160
- `_lip_sync_poll_download_and_process` — L13226
- `_lip_sync_one_group` — L13294
- `_lip_sync_one_scene` — L13471
- `step66_adsd_lip_sync` — L13795
- `step65_motion` — L14116
- `step65_grid_multiref_motion_qa` — L14268
- `_sanitize_scene_for_state` — L14297
- `_save_pipeline_state` — L14316
- `_retime_after_audio_dub` — L14340
- `_build_voice_clone_hybrid_audio` — L14378
- `_build_dynamic_bgm` — L14517

---

### 第七步：拼接视频轨
Range: **L14561 – L14820** (260 lines)

**Functions:**
- `step7_concat` — L14562

---

### 第八步：生成 ASS 字幕
Range: **L14821 – L15623** (803 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L14944-15623 (680 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L14822
- `_word_timings_for_subtitle_align` — L14848
- `_align_segments_via_asr` — L14889
- `step8_subtitles` — L14932
- `_read_output_json` — L15344
- `_qa_file_pass` — L15355
- `_ass_has_dialogue` — L15362
- `_write_adsd_delivery_qa` — L15372
- `_write_bgm_only_qa` — L15512

---

### 第九步：最终合成
Range: **L15624 – L15899** (276 lines)

**Functions:**
- `step9_render` — L15625

---

### 第十步：推送 Telegram
Range: **L15900 – L17561** (1662 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L17000-17368 (369 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L17369-17373 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L17374-17437 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L17438-17483 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L17484-17561 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L16269
- `PANTONE_FALLBACK` — L16296
- `FESTIVAL_DATE_TAG` — L16409

**Functions:**
- `_generate_caption` — L15901
- `_overlay_title_on_cover` — L16139
- `_prepare_tg_photo` — L16249
- `_get_pantone_for_date` — L16299
- `_llm_bottom_note` — L16324
- `_get_bottom_note` — L16353
- `_get_date_tag` — L16431
- `_shrink_to_b64` — L16453
- `_llm_check_scenes_anomalies` — L16469
- `_llm_check_cover_unique` — L16522
- `_llm_check_cover_quality` — L16552
- `_try_almanac_cover` — L16594
- `_generate_cover_image` — L16765
- `_async_kickoff_cover_caption` — L17007
- `_await_async_cover_caption` — L17081
- `step10_deliver` — L17108

---

### 主流程
Range: **L17562 – L17746** (185 lines)

**Functions:**
- `_print_execution_plan` — L17563
- `main` — L17611

---
