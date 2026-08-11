# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (21797 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-124 (124 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L125-2531 (2407 lines · 74 fn · 5 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L2532-5183 (2652 lines · 33 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L5184-6416 (1233 lines · 22 fn · 2 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L6417-6968 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L6969-12604 (5636 lines · 131 fn · 8 sub)
- [`第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）`](#第-6-5-步-动态化-hads-vads-默认-on---no-motion-关) — L12605-18073 (5469 lines · 117 fn · 6 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L18074-18409 (336 lines · 3 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L18410-19368 (959 lines · 10 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L19369-19659 (291 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L19660-21542 (1883 lines · 19 fn · 6 sub)
- [`主流程`](#主流程) — L21543-21797 (255 lines · 3 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L124** (124 lines)

**Sub-sections:**
- _老黄历数据模块_ — L32-124 (93 lines)

**Functions:**
- `get_almanac_data` — L60

---

### 配置
Range: **L125 – L2531** (2407 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L364-493 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L494-1237 (744 lines)
- _工具函数_ — L1238-1613 (376 lines)
- _B87 纹理档系统：LLM 提名 + 代码护栏 + 确定性渲染_ — L1614-1876 (263 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1877-2531 (655 lines)

**Top-level constants:**
- `HEADERS` — L161
- `VIDEO_FORMAT_RAW` — L169
- `MTV_MODE` — L170
- `VIDEO_FORMAT` — L175
- `ADS_DIALOGUE_MODE_EARLY_CHECK` — L186
- `WITH_MOTION` — L193
- `BGM_ONLY_REQUESTED` — L198
- `ADS_DIALOGUE_MODE` — L205
- `GPT_IMAGE2_STORYBOARD` — L217
- `STORYBOARD_REFERENCE_MOTION` — L221
- `STORYBOARD_ANNOTATED_MOTION` — L225
- `GPT_IMAGE2_DIRECT_ANNOTATED_STORYBOARD` — L229
- `GPT_IMAGE2_STORYBOARD_GRID` — L234
- `ADSD_STORYBOARD_GRID` — L242
- `ADS_CHARACTER_SHEET_REQUESTED` — L248
- `STORYBOARD_GRID_MULTIREF_MOTION` — L252
- `STORYBOARD_GRID_MULTIREF_SEGMENTS` — L256
- `STORYBOARD_GRID_MULTIREF_MAIN` — L262
- `GRID_MULTIREF_PRIMARY` — L272
- `PREVIS_PAGE_MOTION` — L284
- `STORYBOARD_TRAILER_MODE` — L288
- `MOTION_ACTION_STORYBOARD` — L293
- `MOTION_BRIDGE_REFS` — L297
- `CHARACTER_TRAILER_MODE` — L301
- `STORYBOARD_TRAILER_MAIN` — L309
- `ADSD_LIP_SYNC_EXPERIMENT` — L322
- `ADSD_RICH_MOTION_PROMPT` — L330
- `ADSD_LLM_VOICE_ASSIGN` — L338
- `ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT` — L342
- `ADSD_CONSECUTIVE_SPEAKER_BATCHING` — L356
- `ADSD_GENDER_FALLBACK_VOICE_ASSET` — L367
- `SILENT_B_SPEAKERS` — L499
- `_PODCAST_TO_VOICE_ASSET_MAP` — L877
- `_VOICE_ASSET_FORBIDDEN_FLAGS` — L895
- `_GENERIC_NARRATOR_NAMES` — L939
- `VOICE_ASSET_AUDIO_DUB_EXPERIMENT` — L976
- `VOICE_ASSET_AUDIO_DUB_PARTIAL_OK` — L984
- `MOTION_VISUAL_QA` — L988
- `MOTION_VOICE_REPAIR` — L996
- `MOTION_VOICE_STRICT_LOCK` — L1001
- `WERYDANCE_CAPTIONS` — L1006
- `ADSD_ONSITE_POV_MODE` — L1018
- `ADSD_LIPS_CHANGE_REPAIR` — L1023
- `ADSD_LIPS_CHANGE_ALL` — L1028
- `ADS_REPORTER_MODE` — L1039
- `ADS_STORYBOARD_FLOW_DEFAULT` — L1056
- `ADS_RETENTION_MODE` — L1070
- `ADSD_MODE_NAME` — L1076
- `EMOTION_STYLE` — L1217
- `EMOTION_STYLE_BRIGHT` — L1229
- `_REDACT_PATTERNS_DEFAULT` — L1243
- `_TG_DASHBOARD_STAGES` — L1295
- `_TG_NOISY_PATTERNS` — L1310
- `_TG_IMMEDIATE_PATTERNS` — L1328
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1607
- `_TEXTURE_MODE_ENUM` — L1615
- `_TEXTURE_SUFFIX_MAP` — L1620
- `_TEXTURE_BODY_DIRECTIVE` — L1647
- `_TEXTURE_SCENE_PHRASE` — L1654
- `_TEXTURE_GRID_PHRASE` — L1661
- `_TEXTURE_MOTION_PHRASE` — L1669
- `_LLM_TIER` — L2057
- `_TOPIC_MODIFIERS` — L2284
- `_TONE_PANTONE_OVERRIDE` — L2301

**Functions:**
- `_read_almighty_model` — L141
- `_is_action_scene` — L376
- `_needs_storyboard_flow_character_sheet` — L387
- `_wuxia_action_panel_prompt` — L416
- `_action_motion_fragment` — L438
- `_infer_emotion_from_text` — L453
- `_emotion_expression_phrase` — L468
- `_infer_needs_lip_sync` — L475
- `_infer_turn_type` — L502
- `_is_action_shout` — L527
- `_resolve_turn_type` — L553
- `_is_silent_b` — L568
- `_is_narrated_b` — L572
- `_is_a_roll` — L576
- `_is_action_b` — L580
- `_voice_asset_id_for_speaker` — L584
- `_llm_assign_voice_assets` — L612
- `_apply_llm_voice_assignment` — L741
- `_voice_asset_is_speech_safe` — L902
- `_podcast_id_to_voice_asset` — L908
- `_resolve_voice_asset_for_ads_speaker` — L942
- `_redact_for_stdout` — L1258
- `log` — L1283
- `_tg_send_raw` — L1351
- `_tg_matches` — L1367
- `_tg_summarize` — L1371
- `_tg_dashboard_stage_for` — L1378
- `_tg_progress_bar` — L1386
- `_tg_dashboard_text` — L1392
- `_tg_dashboard_update` — L1410
- `_tg_maybe_digest` — L1447
- `tg` — L1462
- `_wait_image_submit_slot` — L1511
- `_wait_motion_submit_slot` — L1524
- `_is_rate_limited_error` — L1537
- `_is_rate_limited_response` — L1547
- `_is_transient_workflow_error` — L1559
- `_is_llm_rate_limited_error` — L1583
- `_era_is_pre_photographic` — L1681
- `_texture_mode_fallback` — L1709
- `_texture_guardrail` — L1730
- `_set_active_texture_profile` — L1769
- `_active_texture_suffix` — L1782
- `_active_texture_body_directive` — L1786
- `_active_texture_scene_phrase` — L1790
- `_active_texture_grid_phrase` — L1794
- `_active_texture_motion_phrase` — L1798
- `_inject_image2_quality_suffix` — L1802
- `submit_text_to_image` — L1822
- `req_post` — L1858
- `req_get` — L1872
- `_tg_probe_send` — L1880
- `_tg_probe_delete` — L1900
- `_tg_upload_with_probe_gap` — L1913
- `poll` — L1953
- `poll_podcast` — L1978
- `poll_task_status` — L2000
- `poll_storyboard_task` — L2022
- `tier_chat` — L2065
- `chat` — L2071
- `pick_image_model` — L2130
- `detect_topic_meta` — L2155
- `_topic_culture_guard` — L2205
- `_write_cultural_visual_qa` — L2231
- `is_1919_global_topic` — L2278
- `_strip_topic_modifiers` — L2289
- `apply_1919_global_guardrails` — L2307
- `build_1919_global_cover_prompt` — L2336
- `_shot_blueprint_enums` — L2368
- `build_shot_blueprint` — L2444
- `ffprobe_duration` — L2470
- `ffprobe_video_size` — L2481
- `_video_decode_probe` — L2502
- `ffmpeg` — L2520

---

### 第一步：双导演生成剧本
Range: **L2532 – L5183** (2652 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L4164-5183 (1020 lines)

**Top-level constants:**
- `_ENSEMBLE_CAP_BY_ROUTE` — L2684

**Functions:**
- `_extract_json_array` — L2533
- `_extract_json_object` — L2543
- `_voice_for_speaker` — L2553
- `_adsd_gender_from_voice` — L2589
- `_adsd_infer_gender_from_speaker` — L2597
- `_adsd_gender_lock_phrase` — L2606
- `_adsd_visual_subject_has_gender_conflict` — L2621
- `_adsd_default_roles` — L2633
- `_adsd_allows_media_role` — L2638
- `_adsd_role_candidates` — L2646
- `_adsd_dialogue_shape` — L2673
- `_ensemble_speaker_cap` — L2695
- `_ip_voice_asset_for_speaker` — L2708
- `_finalize_adsd_turns` — L2732
- `_parse_adsd_override_turns` — L2778
- `_parse_timecode_seconds` — L2871
- `_clean_override_line_text` — L2880
- `_parse_override_script_text` — L2886
- `_adsd_pov_contract` — L2920
- `_load_audit_blacklist_block` — L2933
- `_generate_adsd_dialogue_turns` — L2971
- `_broll_rhythm_reviewer` — L3398
- `_sweep_speaker_field` — L3505
- `_should_run_immersion_qa` — L3565
- `_adsd_immersion_qa_rewrite_turns` — L3588
- `_adsd_visual_contract` — L3652
- `_parse_risk_score` — L3704
- `_check_high_risk_hard_abort` — L3733
- `_maybe_neutralize_topic` — L3760
- `_apply_render_budget_scene_cap` — L3799
- `_apply_llm_mode_decision` — L3826
- `step1_script` — L3881
- `_write_ads_retention_qa` — L5127

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L5184 – L6416** (1233 lines)

**Sub-sections:**
- _B88: 内容审核(1002) → 分级软化 → 中性兜底句 → 静音 backstop，绝不崩管线_ — L5879-5907 (29 lines)
- _非内容审核(网络/transient): 有限退避重试，耗尽才抛_ — L5908-6416 (509 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L5259
- `_ADSD_POLICY_REWRITE_TERMS` — L5265
- `_TTS_SAFE_FALLBACK_LINE` — L5366
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L5434

**Functions:**
- `_openai_tts_fallback` — L5185
- `_edge_tts_fallback` — L5231
- `_sanitize_for_external_api` — L5290
- `_is_content_policy_error` — L5299
- `_rewrite_adsd_tts_text_for_policy` — L5313
- `_tts_safe_fallback_line` — L5375
- `_tts_silent_placeholder` — L5380
- `_record_adsd_tts_rewrite` — L5415
- `_build_silence_mp3` — L5440
- `_audio_duration_seconds` — L5453
- `_text_to_audio_master_voice_timed` — L5465
- `_text_to_audio_master_voice` — L5590
- `step2_master_voice` — L5703
- `_tts_turn_to_audio` — L5831
- `_asr_verify_dialogue_audio` — L5918
- `_asr_verify_dialogue_turns` — L5980
- `_normalize_cn_number_token` — L6022
- `_compact_zh_text` — L6044
- `_write_adsd_asr_text_qa` — L6051
- `_write_adsd_speaker_focus_qa` — L6090
- `_write_adsd_gender_voice_qa` — L6150
- `step2_dialogue_voice` — L6203

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L6417 – L6968** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L6424-6546 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L6547-6581 (35 lines)
- _第二层：字符数插值_ — L6582-6606 (25 lines)
- _第三层：silencedetect 物理校准_ — L6607-6968 (362 lines)

**Functions:**
- `_detect_silences` — L6425
- `_calibrate_boundaries` — L6460
- `_enforce_monotonic` — L6494
- `_manual_override_segments` — L6506
- `_calc_sentence_boundaries` — L6527
- `step345_timeline` — L6638
- `_analyze_bgm_energy_cuts` — L6697
- `_snap_bgm_only_boundaries` — L6760
- `step345_bgm_only_timeline` — L6820

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L6969 – L12604** (5636 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L8198-8248 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L8249-9107 (859 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L9108-9595 (488 lines)
- _Speaker IP Card (2026-05-21)_ — L9596-11240 (1645 lines)
- _MTV：原创歌曲 + 主唱人物库 + WeryDance MV_ — L11241-12204 (964 lines)
- _B68 (2026-05-30) WERYDANCE 段长合规 gate_ — L12205-12437 (233 lines)
- _审批流程_ — L12438-12494 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L12495-12604 (110 lines)

**Top-level constants:**
- `_CORE_TERMS_STOP_WORDS` — L7371
- `CHARACTER_META_GRID_COSTUMES` — L8204
- `CHARACTER_META_GRID_POSES` — L8205
- `CHARACTER_META_GRID_SCENES` — L8206
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L8209
- `_SFX_TYPE_ENUM` — L8577
- `_SFX_INTENSITY_ENUM` — L8582
- `_SFX_POSITION_ENUM` — L8583
- `_GRAIN_LEVEL_ENUM` — L8728
- `_CUSTOM_STYLE_BANNED_NAMES` — L9163
- `_DUANGE_XING_TEXT` — L11242

**Functions:**
- `_extract_img_url` — L6970
- `_extract_img_urls` — L6992
- `_extract_video_url` — L7025
- `_count_bands` — L7050
- `_detect_contact_sheet_like_image` — L7062
- `_file_sha256` — L7123
- `_load_upload_cache` — L7136
- `_save_upload_cache` — L7145
- `_cached_upload_url` — L7153
- `_store_upload_url` — L7170
- `_guess_upload_mime` — L7180
- `_upload_to_weryai` — L7203
- `_send_for_approval` — L7264
- `_wait_approval` — L7328
- `_render_still_segment` — L7340
- `_extract_core_terms` — L7377
- `_scene_text_visual_alignment` — L7396
- `_write_text_visual_alignment_qa` — L7417
- `_scene_motion_action_plan` — L7440
- `_ensure_motion_action_plan` — L7494
- `_motion_action_block` — L7503
- `_motion_plan_for_qa` — L7531
- `_write_motion_action_plan_qa` — L7541
- `_write_motion_bridge_refs_qa` — L7571
- `_motion_bridge_ref_prompt` — L7578
- `generate_motion_bridge_refs_gpt_image2` — L7611
- `generate_image` — L7726
- `generate_storyboard_images_gpt_image2` — L7773
- `_storyboard_grid_aspect` — L7959
- `_storyboard_grid_cols_rows` — L7966
- `_storyboard_grid_prompt` — L7988
- `_storyboard_grid_prompt_limit` — L8046
- `_is_prompt_limit_response` — L8050
- `_production_storyboard_prompt` — L8056
- `_write_production_storyboard_page_qa` — L8090
- `_character_sheet_prompt` — L8100
- `_is_audit_blocked` — L8226
- `_paraphrase_sensitive_dialogue` — L8239
- `_topic_cache_dir` — L8253
- `_topic_cache_path` — L8259
- `_load_topic_decomposition_cache` — L8272
- `_save_topic_decomposition_cache` — L8290
- `_briefs_dir` — L8327
- `_brief_path` — L8333
- `_empty_brief` — L8338
- `_deep_merge_brief_skeleton` — L8378
- `_load_brief` — L8392
- `_save_brief` — L8416
- `_brief_get` — L8435
- `_brief_field` — L8447
- `_brief_set` — L8458
- `_brief_claim` — L8474
- `_brief_agent_status` — L8517
- `_brief_from_topic_decomposition` — L8530
- `_rule_based_sfx_design` — L8586
- `_validate_sfx_entry` — L8637
- `_audio_director_design` — L8675
- `_hex_color_validate` — L8731
- `_rule_based_art_design` — L8743
- `_validate_art_design` — L8824
- `_art_director_design` — L8862
- `_coordinator_review` — L8884
- `_llm_topic_decomposition` — L8985
- `_validate_custom_visual_style` — L9170
- `_resolve_route_style` — L9192
- `_director_route_block` — L9217
- `_llm_infer_meta_grid_template` — L9284
- `_resolve_meta_grid_template` — L9341
- `_infer_meta_grid_costume` — L9384
- `_infer_meta_grid_pose` — L9433
- `_adsd_meta_grid_call_prompt` — L9480
- `_meta_grid_panel_index` — L9522
- `_migrate_speaker_ip` — L9602
- `_speaker_ips_dir` — L9627
- `_list_speaker_ips` — L9634
- `_match_speaker_ip` — L9648
- `_build_speaker_ip_context_for_script` — L9668
- `_ip_usage_stats` — L9724
- `_recommend_related_ips` — L9742
- `_save_speaker_ip` — L9767
- `_record_speaker_usage_history` — L9776
- `_format_speaker_usage_history_for_prompt` — L9823
- `_llm_infer_ip_skeleton` — L9841
- `_llm_pick_voice_asset_for_ip` — L9886
- `_auto_incubate_missing_ips` — L9935
- `_character_meta_grid_cache_dir` — L10019
- `_character_meta_grid_cache_path` — L10027
- `_character_meta_grid_cache_legacy_path` — L10035
- `_character_meta_grid_path` — L10042
- `generate_character_meta_grid_gpt_image2` — L10048
- `_generate_all_character_meta_grids` — L10220
- `_write_character_sheet_qa` — L10261
- `generate_character_sheet_gpt_image2` — L10271
- `generate_production_storyboard_page_gpt_image2` — L10371
- `_qa_clean_storyboard_panel` — L10434
- `_crop_storyboard_grid_panels` — L10615
- `generate_storyboard_grid_gpt_image2` — L10662
- `_gpt_image2_direct_annotated_aspect` — L10894
- `_gpt_image2_direct_annotated_prompt` — L10901
- `generate_gpt_image2_direct_annotated_storyboards` — L10931
- `_llm_bgm_description` — L11032
- `_bgm_contains_vocals` — L11071
- `generate_bgm` — L11105
- `_arg_value` — L11254
- `_infer_mtv_singer` — L11263
- `_ensure_mtv_singer_ip` — L11277
- `_mtv_source_lyrics` — L11332
- `_mtv_build_plan` — L11344
- `_generate_mtv_song` — L11429
- `_trim_mtv_song` — L11468
- `_mtv_generate_visual_segments` — L11481
- `_mtv_ass_time` — L11695
- `_mtv_ass_escape` — L11704
- `_mtv_wrap_lyric` — L11710
- `_mtv_vocal_span_from_asr` — L11735
- `_mtv_split_lyric_clauses` — L11779
- `_mtv_split_lyric_phrases` — L11791
- `_mtv_norm_zh` — L11804
- `_mtv_best_phrase_offset` — L11808
- `_mtv_asr_phrase_records` — L11828
- `_mtv_alignment_from_script` — L11871
- `_mtv_split_span` — L11924
- `_mtv_song_slice` — L11934
- `_mtv_normalize_segment_duration` — L11942
- `_mtv_static_fallback_segment` — L11978
- `_mtv_lip_sync_segment` — L12000
- `_write_mtv_subtitles` — L12068
- `_mtv_concat_and_render` — L12140
- `run_mtv_pipeline` — L12190
- `_b68_clamp_scene_durations_to_werydance_bounds` — L12213
- `step6_parallel` — L12273

---

### 第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）
Range: **L12605 – L18073** (5469 lines)

**Sub-sections:**
- _B92 (2026-06-05): 轨迹标记运镜 (Seedance 红线技法)_ — L13749-16208 (2460 lines)
- _PR-A (2026-05-27): merged_a 合并跑 helpers_ — L16209-17808 (1600 lines)
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L17809-17851 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L17852-17889 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回时间轴锚定音轨_ — L17890-18028 (139 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L18029-18073 (45 lines)

**Top-level constants:**
- `_PR3B1_SHOT_TYPE_ENUM` — L13075
- `_PR3B1_CAMERA_ANGLE_ENUM` — L13079
- `_PR3B1_LIGHTING_ENUM` — L13084
- `_PR3B1_CAMERA_MOTION_ENUM` — L13089
- `_SEEDANCE_CAMERA_GRAMMAR` — L13113
- `_DOLLY_ZOOM_EMOTIONS` — L13126
- `_GRAND_EMOTIONS` — L13131
- `_SEEDANCE_CAMERA_COMPACT` — L13136
- `_B92_HIDE_NEGATIVES` — L13752
- `_EMOTION_NARRATION_STYLE_MAP` — L14399

**Functions:**
- `_generate_motion_prompts` — L12608
- `_motion_tasks_file` — L12675
- `_motion_qa_file` — L12679
- `_append_motion_qa` — L12683
- `_finalize_motion_qa` — L12707
- `_lip_sync_tasks_file` — L12791
- `_load_motion_tasks` — L12795
- `_save_motion_task` — L12805
- `_remove_motion_task` — L12813
- `_load_lip_sync_tasks` — L12820
- `_save_lip_sync_task` — L12830
- `_remove_lip_sync_task` — L12837
- `_video_visual_motion_qa` — L12844
- `_motion_output_qa` — L12916
- `_has_audio_stream` — L12961
- `_normalize_motion_video` — L12972
- `_motion_poll_and_download` — L13022
- `_validate_enum_field` — L13095
- `_seedance_camera_directive` — L13151
- `_build_motion_video_prompt` — L13171
- `_short_board_text` — L13227
- `_wrap_board_text` — L13234
- `_storyboard_font` — L13265
- `_draw_storyboard_arrow` — L13280
- `_build_annotated_storyboard_reference` — L13294
- `_plain_caption_text` — L13395
- `_werydance_caption_request` — L13403
- `_werydance_caption_instruction` — L13430
- `_werydance_negative_prompt` — L13442
- `_motion_reference_prompt` — L13464
- `_motion_audio_dub_prompt` — L13487
- `_motion_audio_dub_poll_and_download` — L13521
- `_try_motion_audio_dub_video` — L13586
- `_b92_enabled` — L13758
- `_b92_propose_path` — L13762
- `_b92_draw_path` — L13803
- `_b92_trim_lead_frames` — L13832
- `_b92_trajectory_prompt` — L13861
- `_b92_apply_trajectory` — L13876
- `_b92_preplan_paths` — L13897
- `_try_motion_reference_video` — L13921
- `_motion_one_scene` — L14052
- `_grid_multiref_tasks_file` — L14182
- `_previs_page_tasks_file` — L14186
- `_load_grid_multiref_tasks` — L14190
- `_load_previs_page_tasks` — L14200
- `_save_grid_multiref_task` — L14210
- `_save_previs_page_task` — L14217
- `_remove_grid_multiref_task` — L14224
- `_remove_previs_page_task` — L14231
- `_poll_video_task_download` — L14238
- `_grid_multiref_group_size` — L14287
- `_grid_multiref_adaptive_group_size` — L14297
- `_grid_multiref_duration` — L14321
- `_grid_multiref_tts_buffer_factor` — L14359
- `_grid_multiref_tts_duration_buffered` — L14373
- `_grid_multiref_segment_max_stretch` — L14389
- `_voice_clone_emotion_style` — L14423
- `_grid_multiref_prompt` — L14446
- `_write_grid_multiref_motion_qa` — L14526
- `_write_previs_page_motion_qa` — L14536
- `_write_storyboard_trailer_qa` — L14546
- `_write_character_trailer_qa` — L14556
- `_write_grid_multiref_segment_qa` — L14566
- `_motion_compare_record` — L14576
- `_write_storyboard_motion_compare_qa` — L14598
- `_scene_segment_duration` — L14634
- `_apply_grid_multiref_segments` — L14653
- `_previs_page_duration` — L14858
- `_previs_page_group_prompt` — L14869
- `_previs_page_groups` — L14895
- `_storyboard_trailer_duration` — L14910
- `_storyboard_trailer_prompt` — L14920
- `_character_trailer_max_shots` — L14948
- `_character_trailer_shot_duration` — L14956
- `_character_trailer_prompt` — L14972
- `_concat_character_trailer_segments` — L14987
- `_generate_character_trailer_motion` — L15026
- `_multi_trailer_prompt_for_group` — L15134
- `_generate_multi_trailer_segments` — L15157
- `_generate_storyboard_trailer_motion` — L15268
- `_generate_previs_page_motion_segments` — L15343
- `_generate_grid_multiref_motion_segments` — L15455
- `_grid_multiref_concat_groups` — L15765
- `_grid_multiref_concat_groups_partial` — L15782
- `_grid_multiref_concat_paths` — L15800
- `_lip_sync_slot_duration` — L15842
- `_adsd_lip_sync_prompt` — L15849
- `_adsd_broll_motion_prompt` — L15895
- `_adsd_action_b_motion_prompt` — L15943
- `_adsd_silent_b_motion_prompt` — L15989
- `_adsd_narrated_b_audio_dub_prompt` — L16030
- `_adsd_almighty_audio_dub_prompt` — L16074
- `_postprocess_lip_sync_segment` — L16115
- `_detect_audio_leading_silence` — L16187
- `_concat_audio_files_for_group` — L16212
- `_split_lip_sync_raw_by_durations` — L16235
- `_postprocess_audio_dub_segment` — L16270
- `_lips_change_repair_segment` — L16398
- `_load_lips_change_requested_turns` — L16483
- `_parse_turn_set` — L16500
- `_load_motion_voice_repair_turns` — L16522
- `_voice_assets_file` — L16534
- `_load_voice_assets` — L16541
- `_build_combined_voice_reference` — L16560
- `_select_voice_asset_reference` — L16602
- `_lip_sync_poll_download_and_process` — L16678
- `_lip_sync_one_group` — L16746
- `_lip_sync_one_scene` — L16954
- `step66_adsd_lip_sync` — L17281
- `step65_motion` — L17627
- `step65_grid_multiref_motion_qa` — L17781
- `_sanitize_scene_for_state` — L17810
- `_save_pipeline_state` — L17829
- `_retime_after_audio_dub` — L17853
- `_build_voice_clone_hybrid_audio` — L17891
- `_build_dynamic_bgm` — L18030

---

### 第七步：拼接视频轨
Range: **L18074 – L18409** (336 lines)

**Functions:**
- `_rescue_motion_image_to_video` — L18075
- `_rescue_motion_text_to_video` — L18110
- `step7_concat` — L18141

---

### 第八步：生成 ASS 字幕
Range: **L18410 – L19368** (959 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L18689-19368 (680 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L18411
- `_word_timings_for_subtitle_align` — L18437
- `_align_segments_via_asr` — L18478
- `_b61_1_asr_turn_boundaries` — L18521
- `step8_subtitles` — L18583
- `_read_output_json` — L19089
- `_qa_file_pass` — L19100
- `_ass_has_dialogue` — L19107
- `_write_adsd_delivery_qa` — L19117
- `_write_bgm_only_qa` — L19257

---

### 第九步：最终合成
Range: **L19369 – L19659** (291 lines)

**Functions:**
- `step9_render` — L19370

---

### 第十步：推送 Telegram
Range: **L19660 – L21542** (1883 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L20766-20875 (110 lines)
- _B70 (2026-05-30) TG oversize policy helpers_ — L20876-21347 (472 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L21348-21352 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L21353-21417 (65 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L21418-21464 (47 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L21465-21542 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L20029
- `PANTONE_FALLBACK` — L20056
- `FESTIVAL_DATE_TAG` — L20170

**Functions:**
- `_generate_caption` — L19661
- `_overlay_title_on_cover` — L19899
- `_prepare_tg_photo` — L20009
- `_get_pantone_for_date` — L20059
- `_llm_bottom_note` — L20084
- `_get_bottom_note` — L20114
- `_get_date_tag` — L20192
- `_shrink_to_b64` — L20214
- `_llm_check_scenes_anomalies` — L20230
- `_llm_check_cover_unique` — L20283
- `_llm_check_cover_quality` — L20313
- `_try_almanac_cover` — L20355
- `_generate_cover_image` — L20526
- `_async_kickoff_cover_caption` — L20773
- `_await_async_cover_caption` — L20849
- `_b70_env_float` — L20879
- `_b70_split_and_deliver` — L20894
- `_b70_send_document_first` — L21007
- `step10_deliver` — L21044

---

### 主流程
Range: **L21543 – L21797** (255 lines)

**Functions:**
- `_print_execution_plan` — L21544
- `_write_run_timings` — L21603
- `main` — L21632

---
