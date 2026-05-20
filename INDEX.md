# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (14234 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-1844 (1723 lines · 53 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L1845-3455 (1611 lines · 22 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L3456-4557 (1102 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L4558-5109 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L5110-7348 (2239 lines · 42 fn · 2 sub)
- [`第 6.5 步：动态化（可选，--with-motion 开启）`](#第-6-5-步-动态化-可选---with-motion-开启) — L7349-11293 (3945 lines · 95 fn · 3 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L11294-11463 (170 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L11464-12246 (783 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L12247-12488 (242 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L12489-14075 (1587 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L14076-14234 (159 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L1844** (1723 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L298-423 (126 lines)
- _三类 turn 区分 (silent_b PR)_ — L424-997 (574 lines)
- _工具函数_ — L998-1322 (325 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1323-1844 (522 lines)

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
- `SILENT_B_SPEAKERS` — L428
- `VOICE_ASSET_AUDIO_DUB_EXPERIMENT` — L749
- `VOICE_ASSET_AUDIO_DUB_PARTIAL_OK` — L757
- `MOTION_VISUAL_QA` — L761
- `MOTION_VOICE_REPAIR` — L769
- `MOTION_VOICE_STRICT_LOCK` — L774
- `WERYDANCE_CAPTIONS` — L779
- `ADSD_ONSITE_POV_MODE` — L791
- `ADSD_LIPS_CHANGE_REPAIR` — L796
- `ADSD_LIPS_CHANGE_ALL` — L801
- `ADS_REPORTER_MODE` — L812
- `ADS_STORYBOARD_FLOW_DEFAULT` — L829
- `ADS_RETENTION_MODE` — L842
- `ADSD_MODE_NAME` — L848
- `EMOTION_STYLE` — L977
- `EMOTION_STYLE_BRIGHT` — L989
- `_TG_DASHBOARD_STAGES` — L1011
- `_TG_NOISY_PATTERNS` — L1026
- `_TG_IMMEDIATE_PATTERNS` — L1044
- `_TOPIC_MODIFIERS` — L1676
- `_TONE_PANTONE_OVERRIDE` — L1693

**Functions:**
- `_is_action_scene` — L310
- `_needs_storyboard_flow_character_sheet` — L317
- `_wuxia_action_panel_prompt` — L346
- `_action_motion_fragment` — L368
- `_infer_emotion_from_text` — L383
- `_emotion_expression_phrase` — L398
- `_infer_needs_lip_sync` — L405
- `_infer_turn_type` — L431
- `_resolve_turn_type` — L450
- `_is_silent_b` — L465
- `_is_narrated_b` — L469
- `_is_a_roll` — L473
- `_voice_asset_id_for_speaker` — L477
- `_llm_assign_voice_assets` — L500
- `_apply_llm_voice_assignment` — L624
- `log` — L999
- `_tg_send_raw` — L1067
- `_tg_matches` — L1083
- `_tg_summarize` — L1087
- `_tg_dashboard_stage_for` — L1094
- `_tg_progress_bar` — L1102
- `_tg_dashboard_text` — L1108
- `_tg_dashboard_update` — L1126
- `_tg_maybe_digest` — L1163
- `tg` — L1178
- `_wait_image_submit_slot` — L1227
- `_wait_motion_submit_slot` — L1240
- `_is_rate_limited_error` — L1253
- `_is_rate_limited_response` — L1263
- `submit_text_to_image` — L1275
- `req_post` — L1304
- `req_get` — L1318
- `_tg_probe_send` — L1326
- `_tg_probe_delete` — L1346
- `_tg_upload_with_probe_gap` — L1359
- `poll` — L1399
- `poll_podcast` — L1424
- `poll_task_status` — L1446
- `poll_storyboard_task` — L1468
- `chat` — L1494
- `pick_image_model` — L1522
- `detect_topic_meta` — L1547
- `_topic_culture_guard` — L1597
- `_write_cultural_visual_qa` — L1623
- `is_1919_global_topic` — L1670
- `_strip_topic_modifiers` — L1681
- `apply_1919_global_guardrails` — L1699
- `build_1919_global_cover_prompt` — L1728
- `build_shot_blueprint` — L1757
- `ffprobe_duration` — L1783
- `ffprobe_video_size` — L1794
- `_video_decode_probe` — L1815
- `ffmpeg` — L1833

---

### 第一步：双导演生成剧本
Range: **L1845 – L3455** (1611 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L2749-3455 (707 lines)

**Functions:**
- `_extract_json_array` — L1846
- `_extract_json_object` — L1856
- `_voice_for_speaker` — L1866
- `_adsd_gender_from_voice` — L1902
- `_adsd_infer_gender_from_speaker` — L1910
- `_adsd_gender_lock_phrase` — L1919
- `_adsd_visual_subject_has_gender_conflict` — L1934
- `_adsd_default_roles` — L1946
- `_adsd_allows_media_role` — L1951
- `_adsd_role_candidates` — L1959
- `_adsd_dialogue_shape` — L1975
- `_finalize_adsd_turns` — L1984
- `_parse_adsd_override_turns` — L2018
- `_parse_timecode_seconds` — L2109
- `_clean_override_line_text` — L2118
- `_parse_override_script_text` — L2124
- `_adsd_pov_contract` — L2158
- `_generate_adsd_dialogue_turns` — L2168
- `_adsd_immersion_qa_rewrite_turns` — L2412
- `_adsd_visual_contract` — L2470
- `step1_script` — L2522
- `_write_ads_retention_qa` — L3399

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L3456 – L4557** (1102 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L3531
- `_ADSD_POLICY_REWRITE_TERMS` — L3537
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L3628

**Functions:**
- `_openai_tts_fallback` — L3457
- `_edge_tts_fallback` — L3503
- `_sanitize_for_external_api` — L3546
- `_is_content_policy_error` — L3555
- `_rewrite_adsd_tts_text_for_policy` — L3569
- `_record_adsd_tts_rewrite` — L3609
- `_build_silence_mp3` — L3634
- `_audio_duration_seconds` — L3647
- `_text_to_audio_master_voice_timed` — L3659
- `_text_to_audio_master_voice` — L3784
- `step2_master_voice` — L3887
- `_tts_turn_to_audio` — L4015
- `_asr_verify_dialogue_audio` — L4077
- `_asr_verify_dialogue_turns` — L4139
- `_normalize_cn_number_token` — L4181
- `_compact_zh_text` — L4203
- `_write_adsd_asr_text_qa` — L4210
- `_write_adsd_speaker_focus_qa` — L4249
- `_write_adsd_gender_voice_qa` — L4309
- `step2_dialogue_voice` — L4362

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L4558 – L5109** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L4565-4687 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L4688-4722 (35 lines)
- _第二层：字符数插值_ — L4723-4747 (25 lines)
- _第三层：silencedetect 物理校准_ — L4748-5109 (362 lines)

**Functions:**
- `_detect_silences` — L4566
- `_calibrate_boundaries` — L4601
- `_enforce_monotonic` — L4635
- `_manual_override_segments` — L4647
- `_calc_sentence_boundaries` — L4668
- `step345_timeline` — L4779
- `_analyze_bgm_energy_cuts` — L4838
- `_snap_bgm_only_boundaries` — L4901
- `step345_bgm_only_timeline` — L4961

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L5110 – L7348** (2239 lines)

**Sub-sections:**
- _审批流程_ — L7182-7238 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L7239-7348 (110 lines)

**Functions:**
- `_extract_img_url` — L5111
- `_extract_img_urls` — L5133
- `_extract_video_url` — L5166
- `_count_bands` — L5191
- `_detect_contact_sheet_like_image` — L5203
- `_guess_upload_mime` — L5257
- `_upload_to_weryai` — L5280
- `_send_for_approval` — L5312
- `_wait_approval` — L5376
- `_render_still_segment` — L5388
- `_scene_text_visual_alignment` — L5402
- `_write_text_visual_alignment_qa` — L5438
- `_scene_motion_action_plan` — L5461
- `_ensure_motion_action_plan` — L5515
- `_motion_action_block` — L5524
- `_motion_plan_for_qa` — L5546
- `_write_motion_action_plan_qa` — L5556
- `_write_motion_bridge_refs_qa` — L5586
- `_motion_bridge_ref_prompt` — L5593
- `generate_motion_bridge_refs_gpt_image2` — L5626
- `generate_image` — L5739
- `generate_storyboard_images_gpt_image2` — L5786
- `_storyboard_grid_aspect` — L5971
- `_storyboard_grid_cols_rows` — L5978
- `_storyboard_grid_prompt` — L6000
- `_storyboard_grid_prompt_limit` — L6031
- `_is_prompt_limit_response` — L6035
- `_production_storyboard_prompt` — L6041
- `_write_production_storyboard_page_qa` — L6075
- `_character_sheet_prompt` — L6085
- `_write_character_sheet_qa` — L6183
- `generate_character_sheet_gpt_image2` — L6193
- `generate_production_storyboard_page_gpt_image2` — L6293
- `_qa_clean_storyboard_panel` — L6356
- `_crop_storyboard_grid_panels` — L6537
- `generate_storyboard_grid_gpt_image2` — L6584
- `_gpt_image2_direct_annotated_aspect` — L6815
- `_gpt_image2_direct_annotated_prompt` — L6822
- `generate_gpt_image2_direct_annotated_storyboards` — L6852
- `_llm_bgm_description` — L6953
- `generate_bgm` — L6992
- `step6_parallel` — L7083

---

### 第 6.5 步：动态化（可选，--with-motion 开启）
Range: **L7349 – L11293** (3945 lines)

**Sub-sections:**
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L11078-11115 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回主音轨_ — L11116-11248 (133 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L11249-11293 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L7352
- `_motion_tasks_file` — L7419
- `_motion_qa_file` — L7423
- `_append_motion_qa` — L7427
- `_finalize_motion_qa` — L7451
- `_lip_sync_tasks_file` — L7535
- `_load_motion_tasks` — L7539
- `_save_motion_task` — L7549
- `_remove_motion_task` — L7557
- `_load_lip_sync_tasks` — L7564
- `_save_lip_sync_task` — L7574
- `_remove_lip_sync_task` — L7581
- `_video_visual_motion_qa` — L7588
- `_motion_output_qa` — L7660
- `_has_audio_stream` — L7705
- `_normalize_motion_video` — L7716
- `_motion_poll_and_download` — L7766
- `_build_motion_video_prompt` — L7817
- `_short_board_text` — L7847
- `_wrap_board_text` — L7854
- `_storyboard_font` — L7885
- `_draw_storyboard_arrow` — L7900
- `_build_annotated_storyboard_reference` — L7914
- `_plain_caption_text` — L8015
- `_werydance_caption_request` — L8023
- `_werydance_caption_instruction` — L8050
- `_werydance_negative_prompt` — L8062
- `_motion_reference_prompt` — L8076
- `_motion_audio_dub_prompt` — L8099
- `_motion_audio_dub_poll_and_download` — L8133
- `_try_motion_audio_dub_video` — L8198
- `_try_motion_reference_video` — L8333
- `_motion_one_scene` — L8449
- `_grid_multiref_tasks_file` — L8578
- `_previs_page_tasks_file` — L8582
- `_load_grid_multiref_tasks` — L8586
- `_load_previs_page_tasks` — L8596
- `_save_grid_multiref_task` — L8606
- `_save_previs_page_task` — L8613
- `_remove_grid_multiref_task` — L8620
- `_remove_previs_page_task` — L8627
- `_poll_video_task_download` — L8634
- `_grid_multiref_group_size` — L8683
- `_grid_multiref_duration` — L8691
- `_grid_multiref_segment_max_stretch` — L8707
- `_grid_multiref_prompt` — L8715
- `_write_grid_multiref_motion_qa` — L8763
- `_write_previs_page_motion_qa` — L8773
- `_write_storyboard_trailer_qa` — L8783
- `_write_character_trailer_qa` — L8793
- `_write_grid_multiref_segment_qa` — L8803
- `_motion_compare_record` — L8813
- `_write_storyboard_motion_compare_qa` — L8835
- `_scene_segment_duration` — L8871
- `_apply_grid_multiref_segments` — L8890
- `_previs_page_duration` — L9084
- `_previs_page_group_prompt` — L9094
- `_previs_page_groups` — L9120
- `_storyboard_trailer_duration` — L9135
- `_storyboard_trailer_prompt` — L9145
- `_character_trailer_max_shots` — L9173
- `_character_trailer_shot_duration` — L9181
- `_character_trailer_prompt` — L9195
- `_concat_character_trailer_segments` — L9210
- `_generate_character_trailer_motion` — L9249
- `_multi_trailer_prompt_for_group` — L9357
- `_generate_multi_trailer_segments` — L9380
- `_generate_storyboard_trailer_motion` — L9491
- `_generate_previs_page_motion_segments` — L9566
- `_generate_grid_multiref_motion_segments` — L9678
- `_grid_multiref_concat_groups` — L9848
- `_grid_multiref_concat_groups_partial` — L9865
- `_grid_multiref_concat_paths` — L9883
- `_lip_sync_slot_duration` — L9914
- `_adsd_lip_sync_prompt` — L9921
- `_adsd_broll_motion_prompt` — L9967
- `_adsd_silent_b_motion_prompt` — L10009
- `_adsd_almighty_audio_dub_prompt` — L10044
- `_postprocess_lip_sync_segment` — L10079
- `_postprocess_audio_dub_segment` — L10147
- `_lips_change_repair_segment` — L10230
- `_load_lips_change_requested_turns` — L10315
- `_parse_turn_set` — L10332
- `_load_motion_voice_repair_turns` — L10354
- `_voice_assets_file` — L10366
- `_load_voice_assets` — L10373
- `_select_voice_asset_reference` — L10392
- `_lip_sync_poll_download_and_process` — L10458
- `_lip_sync_one_scene` — L10522
- `step66_adsd_lip_sync` — L10752
- `step65_motion` — L10968
- `step65_grid_multiref_motion_qa` — L11050
- `_retime_after_audio_dub` — L11079
- `_build_voice_clone_hybrid_audio` — L11117
- `_build_dynamic_bgm` — L11250

---

### 第七步：拼接视频轨
Range: **L11294 – L11463** (170 lines)

**Functions:**
- `step7_concat` — L11295

---

### 第八步：生成 ASS 字幕
Range: **L11464 – L12246** (783 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L11587-12246 (660 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L11465
- `_word_timings_for_subtitle_align` — L11491
- `_align_segments_via_asr` — L11532
- `step8_subtitles` — L11575
- `_read_output_json` — L11978
- `_qa_file_pass` — L11989
- `_ass_has_dialogue` — L11996
- `_write_adsd_delivery_qa` — L12006
- `_write_bgm_only_qa` — L12135

---

### 第九步：最终合成
Range: **L12247 – L12488** (242 lines)

**Functions:**
- `step9_render` — L12248

---

### 第十步：推送 Telegram
Range: **L12489 – L14075** (1587 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L13589-13904 (316 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L13905-13909 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L13910-13951 (42 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L13952-13997 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L13998-14075 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L12858
- `PANTONE_FALLBACK` — L12885
- `FESTIVAL_DATE_TAG` — L12998

**Functions:**
- `_generate_caption` — L12490
- `_overlay_title_on_cover` — L12728
- `_prepare_tg_photo` — L12838
- `_get_pantone_for_date` — L12888
- `_llm_bottom_note` — L12913
- `_get_bottom_note` — L12942
- `_get_date_tag` — L13020
- `_shrink_to_b64` — L13042
- `_llm_check_scenes_anomalies` — L13058
- `_llm_check_cover_unique` — L13111
- `_llm_check_cover_quality` — L13141
- `_try_almanac_cover` — L13183
- `_generate_cover_image` — L13354
- `_async_kickoff_cover_caption` — L13596
- `_await_async_cover_caption` — L13626
- `step10_deliver` — L13650

---

### 主流程
Range: **L14076 – L14234** (159 lines)

**Functions:**
- `_print_execution_plan` — L14077
- `main` — L14125

---
