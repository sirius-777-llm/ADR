# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (13188 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-1535 (1414 lines · 46 fn · 3 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L1536-2959 (1424 lines · 22 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L2960-4029 (1070 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L4030-4581 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L4582-6813 (2232 lines · 42 fn · 2 sub)
- [`第 6.5 步：动态化（可选，--with-motion 开启）`](#第-6-5-步-动态化-可选---with-motion-开启) — L6814-10412 (3599 lines · 91 fn · 0 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L10413-10582 (170 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L10583-11236 (654 lines · 7 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L11237-11475 (239 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L11476-13062 (1587 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L13063-13188 (126 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L1535** (1414 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L290-688 (399 lines)
- _工具函数_ — L689-1013 (325 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1014-1535 (522 lines)

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
- `ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT` — L268
- `ADSD_CONSECUTIVE_SPEAKER_BATCHING` — L282
- `ADSD_GENDER_FALLBACK_VOICE_ASSET` — L293
- `VOICE_ASSET_AUDIO_DUB_EXPERIMENT` — L440
- `VOICE_ASSET_AUDIO_DUB_PARTIAL_OK` — L448
- `MOTION_VISUAL_QA` — L452
- `MOTION_VOICE_REPAIR` — L460
- `MOTION_VOICE_STRICT_LOCK` — L465
- `WERYDANCE_CAPTIONS` — L470
- `ADSD_ONSITE_POV_MODE` — L482
- `ADSD_LIPS_CHANGE_REPAIR` — L487
- `ADSD_LIPS_CHANGE_ALL` — L492
- `ADS_REPORTER_MODE` — L503
- `ADS_STORYBOARD_FLOW_DEFAULT` — L520
- `ADS_RETENTION_MODE` — L533
- `ADSD_MODE_NAME` — L539
- `EMOTION_STYLE` — L668
- `EMOTION_STYLE_BRIGHT` — L680
- `_TG_DASHBOARD_STAGES` — L702
- `_TG_NOISY_PATTERNS` — L717
- `_TG_IMMEDIATE_PATTERNS` — L735
- `_TOPIC_MODIFIERS` — L1367
- `_TONE_PANTONE_OVERRIDE` — L1384

**Functions:**
- `_is_action_scene` — L302
- `_needs_storyboard_flow_character_sheet` — L309
- `_wuxia_action_panel_prompt` — L338
- `_action_motion_fragment` — L360
- `_infer_emotion_from_text` — L375
- `_emotion_expression_phrase` — L390
- `_infer_needs_lip_sync` — L397
- `_voice_asset_id_for_speaker` — L416
- `log` — L690
- `_tg_send_raw` — L758
- `_tg_matches` — L774
- `_tg_summarize` — L778
- `_tg_dashboard_stage_for` — L785
- `_tg_progress_bar` — L793
- `_tg_dashboard_text` — L799
- `_tg_dashboard_update` — L817
- `_tg_maybe_digest` — L854
- `tg` — L869
- `_wait_image_submit_slot` — L918
- `_wait_motion_submit_slot` — L931
- `_is_rate_limited_error` — L944
- `_is_rate_limited_response` — L954
- `submit_text_to_image` — L966
- `req_post` — L995
- `req_get` — L1009
- `_tg_probe_send` — L1017
- `_tg_probe_delete` — L1037
- `_tg_upload_with_probe_gap` — L1050
- `poll` — L1090
- `poll_podcast` — L1115
- `poll_task_status` — L1137
- `poll_storyboard_task` — L1159
- `chat` — L1185
- `pick_image_model` — L1213
- `detect_topic_meta` — L1238
- `_topic_culture_guard` — L1288
- `_write_cultural_visual_qa` — L1314
- `is_1919_global_topic` — L1361
- `_strip_topic_modifiers` — L1372
- `apply_1919_global_guardrails` — L1390
- `build_1919_global_cover_prompt` — L1419
- `build_shot_blueprint` — L1448
- `ffprobe_duration` — L1474
- `ffprobe_video_size` — L1485
- `_video_decode_probe` — L1506
- `ffmpeg` — L1524

---

### 第一步：双导演生成剧本
Range: **L1536 – L2959** (1424 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L2269-2959 (691 lines)

**Functions:**
- `_extract_json_array` — L1537
- `_extract_json_object` — L1547
- `_voice_for_speaker` — L1557
- `_adsd_gender_from_voice` — L1593
- `_adsd_infer_gender_from_speaker` — L1601
- `_adsd_gender_lock_phrase` — L1610
- `_adsd_visual_subject_has_gender_conflict` — L1625
- `_adsd_default_roles` — L1637
- `_adsd_allows_media_role` — L1642
- `_adsd_role_candidates` — L1650
- `_adsd_dialogue_shape` — L1666
- `_finalize_adsd_turns` — L1675
- `_parse_adsd_override_turns` — L1698
- `_parse_timecode_seconds` — L1761
- `_clean_override_line_text` — L1770
- `_parse_override_script_text` — L1776
- `_adsd_pov_contract` — L1810
- `_generate_adsd_dialogue_turns` — L1820
- `_adsd_immersion_qa_rewrite_turns` — L1936
- `_adsd_visual_contract` — L1990
- `step1_script` — L2042
- `_write_ads_retention_qa` — L2903

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L2960 – L4029** (1070 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L3035
- `_ADSD_POLICY_REWRITE_TERMS` — L3041
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L3132

**Functions:**
- `_openai_tts_fallback` — L2961
- `_edge_tts_fallback` — L3007
- `_sanitize_for_external_api` — L3050
- `_is_content_policy_error` — L3059
- `_rewrite_adsd_tts_text_for_policy` — L3073
- `_record_adsd_tts_rewrite` — L3113
- `_build_silence_mp3` — L3138
- `_audio_duration_seconds` — L3151
- `_text_to_audio_master_voice_timed` — L3163
- `_text_to_audio_master_voice` — L3288
- `step2_master_voice` — L3391
- `_tts_turn_to_audio` — L3519
- `_asr_verify_dialogue_audio` — L3581
- `_asr_verify_dialogue_turns` — L3623
- `_normalize_cn_number_token` — L3665
- `_compact_zh_text` — L3687
- `_write_adsd_asr_text_qa` — L3694
- `_write_adsd_speaker_focus_qa` — L3733
- `_write_adsd_gender_voice_qa` — L3793
- `step2_dialogue_voice` — L3846

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L4030 – L4581** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L4037-4159 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L4160-4194 (35 lines)
- _第二层：字符数插值_ — L4195-4219 (25 lines)
- _第三层：silencedetect 物理校准_ — L4220-4581 (362 lines)

**Functions:**
- `_detect_silences` — L4038
- `_calibrate_boundaries` — L4073
- `_enforce_monotonic` — L4107
- `_manual_override_segments` — L4119
- `_calc_sentence_boundaries` — L4140
- `step345_timeline` — L4251
- `_analyze_bgm_energy_cuts` — L4310
- `_snap_bgm_only_boundaries` — L4373
- `step345_bgm_only_timeline` — L4433

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L4582 – L6813** (2232 lines)

**Sub-sections:**
- _审批流程_ — L6647-6703 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L6704-6813 (110 lines)

**Functions:**
- `_extract_img_url` — L4583
- `_extract_img_urls` — L4605
- `_extract_video_url` — L4638
- `_count_bands` — L4663
- `_detect_contact_sheet_like_image` — L4675
- `_guess_upload_mime` — L4729
- `_upload_to_weryai` — L4752
- `_send_for_approval` — L4784
- `_wait_approval` — L4848
- `_render_still_segment` — L4860
- `_scene_text_visual_alignment` — L4874
- `_write_text_visual_alignment_qa` — L4910
- `_scene_motion_action_plan` — L4933
- `_ensure_motion_action_plan` — L4987
- `_motion_action_block` — L4996
- `_motion_plan_for_qa` — L5018
- `_write_motion_action_plan_qa` — L5028
- `_write_motion_bridge_refs_qa` — L5058
- `_motion_bridge_ref_prompt` — L5065
- `generate_motion_bridge_refs_gpt_image2` — L5098
- `generate_image` — L5211
- `generate_storyboard_images_gpt_image2` — L5258
- `_storyboard_grid_aspect` — L5443
- `_storyboard_grid_cols_rows` — L5450
- `_storyboard_grid_prompt` — L5472
- `_storyboard_grid_prompt_limit` — L5503
- `_is_prompt_limit_response` — L5507
- `_production_storyboard_prompt` — L5513
- `_write_production_storyboard_page_qa` — L5547
- `_character_sheet_prompt` — L5557
- `_write_character_sheet_qa` — L5655
- `generate_character_sheet_gpt_image2` — L5665
- `generate_production_storyboard_page_gpt_image2` — L5765
- `_qa_clean_storyboard_panel` — L5828
- `_crop_storyboard_grid_panels` — L6009
- `generate_storyboard_grid_gpt_image2` — L6056
- `_gpt_image2_direct_annotated_aspect` — L6287
- `_gpt_image2_direct_annotated_prompt` — L6294
- `generate_gpt_image2_direct_annotated_storyboards` — L6324
- `_llm_bgm_description` — L6425
- `generate_bgm` — L6464
- `step6_parallel` — L6555

---

### 第 6.5 步：动态化（可选，--with-motion 开启）
Range: **L6814 – L10412** (3599 lines)

**Functions:**
- `_generate_motion_prompts` — L6817
- `_motion_tasks_file` — L6884
- `_motion_qa_file` — L6888
- `_append_motion_qa` — L6892
- `_finalize_motion_qa` — L6916
- `_lip_sync_tasks_file` — L7000
- `_load_motion_tasks` — L7004
- `_save_motion_task` — L7014
- `_remove_motion_task` — L7022
- `_load_lip_sync_tasks` — L7029
- `_save_lip_sync_task` — L7039
- `_remove_lip_sync_task` — L7046
- `_video_visual_motion_qa` — L7053
- `_motion_output_qa` — L7125
- `_has_audio_stream` — L7170
- `_normalize_motion_video` — L7181
- `_motion_poll_and_download` — L7231
- `_build_motion_video_prompt` — L7282
- `_short_board_text` — L7312
- `_wrap_board_text` — L7319
- `_storyboard_font` — L7350
- `_draw_storyboard_arrow` — L7365
- `_build_annotated_storyboard_reference` — L7379
- `_plain_caption_text` — L7480
- `_werydance_caption_request` — L7488
- `_werydance_caption_instruction` — L7515
- `_werydance_negative_prompt` — L7527
- `_motion_reference_prompt` — L7533
- `_motion_audio_dub_prompt` — L7556
- `_motion_audio_dub_poll_and_download` — L7590
- `_try_motion_audio_dub_video` — L7655
- `_try_motion_reference_video` — L7790
- `_motion_one_scene` — L7906
- `_grid_multiref_tasks_file` — L8035
- `_previs_page_tasks_file` — L8039
- `_load_grid_multiref_tasks` — L8043
- `_load_previs_page_tasks` — L8053
- `_save_grid_multiref_task` — L8063
- `_save_previs_page_task` — L8070
- `_remove_grid_multiref_task` — L8077
- `_remove_previs_page_task` — L8084
- `_poll_video_task_download` — L8091
- `_grid_multiref_group_size` — L8140
- `_grid_multiref_duration` — L8148
- `_grid_multiref_segment_max_stretch` — L8164
- `_grid_multiref_prompt` — L8172
- `_write_grid_multiref_motion_qa` — L8220
- `_write_previs_page_motion_qa` — L8230
- `_write_storyboard_trailer_qa` — L8240
- `_write_character_trailer_qa` — L8250
- `_write_grid_multiref_segment_qa` — L8260
- `_motion_compare_record` — L8270
- `_write_storyboard_motion_compare_qa` — L8292
- `_scene_segment_duration` — L8328
- `_apply_grid_multiref_segments` — L8347
- `_previs_page_duration` — L8541
- `_previs_page_group_prompt` — L8551
- `_previs_page_groups` — L8577
- `_storyboard_trailer_duration` — L8592
- `_storyboard_trailer_prompt` — L8602
- `_character_trailer_max_shots` — L8630
- `_character_trailer_shot_duration` — L8638
- `_character_trailer_prompt` — L8652
- `_concat_character_trailer_segments` — L8667
- `_generate_character_trailer_motion` — L8706
- `_multi_trailer_prompt_for_group` — L8814
- `_generate_multi_trailer_segments` — L8837
- `_generate_storyboard_trailer_motion` — L8948
- `_generate_previs_page_motion_segments` — L9023
- `_generate_grid_multiref_motion_segments` — L9135
- `_grid_multiref_concat_groups` — L9305
- `_grid_multiref_concat_groups_partial` — L9322
- `_grid_multiref_concat_paths` — L9340
- `_lip_sync_slot_duration` — L9371
- `_adsd_lip_sync_prompt` — L9378
- `_adsd_broll_motion_prompt` — L9417
- `_adsd_almighty_audio_dub_prompt` — L9454
- `_postprocess_lip_sync_segment` — L9489
- `_postprocess_audio_dub_segment` — L9557
- `_lips_change_repair_segment` — L9633
- `_load_lips_change_requested_turns` — L9718
- `_parse_turn_set` — L9735
- `_load_motion_voice_repair_turns` — L9757
- `_voice_assets_file` — L9769
- `_load_voice_assets` — L9776
- `_select_voice_asset_reference` — L9795
- `_lip_sync_poll_download_and_process` — L9861
- `_lip_sync_one_scene` — L9925
- `step66_adsd_lip_sync` — L10125
- `step65_motion` — L10303
- `step65_grid_multiref_motion_qa` — L10385

---

### 第七步：拼接视频轨
Range: **L10413 – L10582** (170 lines)

**Functions:**
- `step7_concat` — L10414

---

### 第八步：生成 ASS 字幕
Range: **L10583 – L11236** (654 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L10622-11236 (615 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L10584
- `step8_subtitles` — L10610
- `_read_output_json` — L10978
- `_qa_file_pass` — L10989
- `_ass_has_dialogue` — L10996
- `_write_adsd_delivery_qa` — L11006
- `_write_bgm_only_qa` — L11125

---

### 第九步：最终合成
Range: **L11237 – L11475** (239 lines)

**Functions:**
- `step9_render` — L11238

---

### 第十步：推送 Telegram
Range: **L11476 – L13062** (1587 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L12576-12891 (316 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L12892-12896 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L12897-12938 (42 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L12939-12984 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L12985-13062 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L11845
- `PANTONE_FALLBACK` — L11872
- `FESTIVAL_DATE_TAG` — L11985

**Functions:**
- `_generate_caption` — L11477
- `_overlay_title_on_cover` — L11715
- `_prepare_tg_photo` — L11825
- `_get_pantone_for_date` — L11875
- `_llm_bottom_note` — L11900
- `_get_bottom_note` — L11929
- `_get_date_tag` — L12007
- `_shrink_to_b64` — L12029
- `_llm_check_scenes_anomalies` — L12045
- `_llm_check_cover_unique` — L12098
- `_llm_check_cover_quality` — L12128
- `_try_almanac_cover` — L12170
- `_generate_cover_image` — L12341
- `_async_kickoff_cover_caption` — L12583
- `_await_async_cover_caption` — L12613
- `step10_deliver` — L12637

---

### 主流程
Range: **L13063 – L13188** (126 lines)

**Functions:**
- `_print_execution_plan` — L13064
- `main` — L13112

---
