# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (13508 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-1791 (1670 lines · 48 fn · 3 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L1792-3231 (1440 lines · 22 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L3232-4301 (1070 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L4302-4853 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L4854-7085 (2232 lines · 42 fn · 2 sub)
- [`第 6.5 步：动态化（可选，--with-motion 开启）`](#第-6-5-步-动态化-可选---with-motion-开启) — L7086-10722 (3637 lines · 91 fn · 0 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L10723-10892 (170 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L10893-11556 (664 lines · 7 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L11557-11795 (239 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L11796-13382 (1587 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L13383-13508 (126 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L1791** (1670 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L298-944 (647 lines)
- _工具函数_ — L945-1269 (325 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1270-1791 (522 lines)

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
- `VOICE_ASSET_AUDIO_DUB_EXPERIMENT` — L696
- `VOICE_ASSET_AUDIO_DUB_PARTIAL_OK` — L704
- `MOTION_VISUAL_QA` — L708
- `MOTION_VOICE_REPAIR` — L716
- `MOTION_VOICE_STRICT_LOCK` — L721
- `WERYDANCE_CAPTIONS` — L726
- `ADSD_ONSITE_POV_MODE` — L738
- `ADSD_LIPS_CHANGE_REPAIR` — L743
- `ADSD_LIPS_CHANGE_ALL` — L748
- `ADS_REPORTER_MODE` — L759
- `ADS_STORYBOARD_FLOW_DEFAULT` — L776
- `ADS_RETENTION_MODE` — L789
- `ADSD_MODE_NAME` — L795
- `EMOTION_STYLE` — L924
- `EMOTION_STYLE_BRIGHT` — L936
- `_TG_DASHBOARD_STAGES` — L958
- `_TG_NOISY_PATTERNS` — L973
- `_TG_IMMEDIATE_PATTERNS` — L991
- `_TOPIC_MODIFIERS` — L1623
- `_TONE_PANTONE_OVERRIDE` — L1640

**Functions:**
- `_is_action_scene` — L310
- `_needs_storyboard_flow_character_sheet` — L317
- `_wuxia_action_panel_prompt` — L346
- `_action_motion_fragment` — L368
- `_infer_emotion_from_text` — L383
- `_emotion_expression_phrase` — L398
- `_infer_needs_lip_sync` — L405
- `_voice_asset_id_for_speaker` — L424
- `_llm_assign_voice_assets` — L447
- `_apply_llm_voice_assignment` — L571
- `log` — L946
- `_tg_send_raw` — L1014
- `_tg_matches` — L1030
- `_tg_summarize` — L1034
- `_tg_dashboard_stage_for` — L1041
- `_tg_progress_bar` — L1049
- `_tg_dashboard_text` — L1055
- `_tg_dashboard_update` — L1073
- `_tg_maybe_digest` — L1110
- `tg` — L1125
- `_wait_image_submit_slot` — L1174
- `_wait_motion_submit_slot` — L1187
- `_is_rate_limited_error` — L1200
- `_is_rate_limited_response` — L1210
- `submit_text_to_image` — L1222
- `req_post` — L1251
- `req_get` — L1265
- `_tg_probe_send` — L1273
- `_tg_probe_delete` — L1293
- `_tg_upload_with_probe_gap` — L1306
- `poll` — L1346
- `poll_podcast` — L1371
- `poll_task_status` — L1393
- `poll_storyboard_task` — L1415
- `chat` — L1441
- `pick_image_model` — L1469
- `detect_topic_meta` — L1494
- `_topic_culture_guard` — L1544
- `_write_cultural_visual_qa` — L1570
- `is_1919_global_topic` — L1617
- `_strip_topic_modifiers` — L1628
- `apply_1919_global_guardrails` — L1646
- `build_1919_global_cover_prompt` — L1675
- `build_shot_blueprint` — L1704
- `ffprobe_duration` — L1730
- `ffprobe_video_size` — L1741
- `_video_decode_probe` — L1762
- `ffmpeg` — L1780

---

### 第一步：双导演生成剧本
Range: **L1792 – L3231** (1440 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L2525-3231 (707 lines)

**Functions:**
- `_extract_json_array` — L1793
- `_extract_json_object` — L1803
- `_voice_for_speaker` — L1813
- `_adsd_gender_from_voice` — L1849
- `_adsd_infer_gender_from_speaker` — L1857
- `_adsd_gender_lock_phrase` — L1866
- `_adsd_visual_subject_has_gender_conflict` — L1881
- `_adsd_default_roles` — L1893
- `_adsd_allows_media_role` — L1898
- `_adsd_role_candidates` — L1906
- `_adsd_dialogue_shape` — L1922
- `_finalize_adsd_turns` — L1931
- `_parse_adsd_override_turns` — L1954
- `_parse_timecode_seconds` — L2017
- `_clean_override_line_text` — L2026
- `_parse_override_script_text` — L2032
- `_adsd_pov_contract` — L2066
- `_generate_adsd_dialogue_turns` — L2076
- `_adsd_immersion_qa_rewrite_turns` — L2192
- `_adsd_visual_contract` — L2246
- `step1_script` — L2298
- `_write_ads_retention_qa` — L3175

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L3232 – L4301** (1070 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L3307
- `_ADSD_POLICY_REWRITE_TERMS` — L3313
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L3404

**Functions:**
- `_openai_tts_fallback` — L3233
- `_edge_tts_fallback` — L3279
- `_sanitize_for_external_api` — L3322
- `_is_content_policy_error` — L3331
- `_rewrite_adsd_tts_text_for_policy` — L3345
- `_record_adsd_tts_rewrite` — L3385
- `_build_silence_mp3` — L3410
- `_audio_duration_seconds` — L3423
- `_text_to_audio_master_voice_timed` — L3435
- `_text_to_audio_master_voice` — L3560
- `step2_master_voice` — L3663
- `_tts_turn_to_audio` — L3791
- `_asr_verify_dialogue_audio` — L3853
- `_asr_verify_dialogue_turns` — L3895
- `_normalize_cn_number_token` — L3937
- `_compact_zh_text` — L3959
- `_write_adsd_asr_text_qa` — L3966
- `_write_adsd_speaker_focus_qa` — L4005
- `_write_adsd_gender_voice_qa` — L4065
- `step2_dialogue_voice` — L4118

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L4302 – L4853** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L4309-4431 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L4432-4466 (35 lines)
- _第二层：字符数插值_ — L4467-4491 (25 lines)
- _第三层：silencedetect 物理校准_ — L4492-4853 (362 lines)

**Functions:**
- `_detect_silences` — L4310
- `_calibrate_boundaries` — L4345
- `_enforce_monotonic` — L4379
- `_manual_override_segments` — L4391
- `_calc_sentence_boundaries` — L4412
- `step345_timeline` — L4523
- `_analyze_bgm_energy_cuts` — L4582
- `_snap_bgm_only_boundaries` — L4645
- `step345_bgm_only_timeline` — L4705

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L4854 – L7085** (2232 lines)

**Sub-sections:**
- _审批流程_ — L6919-6975 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L6976-7085 (110 lines)

**Functions:**
- `_extract_img_url` — L4855
- `_extract_img_urls` — L4877
- `_extract_video_url` — L4910
- `_count_bands` — L4935
- `_detect_contact_sheet_like_image` — L4947
- `_guess_upload_mime` — L5001
- `_upload_to_weryai` — L5024
- `_send_for_approval` — L5056
- `_wait_approval` — L5120
- `_render_still_segment` — L5132
- `_scene_text_visual_alignment` — L5146
- `_write_text_visual_alignment_qa` — L5182
- `_scene_motion_action_plan` — L5205
- `_ensure_motion_action_plan` — L5259
- `_motion_action_block` — L5268
- `_motion_plan_for_qa` — L5290
- `_write_motion_action_plan_qa` — L5300
- `_write_motion_bridge_refs_qa` — L5330
- `_motion_bridge_ref_prompt` — L5337
- `generate_motion_bridge_refs_gpt_image2` — L5370
- `generate_image` — L5483
- `generate_storyboard_images_gpt_image2` — L5530
- `_storyboard_grid_aspect` — L5715
- `_storyboard_grid_cols_rows` — L5722
- `_storyboard_grid_prompt` — L5744
- `_storyboard_grid_prompt_limit` — L5775
- `_is_prompt_limit_response` — L5779
- `_production_storyboard_prompt` — L5785
- `_write_production_storyboard_page_qa` — L5819
- `_character_sheet_prompt` — L5829
- `_write_character_sheet_qa` — L5927
- `generate_character_sheet_gpt_image2` — L5937
- `generate_production_storyboard_page_gpt_image2` — L6037
- `_qa_clean_storyboard_panel` — L6100
- `_crop_storyboard_grid_panels` — L6281
- `generate_storyboard_grid_gpt_image2` — L6328
- `_gpt_image2_direct_annotated_aspect` — L6559
- `_gpt_image2_direct_annotated_prompt` — L6566
- `generate_gpt_image2_direct_annotated_storyboards` — L6596
- `_llm_bgm_description` — L6697
- `generate_bgm` — L6736
- `step6_parallel` — L6827

---

### 第 6.5 步：动态化（可选，--with-motion 开启）
Range: **L7086 – L10722** (3637 lines)

**Functions:**
- `_generate_motion_prompts` — L7089
- `_motion_tasks_file` — L7156
- `_motion_qa_file` — L7160
- `_append_motion_qa` — L7164
- `_finalize_motion_qa` — L7188
- `_lip_sync_tasks_file` — L7272
- `_load_motion_tasks` — L7276
- `_save_motion_task` — L7286
- `_remove_motion_task` — L7294
- `_load_lip_sync_tasks` — L7301
- `_save_lip_sync_task` — L7311
- `_remove_lip_sync_task` — L7318
- `_video_visual_motion_qa` — L7325
- `_motion_output_qa` — L7397
- `_has_audio_stream` — L7442
- `_normalize_motion_video` — L7453
- `_motion_poll_and_download` — L7503
- `_build_motion_video_prompt` — L7554
- `_short_board_text` — L7584
- `_wrap_board_text` — L7591
- `_storyboard_font` — L7622
- `_draw_storyboard_arrow` — L7637
- `_build_annotated_storyboard_reference` — L7651
- `_plain_caption_text` — L7752
- `_werydance_caption_request` — L7760
- `_werydance_caption_instruction` — L7787
- `_werydance_negative_prompt` — L7799
- `_motion_reference_prompt` — L7805
- `_motion_audio_dub_prompt` — L7828
- `_motion_audio_dub_poll_and_download` — L7862
- `_try_motion_audio_dub_video` — L7927
- `_try_motion_reference_video` — L8062
- `_motion_one_scene` — L8178
- `_grid_multiref_tasks_file` — L8307
- `_previs_page_tasks_file` — L8311
- `_load_grid_multiref_tasks` — L8315
- `_load_previs_page_tasks` — L8325
- `_save_grid_multiref_task` — L8335
- `_save_previs_page_task` — L8342
- `_remove_grid_multiref_task` — L8349
- `_remove_previs_page_task` — L8356
- `_poll_video_task_download` — L8363
- `_grid_multiref_group_size` — L8412
- `_grid_multiref_duration` — L8420
- `_grid_multiref_segment_max_stretch` — L8436
- `_grid_multiref_prompt` — L8444
- `_write_grid_multiref_motion_qa` — L8492
- `_write_previs_page_motion_qa` — L8502
- `_write_storyboard_trailer_qa` — L8512
- `_write_character_trailer_qa` — L8522
- `_write_grid_multiref_segment_qa` — L8532
- `_motion_compare_record` — L8542
- `_write_storyboard_motion_compare_qa` — L8564
- `_scene_segment_duration` — L8600
- `_apply_grid_multiref_segments` — L8619
- `_previs_page_duration` — L8813
- `_previs_page_group_prompt` — L8823
- `_previs_page_groups` — L8849
- `_storyboard_trailer_duration` — L8864
- `_storyboard_trailer_prompt` — L8874
- `_character_trailer_max_shots` — L8902
- `_character_trailer_shot_duration` — L8910
- `_character_trailer_prompt` — L8924
- `_concat_character_trailer_segments` — L8939
- `_generate_character_trailer_motion` — L8978
- `_multi_trailer_prompt_for_group` — L9086
- `_generate_multi_trailer_segments` — L9109
- `_generate_storyboard_trailer_motion` — L9220
- `_generate_previs_page_motion_segments` — L9295
- `_generate_grid_multiref_motion_segments` — L9407
- `_grid_multiref_concat_groups` — L9577
- `_grid_multiref_concat_groups_partial` — L9594
- `_grid_multiref_concat_paths` — L9612
- `_lip_sync_slot_duration` — L9643
- `_adsd_lip_sync_prompt` — L9650
- `_adsd_broll_motion_prompt` — L9689
- `_adsd_almighty_audio_dub_prompt` — L9726
- `_postprocess_lip_sync_segment` — L9761
- `_postprocess_audio_dub_segment` — L9829
- `_lips_change_repair_segment` — L9905
- `_load_lips_change_requested_turns` — L9990
- `_parse_turn_set` — L10007
- `_load_motion_voice_repair_turns` — L10029
- `_voice_assets_file` — L10041
- `_load_voice_assets` — L10048
- `_select_voice_asset_reference` — L10067
- `_lip_sync_poll_download_and_process` — L10133
- `_lip_sync_one_scene` — L10197
- `step66_adsd_lip_sync` — L10397
- `step65_motion` — L10613
- `step65_grid_multiref_motion_qa` — L10695

---

### 第七步：拼接视频轨
Range: **L10723 – L10892** (170 lines)

**Functions:**
- `step7_concat` — L10724

---

### 第八步：生成 ASS 字幕
Range: **L10893 – L11556** (664 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L10932-11556 (625 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L10894
- `step8_subtitles` — L10920
- `_read_output_json` — L11288
- `_qa_file_pass` — L11299
- `_ass_has_dialogue` — L11306
- `_write_adsd_delivery_qa` — L11316
- `_write_bgm_only_qa` — L11445

---

### 第九步：最终合成
Range: **L11557 – L11795** (239 lines)

**Functions:**
- `step9_render` — L11558

---

### 第十步：推送 Telegram
Range: **L11796 – L13382** (1587 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L12896-13211 (316 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L13212-13216 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L13217-13258 (42 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L13259-13304 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L13305-13382 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L12165
- `PANTONE_FALLBACK` — L12192
- `FESTIVAL_DATE_TAG` — L12305

**Functions:**
- `_generate_caption` — L11797
- `_overlay_title_on_cover` — L12035
- `_prepare_tg_photo` — L12145
- `_get_pantone_for_date` — L12195
- `_llm_bottom_note` — L12220
- `_get_bottom_note` — L12249
- `_get_date_tag` — L12327
- `_shrink_to_b64` — L12349
- `_llm_check_scenes_anomalies` — L12365
- `_llm_check_cover_unique` — L12418
- `_llm_check_cover_quality` — L12448
- `_try_almanac_cover` — L12490
- `_generate_cover_image` — L12661
- `_async_kickoff_cover_caption` — L12903
- `_await_async_cover_caption` — L12933
- `step10_deliver` — L12957

---

### 主流程
Range: **L13383 – L13508** (126 lines)

**Functions:**
- `_print_execution_plan` — L13384
- `main` — L13432

---
