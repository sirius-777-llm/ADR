# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (13088 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-100 (100 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L101-1560 (1460 lines · 45 fn · 3 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L1561-2989 (1429 lines · 22 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L2990-4059 (1070 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L4060-4611 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L4612-6834 (2223 lines · 42 fn · 2 sub)
- [`第 6.5 步：动态化（可选，--with-motion 开启）`](#第-6-5-步-动态化-可选---with-motion-开启) — L6835-10382 (3548 lines · 91 fn · 0 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L10383-10552 (170 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L10553-11206 (654 lines · 7 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L11207-11445 (239 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L11446-12962 (1517 lines · 16 fn · 4 sub)
- [`主流程`](#主流程) — L12963-13088 (126 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L100** (100 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-100 (72 lines)

**Functions:**
- `get_almanac_data` — L36

---

### 配置
Range: **L101 – L1560** (1460 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L269-713 (445 lines)
- _工具函数_ — L714-1038 (325 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1039-1560 (522 lines)

**Top-level constants:**
- `HEADERS` — L114
- `VIDEO_FORMAT` — L122
- `BGM_ONLY_REQUESTED` — L130
- `ADS_DIALOGUE_MODE` — L137
- `GPT_IMAGE2_STORYBOARD` — L146
- `STORYBOARD_REFERENCE_MOTION` — L150
- `STORYBOARD_ANNOTATED_MOTION` — L154
- `GPT_IMAGE2_DIRECT_ANNOTATED_STORYBOARD` — L158
- `GPT_IMAGE2_STORYBOARD_GRID` — L163
- `ADSD_STORYBOARD_GRID` — L171
- `ADS_CHARACTER_SHEET_REQUESTED` — L177
- `STORYBOARD_GRID_MULTIREF_MOTION` — L181
- `STORYBOARD_GRID_MULTIREF_SEGMENTS` — L185
- `STORYBOARD_GRID_MULTIREF_MAIN` — L191
- `PREVIS_PAGE_MOTION` — L197
- `STORYBOARD_TRAILER_MODE` — L201
- `MOTION_ACTION_STORYBOARD` — L206
- `MOTION_BRIDGE_REFS` — L210
- `CHARACTER_TRAILER_MODE` — L214
- `STORYBOARD_TRAILER_MAIN` — L222
- `ADSD_LIP_SYNC_EXPERIMENT` — L235
- `ADSD_RICH_MOTION_PROMPT` — L243
- `ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT` — L247
- `ADSD_CONSECUTIVE_SPEAKER_BATCHING` — L261
- `ADSD_GENDER_FALLBACK_VOICE_ASSET` — L303
- `_ACTION_KEYWORDS_ZH` — L309
- `_EMOTION_KEYWORDS` — L359
- `_EMOTION_EXPRESSION_PHRASE` — L370
- `VOICE_ASSET_AUDIO_DUB_EXPERIMENT` — L449
- `VOICE_ASSET_AUDIO_DUB_PARTIAL_OK` — L457
- `MOTION_VISUAL_QA` — L461
- `MOTION_VOICE_REPAIR` — L469
- `MOTION_VOICE_STRICT_LOCK` — L474
- `WERYDANCE_CAPTIONS` — L479
- `ADSD_ONSITE_POV_MODE` — L491
- `ADSD_LIPS_CHANGE_REPAIR` — L496
- `ADSD_LIPS_CHANGE_ALL` — L501
- `ADS_REPORTER_MODE` — L512
- `ADS_RETENTION_MODE` — L527
- `ADSD_MODE_NAME` — L533
- `ADSD_VOICES` — L535
- `ADSD_MALE_VOICE_POOL` — L545
- `ADSD_FEMALE_VOICE_POOL` — L555
- `ADSD_MALE_VOICE_IDS` — L562
- `ADSD_FEMALE_VOICE_IDS` — L563
- `ADSD_VOICE_GENDER_BY_ID` — L564
- `EMOTION_STYLE` — L693
- `EMOTION_STYLE_BRIGHT` — L705
- `_TG_DASHBOARD_STAGES` — L727
- `_TG_NOISY_PATTERNS` — L742
- `_TG_IMMEDIATE_PATTERNS` — L760
- `_TOPIC_MODIFIERS` — L1392
- `_TONE_PANTONE_OVERRIDE` — L1409

**Functions:**
- `_is_action_scene` — L318
- `_wuxia_action_panel_prompt` — L325
- `_action_motion_fragment` — L347
- `_infer_emotion_from_text` — L384
- `_emotion_expression_phrase` — L399
- `_infer_needs_lip_sync` — L406
- `_voice_asset_id_for_speaker` — L425
- `log` — L715
- `_tg_send_raw` — L783
- `_tg_matches` — L799
- `_tg_summarize` — L803
- `_tg_dashboard_stage_for` — L810
- `_tg_progress_bar` — L818
- `_tg_dashboard_text` — L824
- `_tg_dashboard_update` — L842
- `_tg_maybe_digest` — L879
- `tg` — L894
- `_wait_image_submit_slot` — L943
- `_wait_motion_submit_slot` — L956
- `_is_rate_limited_error` — L969
- `_is_rate_limited_response` — L979
- `submit_text_to_image` — L991
- `req_post` — L1020
- `req_get` — L1034
- `_tg_probe_send` — L1042
- `_tg_probe_delete` — L1062
- `_tg_upload_with_probe_gap` — L1075
- `poll` — L1115
- `poll_podcast` — L1140
- `poll_task_status` — L1162
- `poll_storyboard_task` — L1184
- `chat` — L1210
- `pick_image_model` — L1238
- `detect_topic_meta` — L1263
- `_topic_culture_guard` — L1313
- `_write_cultural_visual_qa` — L1339
- `is_1919_global_topic` — L1386
- `_strip_topic_modifiers` — L1397
- `apply_1919_global_guardrails` — L1415
- `build_1919_global_cover_prompt` — L1444
- `build_shot_blueprint` — L1473
- `ffprobe_duration` — L1499
- `ffprobe_video_size` — L1510
- `_video_decode_probe` — L1531
- `ffmpeg` — L1549

---

### 第一步：双导演生成剧本
Range: **L1561 – L2989** (1429 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L2299-2989 (691 lines)

**Functions:**
- `_extract_json_array` — L1562
- `_extract_json_object` — L1572
- `_voice_for_speaker` — L1582
- `_adsd_gender_from_voice` — L1618
- `_adsd_infer_gender_from_speaker` — L1626
- `_adsd_gender_lock_phrase` — L1635
- `_adsd_visual_subject_has_gender_conflict` — L1650
- `_adsd_default_roles` — L1662
- `_adsd_allows_media_role` — L1667
- `_adsd_role_candidates` — L1675
- `_adsd_dialogue_shape` — L1691
- `_finalize_adsd_turns` — L1700
- `_parse_adsd_override_turns` — L1723
- `_parse_timecode_seconds` — L1786
- `_clean_override_line_text` — L1795
- `_parse_override_script_text` — L1801
- `_adsd_pov_contract` — L1835
- `_generate_adsd_dialogue_turns` — L1845
- `_adsd_immersion_qa_rewrite_turns` — L1966
- `_adsd_visual_contract` — L2020
- `step1_script` — L2072
- `_write_ads_retention_qa` — L2933

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L2990 – L4059** (1070 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L3065
- `_ADSD_POLICY_REWRITE_TERMS` — L3071
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L3162

**Functions:**
- `_openai_tts_fallback` — L2991
- `_edge_tts_fallback` — L3037
- `_sanitize_for_external_api` — L3080
- `_is_content_policy_error` — L3089
- `_rewrite_adsd_tts_text_for_policy` — L3103
- `_record_adsd_tts_rewrite` — L3143
- `_build_silence_mp3` — L3168
- `_audio_duration_seconds` — L3181
- `_text_to_audio_master_voice_timed` — L3193
- `_text_to_audio_master_voice` — L3318
- `step2_master_voice` — L3421
- `_tts_turn_to_audio` — L3549
- `_asr_verify_dialogue_audio` — L3611
- `_asr_verify_dialogue_turns` — L3653
- `_normalize_cn_number_token` — L3695
- `_compact_zh_text` — L3717
- `_write_adsd_asr_text_qa` — L3724
- `_write_adsd_speaker_focus_qa` — L3763
- `_write_adsd_gender_voice_qa` — L3823
- `step2_dialogue_voice` — L3876

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L4060 – L4611** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L4067-4189 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L4190-4224 (35 lines)
- _第二层：字符数插值_ — L4225-4249 (25 lines)
- _第三层：silencedetect 物理校准_ — L4250-4611 (362 lines)

**Functions:**
- `_detect_silences` — L4068
- `_calibrate_boundaries` — L4103
- `_enforce_monotonic` — L4137
- `_manual_override_segments` — L4149
- `_calc_sentence_boundaries` — L4170
- `step345_timeline` — L4281
- `_analyze_bgm_energy_cuts` — L4340
- `_snap_bgm_only_boundaries` — L4403
- `step345_bgm_only_timeline` — L4463

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L4612 – L6834** (2223 lines)

**Sub-sections:**
- _审批流程_ — L6668-6724 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L6725-6834 (110 lines)

**Functions:**
- `_extract_img_url` — L4613
- `_extract_img_urls` — L4635
- `_extract_video_url` — L4668
- `_count_bands` — L4693
- `_detect_contact_sheet_like_image` — L4705
- `_guess_upload_mime` — L4759
- `_upload_to_weryai` — L4782
- `_send_for_approval` — L4814
- `_wait_approval` — L4878
- `_render_still_segment` — L4890
- `_scene_text_visual_alignment` — L4904
- `_write_text_visual_alignment_qa` — L4940
- `_scene_motion_action_plan` — L4963
- `_ensure_motion_action_plan` — L5014
- `_motion_action_block` — L5023
- `_motion_plan_for_qa` — L5045
- `_write_motion_action_plan_qa` — L5055
- `_write_motion_bridge_refs_qa` — L5085
- `_motion_bridge_ref_prompt` — L5092
- `generate_motion_bridge_refs_gpt_image2` — L5125
- `generate_image` — L5238
- `generate_storyboard_images_gpt_image2` — L5285
- `_storyboard_grid_aspect` — L5470
- `_storyboard_grid_cols_rows` — L5477
- `_storyboard_grid_prompt` — L5499
- `_storyboard_grid_prompt_limit` — L5530
- `_is_prompt_limit_response` — L5534
- `_production_storyboard_prompt` — L5540
- `_write_production_storyboard_page_qa` — L5574
- `_character_sheet_prompt` — L5584
- `_write_character_sheet_qa` — L5682
- `generate_character_sheet_gpt_image2` — L5692
- `generate_production_storyboard_page_gpt_image2` — L5786
- `_qa_clean_storyboard_panel` — L5849
- `_crop_storyboard_grid_panels` — L6030
- `generate_storyboard_grid_gpt_image2` — L6077
- `_gpt_image2_direct_annotated_aspect` — L6308
- `_gpt_image2_direct_annotated_prompt` — L6315
- `generate_gpt_image2_direct_annotated_storyboards` — L6345
- `_llm_bgm_description` — L6446
- `generate_bgm` — L6485
- `step6_parallel` — L6576

---

### 第 6.5 步：动态化（可选，--with-motion 开启）
Range: **L6835 – L10382** (3548 lines)

**Functions:**
- `_generate_motion_prompts` — L6838
- `_motion_tasks_file` — L6905
- `_motion_qa_file` — L6909
- `_append_motion_qa` — L6913
- `_finalize_motion_qa` — L6937
- `_lip_sync_tasks_file` — L7021
- `_load_motion_tasks` — L7025
- `_save_motion_task` — L7035
- `_remove_motion_task` — L7043
- `_load_lip_sync_tasks` — L7050
- `_save_lip_sync_task` — L7060
- `_remove_lip_sync_task` — L7067
- `_video_visual_motion_qa` — L7074
- `_motion_output_qa` — L7146
- `_has_audio_stream` — L7191
- `_normalize_motion_video` — L7202
- `_motion_poll_and_download` — L7252
- `_build_motion_video_prompt` — L7303
- `_short_board_text` — L7333
- `_wrap_board_text` — L7340
- `_storyboard_font` — L7371
- `_draw_storyboard_arrow` — L7386
- `_build_annotated_storyboard_reference` — L7400
- `_plain_caption_text` — L7501
- `_werydance_caption_request` — L7509
- `_werydance_caption_instruction` — L7536
- `_werydance_negative_prompt` — L7548
- `_motion_reference_prompt` — L7554
- `_motion_audio_dub_prompt` — L7577
- `_motion_audio_dub_poll_and_download` — L7611
- `_try_motion_audio_dub_video` — L7676
- `_try_motion_reference_video` — L7811
- `_motion_one_scene` — L7927
- `_grid_multiref_tasks_file` — L8056
- `_previs_page_tasks_file` — L8060
- `_load_grid_multiref_tasks` — L8064
- `_load_previs_page_tasks` — L8074
- `_save_grid_multiref_task` — L8084
- `_save_previs_page_task` — L8091
- `_remove_grid_multiref_task` — L8098
- `_remove_previs_page_task` — L8105
- `_poll_video_task_download` — L8112
- `_grid_multiref_group_size` — L8161
- `_grid_multiref_duration` — L8169
- `_grid_multiref_segment_max_stretch` — L8185
- `_grid_multiref_prompt` — L8193
- `_write_grid_multiref_motion_qa` — L8212
- `_write_previs_page_motion_qa` — L8222
- `_write_storyboard_trailer_qa` — L8232
- `_write_character_trailer_qa` — L8242
- `_write_grid_multiref_segment_qa` — L8252
- `_motion_compare_record` — L8262
- `_write_storyboard_motion_compare_qa` — L8284
- `_scene_segment_duration` — L8320
- `_apply_grid_multiref_segments` — L8339
- `_previs_page_duration` — L8533
- `_previs_page_group_prompt` — L8543
- `_previs_page_groups` — L8569
- `_storyboard_trailer_duration` — L8584
- `_storyboard_trailer_prompt` — L8594
- `_character_trailer_max_shots` — L8622
- `_character_trailer_shot_duration` — L8630
- `_character_trailer_prompt` — L8644
- `_concat_character_trailer_segments` — L8659
- `_generate_character_trailer_motion` — L8698
- `_multi_trailer_prompt_for_group` — L8806
- `_generate_multi_trailer_segments` — L8829
- `_generate_storyboard_trailer_motion` — L8940
- `_generate_previs_page_motion_segments` — L9015
- `_generate_grid_multiref_motion_segments` — L9127
- `_grid_multiref_concat_groups` — L9279
- `_grid_multiref_concat_groups_partial` — L9296
- `_grid_multiref_concat_paths` — L9314
- `_lip_sync_slot_duration` — L9345
- `_adsd_lip_sync_prompt` — L9352
- `_adsd_broll_motion_prompt` — L9391
- `_adsd_almighty_audio_dub_prompt` — L9428
- `_postprocess_lip_sync_segment` — L9463
- `_postprocess_audio_dub_segment` — L9531
- `_lips_change_repair_segment` — L9607
- `_load_lips_change_requested_turns` — L9692
- `_parse_turn_set` — L9709
- `_load_motion_voice_repair_turns` — L9731
- `_voice_assets_file` — L9743
- `_load_voice_assets` — L9750
- `_select_voice_asset_reference` — L9769
- `_lip_sync_poll_download_and_process` — L9835
- `_lip_sync_one_scene` — L9899
- `step66_adsd_lip_sync` — L10095
- `step65_motion` — L10273
- `step65_grid_multiref_motion_qa` — L10355

---

### 第七步：拼接视频轨
Range: **L10383 – L10552** (170 lines)

**Functions:**
- `step7_concat` — L10384

---

### 第八步：生成 ASS 字幕
Range: **L10553 – L11206** (654 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L10592-11206 (615 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L10554
- `step8_subtitles` — L10580
- `_read_output_json` — L10948
- `_qa_file_pass` — L10959
- `_ass_has_dialogue` — L10966
- `_write_adsd_delivery_qa` — L10976
- `_write_bgm_only_qa` — L11095

---

### 第九步：最终合成
Range: **L11207 – L11445** (239 lines)

**Functions:**
- `step9_render` — L11208

---

### 第十步：推送 Telegram
Range: **L11446 – L12962** (1517 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L12546-12861 (316 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L12862-12866 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L12867-12908 (42 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L12909-12962 (54 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L11815
- `PANTONE_FALLBACK` — L11842
- `FESTIVAL_DATE_TAG` — L11955

**Functions:**
- `_generate_caption` — L11447
- `_overlay_title_on_cover` — L11685
- `_prepare_tg_photo` — L11795
- `_get_pantone_for_date` — L11845
- `_llm_bottom_note` — L11870
- `_get_bottom_note` — L11899
- `_get_date_tag` — L11977
- `_shrink_to_b64` — L11999
- `_llm_check_scenes_anomalies` — L12015
- `_llm_check_cover_unique` — L12068
- `_llm_check_cover_quality` — L12098
- `_try_almanac_cover` — L12140
- `_generate_cover_image` — L12311
- `_async_kickoff_cover_caption` — L12553
- `_await_async_cover_caption` — L12583
- `step10_deliver` — L12607

---

### 主流程
Range: **L12963 – L13088** (126 lines)

**Functions:**
- `_print_execution_plan` — L12964
- `main` — L13012

---
