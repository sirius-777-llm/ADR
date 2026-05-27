# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (17057 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-2013 (1892 lines · 59 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L2014-4247 (2234 lines · 30 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L4248-5369 (1122 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L5370-5921 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L5922-9692 (3771 lines · 82 fn · 6 sub)
- [`第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）`](#第-6-5-步-动态化-hads-vads-默认-on---no-motion-关) — L9693-13983 (4291 lines · 100 fn · 4 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L13984-14215 (232 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L14216-15018 (803 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L15019-15264 (246 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L15265-16879 (1615 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L16880-17057 (178 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L2013** (1892 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L308-437 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L438-1125 (688 lines)
- _工具函数_ — L1126-1475 (350 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1476-2013 (538 lines)

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
- `_LLM_TIER` — L1649
- `_TOPIC_MODIFIERS` — L1845
- `_TONE_PANTONE_OVERRIDE` — L1862

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
- `tier_chat` — L1657
- `chat` — L1663
- `pick_image_model` — L1691
- `detect_topic_meta` — L1716
- `_topic_culture_guard` — L1766
- `_write_cultural_visual_qa` — L1792
- `is_1919_global_topic` — L1839
- `_strip_topic_modifiers` — L1850
- `apply_1919_global_guardrails` — L1868
- `build_1919_global_cover_prompt` — L1897
- `build_shot_blueprint` — L1926
- `ffprobe_duration` — L1952
- `ffprobe_video_size` — L1963
- `_video_decode_probe` — L1984
- `ffmpeg` — L2002

---

### 第一步：双导演生成剧本
Range: **L2014 – L4247** (2234 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L3476-4247 (772 lines)

**Top-level constants:**
- `_ENSEMBLE_CAP_BY_ROUTE` — L2162

**Functions:**
- `_extract_json_array` — L2015
- `_extract_json_object` — L2025
- `_voice_for_speaker` — L2035
- `_adsd_gender_from_voice` — L2071
- `_adsd_infer_gender_from_speaker` — L2079
- `_adsd_gender_lock_phrase` — L2088
- `_adsd_visual_subject_has_gender_conflict` — L2103
- `_adsd_default_roles` — L2115
- `_adsd_allows_media_role` — L2120
- `_adsd_role_candidates` — L2128
- `_adsd_dialogue_shape` — L2151
- `_ensemble_speaker_cap` — L2173
- `_finalize_adsd_turns` — L2186
- `_parse_adsd_override_turns` — L2220
- `_parse_timecode_seconds` — L2311
- `_clean_override_line_text` — L2320
- `_parse_override_script_text` — L2326
- `_adsd_pov_contract` — L2360
- `_load_audit_blacklist_block` — L2373
- `_generate_adsd_dialogue_turns` — L2411
- `_broll_rhythm_reviewer` — L2838
- `_sweep_speaker_field` — L2945
- `_should_run_immersion_qa` — L3005
- `_adsd_immersion_qa_rewrite_turns` — L3028
- `_adsd_visual_contract` — L3092
- `_parse_risk_score` — L3144
- `_check_high_risk_hard_abort` — L3173
- `_maybe_neutralize_topic` — L3200
- `step1_script` — L3239
- `_write_ads_retention_qa` — L4191

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L4248 – L5369** (1122 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L4323
- `_ADSD_POLICY_REWRITE_TERMS` — L4329
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L4420

**Functions:**
- `_openai_tts_fallback` — L4249
- `_edge_tts_fallback` — L4295
- `_sanitize_for_external_api` — L4338
- `_is_content_policy_error` — L4347
- `_rewrite_adsd_tts_text_for_policy` — L4361
- `_record_adsd_tts_rewrite` — L4401
- `_build_silence_mp3` — L4426
- `_audio_duration_seconds` — L4439
- `_text_to_audio_master_voice_timed` — L4451
- `_text_to_audio_master_voice` — L4576
- `step2_master_voice` — L4679
- `_tts_turn_to_audio` — L4807
- `_asr_verify_dialogue_audio` — L4871
- `_asr_verify_dialogue_turns` — L4933
- `_normalize_cn_number_token` — L4975
- `_compact_zh_text` — L4997
- `_write_adsd_asr_text_qa` — L5004
- `_write_adsd_speaker_focus_qa` — L5043
- `_write_adsd_gender_voice_qa` — L5103
- `step2_dialogue_voice` — L5156

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L5370 – L5921** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L5377-5499 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L5500-5534 (35 lines)
- _第二层：字符数插值_ — L5535-5559 (25 lines)
- _第三层：silencedetect 物理校准_ — L5560-5921 (362 lines)

**Functions:**
- `_detect_silences` — L5378
- `_calibrate_boundaries` — L5413
- `_enforce_monotonic` — L5447
- `_manual_override_segments` — L5459
- `_calc_sentence_boundaries` — L5480
- `step345_timeline` — L5591
- `_analyze_bgm_energy_cuts` — L5650
- `_snap_bgm_only_boundaries` — L5713
- `step345_bgm_only_timeline` — L5773

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L5922 – L9692** (3771 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L7121-7171 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L7172-7312 (141 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L7313-7747 (435 lines)
- _Speaker IP Card (2026-05-21)_ — L7748-9525 (1778 lines)
- _审批流程_ — L9526-9582 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L9583-9692 (110 lines)

**Top-level constants:**
- `_CORE_TERMS_STOP_WORDS` — L6317
- `CHARACTER_META_GRID_COSTUMES` — L7127
- `CHARACTER_META_GRID_POSES` — L7128
- `CHARACTER_META_GRID_SCENES` — L7129
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L7132

**Functions:**
- `_extract_img_url` — L5923
- `_extract_img_urls` — L5945
- `_extract_video_url` — L5978
- `_count_bands` — L6003
- `_detect_contact_sheet_like_image` — L6015
- `_file_sha256` — L6076
- `_load_upload_cache` — L6089
- `_save_upload_cache` — L6098
- `_cached_upload_url` — L6106
- `_store_upload_url` — L6123
- `_guess_upload_mime` — L6133
- `_upload_to_weryai` — L6156
- `_send_for_approval` — L6210
- `_wait_approval` — L6274
- `_render_still_segment` — L6286
- `_extract_core_terms` — L6323
- `_scene_text_visual_alignment` — L6342
- `_write_text_visual_alignment_qa` — L6363
- `_scene_motion_action_plan` — L6386
- `_ensure_motion_action_plan` — L6440
- `_motion_action_block` — L6449
- `_motion_plan_for_qa` — L6477
- `_write_motion_action_plan_qa` — L6487
- `_write_motion_bridge_refs_qa` — L6517
- `_motion_bridge_ref_prompt` — L6524
- `generate_motion_bridge_refs_gpt_image2` — L6557
- `generate_image` — L6670
- `generate_storyboard_images_gpt_image2` — L6717
- `_storyboard_grid_aspect` — L6902
- `_storyboard_grid_cols_rows` — L6909
- `_storyboard_grid_prompt` — L6931
- `_storyboard_grid_prompt_limit` — L6969
- `_is_prompt_limit_response` — L6973
- `_production_storyboard_prompt` — L6979
- `_write_production_storyboard_page_qa` — L7013
- `_character_sheet_prompt` — L7023
- `_is_audit_blocked` — L7149
- `_paraphrase_sensitive_dialogue` — L7162
- `_topic_cache_dir` — L7176
- `_topic_cache_path` — L7182
- `_load_topic_decomposition_cache` — L7195
- `_save_topic_decomposition_cache` — L7213
- `_llm_topic_decomposition` — L7219
- `_director_route_block` — L7366
- `_llm_infer_meta_grid_template` — L7436
- `_resolve_meta_grid_template` — L7493
- `_infer_meta_grid_costume` — L7536
- `_infer_meta_grid_pose` — L7585
- `_adsd_meta_grid_call_prompt` — L7632
- `_meta_grid_panel_index` — L7674
- `_migrate_speaker_ip` — L7754
- `_speaker_ips_dir` — L7779
- `_list_speaker_ips` — L7786
- `_match_speaker_ip` — L7800
- `_build_speaker_ip_context_for_script` — L7820
- `_ip_usage_stats` — L7876
- `_recommend_related_ips` — L7894
- `_save_speaker_ip` — L7919
- `_record_speaker_usage_history` — L7928
- `_format_speaker_usage_history_for_prompt` — L7975
- `_llm_infer_ip_skeleton` — L7993
- `_llm_pick_voice_asset_for_ip` — L8038
- `_auto_incubate_missing_ips` — L8086
- `_character_meta_grid_cache_dir` — L8170
- `_character_meta_grid_cache_path` — L8178
- `_character_meta_grid_cache_legacy_path` — L8186
- `_character_meta_grid_path` — L8193
- `generate_character_meta_grid_gpt_image2` — L8199
- `_generate_all_character_meta_grids` — L8371
- `_write_character_sheet_qa` — L8412
- `generate_character_sheet_gpt_image2` — L8422
- `generate_production_storyboard_page_gpt_image2` — L8522
- `_qa_clean_storyboard_panel` — L8585
- `_crop_storyboard_grid_panels` — L8766
- `generate_storyboard_grid_gpt_image2` — L8813
- `_gpt_image2_direct_annotated_aspect` — L9044
- `_gpt_image2_direct_annotated_prompt` — L9051
- `generate_gpt_image2_direct_annotated_storyboards` — L9081
- `_llm_bgm_description` — L9182
- `_bgm_contains_vocals` — L9221
- `generate_bgm` — L9255
- `step6_parallel` — L9372

---

### 第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）
Range: **L9693 – L13983** (4291 lines)

**Sub-sections:**
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L13720-13762 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L13763-13800 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回主音轨_ — L13801-13938 (138 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L13939-13983 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L9696
- `_motion_tasks_file` — L9763
- `_motion_qa_file` — L9767
- `_append_motion_qa` — L9771
- `_finalize_motion_qa` — L9795
- `_lip_sync_tasks_file` — L9879
- `_load_motion_tasks` — L9883
- `_save_motion_task` — L9893
- `_remove_motion_task` — L9901
- `_load_lip_sync_tasks` — L9908
- `_save_lip_sync_task` — L9918
- `_remove_lip_sync_task` — L9925
- `_video_visual_motion_qa` — L9932
- `_motion_output_qa` — L10004
- `_has_audio_stream` — L10049
- `_normalize_motion_video` — L10060
- `_motion_poll_and_download` — L10110
- `_build_motion_video_prompt` — L10161
- `_short_board_text` — L10191
- `_wrap_board_text` — L10198
- `_storyboard_font` — L10229
- `_draw_storyboard_arrow` — L10244
- `_build_annotated_storyboard_reference` — L10258
- `_plain_caption_text` — L10359
- `_werydance_caption_request` — L10367
- `_werydance_caption_instruction` — L10394
- `_werydance_negative_prompt` — L10406
- `_motion_reference_prompt` — L10424
- `_motion_audio_dub_prompt` — L10447
- `_motion_audio_dub_poll_and_download` — L10481
- `_try_motion_audio_dub_video` — L10546
- `_try_motion_reference_video` — L10681
- `_motion_one_scene` — L10797
- `_grid_multiref_tasks_file` — L10926
- `_previs_page_tasks_file` — L10930
- `_load_grid_multiref_tasks` — L10934
- `_load_previs_page_tasks` — L10944
- `_save_grid_multiref_task` — L10954
- `_save_previs_page_task` — L10961
- `_remove_grid_multiref_task` — L10968
- `_remove_previs_page_task` — L10975
- `_poll_video_task_download` — L10982
- `_grid_multiref_group_size` — L11031
- `_grid_multiref_duration` — L11039
- `_grid_multiref_segment_max_stretch` — L11055
- `_grid_multiref_prompt` — L11063
- `_write_grid_multiref_motion_qa` — L11111
- `_write_previs_page_motion_qa` — L11121
- `_write_storyboard_trailer_qa` — L11131
- `_write_character_trailer_qa` — L11141
- `_write_grid_multiref_segment_qa` — L11151
- `_motion_compare_record` — L11161
- `_write_storyboard_motion_compare_qa` — L11183
- `_scene_segment_duration` — L11219
- `_apply_grid_multiref_segments` — L11238
- `_previs_page_duration` — L11432
- `_previs_page_group_prompt` — L11442
- `_previs_page_groups` — L11468
- `_storyboard_trailer_duration` — L11483
- `_storyboard_trailer_prompt` — L11493
- `_character_trailer_max_shots` — L11521
- `_character_trailer_shot_duration` — L11529
- `_character_trailer_prompt` — L11543
- `_concat_character_trailer_segments` — L11558
- `_generate_character_trailer_motion` — L11597
- `_multi_trailer_prompt_for_group` — L11705
- `_generate_multi_trailer_segments` — L11728
- `_generate_storyboard_trailer_motion` — L11839
- `_generate_previs_page_motion_segments` — L11914
- `_generate_grid_multiref_motion_segments` — L12026
- `_grid_multiref_concat_groups` — L12196
- `_grid_multiref_concat_groups_partial` — L12213
- `_grid_multiref_concat_paths` — L12231
- `_lip_sync_slot_duration` — L12262
- `_adsd_lip_sync_prompt` — L12269
- `_adsd_broll_motion_prompt` — L12315
- `_adsd_action_b_motion_prompt` — L12357
- `_adsd_silent_b_motion_prompt` — L12403
- `_adsd_narrated_b_audio_dub_prompt` — L12438
- `_adsd_almighty_audio_dub_prompt` — L12482
- `_postprocess_lip_sync_segment` — L12523
- `_detect_audio_leading_silence` — L12595
- `_postprocess_audio_dub_segment` — L12617
- `_lips_change_repair_segment` — L12732
- `_load_lips_change_requested_turns` — L12817
- `_parse_turn_set` — L12834
- `_load_motion_voice_repair_turns` — L12856
- `_voice_assets_file` — L12868
- `_load_voice_assets` — L12875
- `_select_voice_asset_reference` — L12894
- `_lip_sync_poll_download_and_process` — L12960
- `_lip_sync_one_scene` — L13028
- `step66_adsd_lip_sync` — L13352
- `step65_motion` — L13610
- `step65_grid_multiref_motion_qa` — L13692
- `_sanitize_scene_for_state` — L13721
- `_save_pipeline_state` — L13740
- `_retime_after_audio_dub` — L13764
- `_build_voice_clone_hybrid_audio` — L13802
- `_build_dynamic_bgm` — L13940

---

### 第七步：拼接视频轨
Range: **L13984 – L14215** (232 lines)

**Functions:**
- `step7_concat` — L13985

---

### 第八步：生成 ASS 字幕
Range: **L14216 – L15018** (803 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L14339-15018 (680 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L14217
- `_word_timings_for_subtitle_align` — L14243
- `_align_segments_via_asr` — L14284
- `step8_subtitles` — L14327
- `_read_output_json` — L14739
- `_qa_file_pass` — L14750
- `_ass_has_dialogue` — L14757
- `_write_adsd_delivery_qa` — L14767
- `_write_bgm_only_qa` — L14907

---

### 第九步：最终合成
Range: **L15019 – L15264** (246 lines)

**Functions:**
- `step9_render` — L15020

---

### 第十步：推送 Telegram
Range: **L15265 – L16879** (1615 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L16365-16686 (322 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L16687-16691 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L16692-16755 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L16756-16801 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L16802-16879 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L15634
- `PANTONE_FALLBACK` — L15661
- `FESTIVAL_DATE_TAG` — L15774

**Functions:**
- `_generate_caption` — L15266
- `_overlay_title_on_cover` — L15504
- `_prepare_tg_photo` — L15614
- `_get_pantone_for_date` — L15664
- `_llm_bottom_note` — L15689
- `_get_bottom_note` — L15718
- `_get_date_tag` — L15796
- `_shrink_to_b64` — L15818
- `_llm_check_scenes_anomalies` — L15834
- `_llm_check_cover_unique` — L15887
- `_llm_check_cover_quality` — L15917
- `_try_almanac_cover` — L15959
- `_generate_cover_image` — L16130
- `_async_kickoff_cover_caption` — L16372
- `_await_async_cover_caption` — L16402
- `step10_deliver` — L16426

---

### 主流程
Range: **L16880 – L17057** (178 lines)

**Functions:**
- `_print_execution_plan` — L16881
- `main` — L16929

---
