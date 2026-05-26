# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (16895 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-1992 (1871 lines · 58 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L1993-4153 (2161 lines · 29 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L4154-5257 (1104 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L5258-5809 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L5810-9549 (3740 lines · 80 fn · 6 sub)
- [`第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）`](#第-6-5-步-动态化-hads-vads-默认-on---no-motion-关) — L9550-13832 (4283 lines · 100 fn · 4 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L13833-14064 (232 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L14065-14856 (792 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L14857-15102 (246 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L15103-16717 (1615 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L16718-16895 (178 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L1992** (1871 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L308-437 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L438-1120 (683 lines)
- _工具函数_ — L1121-1470 (350 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1471-1992 (522 lines)

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
- `_PODCAST_TO_VOICE_ASSET_MAP` — L806
- `_VOICE_ASSET_FORBIDDEN_FLAGS` — L824
- `VOICE_ASSET_AUDIO_DUB_EXPERIMENT` — L862
- `VOICE_ASSET_AUDIO_DUB_PARTIAL_OK` — L870
- `MOTION_VISUAL_QA` — L874
- `MOTION_VOICE_REPAIR` — L882
- `MOTION_VOICE_STRICT_LOCK` — L887
- `WERYDANCE_CAPTIONS` — L892
- `ADSD_ONSITE_POV_MODE` — L904
- `ADSD_LIPS_CHANGE_REPAIR` — L909
- `ADSD_LIPS_CHANGE_ALL` — L914
- `ADS_REPORTER_MODE` — L925
- `ADS_STORYBOARD_FLOW_DEFAULT` — L942
- `ADS_RETENTION_MODE` — L955
- `ADSD_MODE_NAME` — L961
- `EMOTION_STYLE` — L1100
- `EMOTION_STYLE_BRIGHT` — L1112
- `_TG_DASHBOARD_STAGES` — L1134
- `_TG_NOISY_PATTERNS` — L1149
- `_TG_IMMEDIATE_PATTERNS` — L1167
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1400
- `_TOPIC_MODIFIERS` — L1824
- `_TONE_PANTONE_OVERRIDE` — L1841

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
- `_apply_llm_voice_assignment` — L680
- `_voice_asset_is_speech_safe` — L831
- `_podcast_id_to_voice_asset` — L837
- `log` — L1122
- `_tg_send_raw` — L1190
- `_tg_matches` — L1206
- `_tg_summarize` — L1210
- `_tg_dashboard_stage_for` — L1217
- `_tg_progress_bar` — L1225
- `_tg_dashboard_text` — L1231
- `_tg_dashboard_update` — L1249
- `_tg_maybe_digest` — L1286
- `tg` — L1301
- `_wait_image_submit_slot` — L1350
- `_wait_motion_submit_slot` — L1363
- `_is_rate_limited_error` — L1376
- `_is_rate_limited_response` — L1386
- `_inject_image2_quality_suffix` — L1408
- `submit_text_to_image` — L1422
- `req_post` — L1452
- `req_get` — L1466
- `_tg_probe_send` — L1474
- `_tg_probe_delete` — L1494
- `_tg_upload_with_probe_gap` — L1507
- `poll` — L1547
- `poll_podcast` — L1572
- `poll_task_status` — L1594
- `poll_storyboard_task` — L1616
- `chat` — L1642
- `pick_image_model` — L1670
- `detect_topic_meta` — L1695
- `_topic_culture_guard` — L1745
- `_write_cultural_visual_qa` — L1771
- `is_1919_global_topic` — L1818
- `_strip_topic_modifiers` — L1829
- `apply_1919_global_guardrails` — L1847
- `build_1919_global_cover_prompt` — L1876
- `build_shot_blueprint` — L1905
- `ffprobe_duration` — L1931
- `ffprobe_video_size` — L1942
- `_video_decode_probe` — L1963
- `ffmpeg` — L1981

---

### 第一步：双导演生成剧本
Range: **L1993 – L4153** (2161 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L3425-4153 (729 lines)

**Functions:**
- `_extract_json_array` — L1994
- `_extract_json_object` — L2004
- `_voice_for_speaker` — L2014
- `_adsd_gender_from_voice` — L2050
- `_adsd_infer_gender_from_speaker` — L2058
- `_adsd_gender_lock_phrase` — L2067
- `_adsd_visual_subject_has_gender_conflict` — L2082
- `_adsd_default_roles` — L2094
- `_adsd_allows_media_role` — L2099
- `_adsd_role_candidates` — L2107
- `_adsd_dialogue_shape` — L2130
- `_finalize_adsd_turns` — L2139
- `_parse_adsd_override_turns` — L2173
- `_parse_timecode_seconds` — L2264
- `_clean_override_line_text` — L2273
- `_parse_override_script_text` — L2279
- `_adsd_pov_contract` — L2313
- `_load_audit_blacklist_block` — L2326
- `_generate_adsd_dialogue_turns` — L2364
- `_broll_rhythm_reviewer` — L2787
- `_sweep_speaker_field` — L2894
- `_should_run_immersion_qa` — L2954
- `_adsd_immersion_qa_rewrite_turns` — L2977
- `_adsd_visual_contract` — L3041
- `_parse_risk_score` — L3093
- `_check_high_risk_hard_abort` — L3122
- `_maybe_neutralize_topic` — L3149
- `step1_script` — L3188
- `_write_ads_retention_qa` — L4097

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L4154 – L5257** (1104 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L4229
- `_ADSD_POLICY_REWRITE_TERMS` — L4235
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L4326

**Functions:**
- `_openai_tts_fallback` — L4155
- `_edge_tts_fallback` — L4201
- `_sanitize_for_external_api` — L4244
- `_is_content_policy_error` — L4253
- `_rewrite_adsd_tts_text_for_policy` — L4267
- `_record_adsd_tts_rewrite` — L4307
- `_build_silence_mp3` — L4332
- `_audio_duration_seconds` — L4345
- `_text_to_audio_master_voice_timed` — L4357
- `_text_to_audio_master_voice` — L4482
- `step2_master_voice` — L4585
- `_tts_turn_to_audio` — L4713
- `_asr_verify_dialogue_audio` — L4777
- `_asr_verify_dialogue_turns` — L4839
- `_normalize_cn_number_token` — L4881
- `_compact_zh_text` — L4903
- `_write_adsd_asr_text_qa` — L4910
- `_write_adsd_speaker_focus_qa` — L4949
- `_write_adsd_gender_voice_qa` — L5009
- `step2_dialogue_voice` — L5062

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L5258 – L5809** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L5265-5387 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L5388-5422 (35 lines)
- _第二层：字符数插值_ — L5423-5447 (25 lines)
- _第三层：silencedetect 物理校准_ — L5448-5809 (362 lines)

**Functions:**
- `_detect_silences` — L5266
- `_calibrate_boundaries` — L5301
- `_enforce_monotonic` — L5335
- `_manual_override_segments` — L5347
- `_calc_sentence_boundaries` — L5368
- `step345_timeline` — L5479
- `_analyze_bgm_energy_cuts` — L5538
- `_snap_bgm_only_boundaries` — L5601
- `step345_bgm_only_timeline` — L5661

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L5810 – L9549** (3740 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L6999-7049 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L7050-7190 (141 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L7191-7625 (435 lines)
- _Speaker IP Card (2026-05-21)_ — L7626-9382 (1757 lines)
- _审批流程_ — L9383-9439 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L9440-9549 (110 lines)

**Top-level constants:**
- `CHARACTER_META_GRID_COSTUMES` — L7005
- `CHARACTER_META_GRID_POSES` — L7006
- `CHARACTER_META_GRID_SCENES` — L7007
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L7010

**Functions:**
- `_extract_img_url` — L5811
- `_extract_img_urls` — L5833
- `_extract_video_url` — L5866
- `_count_bands` — L5891
- `_detect_contact_sheet_like_image` — L5903
- `_file_sha256` — L5964
- `_load_upload_cache` — L5977
- `_save_upload_cache` — L5986
- `_cached_upload_url` — L5994
- `_store_upload_url` — L6011
- `_guess_upload_mime` — L6021
- `_upload_to_weryai` — L6044
- `_send_for_approval` — L6098
- `_wait_approval` — L6162
- `_render_still_segment` — L6174
- `_scene_text_visual_alignment` — L6205
- `_write_text_visual_alignment_qa` — L6241
- `_scene_motion_action_plan` — L6264
- `_ensure_motion_action_plan` — L6318
- `_motion_action_block` — L6327
- `_motion_plan_for_qa` — L6355
- `_write_motion_action_plan_qa` — L6365
- `_write_motion_bridge_refs_qa` — L6395
- `_motion_bridge_ref_prompt` — L6402
- `generate_motion_bridge_refs_gpt_image2` — L6435
- `generate_image` — L6548
- `generate_storyboard_images_gpt_image2` — L6595
- `_storyboard_grid_aspect` — L6780
- `_storyboard_grid_cols_rows` — L6787
- `_storyboard_grid_prompt` — L6809
- `_storyboard_grid_prompt_limit` — L6847
- `_is_prompt_limit_response` — L6851
- `_production_storyboard_prompt` — L6857
- `_write_production_storyboard_page_qa` — L6891
- `_character_sheet_prompt` — L6901
- `_is_audit_blocked` — L7027
- `_paraphrase_sensitive_dialogue` — L7040
- `_topic_cache_dir` — L7054
- `_topic_cache_path` — L7060
- `_load_topic_decomposition_cache` — L7073
- `_save_topic_decomposition_cache` — L7091
- `_llm_topic_decomposition` — L7097
- `_director_route_block` — L7244
- `_llm_infer_meta_grid_template` — L7314
- `_resolve_meta_grid_template` — L7371
- `_infer_meta_grid_costume` — L7414
- `_infer_meta_grid_pose` — L7463
- `_adsd_meta_grid_call_prompt` — L7510
- `_meta_grid_panel_index` — L7552
- `_migrate_speaker_ip` — L7632
- `_speaker_ips_dir` — L7657
- `_list_speaker_ips` — L7664
- `_match_speaker_ip` — L7678
- `_build_speaker_ip_context_for_script` — L7698
- `_ip_usage_stats` — L7754
- `_recommend_related_ips` — L7772
- `_save_speaker_ip` — L7797
- `_record_speaker_usage_history` — L7806
- `_format_speaker_usage_history_for_prompt` — L7853
- `_llm_infer_ip_skeleton` — L7871
- `_llm_pick_voice_asset_for_ip` — L7916
- `_auto_incubate_missing_ips` — L7964
- `_character_meta_grid_cache_dir` — L8048
- `_character_meta_grid_cache_path` — L8056
- `_character_meta_grid_path` — L8064
- `generate_character_meta_grid_gpt_image2` — L8070
- `_generate_all_character_meta_grids` — L8228
- `_write_character_sheet_qa` — L8269
- `generate_character_sheet_gpt_image2` — L8279
- `generate_production_storyboard_page_gpt_image2` — L8379
- `_qa_clean_storyboard_panel` — L8442
- `_crop_storyboard_grid_panels` — L8623
- `generate_storyboard_grid_gpt_image2` — L8670
- `_gpt_image2_direct_annotated_aspect` — L8901
- `_gpt_image2_direct_annotated_prompt` — L8908
- `generate_gpt_image2_direct_annotated_storyboards` — L8938
- `_llm_bgm_description` — L9039
- `_bgm_contains_vocals` — L9078
- `generate_bgm` — L9112
- `step6_parallel` — L9229

---

### 第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）
Range: **L9550 – L13832** (4283 lines)

**Sub-sections:**
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L13569-13611 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L13612-13649 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回主音轨_ — L13650-13787 (138 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L13788-13832 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L9553
- `_motion_tasks_file` — L9620
- `_motion_qa_file` — L9624
- `_append_motion_qa` — L9628
- `_finalize_motion_qa` — L9652
- `_lip_sync_tasks_file` — L9736
- `_load_motion_tasks` — L9740
- `_save_motion_task` — L9750
- `_remove_motion_task` — L9758
- `_load_lip_sync_tasks` — L9765
- `_save_lip_sync_task` — L9775
- `_remove_lip_sync_task` — L9782
- `_video_visual_motion_qa` — L9789
- `_motion_output_qa` — L9861
- `_has_audio_stream` — L9906
- `_normalize_motion_video` — L9917
- `_motion_poll_and_download` — L9967
- `_build_motion_video_prompt` — L10018
- `_short_board_text` — L10048
- `_wrap_board_text` — L10055
- `_storyboard_font` — L10086
- `_draw_storyboard_arrow` — L10101
- `_build_annotated_storyboard_reference` — L10115
- `_plain_caption_text` — L10216
- `_werydance_caption_request` — L10224
- `_werydance_caption_instruction` — L10251
- `_werydance_negative_prompt` — L10263
- `_motion_reference_prompt` — L10281
- `_motion_audio_dub_prompt` — L10304
- `_motion_audio_dub_poll_and_download` — L10338
- `_try_motion_audio_dub_video` — L10403
- `_try_motion_reference_video` — L10538
- `_motion_one_scene` — L10654
- `_grid_multiref_tasks_file` — L10783
- `_previs_page_tasks_file` — L10787
- `_load_grid_multiref_tasks` — L10791
- `_load_previs_page_tasks` — L10801
- `_save_grid_multiref_task` — L10811
- `_save_previs_page_task` — L10818
- `_remove_grid_multiref_task` — L10825
- `_remove_previs_page_task` — L10832
- `_poll_video_task_download` — L10839
- `_grid_multiref_group_size` — L10888
- `_grid_multiref_duration` — L10896
- `_grid_multiref_segment_max_stretch` — L10912
- `_grid_multiref_prompt` — L10920
- `_write_grid_multiref_motion_qa` — L10968
- `_write_previs_page_motion_qa` — L10978
- `_write_storyboard_trailer_qa` — L10988
- `_write_character_trailer_qa` — L10998
- `_write_grid_multiref_segment_qa` — L11008
- `_motion_compare_record` — L11018
- `_write_storyboard_motion_compare_qa` — L11040
- `_scene_segment_duration` — L11076
- `_apply_grid_multiref_segments` — L11095
- `_previs_page_duration` — L11289
- `_previs_page_group_prompt` — L11299
- `_previs_page_groups` — L11325
- `_storyboard_trailer_duration` — L11340
- `_storyboard_trailer_prompt` — L11350
- `_character_trailer_max_shots` — L11378
- `_character_trailer_shot_duration` — L11386
- `_character_trailer_prompt` — L11400
- `_concat_character_trailer_segments` — L11415
- `_generate_character_trailer_motion` — L11454
- `_multi_trailer_prompt_for_group` — L11562
- `_generate_multi_trailer_segments` — L11585
- `_generate_storyboard_trailer_motion` — L11696
- `_generate_previs_page_motion_segments` — L11771
- `_generate_grid_multiref_motion_segments` — L11883
- `_grid_multiref_concat_groups` — L12053
- `_grid_multiref_concat_groups_partial` — L12070
- `_grid_multiref_concat_paths` — L12088
- `_lip_sync_slot_duration` — L12119
- `_adsd_lip_sync_prompt` — L12126
- `_adsd_broll_motion_prompt` — L12172
- `_adsd_action_b_motion_prompt` — L12214
- `_adsd_silent_b_motion_prompt` — L12260
- `_adsd_narrated_b_audio_dub_prompt` — L12295
- `_adsd_almighty_audio_dub_prompt` — L12339
- `_postprocess_lip_sync_segment` — L12380
- `_detect_audio_leading_silence` — L12448
- `_postprocess_audio_dub_segment` — L12470
- `_lips_change_repair_segment` — L12581
- `_load_lips_change_requested_turns` — L12666
- `_parse_turn_set` — L12683
- `_load_motion_voice_repair_turns` — L12705
- `_voice_assets_file` — L12717
- `_load_voice_assets` — L12724
- `_select_voice_asset_reference` — L12743
- `_lip_sync_poll_download_and_process` — L12809
- `_lip_sync_one_scene` — L12877
- `step66_adsd_lip_sync` — L13201
- `step65_motion` — L13459
- `step65_grid_multiref_motion_qa` — L13541
- `_sanitize_scene_for_state` — L13570
- `_save_pipeline_state` — L13589
- `_retime_after_audio_dub` — L13613
- `_build_voice_clone_hybrid_audio` — L13651
- `_build_dynamic_bgm` — L13789

---

### 第七步：拼接视频轨
Range: **L13833 – L14064** (232 lines)

**Functions:**
- `step7_concat` — L13834

---

### 第八步：生成 ASS 字幕
Range: **L14065 – L14856** (792 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L14188-14856 (669 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L14066
- `_word_timings_for_subtitle_align` — L14092
- `_align_segments_via_asr` — L14133
- `step8_subtitles` — L14176
- `_read_output_json` — L14588
- `_qa_file_pass` — L14599
- `_ass_has_dialogue` — L14606
- `_write_adsd_delivery_qa` — L14616
- `_write_bgm_only_qa` — L14745

---

### 第九步：最终合成
Range: **L14857 – L15102** (246 lines)

**Functions:**
- `step9_render` — L14858

---

### 第十步：推送 Telegram
Range: **L15103 – L16717** (1615 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L16203-16524 (322 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L16525-16529 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L16530-16593 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L16594-16639 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L16640-16717 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L15472
- `PANTONE_FALLBACK` — L15499
- `FESTIVAL_DATE_TAG` — L15612

**Functions:**
- `_generate_caption` — L15104
- `_overlay_title_on_cover` — L15342
- `_prepare_tg_photo` — L15452
- `_get_pantone_for_date` — L15502
- `_llm_bottom_note` — L15527
- `_get_bottom_note` — L15556
- `_get_date_tag` — L15634
- `_shrink_to_b64` — L15656
- `_llm_check_scenes_anomalies` — L15672
- `_llm_check_cover_unique` — L15725
- `_llm_check_cover_quality` — L15755
- `_try_almanac_cover` — L15797
- `_generate_cover_image` — L15968
- `_async_kickoff_cover_caption` — L16210
- `_await_async_cover_caption` — L16240
- `step10_deliver` — L16264

---

### 主流程
Range: **L16718 – L16895** (178 lines)

**Functions:**
- `_print_execution_plan` — L16719
- `main` — L16767

---
