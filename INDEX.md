# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (16916 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-1997 (1876 lines · 58 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L1998-4158 (2161 lines · 29 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L4159-5262 (1104 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L5263-5814 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L5815-9554 (3740 lines · 80 fn · 6 sub)
- [`第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）`](#第-6-5-步-动态化-hads-vads-默认-on---no-motion-关) — L9555-13845 (4291 lines · 100 fn · 4 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L13846-14077 (232 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L14078-14877 (800 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L14878-15123 (246 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L15124-16738 (1615 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L16739-16916 (178 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L1997** (1876 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L308-437 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L438-1125 (688 lines)
- _工具函数_ — L1126-1475 (350 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1476-1997 (522 lines)

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
- `_TOPIC_MODIFIERS` — L1829
- `_TONE_PANTONE_OVERRIDE` — L1846

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
- `chat` — L1647
- `pick_image_model` — L1675
- `detect_topic_meta` — L1700
- `_topic_culture_guard` — L1750
- `_write_cultural_visual_qa` — L1776
- `is_1919_global_topic` — L1823
- `_strip_topic_modifiers` — L1834
- `apply_1919_global_guardrails` — L1852
- `build_1919_global_cover_prompt` — L1881
- `build_shot_blueprint` — L1910
- `ffprobe_duration` — L1936
- `ffprobe_video_size` — L1947
- `_video_decode_probe` — L1968
- `ffmpeg` — L1986

---

### 第一步：双导演生成剧本
Range: **L1998 – L4158** (2161 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L3430-4158 (729 lines)

**Functions:**
- `_extract_json_array` — L1999
- `_extract_json_object` — L2009
- `_voice_for_speaker` — L2019
- `_adsd_gender_from_voice` — L2055
- `_adsd_infer_gender_from_speaker` — L2063
- `_adsd_gender_lock_phrase` — L2072
- `_adsd_visual_subject_has_gender_conflict` — L2087
- `_adsd_default_roles` — L2099
- `_adsd_allows_media_role` — L2104
- `_adsd_role_candidates` — L2112
- `_adsd_dialogue_shape` — L2135
- `_finalize_adsd_turns` — L2144
- `_parse_adsd_override_turns` — L2178
- `_parse_timecode_seconds` — L2269
- `_clean_override_line_text` — L2278
- `_parse_override_script_text` — L2284
- `_adsd_pov_contract` — L2318
- `_load_audit_blacklist_block` — L2331
- `_generate_adsd_dialogue_turns` — L2369
- `_broll_rhythm_reviewer` — L2792
- `_sweep_speaker_field` — L2899
- `_should_run_immersion_qa` — L2959
- `_adsd_immersion_qa_rewrite_turns` — L2982
- `_adsd_visual_contract` — L3046
- `_parse_risk_score` — L3098
- `_check_high_risk_hard_abort` — L3127
- `_maybe_neutralize_topic` — L3154
- `step1_script` — L3193
- `_write_ads_retention_qa` — L4102

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L4159 – L5262** (1104 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L4234
- `_ADSD_POLICY_REWRITE_TERMS` — L4240
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L4331

**Functions:**
- `_openai_tts_fallback` — L4160
- `_edge_tts_fallback` — L4206
- `_sanitize_for_external_api` — L4249
- `_is_content_policy_error` — L4258
- `_rewrite_adsd_tts_text_for_policy` — L4272
- `_record_adsd_tts_rewrite` — L4312
- `_build_silence_mp3` — L4337
- `_audio_duration_seconds` — L4350
- `_text_to_audio_master_voice_timed` — L4362
- `_text_to_audio_master_voice` — L4487
- `step2_master_voice` — L4590
- `_tts_turn_to_audio` — L4718
- `_asr_verify_dialogue_audio` — L4782
- `_asr_verify_dialogue_turns` — L4844
- `_normalize_cn_number_token` — L4886
- `_compact_zh_text` — L4908
- `_write_adsd_asr_text_qa` — L4915
- `_write_adsd_speaker_focus_qa` — L4954
- `_write_adsd_gender_voice_qa` — L5014
- `step2_dialogue_voice` — L5067

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L5263 – L5814** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L5270-5392 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L5393-5427 (35 lines)
- _第二层：字符数插值_ — L5428-5452 (25 lines)
- _第三层：silencedetect 物理校准_ — L5453-5814 (362 lines)

**Functions:**
- `_detect_silences` — L5271
- `_calibrate_boundaries` — L5306
- `_enforce_monotonic` — L5340
- `_manual_override_segments` — L5352
- `_calc_sentence_boundaries` — L5373
- `step345_timeline` — L5484
- `_analyze_bgm_energy_cuts` — L5543
- `_snap_bgm_only_boundaries` — L5606
- `step345_bgm_only_timeline` — L5666

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L5815 – L9554** (3740 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L7004-7054 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L7055-7195 (141 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L7196-7630 (435 lines)
- _Speaker IP Card (2026-05-21)_ — L7631-9387 (1757 lines)
- _审批流程_ — L9388-9444 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L9445-9554 (110 lines)

**Top-level constants:**
- `CHARACTER_META_GRID_COSTUMES` — L7010
- `CHARACTER_META_GRID_POSES` — L7011
- `CHARACTER_META_GRID_SCENES` — L7012
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L7015

**Functions:**
- `_extract_img_url` — L5816
- `_extract_img_urls` — L5838
- `_extract_video_url` — L5871
- `_count_bands` — L5896
- `_detect_contact_sheet_like_image` — L5908
- `_file_sha256` — L5969
- `_load_upload_cache` — L5982
- `_save_upload_cache` — L5991
- `_cached_upload_url` — L5999
- `_store_upload_url` — L6016
- `_guess_upload_mime` — L6026
- `_upload_to_weryai` — L6049
- `_send_for_approval` — L6103
- `_wait_approval` — L6167
- `_render_still_segment` — L6179
- `_scene_text_visual_alignment` — L6210
- `_write_text_visual_alignment_qa` — L6246
- `_scene_motion_action_plan` — L6269
- `_ensure_motion_action_plan` — L6323
- `_motion_action_block` — L6332
- `_motion_plan_for_qa` — L6360
- `_write_motion_action_plan_qa` — L6370
- `_write_motion_bridge_refs_qa` — L6400
- `_motion_bridge_ref_prompt` — L6407
- `generate_motion_bridge_refs_gpt_image2` — L6440
- `generate_image` — L6553
- `generate_storyboard_images_gpt_image2` — L6600
- `_storyboard_grid_aspect` — L6785
- `_storyboard_grid_cols_rows` — L6792
- `_storyboard_grid_prompt` — L6814
- `_storyboard_grid_prompt_limit` — L6852
- `_is_prompt_limit_response` — L6856
- `_production_storyboard_prompt` — L6862
- `_write_production_storyboard_page_qa` — L6896
- `_character_sheet_prompt` — L6906
- `_is_audit_blocked` — L7032
- `_paraphrase_sensitive_dialogue` — L7045
- `_topic_cache_dir` — L7059
- `_topic_cache_path` — L7065
- `_load_topic_decomposition_cache` — L7078
- `_save_topic_decomposition_cache` — L7096
- `_llm_topic_decomposition` — L7102
- `_director_route_block` — L7249
- `_llm_infer_meta_grid_template` — L7319
- `_resolve_meta_grid_template` — L7376
- `_infer_meta_grid_costume` — L7419
- `_infer_meta_grid_pose` — L7468
- `_adsd_meta_grid_call_prompt` — L7515
- `_meta_grid_panel_index` — L7557
- `_migrate_speaker_ip` — L7637
- `_speaker_ips_dir` — L7662
- `_list_speaker_ips` — L7669
- `_match_speaker_ip` — L7683
- `_build_speaker_ip_context_for_script` — L7703
- `_ip_usage_stats` — L7759
- `_recommend_related_ips` — L7777
- `_save_speaker_ip` — L7802
- `_record_speaker_usage_history` — L7811
- `_format_speaker_usage_history_for_prompt` — L7858
- `_llm_infer_ip_skeleton` — L7876
- `_llm_pick_voice_asset_for_ip` — L7921
- `_auto_incubate_missing_ips` — L7969
- `_character_meta_grid_cache_dir` — L8053
- `_character_meta_grid_cache_path` — L8061
- `_character_meta_grid_path` — L8069
- `generate_character_meta_grid_gpt_image2` — L8075
- `_generate_all_character_meta_grids` — L8233
- `_write_character_sheet_qa` — L8274
- `generate_character_sheet_gpt_image2` — L8284
- `generate_production_storyboard_page_gpt_image2` — L8384
- `_qa_clean_storyboard_panel` — L8447
- `_crop_storyboard_grid_panels` — L8628
- `generate_storyboard_grid_gpt_image2` — L8675
- `_gpt_image2_direct_annotated_aspect` — L8906
- `_gpt_image2_direct_annotated_prompt` — L8913
- `generate_gpt_image2_direct_annotated_storyboards` — L8943
- `_llm_bgm_description` — L9044
- `_bgm_contains_vocals` — L9083
- `generate_bgm` — L9117
- `step6_parallel` — L9234

---

### 第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）
Range: **L9555 – L13845** (4291 lines)

**Sub-sections:**
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L13582-13624 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L13625-13662 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回主音轨_ — L13663-13800 (138 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L13801-13845 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L9558
- `_motion_tasks_file` — L9625
- `_motion_qa_file` — L9629
- `_append_motion_qa` — L9633
- `_finalize_motion_qa` — L9657
- `_lip_sync_tasks_file` — L9741
- `_load_motion_tasks` — L9745
- `_save_motion_task` — L9755
- `_remove_motion_task` — L9763
- `_load_lip_sync_tasks` — L9770
- `_save_lip_sync_task` — L9780
- `_remove_lip_sync_task` — L9787
- `_video_visual_motion_qa` — L9794
- `_motion_output_qa` — L9866
- `_has_audio_stream` — L9911
- `_normalize_motion_video` — L9922
- `_motion_poll_and_download` — L9972
- `_build_motion_video_prompt` — L10023
- `_short_board_text` — L10053
- `_wrap_board_text` — L10060
- `_storyboard_font` — L10091
- `_draw_storyboard_arrow` — L10106
- `_build_annotated_storyboard_reference` — L10120
- `_plain_caption_text` — L10221
- `_werydance_caption_request` — L10229
- `_werydance_caption_instruction` — L10256
- `_werydance_negative_prompt` — L10268
- `_motion_reference_prompt` — L10286
- `_motion_audio_dub_prompt` — L10309
- `_motion_audio_dub_poll_and_download` — L10343
- `_try_motion_audio_dub_video` — L10408
- `_try_motion_reference_video` — L10543
- `_motion_one_scene` — L10659
- `_grid_multiref_tasks_file` — L10788
- `_previs_page_tasks_file` — L10792
- `_load_grid_multiref_tasks` — L10796
- `_load_previs_page_tasks` — L10806
- `_save_grid_multiref_task` — L10816
- `_save_previs_page_task` — L10823
- `_remove_grid_multiref_task` — L10830
- `_remove_previs_page_task` — L10837
- `_poll_video_task_download` — L10844
- `_grid_multiref_group_size` — L10893
- `_grid_multiref_duration` — L10901
- `_grid_multiref_segment_max_stretch` — L10917
- `_grid_multiref_prompt` — L10925
- `_write_grid_multiref_motion_qa` — L10973
- `_write_previs_page_motion_qa` — L10983
- `_write_storyboard_trailer_qa` — L10993
- `_write_character_trailer_qa` — L11003
- `_write_grid_multiref_segment_qa` — L11013
- `_motion_compare_record` — L11023
- `_write_storyboard_motion_compare_qa` — L11045
- `_scene_segment_duration` — L11081
- `_apply_grid_multiref_segments` — L11100
- `_previs_page_duration` — L11294
- `_previs_page_group_prompt` — L11304
- `_previs_page_groups` — L11330
- `_storyboard_trailer_duration` — L11345
- `_storyboard_trailer_prompt` — L11355
- `_character_trailer_max_shots` — L11383
- `_character_trailer_shot_duration` — L11391
- `_character_trailer_prompt` — L11405
- `_concat_character_trailer_segments` — L11420
- `_generate_character_trailer_motion` — L11459
- `_multi_trailer_prompt_for_group` — L11567
- `_generate_multi_trailer_segments` — L11590
- `_generate_storyboard_trailer_motion` — L11701
- `_generate_previs_page_motion_segments` — L11776
- `_generate_grid_multiref_motion_segments` — L11888
- `_grid_multiref_concat_groups` — L12058
- `_grid_multiref_concat_groups_partial` — L12075
- `_grid_multiref_concat_paths` — L12093
- `_lip_sync_slot_duration` — L12124
- `_adsd_lip_sync_prompt` — L12131
- `_adsd_broll_motion_prompt` — L12177
- `_adsd_action_b_motion_prompt` — L12219
- `_adsd_silent_b_motion_prompt` — L12265
- `_adsd_narrated_b_audio_dub_prompt` — L12300
- `_adsd_almighty_audio_dub_prompt` — L12344
- `_postprocess_lip_sync_segment` — L12385
- `_detect_audio_leading_silence` — L12457
- `_postprocess_audio_dub_segment` — L12479
- `_lips_change_repair_segment` — L12594
- `_load_lips_change_requested_turns` — L12679
- `_parse_turn_set` — L12696
- `_load_motion_voice_repair_turns` — L12718
- `_voice_assets_file` — L12730
- `_load_voice_assets` — L12737
- `_select_voice_asset_reference` — L12756
- `_lip_sync_poll_download_and_process` — L12822
- `_lip_sync_one_scene` — L12890
- `step66_adsd_lip_sync` — L13214
- `step65_motion` — L13472
- `step65_grid_multiref_motion_qa` — L13554
- `_sanitize_scene_for_state` — L13583
- `_save_pipeline_state` — L13602
- `_retime_after_audio_dub` — L13626
- `_build_voice_clone_hybrid_audio` — L13664
- `_build_dynamic_bgm` — L13802

---

### 第七步：拼接视频轨
Range: **L13846 – L14077** (232 lines)

**Functions:**
- `step7_concat` — L13847

---

### 第八步：生成 ASS 字幕
Range: **L14078 – L14877** (800 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L14201-14877 (677 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L14079
- `_word_timings_for_subtitle_align` — L14105
- `_align_segments_via_asr` — L14146
- `step8_subtitles` — L14189
- `_read_output_json` — L14601
- `_qa_file_pass` — L14612
- `_ass_has_dialogue` — L14619
- `_write_adsd_delivery_qa` — L14629
- `_write_bgm_only_qa` — L14766

---

### 第九步：最终合成
Range: **L14878 – L15123** (246 lines)

**Functions:**
- `step9_render` — L14879

---

### 第十步：推送 Telegram
Range: **L15124 – L16738** (1615 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L16224-16545 (322 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L16546-16550 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L16551-16614 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L16615-16660 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L16661-16738 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L15493
- `PANTONE_FALLBACK` — L15520
- `FESTIVAL_DATE_TAG` — L15633

**Functions:**
- `_generate_caption` — L15125
- `_overlay_title_on_cover` — L15363
- `_prepare_tg_photo` — L15473
- `_get_pantone_for_date` — L15523
- `_llm_bottom_note` — L15548
- `_get_bottom_note` — L15577
- `_get_date_tag` — L15655
- `_shrink_to_b64` — L15677
- `_llm_check_scenes_anomalies` — L15693
- `_llm_check_cover_unique` — L15746
- `_llm_check_cover_quality` — L15776
- `_try_almanac_cover` — L15818
- `_generate_cover_image` — L15989
- `_async_kickoff_cover_caption` — L16231
- `_await_async_cover_caption` — L16261
- `step10_deliver` — L16285

---

### 主流程
Range: **L16739 – L16916** (178 lines)

**Functions:**
- `_print_execution_plan` — L16740
- `main` — L16788

---
