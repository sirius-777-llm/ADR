# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (15380 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-1878 (1757 lines · 54 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L1879-3506 (1628 lines · 22 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L3507-4608 (1102 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L4609-5160 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L5161-8283 (3123 lines · 67 fn · 6 sub)
- [`第 6.5 步：动态化（可选，--with-motion 开启）`](#第-6-5-步-动态化-可选---with-motion-开启) — L8284-12392 (4109 lines · 99 fn · 4 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L12393-12562 (170 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L12563-13354 (792 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L13355-13595 (241 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L13596-15210 (1615 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L15211-15380 (170 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L1878** (1757 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L298-427 (130 lines)
- _三类 turn 区分 (silent_b PR)_ — L428-1006 (579 lines)
- _工具函数_ — L1007-1356 (350 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1357-1878 (522 lines)

**Top-level constants:**
- `HEADERS` — L135
- `VIDEO_FORMAT` — L143
- `BGM_ONLY_REQUESTED` — L151
- `ADS_DIALOGUE_MODE` — L158
- `GPT_IMAGE2_STORYBOARD` — L167
- `STORYBOARD_REFERENCE_MOTION` — L171
- `STORYBOARD_ANNOTATED_MOTION` — L175
- `GPT_IMAGE2_DIRECT_ANNOTATED_STORYBOARD` — L179
- `GPT_IMAGE2_STORYBOARD_GRID` — L184
- `ADSD_STORYBOARD_GRID` — L192
- `ADS_CHARACTER_SHEET_REQUESTED` — L198
- `STORYBOARD_GRID_MULTIREF_MOTION` — L202
- `STORYBOARD_GRID_MULTIREF_SEGMENTS` — L206
- `STORYBOARD_GRID_MULTIREF_MAIN` — L212
- `PREVIS_PAGE_MOTION` — L218
- `STORYBOARD_TRAILER_MODE` — L222
- `MOTION_ACTION_STORYBOARD` — L227
- `MOTION_BRIDGE_REFS` — L231
- `CHARACTER_TRAILER_MODE` — L235
- `STORYBOARD_TRAILER_MAIN` — L243
- `ADSD_LIP_SYNC_EXPERIMENT` — L256
- `ADSD_RICH_MOTION_PROMPT` — L264
- `ADSD_LLM_VOICE_ASSIGN` — L272
- `ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT` — L276
- `ADSD_CONSECUTIVE_SPEAKER_BATCHING` — L290
- `ADSD_GENDER_FALLBACK_VOICE_ASSET` — L301
- `SILENT_B_SPEAKERS` — L432
- `VOICE_ASSET_AUDIO_DUB_EXPERIMENT` — L758
- `VOICE_ASSET_AUDIO_DUB_PARTIAL_OK` — L766
- `MOTION_VISUAL_QA` — L770
- `MOTION_VOICE_REPAIR` — L778
- `MOTION_VOICE_STRICT_LOCK` — L783
- `WERYDANCE_CAPTIONS` — L788
- `ADSD_ONSITE_POV_MODE` — L800
- `ADSD_LIPS_CHANGE_REPAIR` — L805
- `ADSD_LIPS_CHANGE_ALL` — L810
- `ADS_REPORTER_MODE` — L821
- `ADS_STORYBOARD_FLOW_DEFAULT` — L838
- `ADS_RETENTION_MODE` — L851
- `ADSD_MODE_NAME` — L857
- `EMOTION_STYLE` — L986
- `EMOTION_STYLE_BRIGHT` — L998
- `_TG_DASHBOARD_STAGES` — L1020
- `_TG_NOISY_PATTERNS` — L1035
- `_TG_IMMEDIATE_PATTERNS` — L1053
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1286
- `_TOPIC_MODIFIERS` — L1710
- `_TONE_PANTONE_OVERRIDE` — L1727

**Functions:**
- `_is_action_scene` — L310
- `_needs_storyboard_flow_character_sheet` — L321
- `_wuxia_action_panel_prompt` — L350
- `_action_motion_fragment` — L372
- `_infer_emotion_from_text` — L387
- `_emotion_expression_phrase` — L402
- `_infer_needs_lip_sync` — L409
- `_infer_turn_type` — L435
- `_resolve_turn_type` — L454
- `_is_silent_b` — L469
- `_is_narrated_b` — L473
- `_is_a_roll` — L477
- `_voice_asset_id_for_speaker` — L481
- `_llm_assign_voice_assets` — L509
- `_apply_llm_voice_assignment` — L633
- `log` — L1008
- `_tg_send_raw` — L1076
- `_tg_matches` — L1092
- `_tg_summarize` — L1096
- `_tg_dashboard_stage_for` — L1103
- `_tg_progress_bar` — L1111
- `_tg_dashboard_text` — L1117
- `_tg_dashboard_update` — L1135
- `_tg_maybe_digest` — L1172
- `tg` — L1187
- `_wait_image_submit_slot` — L1236
- `_wait_motion_submit_slot` — L1249
- `_is_rate_limited_error` — L1262
- `_is_rate_limited_response` — L1272
- `_inject_image2_quality_suffix` — L1294
- `submit_text_to_image` — L1308
- `req_post` — L1338
- `req_get` — L1352
- `_tg_probe_send` — L1360
- `_tg_probe_delete` — L1380
- `_tg_upload_with_probe_gap` — L1393
- `poll` — L1433
- `poll_podcast` — L1458
- `poll_task_status` — L1480
- `poll_storyboard_task` — L1502
- `chat` — L1528
- `pick_image_model` — L1556
- `detect_topic_meta` — L1581
- `_topic_culture_guard` — L1631
- `_write_cultural_visual_qa` — L1657
- `is_1919_global_topic` — L1704
- `_strip_topic_modifiers` — L1715
- `apply_1919_global_guardrails` — L1733
- `build_1919_global_cover_prompt` — L1762
- `build_shot_blueprint` — L1791
- `ffprobe_duration` — L1817
- `ffprobe_video_size` — L1828
- `_video_decode_probe` — L1849
- `ffmpeg` — L1867

---

### 第一步：双导演生成剧本
Range: **L1879 – L3506** (1628 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L2800-3506 (707 lines)

**Functions:**
- `_extract_json_array` — L1880
- `_extract_json_object` — L1890
- `_voice_for_speaker` — L1900
- `_adsd_gender_from_voice` — L1936
- `_adsd_infer_gender_from_speaker` — L1944
- `_adsd_gender_lock_phrase` — L1953
- `_adsd_visual_subject_has_gender_conflict` — L1968
- `_adsd_default_roles` — L1980
- `_adsd_allows_media_role` — L1985
- `_adsd_role_candidates` — L1993
- `_adsd_dialogue_shape` — L2016
- `_finalize_adsd_turns` — L2025
- `_parse_adsd_override_turns` — L2059
- `_parse_timecode_seconds` — L2150
- `_clean_override_line_text` — L2159
- `_parse_override_script_text` — L2165
- `_adsd_pov_contract` — L2199
- `_generate_adsd_dialogue_turns` — L2209
- `_adsd_immersion_qa_rewrite_turns` — L2463
- `_adsd_visual_contract` — L2521
- `step1_script` — L2573
- `_write_ads_retention_qa` — L3450

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L3507 – L4608** (1102 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L3582
- `_ADSD_POLICY_REWRITE_TERMS` — L3588
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L3679

**Functions:**
- `_openai_tts_fallback` — L3508
- `_edge_tts_fallback` — L3554
- `_sanitize_for_external_api` — L3597
- `_is_content_policy_error` — L3606
- `_rewrite_adsd_tts_text_for_policy` — L3620
- `_record_adsd_tts_rewrite` — L3660
- `_build_silence_mp3` — L3685
- `_audio_duration_seconds` — L3698
- `_text_to_audio_master_voice_timed` — L3710
- `_text_to_audio_master_voice` — L3835
- `step2_master_voice` — L3938
- `_tts_turn_to_audio` — L4066
- `_asr_verify_dialogue_audio` — L4128
- `_asr_verify_dialogue_turns` — L4190
- `_normalize_cn_number_token` — L4232
- `_compact_zh_text` — L4254
- `_write_adsd_asr_text_qa` — L4261
- `_write_adsd_speaker_focus_qa` — L4300
- `_write_adsd_gender_voice_qa` — L4360
- `step2_dialogue_voice` — L4413

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L4609 – L5160** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L4616-4738 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L4739-4773 (35 lines)
- _第二层：字符数插值_ — L4774-4798 (25 lines)
- _第三层：silencedetect 物理校准_ — L4799-5160 (362 lines)

**Functions:**
- `_detect_silences` — L4617
- `_calibrate_boundaries` — L4652
- `_enforce_monotonic` — L4686
- `_manual_override_segments` — L4698
- `_calc_sentence_boundaries` — L4719
- `step345_timeline` — L4830
- `_analyze_bgm_energy_cuts` — L4889
- `_snap_bgm_only_boundaries` — L4952
- `step345_bgm_only_timeline` — L5012

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L5161 – L8283** (3123 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L6241-6291 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L6292-6392 (101 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L6393-6664 (272 lines)
- _Speaker IP Card (2026-05-21)_ — L6665-8116 (1452 lines)
- _审批流程_ — L8117-8173 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L8174-8283 (110 lines)

**Top-level constants:**
- `CHARACTER_META_GRID_COSTUMES` — L6247
- `CHARACTER_META_GRID_POSES` — L6248
- `CHARACTER_META_GRID_SCENES` — L6249
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L6252

**Functions:**
- `_extract_img_url` — L5162
- `_extract_img_urls` — L5184
- `_extract_video_url` — L5217
- `_count_bands` — L5242
- `_detect_contact_sheet_like_image` — L5254
- `_guess_upload_mime` — L5308
- `_upload_to_weryai` — L5331
- `_send_for_approval` — L5363
- `_wait_approval` — L5427
- `_render_still_segment` — L5439
- `_scene_text_visual_alignment` — L5453
- `_write_text_visual_alignment_qa` — L5489
- `_scene_motion_action_plan` — L5512
- `_ensure_motion_action_plan` — L5566
- `_motion_action_block` — L5575
- `_motion_plan_for_qa` — L5597
- `_write_motion_action_plan_qa` — L5607
- `_write_motion_bridge_refs_qa` — L5637
- `_motion_bridge_ref_prompt` — L5644
- `generate_motion_bridge_refs_gpt_image2` — L5677
- `generate_image` — L5790
- `generate_storyboard_images_gpt_image2` — L5837
- `_storyboard_grid_aspect` — L6022
- `_storyboard_grid_cols_rows` — L6029
- `_storyboard_grid_prompt` — L6051
- `_storyboard_grid_prompt_limit` — L6089
- `_is_prompt_limit_response` — L6093
- `_production_storyboard_prompt` — L6099
- `_write_production_storyboard_page_qa` — L6133
- `_character_sheet_prompt` — L6143
- `_is_audit_blocked` — L6269
- `_paraphrase_sensitive_dialogue` — L6282
- `_topic_cache_dir` — L6296
- `_topic_cache_path` — L6302
- `_load_topic_decomposition_cache` — L6307
- `_save_topic_decomposition_cache` — L6317
- `_llm_topic_decomposition` — L6322
- `_llm_infer_meta_grid_template` — L6450
- `_resolve_meta_grid_template` — L6507
- `_infer_meta_grid_costume` — L6550
- `_infer_meta_grid_pose` — L6595
- `_adsd_meta_grid_call_prompt` — L6638
- `_speaker_ips_dir` — L6668
- `_list_speaker_ips` — L6675
- `_match_speaker_ip` — L6689
- `_build_speaker_ip_context_for_script` — L6709
- `_save_speaker_ip` — L6755
- `_record_speaker_usage_history` — L6763
- `_format_speaker_usage_history_for_prompt` — L6805
- `_character_meta_grid_cache_dir` — L6823
- `_character_meta_grid_cache_path` — L6831
- `_character_meta_grid_path` — L6837
- `generate_character_meta_grid_gpt_image2` — L6843
- `_generate_all_character_meta_grids` — L6962
- `_write_character_sheet_qa` — L7003
- `generate_character_sheet_gpt_image2` — L7013
- `generate_production_storyboard_page_gpt_image2` — L7113
- `_qa_clean_storyboard_panel` — L7176
- `_crop_storyboard_grid_panels` — L7357
- `generate_storyboard_grid_gpt_image2` — L7404
- `_gpt_image2_direct_annotated_aspect` — L7635
- `_gpt_image2_direct_annotated_prompt` — L7642
- `generate_gpt_image2_direct_annotated_storyboards` — L7672
- `_llm_bgm_description` — L7773
- `_bgm_contains_vocals` — L7812
- `generate_bgm` — L7846
- `step6_parallel` — L7963

---

### 第 6.5 步：动态化（可选，--with-motion 开启）
Range: **L8284 – L12392** (4109 lines)

**Sub-sections:**
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L12134-12176 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L12177-12214 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回主音轨_ — L12215-12347 (133 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L12348-12392 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L8287
- `_motion_tasks_file` — L8354
- `_motion_qa_file` — L8358
- `_append_motion_qa` — L8362
- `_finalize_motion_qa` — L8386
- `_lip_sync_tasks_file` — L8470
- `_load_motion_tasks` — L8474
- `_save_motion_task` — L8484
- `_remove_motion_task` — L8492
- `_load_lip_sync_tasks` — L8499
- `_save_lip_sync_task` — L8509
- `_remove_lip_sync_task` — L8516
- `_video_visual_motion_qa` — L8523
- `_motion_output_qa` — L8595
- `_has_audio_stream` — L8640
- `_normalize_motion_video` — L8651
- `_motion_poll_and_download` — L8701
- `_build_motion_video_prompt` — L8752
- `_short_board_text` — L8782
- `_wrap_board_text` — L8789
- `_storyboard_font` — L8820
- `_draw_storyboard_arrow` — L8835
- `_build_annotated_storyboard_reference` — L8849
- `_plain_caption_text` — L8950
- `_werydance_caption_request` — L8958
- `_werydance_caption_instruction` — L8985
- `_werydance_negative_prompt` — L8997
- `_motion_reference_prompt` — L9011
- `_motion_audio_dub_prompt` — L9034
- `_motion_audio_dub_poll_and_download` — L9068
- `_try_motion_audio_dub_video` — L9133
- `_try_motion_reference_video` — L9268
- `_motion_one_scene` — L9384
- `_grid_multiref_tasks_file` — L9513
- `_previs_page_tasks_file` — L9517
- `_load_grid_multiref_tasks` — L9521
- `_load_previs_page_tasks` — L9531
- `_save_grid_multiref_task` — L9541
- `_save_previs_page_task` — L9548
- `_remove_grid_multiref_task` — L9555
- `_remove_previs_page_task` — L9562
- `_poll_video_task_download` — L9569
- `_grid_multiref_group_size` — L9618
- `_grid_multiref_duration` — L9626
- `_grid_multiref_segment_max_stretch` — L9642
- `_grid_multiref_prompt` — L9650
- `_write_grid_multiref_motion_qa` — L9698
- `_write_previs_page_motion_qa` — L9708
- `_write_storyboard_trailer_qa` — L9718
- `_write_character_trailer_qa` — L9728
- `_write_grid_multiref_segment_qa` — L9738
- `_motion_compare_record` — L9748
- `_write_storyboard_motion_compare_qa` — L9770
- `_scene_segment_duration` — L9806
- `_apply_grid_multiref_segments` — L9825
- `_previs_page_duration` — L10019
- `_previs_page_group_prompt` — L10029
- `_previs_page_groups` — L10055
- `_storyboard_trailer_duration` — L10070
- `_storyboard_trailer_prompt` — L10080
- `_character_trailer_max_shots` — L10108
- `_character_trailer_shot_duration` — L10116
- `_character_trailer_prompt` — L10130
- `_concat_character_trailer_segments` — L10145
- `_generate_character_trailer_motion` — L10184
- `_multi_trailer_prompt_for_group` — L10292
- `_generate_multi_trailer_segments` — L10315
- `_generate_storyboard_trailer_motion` — L10426
- `_generate_previs_page_motion_segments` — L10501
- `_generate_grid_multiref_motion_segments` — L10613
- `_grid_multiref_concat_groups` — L10783
- `_grid_multiref_concat_groups_partial` — L10800
- `_grid_multiref_concat_paths` — L10818
- `_lip_sync_slot_duration` — L10849
- `_adsd_lip_sync_prompt` — L10856
- `_adsd_broll_motion_prompt` — L10902
- `_adsd_silent_b_motion_prompt` — L10944
- `_adsd_narrated_b_audio_dub_prompt` — L10979
- `_adsd_almighty_audio_dub_prompt` — L11023
- `_postprocess_lip_sync_segment` — L11058
- `_detect_audio_leading_silence` — L11126
- `_postprocess_audio_dub_segment` — L11148
- `_lips_change_repair_segment` — L11254
- `_load_lips_change_requested_turns` — L11339
- `_parse_turn_set` — L11356
- `_load_motion_voice_repair_turns` — L11378
- `_voice_assets_file` — L11390
- `_load_voice_assets` — L11397
- `_select_voice_asset_reference` — L11416
- `_lip_sync_poll_download_and_process` — L11482
- `_lip_sync_one_scene` — L11546
- `step66_adsd_lip_sync` — L11808
- `step65_motion` — L12024
- `step65_grid_multiref_motion_qa` — L12106
- `_sanitize_scene_for_state` — L12135
- `_save_pipeline_state` — L12154
- `_retime_after_audio_dub` — L12178
- `_build_voice_clone_hybrid_audio` — L12216
- `_build_dynamic_bgm` — L12349

---

### 第七步：拼接视频轨
Range: **L12393 – L12562** (170 lines)

**Functions:**
- `step7_concat` — L12394

---

### 第八步：生成 ASS 字幕
Range: **L12563 – L13354** (792 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L12686-13354 (669 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L12564
- `_word_timings_for_subtitle_align` — L12590
- `_align_segments_via_asr` — L12631
- `step8_subtitles` — L12674
- `_read_output_json` — L13086
- `_qa_file_pass` — L13097
- `_ass_has_dialogue` — L13104
- `_write_adsd_delivery_qa` — L13114
- `_write_bgm_only_qa` — L13243

---

### 第九步：最终合成
Range: **L13355 – L13595** (241 lines)

**Functions:**
- `step9_render` — L13356

---

### 第十步：推送 Telegram
Range: **L13596 – L15210** (1615 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L14696-15017 (322 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L15018-15022 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L15023-15086 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L15087-15132 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L15133-15210 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L13965
- `PANTONE_FALLBACK` — L13992
- `FESTIVAL_DATE_TAG` — L14105

**Functions:**
- `_generate_caption` — L13597
- `_overlay_title_on_cover` — L13835
- `_prepare_tg_photo` — L13945
- `_get_pantone_for_date` — L13995
- `_llm_bottom_note` — L14020
- `_get_bottom_note` — L14049
- `_get_date_tag` — L14127
- `_shrink_to_b64` — L14149
- `_llm_check_scenes_anomalies` — L14165
- `_llm_check_cover_unique` — L14218
- `_llm_check_cover_quality` — L14248
- `_try_almanac_cover` — L14290
- `_generate_cover_image` — L14461
- `_async_kickoff_cover_caption` — L14703
- `_await_async_cover_caption` — L14733
- `step10_deliver` — L14757

---

### 主流程
Range: **L15211 – L15380** (170 lines)

**Functions:**
- `_print_execution_plan` — L15212
- `main` — L15260

---
