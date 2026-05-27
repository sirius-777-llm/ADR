# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (17383 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-2014 (1893 lines · 59 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L2015-4250 (2236 lines · 30 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L4251-5382 (1132 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L5383-5934 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L5935-9705 (3771 lines · 82 fn · 6 sub)
- [`第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）`](#第-6-5-步-动态化-hads-vads-默认-on---no-motion-关) — L9706-14302 (4597 lines · 103 fn · 5 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L14303-14534 (232 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L14535-15337 (803 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L15338-15590 (253 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L15591-17205 (1615 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L17206-17383 (178 lines · 2 fn · 0 sub)

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
Range: **L2015 – L4250** (2236 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L3479-4250 (772 lines)

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
- `_parse_timecode_seconds` — L2314
- `_clean_override_line_text` — L2323
- `_parse_override_script_text` — L2329
- `_adsd_pov_contract` — L2363
- `_load_audit_blacklist_block` — L2376
- `_generate_adsd_dialogue_turns` — L2414
- `_broll_rhythm_reviewer` — L2841
- `_sweep_speaker_field` — L2948
- `_should_run_immersion_qa` — L3008
- `_adsd_immersion_qa_rewrite_turns` — L3031
- `_adsd_visual_contract` — L3095
- `_parse_risk_score` — L3147
- `_check_high_risk_hard_abort` — L3176
- `_maybe_neutralize_topic` — L3203
- `step1_script` — L3242
- `_write_ads_retention_qa` — L4194

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L4251 – L5382** (1132 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L4326
- `_ADSD_POLICY_REWRITE_TERMS` — L4332
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L4423

**Functions:**
- `_openai_tts_fallback` — L4252
- `_edge_tts_fallback` — L4298
- `_sanitize_for_external_api` — L4341
- `_is_content_policy_error` — L4350
- `_rewrite_adsd_tts_text_for_policy` — L4364
- `_record_adsd_tts_rewrite` — L4404
- `_build_silence_mp3` — L4429
- `_audio_duration_seconds` — L4442
- `_text_to_audio_master_voice_timed` — L4454
- `_text_to_audio_master_voice` — L4579
- `step2_master_voice` — L4692
- `_tts_turn_to_audio` — L4820
- `_asr_verify_dialogue_audio` — L4884
- `_asr_verify_dialogue_turns` — L4946
- `_normalize_cn_number_token` — L4988
- `_compact_zh_text` — L5010
- `_write_adsd_asr_text_qa` — L5017
- `_write_adsd_speaker_focus_qa` — L5056
- `_write_adsd_gender_voice_qa` — L5116
- `step2_dialogue_voice` — L5169

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L5383 – L5934** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L5390-5512 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L5513-5547 (35 lines)
- _第二层：字符数插值_ — L5548-5572 (25 lines)
- _第三层：silencedetect 物理校准_ — L5573-5934 (362 lines)

**Functions:**
- `_detect_silences` — L5391
- `_calibrate_boundaries` — L5426
- `_enforce_monotonic` — L5460
- `_manual_override_segments` — L5472
- `_calc_sentence_boundaries` — L5493
- `step345_timeline` — L5604
- `_analyze_bgm_energy_cuts` — L5663
- `_snap_bgm_only_boundaries` — L5726
- `step345_bgm_only_timeline` — L5786

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L5935 – L9705** (3771 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L7134-7184 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L7185-7325 (141 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L7326-7760 (435 lines)
- _Speaker IP Card (2026-05-21)_ — L7761-9538 (1778 lines)
- _审批流程_ — L9539-9595 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L9596-9705 (110 lines)

**Top-level constants:**
- `_CORE_TERMS_STOP_WORDS` — L6330
- `CHARACTER_META_GRID_COSTUMES` — L7140
- `CHARACTER_META_GRID_POSES` — L7141
- `CHARACTER_META_GRID_SCENES` — L7142
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L7145

**Functions:**
- `_extract_img_url` — L5936
- `_extract_img_urls` — L5958
- `_extract_video_url` — L5991
- `_count_bands` — L6016
- `_detect_contact_sheet_like_image` — L6028
- `_file_sha256` — L6089
- `_load_upload_cache` — L6102
- `_save_upload_cache` — L6111
- `_cached_upload_url` — L6119
- `_store_upload_url` — L6136
- `_guess_upload_mime` — L6146
- `_upload_to_weryai` — L6169
- `_send_for_approval` — L6223
- `_wait_approval` — L6287
- `_render_still_segment` — L6299
- `_extract_core_terms` — L6336
- `_scene_text_visual_alignment` — L6355
- `_write_text_visual_alignment_qa` — L6376
- `_scene_motion_action_plan` — L6399
- `_ensure_motion_action_plan` — L6453
- `_motion_action_block` — L6462
- `_motion_plan_for_qa` — L6490
- `_write_motion_action_plan_qa` — L6500
- `_write_motion_bridge_refs_qa` — L6530
- `_motion_bridge_ref_prompt` — L6537
- `generate_motion_bridge_refs_gpt_image2` — L6570
- `generate_image` — L6683
- `generate_storyboard_images_gpt_image2` — L6730
- `_storyboard_grid_aspect` — L6915
- `_storyboard_grid_cols_rows` — L6922
- `_storyboard_grid_prompt` — L6944
- `_storyboard_grid_prompt_limit` — L6982
- `_is_prompt_limit_response` — L6986
- `_production_storyboard_prompt` — L6992
- `_write_production_storyboard_page_qa` — L7026
- `_character_sheet_prompt` — L7036
- `_is_audit_blocked` — L7162
- `_paraphrase_sensitive_dialogue` — L7175
- `_topic_cache_dir` — L7189
- `_topic_cache_path` — L7195
- `_load_topic_decomposition_cache` — L7208
- `_save_topic_decomposition_cache` — L7226
- `_llm_topic_decomposition` — L7232
- `_director_route_block` — L7379
- `_llm_infer_meta_grid_template` — L7449
- `_resolve_meta_grid_template` — L7506
- `_infer_meta_grid_costume` — L7549
- `_infer_meta_grid_pose` — L7598
- `_adsd_meta_grid_call_prompt` — L7645
- `_meta_grid_panel_index` — L7687
- `_migrate_speaker_ip` — L7767
- `_speaker_ips_dir` — L7792
- `_list_speaker_ips` — L7799
- `_match_speaker_ip` — L7813
- `_build_speaker_ip_context_for_script` — L7833
- `_ip_usage_stats` — L7889
- `_recommend_related_ips` — L7907
- `_save_speaker_ip` — L7932
- `_record_speaker_usage_history` — L7941
- `_format_speaker_usage_history_for_prompt` — L7988
- `_llm_infer_ip_skeleton` — L8006
- `_llm_pick_voice_asset_for_ip` — L8051
- `_auto_incubate_missing_ips` — L8099
- `_character_meta_grid_cache_dir` — L8183
- `_character_meta_grid_cache_path` — L8191
- `_character_meta_grid_cache_legacy_path` — L8199
- `_character_meta_grid_path` — L8206
- `generate_character_meta_grid_gpt_image2` — L8212
- `_generate_all_character_meta_grids` — L8384
- `_write_character_sheet_qa` — L8425
- `generate_character_sheet_gpt_image2` — L8435
- `generate_production_storyboard_page_gpt_image2` — L8535
- `_qa_clean_storyboard_panel` — L8598
- `_crop_storyboard_grid_panels` — L8779
- `generate_storyboard_grid_gpt_image2` — L8826
- `_gpt_image2_direct_annotated_aspect` — L9057
- `_gpt_image2_direct_annotated_prompt` — L9064
- `generate_gpt_image2_direct_annotated_storyboards` — L9094
- `_llm_bgm_description` — L9195
- `_bgm_contains_vocals` — L9234
- `generate_bgm` — L9268
- `step6_parallel` — L9385

---

### 第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）
Range: **L9706 – L14302** (4597 lines)

**Sub-sections:**
- _PR-A (2026-05-27): merged_a 合并跑 helpers_ — L12634-14037 (1404 lines)
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L14038-14080 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L14081-14118 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回时间轴锚定音轨_ — L14119-14257 (139 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L14258-14302 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L9709
- `_motion_tasks_file` — L9776
- `_motion_qa_file` — L9780
- `_append_motion_qa` — L9784
- `_finalize_motion_qa` — L9808
- `_lip_sync_tasks_file` — L9892
- `_load_motion_tasks` — L9896
- `_save_motion_task` — L9906
- `_remove_motion_task` — L9914
- `_load_lip_sync_tasks` — L9921
- `_save_lip_sync_task` — L9931
- `_remove_lip_sync_task` — L9938
- `_video_visual_motion_qa` — L9945
- `_motion_output_qa` — L10017
- `_has_audio_stream` — L10062
- `_normalize_motion_video` — L10073
- `_motion_poll_and_download` — L10123
- `_build_motion_video_prompt` — L10174
- `_short_board_text` — L10204
- `_wrap_board_text` — L10211
- `_storyboard_font` — L10242
- `_draw_storyboard_arrow` — L10257
- `_build_annotated_storyboard_reference` — L10271
- `_plain_caption_text` — L10372
- `_werydance_caption_request` — L10380
- `_werydance_caption_instruction` — L10407
- `_werydance_negative_prompt` — L10419
- `_motion_reference_prompt` — L10437
- `_motion_audio_dub_prompt` — L10460
- `_motion_audio_dub_poll_and_download` — L10494
- `_try_motion_audio_dub_video` — L10559
- `_try_motion_reference_video` — L10698
- `_motion_one_scene` — L10814
- `_grid_multiref_tasks_file` — L10943
- `_previs_page_tasks_file` — L10947
- `_load_grid_multiref_tasks` — L10951
- `_load_previs_page_tasks` — L10961
- `_save_grid_multiref_task` — L10971
- `_save_previs_page_task` — L10978
- `_remove_grid_multiref_task` — L10985
- `_remove_previs_page_task` — L10992
- `_poll_video_task_download` — L10999
- `_grid_multiref_group_size` — L11048
- `_grid_multiref_duration` — L11056
- `_grid_multiref_segment_max_stretch` — L11072
- `_grid_multiref_prompt` — L11080
- `_write_grid_multiref_motion_qa` — L11128
- `_write_previs_page_motion_qa` — L11138
- `_write_storyboard_trailer_qa` — L11148
- `_write_character_trailer_qa` — L11158
- `_write_grid_multiref_segment_qa` — L11168
- `_motion_compare_record` — L11178
- `_write_storyboard_motion_compare_qa` — L11200
- `_scene_segment_duration` — L11236
- `_apply_grid_multiref_segments` — L11255
- `_previs_page_duration` — L11449
- `_previs_page_group_prompt` — L11459
- `_previs_page_groups` — L11485
- `_storyboard_trailer_duration` — L11500
- `_storyboard_trailer_prompt` — L11510
- `_character_trailer_max_shots` — L11538
- `_character_trailer_shot_duration` — L11546
- `_character_trailer_prompt` — L11560
- `_concat_character_trailer_segments` — L11575
- `_generate_character_trailer_motion` — L11614
- `_multi_trailer_prompt_for_group` — L11722
- `_generate_multi_trailer_segments` — L11745
- `_generate_storyboard_trailer_motion` — L11856
- `_generate_previs_page_motion_segments` — L11931
- `_generate_grid_multiref_motion_segments` — L12043
- `_grid_multiref_concat_groups` — L12213
- `_grid_multiref_concat_groups_partial` — L12230
- `_grid_multiref_concat_paths` — L12248
- `_lip_sync_slot_duration` — L12279
- `_adsd_lip_sync_prompt` — L12286
- `_adsd_broll_motion_prompt` — L12332
- `_adsd_action_b_motion_prompt` — L12374
- `_adsd_silent_b_motion_prompt` — L12420
- `_adsd_narrated_b_audio_dub_prompt` — L12455
- `_adsd_almighty_audio_dub_prompt` — L12499
- `_postprocess_lip_sync_segment` — L12540
- `_detect_audio_leading_silence` — L12612
- `_concat_audio_files_for_group` — L12637
- `_split_lip_sync_raw_by_durations` — L12660
- `_postprocess_audio_dub_segment` — L12695
- `_lips_change_repair_segment` — L12810
- `_load_lips_change_requested_turns` — L12895
- `_parse_turn_set` — L12912
- `_load_motion_voice_repair_turns` — L12934
- `_voice_assets_file` — L12946
- `_load_voice_assets` — L12953
- `_select_voice_asset_reference` — L12972
- `_lip_sync_poll_download_and_process` — L13038
- `_lip_sync_one_group` — L13106
- `_lip_sync_one_scene` — L13283
- `step66_adsd_lip_sync` — L13607
- `step65_motion` — L13928
- `step65_grid_multiref_motion_qa` — L14010
- `_sanitize_scene_for_state` — L14039
- `_save_pipeline_state` — L14058
- `_retime_after_audio_dub` — L14082
- `_build_voice_clone_hybrid_audio` — L14120
- `_build_dynamic_bgm` — L14259

---

### 第七步：拼接视频轨
Range: **L14303 – L14534** (232 lines)

**Functions:**
- `step7_concat` — L14304

---

### 第八步：生成 ASS 字幕
Range: **L14535 – L15337** (803 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L14658-15337 (680 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L14536
- `_word_timings_for_subtitle_align` — L14562
- `_align_segments_via_asr` — L14603
- `step8_subtitles` — L14646
- `_read_output_json` — L15058
- `_qa_file_pass` — L15069
- `_ass_has_dialogue` — L15076
- `_write_adsd_delivery_qa` — L15086
- `_write_bgm_only_qa` — L15226

---

### 第九步：最终合成
Range: **L15338 – L15590** (253 lines)

**Functions:**
- `step9_render` — L15339

---

### 第十步：推送 Telegram
Range: **L15591 – L17205** (1615 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L16691-17012 (322 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L17013-17017 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L17018-17081 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L17082-17127 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L17128-17205 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L15960
- `PANTONE_FALLBACK` — L15987
- `FESTIVAL_DATE_TAG` — L16100

**Functions:**
- `_generate_caption` — L15592
- `_overlay_title_on_cover` — L15830
- `_prepare_tg_photo` — L15940
- `_get_pantone_for_date` — L15990
- `_llm_bottom_note` — L16015
- `_get_bottom_note` — L16044
- `_get_date_tag` — L16122
- `_shrink_to_b64` — L16144
- `_llm_check_scenes_anomalies` — L16160
- `_llm_check_cover_unique` — L16213
- `_llm_check_cover_quality` — L16243
- `_try_almanac_cover` — L16285
- `_generate_cover_image` — L16456
- `_async_kickoff_cover_caption` — L16698
- `_await_async_cover_caption` — L16728
- `step10_deliver` — L16752

---

### 主流程
Range: **L17206 – L17383** (178 lines)

**Functions:**
- `_print_execution_plan` — L17207
- `main` — L17255

---
