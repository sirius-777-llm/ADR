# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (15236 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-1874 (1753 lines · 54 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L1875-3488 (1614 lines · 22 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L3489-4590 (1102 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L4591-5142 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L5143-8139 (2997 lines · 62 fn · 5 sub)
- [`第 6.5 步：动态化（可选，--with-motion 开启）`](#第-6-5-步-动态化-可选---with-motion-开启) — L8140-12248 (4109 lines · 99 fn · 4 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L12249-12418 (170 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L12419-13210 (792 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L13211-13451 (241 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L13452-15066 (1615 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L15067-15236 (170 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L1874** (1753 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L298-423 (126 lines)
- _三类 turn 区分 (silent_b PR)_ — L424-1002 (579 lines)
- _工具函数_ — L1003-1352 (350 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1353-1874 (522 lines)

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
- `VOICE_ASSET_AUDIO_DUB_EXPERIMENT` — L754
- `VOICE_ASSET_AUDIO_DUB_PARTIAL_OK` — L762
- `MOTION_VISUAL_QA` — L766
- `MOTION_VOICE_REPAIR` — L774
- `MOTION_VOICE_STRICT_LOCK` — L779
- `WERYDANCE_CAPTIONS` — L784
- `ADSD_ONSITE_POV_MODE` — L796
- `ADSD_LIPS_CHANGE_REPAIR` — L801
- `ADSD_LIPS_CHANGE_ALL` — L806
- `ADS_REPORTER_MODE` — L817
- `ADS_STORYBOARD_FLOW_DEFAULT` — L834
- `ADS_RETENTION_MODE` — L847
- `ADSD_MODE_NAME` — L853
- `EMOTION_STYLE` — L982
- `EMOTION_STYLE_BRIGHT` — L994
- `_TG_DASHBOARD_STAGES` — L1016
- `_TG_NOISY_PATTERNS` — L1031
- `_TG_IMMEDIATE_PATTERNS` — L1049
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1282
- `_TOPIC_MODIFIERS` — L1706
- `_TONE_PANTONE_OVERRIDE` — L1723

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
- `_llm_assign_voice_assets` — L505
- `_apply_llm_voice_assignment` — L629
- `log` — L1004
- `_tg_send_raw` — L1072
- `_tg_matches` — L1088
- `_tg_summarize` — L1092
- `_tg_dashboard_stage_for` — L1099
- `_tg_progress_bar` — L1107
- `_tg_dashboard_text` — L1113
- `_tg_dashboard_update` — L1131
- `_tg_maybe_digest` — L1168
- `tg` — L1183
- `_wait_image_submit_slot` — L1232
- `_wait_motion_submit_slot` — L1245
- `_is_rate_limited_error` — L1258
- `_is_rate_limited_response` — L1268
- `_inject_image2_quality_suffix` — L1290
- `submit_text_to_image` — L1304
- `req_post` — L1334
- `req_get` — L1348
- `_tg_probe_send` — L1356
- `_tg_probe_delete` — L1376
- `_tg_upload_with_probe_gap` — L1389
- `poll` — L1429
- `poll_podcast` — L1454
- `poll_task_status` — L1476
- `poll_storyboard_task` — L1498
- `chat` — L1524
- `pick_image_model` — L1552
- `detect_topic_meta` — L1577
- `_topic_culture_guard` — L1627
- `_write_cultural_visual_qa` — L1653
- `is_1919_global_topic` — L1700
- `_strip_topic_modifiers` — L1711
- `apply_1919_global_guardrails` — L1729
- `build_1919_global_cover_prompt` — L1758
- `build_shot_blueprint` — L1787
- `ffprobe_duration` — L1813
- `ffprobe_video_size` — L1824
- `_video_decode_probe` — L1845
- `ffmpeg` — L1863

---

### 第一步：双导演生成剧本
Range: **L1875 – L3488** (1614 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L2782-3488 (707 lines)

**Functions:**
- `_extract_json_array` — L1876
- `_extract_json_object` — L1886
- `_voice_for_speaker` — L1896
- `_adsd_gender_from_voice` — L1932
- `_adsd_infer_gender_from_speaker` — L1940
- `_adsd_gender_lock_phrase` — L1949
- `_adsd_visual_subject_has_gender_conflict` — L1964
- `_adsd_default_roles` — L1976
- `_adsd_allows_media_role` — L1981
- `_adsd_role_candidates` — L1989
- `_adsd_dialogue_shape` — L2005
- `_finalize_adsd_turns` — L2014
- `_parse_adsd_override_turns` — L2048
- `_parse_timecode_seconds` — L2139
- `_clean_override_line_text` — L2148
- `_parse_override_script_text` — L2154
- `_adsd_pov_contract` — L2188
- `_generate_adsd_dialogue_turns` — L2198
- `_adsd_immersion_qa_rewrite_turns` — L2445
- `_adsd_visual_contract` — L2503
- `step1_script` — L2555
- `_write_ads_retention_qa` — L3432

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L3489 – L4590** (1102 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L3564
- `_ADSD_POLICY_REWRITE_TERMS` — L3570
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L3661

**Functions:**
- `_openai_tts_fallback` — L3490
- `_edge_tts_fallback` — L3536
- `_sanitize_for_external_api` — L3579
- `_is_content_policy_error` — L3588
- `_rewrite_adsd_tts_text_for_policy` — L3602
- `_record_adsd_tts_rewrite` — L3642
- `_build_silence_mp3` — L3667
- `_audio_duration_seconds` — L3680
- `_text_to_audio_master_voice_timed` — L3692
- `_text_to_audio_master_voice` — L3817
- `step2_master_voice` — L3920
- `_tts_turn_to_audio` — L4048
- `_asr_verify_dialogue_audio` — L4110
- `_asr_verify_dialogue_turns` — L4172
- `_normalize_cn_number_token` — L4214
- `_compact_zh_text` — L4236
- `_write_adsd_asr_text_qa` — L4243
- `_write_adsd_speaker_focus_qa` — L4282
- `_write_adsd_gender_voice_qa` — L4342
- `step2_dialogue_voice` — L4395

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L4591 – L5142** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L4598-4720 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L4721-4755 (35 lines)
- _第二层：字符数插值_ — L4756-4780 (25 lines)
- _第三层：silencedetect 物理校准_ — L4781-5142 (362 lines)

**Functions:**
- `_detect_silences` — L4599
- `_calibrate_boundaries` — L4634
- `_enforce_monotonic` — L4668
- `_manual_override_segments` — L4680
- `_calc_sentence_boundaries` — L4701
- `step345_timeline` — L4812
- `_analyze_bgm_energy_cuts` — L4871
- `_snap_bgm_only_boundaries` — L4934
- `step345_bgm_only_timeline` — L4994

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L5143 – L8139** (2997 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L6216-6266 (51 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L6267-6538 (272 lines)
- _Speaker IP Card (2026-05-21)_ — L6539-7972 (1434 lines)
- _审批流程_ — L7973-8029 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L8030-8139 (110 lines)

**Top-level constants:**
- `CHARACTER_META_GRID_COSTUMES` — L6222
- `CHARACTER_META_GRID_POSES` — L6223
- `CHARACTER_META_GRID_SCENES` — L6224
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L6227

**Functions:**
- `_extract_img_url` — L5144
- `_extract_img_urls` — L5166
- `_extract_video_url` — L5199
- `_count_bands` — L5224
- `_detect_contact_sheet_like_image` — L5236
- `_guess_upload_mime` — L5290
- `_upload_to_weryai` — L5313
- `_send_for_approval` — L5345
- `_wait_approval` — L5409
- `_render_still_segment` — L5421
- `_scene_text_visual_alignment` — L5435
- `_write_text_visual_alignment_qa` — L5471
- `_scene_motion_action_plan` — L5494
- `_ensure_motion_action_plan` — L5548
- `_motion_action_block` — L5557
- `_motion_plan_for_qa` — L5579
- `_write_motion_action_plan_qa` — L5589
- `_write_motion_bridge_refs_qa` — L5619
- `_motion_bridge_ref_prompt` — L5626
- `generate_motion_bridge_refs_gpt_image2` — L5659
- `generate_image` — L5772
- `generate_storyboard_images_gpt_image2` — L5819
- `_storyboard_grid_aspect` — L6004
- `_storyboard_grid_cols_rows` — L6011
- `_storyboard_grid_prompt` — L6033
- `_storyboard_grid_prompt_limit` — L6064
- `_is_prompt_limit_response` — L6068
- `_production_storyboard_prompt` — L6074
- `_write_production_storyboard_page_qa` — L6108
- `_character_sheet_prompt` — L6118
- `_is_audit_blocked` — L6244
- `_paraphrase_sensitive_dialogue` — L6257
- `_llm_infer_meta_grid_template` — L6324
- `_resolve_meta_grid_template` — L6381
- `_infer_meta_grid_costume` — L6424
- `_infer_meta_grid_pose` — L6469
- `_adsd_meta_grid_call_prompt` — L6512
- `_speaker_ips_dir` — L6542
- `_list_speaker_ips` — L6549
- `_match_speaker_ip` — L6563
- `_build_speaker_ip_context_for_script` — L6583
- `_save_speaker_ip` — L6629
- `_record_speaker_usage_history` — L6637
- `_format_speaker_usage_history_for_prompt` — L6679
- `_character_meta_grid_cache_dir` — L6697
- `_character_meta_grid_cache_path` — L6705
- `_character_meta_grid_path` — L6711
- `generate_character_meta_grid_gpt_image2` — L6717
- `_generate_all_character_meta_grids` — L6836
- `_write_character_sheet_qa` — L6877
- `generate_character_sheet_gpt_image2` — L6887
- `generate_production_storyboard_page_gpt_image2` — L6987
- `_qa_clean_storyboard_panel` — L7050
- `_crop_storyboard_grid_panels` — L7231
- `generate_storyboard_grid_gpt_image2` — L7278
- `_gpt_image2_direct_annotated_aspect` — L7509
- `_gpt_image2_direct_annotated_prompt` — L7516
- `generate_gpt_image2_direct_annotated_storyboards` — L7546
- `_llm_bgm_description` — L7647
- `_bgm_contains_vocals` — L7686
- `generate_bgm` — L7720
- `step6_parallel` — L7819

---

### 第 6.5 步：动态化（可选，--with-motion 开启）
Range: **L8140 – L12248** (4109 lines)

**Sub-sections:**
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L11990-12032 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L12033-12070 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回主音轨_ — L12071-12203 (133 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L12204-12248 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L8143
- `_motion_tasks_file` — L8210
- `_motion_qa_file` — L8214
- `_append_motion_qa` — L8218
- `_finalize_motion_qa` — L8242
- `_lip_sync_tasks_file` — L8326
- `_load_motion_tasks` — L8330
- `_save_motion_task` — L8340
- `_remove_motion_task` — L8348
- `_load_lip_sync_tasks` — L8355
- `_save_lip_sync_task` — L8365
- `_remove_lip_sync_task` — L8372
- `_video_visual_motion_qa` — L8379
- `_motion_output_qa` — L8451
- `_has_audio_stream` — L8496
- `_normalize_motion_video` — L8507
- `_motion_poll_and_download` — L8557
- `_build_motion_video_prompt` — L8608
- `_short_board_text` — L8638
- `_wrap_board_text` — L8645
- `_storyboard_font` — L8676
- `_draw_storyboard_arrow` — L8691
- `_build_annotated_storyboard_reference` — L8705
- `_plain_caption_text` — L8806
- `_werydance_caption_request` — L8814
- `_werydance_caption_instruction` — L8841
- `_werydance_negative_prompt` — L8853
- `_motion_reference_prompt` — L8867
- `_motion_audio_dub_prompt` — L8890
- `_motion_audio_dub_poll_and_download` — L8924
- `_try_motion_audio_dub_video` — L8989
- `_try_motion_reference_video` — L9124
- `_motion_one_scene` — L9240
- `_grid_multiref_tasks_file` — L9369
- `_previs_page_tasks_file` — L9373
- `_load_grid_multiref_tasks` — L9377
- `_load_previs_page_tasks` — L9387
- `_save_grid_multiref_task` — L9397
- `_save_previs_page_task` — L9404
- `_remove_grid_multiref_task` — L9411
- `_remove_previs_page_task` — L9418
- `_poll_video_task_download` — L9425
- `_grid_multiref_group_size` — L9474
- `_grid_multiref_duration` — L9482
- `_grid_multiref_segment_max_stretch` — L9498
- `_grid_multiref_prompt` — L9506
- `_write_grid_multiref_motion_qa` — L9554
- `_write_previs_page_motion_qa` — L9564
- `_write_storyboard_trailer_qa` — L9574
- `_write_character_trailer_qa` — L9584
- `_write_grid_multiref_segment_qa` — L9594
- `_motion_compare_record` — L9604
- `_write_storyboard_motion_compare_qa` — L9626
- `_scene_segment_duration` — L9662
- `_apply_grid_multiref_segments` — L9681
- `_previs_page_duration` — L9875
- `_previs_page_group_prompt` — L9885
- `_previs_page_groups` — L9911
- `_storyboard_trailer_duration` — L9926
- `_storyboard_trailer_prompt` — L9936
- `_character_trailer_max_shots` — L9964
- `_character_trailer_shot_duration` — L9972
- `_character_trailer_prompt` — L9986
- `_concat_character_trailer_segments` — L10001
- `_generate_character_trailer_motion` — L10040
- `_multi_trailer_prompt_for_group` — L10148
- `_generate_multi_trailer_segments` — L10171
- `_generate_storyboard_trailer_motion` — L10282
- `_generate_previs_page_motion_segments` — L10357
- `_generate_grid_multiref_motion_segments` — L10469
- `_grid_multiref_concat_groups` — L10639
- `_grid_multiref_concat_groups_partial` — L10656
- `_grid_multiref_concat_paths` — L10674
- `_lip_sync_slot_duration` — L10705
- `_adsd_lip_sync_prompt` — L10712
- `_adsd_broll_motion_prompt` — L10758
- `_adsd_silent_b_motion_prompt` — L10800
- `_adsd_narrated_b_audio_dub_prompt` — L10835
- `_adsd_almighty_audio_dub_prompt` — L10879
- `_postprocess_lip_sync_segment` — L10914
- `_detect_audio_leading_silence` — L10982
- `_postprocess_audio_dub_segment` — L11004
- `_lips_change_repair_segment` — L11110
- `_load_lips_change_requested_turns` — L11195
- `_parse_turn_set` — L11212
- `_load_motion_voice_repair_turns` — L11234
- `_voice_assets_file` — L11246
- `_load_voice_assets` — L11253
- `_select_voice_asset_reference` — L11272
- `_lip_sync_poll_download_and_process` — L11338
- `_lip_sync_one_scene` — L11402
- `step66_adsd_lip_sync` — L11664
- `step65_motion` — L11880
- `step65_grid_multiref_motion_qa` — L11962
- `_sanitize_scene_for_state` — L11991
- `_save_pipeline_state` — L12010
- `_retime_after_audio_dub` — L12034
- `_build_voice_clone_hybrid_audio` — L12072
- `_build_dynamic_bgm` — L12205

---

### 第七步：拼接视频轨
Range: **L12249 – L12418** (170 lines)

**Functions:**
- `step7_concat` — L12250

---

### 第八步：生成 ASS 字幕
Range: **L12419 – L13210** (792 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L12542-13210 (669 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L12420
- `_word_timings_for_subtitle_align` — L12446
- `_align_segments_via_asr` — L12487
- `step8_subtitles` — L12530
- `_read_output_json` — L12942
- `_qa_file_pass` — L12953
- `_ass_has_dialogue` — L12960
- `_write_adsd_delivery_qa` — L12970
- `_write_bgm_only_qa` — L13099

---

### 第九步：最终合成
Range: **L13211 – L13451** (241 lines)

**Functions:**
- `step9_render` — L13212

---

### 第十步：推送 Telegram
Range: **L13452 – L15066** (1615 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L14552-14873 (322 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L14874-14878 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L14879-14942 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L14943-14988 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L14989-15066 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L13821
- `PANTONE_FALLBACK` — L13848
- `FESTIVAL_DATE_TAG` — L13961

**Functions:**
- `_generate_caption` — L13453
- `_overlay_title_on_cover` — L13691
- `_prepare_tg_photo` — L13801
- `_get_pantone_for_date` — L13851
- `_llm_bottom_note` — L13876
- `_get_bottom_note` — L13905
- `_get_date_tag` — L13983
- `_shrink_to_b64` — L14005
- `_llm_check_scenes_anomalies` — L14021
- `_llm_check_cover_unique` — L14074
- `_llm_check_cover_quality` — L14104
- `_try_almanac_cover` — L14146
- `_generate_cover_image` — L14317
- `_async_kickoff_cover_caption` — L14559
- `_await_async_cover_caption` — L14589
- `step10_deliver` — L14613

---

### 主流程
Range: **L15067 – L15236** (170 lines)

**Functions:**
- `_print_execution_plan` — L15068
- `main` — L15116

---
