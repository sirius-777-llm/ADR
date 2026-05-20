# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (14838 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-1874 (1753 lines · 54 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L1875-3485 (1611 lines · 22 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L3486-4587 (1102 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L4588-5139 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L5140-7751 (2612 lines · 56 fn · 4 sub)
- [`第 6.5 步：动态化（可选，--with-motion 开启）`](#第-6-5-步-动态化-可选---with-motion-开启) — L7752-11860 (4109 lines · 99 fn · 4 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L11861-12030 (170 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L12031-12818 (788 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L12819-13059 (241 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L13060-14674 (1615 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L14675-14838 (164 lines · 2 fn · 0 sub)

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
Range: **L1875 – L3485** (1611 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L2779-3485 (707 lines)

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
- `_adsd_immersion_qa_rewrite_turns` — L2442
- `_adsd_visual_contract` — L2500
- `step1_script` — L2552
- `_write_ads_retention_qa` — L3429

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L3486 – L4587** (1102 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L3561
- `_ADSD_POLICY_REWRITE_TERMS` — L3567
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L3658

**Functions:**
- `_openai_tts_fallback` — L3487
- `_edge_tts_fallback` — L3533
- `_sanitize_for_external_api` — L3576
- `_is_content_policy_error` — L3585
- `_rewrite_adsd_tts_text_for_policy` — L3599
- `_record_adsd_tts_rewrite` — L3639
- `_build_silence_mp3` — L3664
- `_audio_duration_seconds` — L3677
- `_text_to_audio_master_voice_timed` — L3689
- `_text_to_audio_master_voice` — L3814
- `step2_master_voice` — L3917
- `_tts_turn_to_audio` — L4045
- `_asr_verify_dialogue_audio` — L4107
- `_asr_verify_dialogue_turns` — L4169
- `_normalize_cn_number_token` — L4211
- `_compact_zh_text` — L4233
- `_write_adsd_asr_text_qa` — L4240
- `_write_adsd_speaker_focus_qa` — L4279
- `_write_adsd_gender_voice_qa` — L4339
- `step2_dialogue_voice` — L4392

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L4588 – L5139** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L4595-4717 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L4718-4752 (35 lines)
- _第二层：字符数插值_ — L4753-4777 (25 lines)
- _第三层：silencedetect 物理校准_ — L4778-5139 (362 lines)

**Functions:**
- `_detect_silences` — L4596
- `_calibrate_boundaries` — L4631
- `_enforce_monotonic` — L4665
- `_manual_override_segments` — L4677
- `_calc_sentence_boundaries` — L4698
- `step345_timeline` — L4809
- `_analyze_bgm_energy_cuts` — L4868
- `_snap_bgm_only_boundaries` — L4931
- `step345_bgm_only_timeline` — L4991

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L5140 – L7751** (2612 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L6213-6317 (105 lines)
- _Speaker IP Card (2026-05-21)_ — L6318-7584 (1267 lines)
- _审批流程_ — L7585-7641 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L7642-7751 (110 lines)

**Top-level constants:**
- `CHARACTER_META_GRID_COSTUMES` — L6219
- `CHARACTER_META_GRID_POSES` — L6220
- `CHARACTER_META_GRID_SCENES` — L6221
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L6224

**Functions:**
- `_extract_img_url` — L5141
- `_extract_img_urls` — L5163
- `_extract_video_url` — L5196
- `_count_bands` — L5221
- `_detect_contact_sheet_like_image` — L5233
- `_guess_upload_mime` — L5287
- `_upload_to_weryai` — L5310
- `_send_for_approval` — L5342
- `_wait_approval` — L5406
- `_render_still_segment` — L5418
- `_scene_text_visual_alignment` — L5432
- `_write_text_visual_alignment_qa` — L5468
- `_scene_motion_action_plan` — L5491
- `_ensure_motion_action_plan` — L5545
- `_motion_action_block` — L5554
- `_motion_plan_for_qa` — L5576
- `_write_motion_action_plan_qa` — L5586
- `_write_motion_bridge_refs_qa` — L5616
- `_motion_bridge_ref_prompt` — L5623
- `generate_motion_bridge_refs_gpt_image2` — L5656
- `generate_image` — L5769
- `generate_storyboard_images_gpt_image2` — L5816
- `_storyboard_grid_aspect` — L6001
- `_storyboard_grid_cols_rows` — L6008
- `_storyboard_grid_prompt` — L6030
- `_storyboard_grid_prompt_limit` — L6061
- `_is_prompt_limit_response` — L6065
- `_production_storyboard_prompt` — L6071
- `_write_production_storyboard_page_qa` — L6105
- `_character_sheet_prompt` — L6115
- `_is_audit_blocked` — L6241
- `_paraphrase_sensitive_dialogue` — L6254
- `_infer_meta_grid_costume` — L6264
- `_infer_meta_grid_pose` — L6276
- `_adsd_meta_grid_call_prompt` — L6291
- `_speaker_ips_dir` — L6321
- `_list_speaker_ips` — L6328
- `_match_speaker_ip` — L6342
- `_save_speaker_ip` — L6362
- `_character_meta_grid_cache_dir` — L6370
- `_character_meta_grid_cache_path` — L6378
- `_character_meta_grid_path` — L6384
- `generate_character_meta_grid_gpt_image2` — L6390
- `_generate_all_character_meta_grids` — L6490
- `_write_character_sheet_qa` — L6531
- `generate_character_sheet_gpt_image2` — L6541
- `generate_production_storyboard_page_gpt_image2` — L6641
- `_qa_clean_storyboard_panel` — L6704
- `_crop_storyboard_grid_panels` — L6885
- `generate_storyboard_grid_gpt_image2` — L6932
- `_gpt_image2_direct_annotated_aspect` — L7163
- `_gpt_image2_direct_annotated_prompt` — L7170
- `generate_gpt_image2_direct_annotated_storyboards` — L7200
- `_llm_bgm_description` — L7301
- `generate_bgm` — L7340
- `step6_parallel` — L7431

---

### 第 6.5 步：动态化（可选，--with-motion 开启）
Range: **L7752 – L11860** (4109 lines)

**Sub-sections:**
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L11602-11644 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L11645-11682 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回主音轨_ — L11683-11815 (133 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L11816-11860 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L7755
- `_motion_tasks_file` — L7822
- `_motion_qa_file` — L7826
- `_append_motion_qa` — L7830
- `_finalize_motion_qa` — L7854
- `_lip_sync_tasks_file` — L7938
- `_load_motion_tasks` — L7942
- `_save_motion_task` — L7952
- `_remove_motion_task` — L7960
- `_load_lip_sync_tasks` — L7967
- `_save_lip_sync_task` — L7977
- `_remove_lip_sync_task` — L7984
- `_video_visual_motion_qa` — L7991
- `_motion_output_qa` — L8063
- `_has_audio_stream` — L8108
- `_normalize_motion_video` — L8119
- `_motion_poll_and_download` — L8169
- `_build_motion_video_prompt` — L8220
- `_short_board_text` — L8250
- `_wrap_board_text` — L8257
- `_storyboard_font` — L8288
- `_draw_storyboard_arrow` — L8303
- `_build_annotated_storyboard_reference` — L8317
- `_plain_caption_text` — L8418
- `_werydance_caption_request` — L8426
- `_werydance_caption_instruction` — L8453
- `_werydance_negative_prompt` — L8465
- `_motion_reference_prompt` — L8479
- `_motion_audio_dub_prompt` — L8502
- `_motion_audio_dub_poll_and_download` — L8536
- `_try_motion_audio_dub_video` — L8601
- `_try_motion_reference_video` — L8736
- `_motion_one_scene` — L8852
- `_grid_multiref_tasks_file` — L8981
- `_previs_page_tasks_file` — L8985
- `_load_grid_multiref_tasks` — L8989
- `_load_previs_page_tasks` — L8999
- `_save_grid_multiref_task` — L9009
- `_save_previs_page_task` — L9016
- `_remove_grid_multiref_task` — L9023
- `_remove_previs_page_task` — L9030
- `_poll_video_task_download` — L9037
- `_grid_multiref_group_size` — L9086
- `_grid_multiref_duration` — L9094
- `_grid_multiref_segment_max_stretch` — L9110
- `_grid_multiref_prompt` — L9118
- `_write_grid_multiref_motion_qa` — L9166
- `_write_previs_page_motion_qa` — L9176
- `_write_storyboard_trailer_qa` — L9186
- `_write_character_trailer_qa` — L9196
- `_write_grid_multiref_segment_qa` — L9206
- `_motion_compare_record` — L9216
- `_write_storyboard_motion_compare_qa` — L9238
- `_scene_segment_duration` — L9274
- `_apply_grid_multiref_segments` — L9293
- `_previs_page_duration` — L9487
- `_previs_page_group_prompt` — L9497
- `_previs_page_groups` — L9523
- `_storyboard_trailer_duration` — L9538
- `_storyboard_trailer_prompt` — L9548
- `_character_trailer_max_shots` — L9576
- `_character_trailer_shot_duration` — L9584
- `_character_trailer_prompt` — L9598
- `_concat_character_trailer_segments` — L9613
- `_generate_character_trailer_motion` — L9652
- `_multi_trailer_prompt_for_group` — L9760
- `_generate_multi_trailer_segments` — L9783
- `_generate_storyboard_trailer_motion` — L9894
- `_generate_previs_page_motion_segments` — L9969
- `_generate_grid_multiref_motion_segments` — L10081
- `_grid_multiref_concat_groups` — L10251
- `_grid_multiref_concat_groups_partial` — L10268
- `_grid_multiref_concat_paths` — L10286
- `_lip_sync_slot_duration` — L10317
- `_adsd_lip_sync_prompt` — L10324
- `_adsd_broll_motion_prompt` — L10370
- `_adsd_silent_b_motion_prompt` — L10412
- `_adsd_narrated_b_audio_dub_prompt` — L10447
- `_adsd_almighty_audio_dub_prompt` — L10491
- `_postprocess_lip_sync_segment` — L10526
- `_detect_audio_leading_silence` — L10594
- `_postprocess_audio_dub_segment` — L10616
- `_lips_change_repair_segment` — L10722
- `_load_lips_change_requested_turns` — L10807
- `_parse_turn_set` — L10824
- `_load_motion_voice_repair_turns` — L10846
- `_voice_assets_file` — L10858
- `_load_voice_assets` — L10865
- `_select_voice_asset_reference` — L10884
- `_lip_sync_poll_download_and_process` — L10950
- `_lip_sync_one_scene` — L11014
- `step66_adsd_lip_sync` — L11276
- `step65_motion` — L11492
- `step65_grid_multiref_motion_qa` — L11574
- `_sanitize_scene_for_state` — L11603
- `_save_pipeline_state` — L11622
- `_retime_after_audio_dub` — L11646
- `_build_voice_clone_hybrid_audio` — L11684
- `_build_dynamic_bgm` — L11817

---

### 第七步：拼接视频轨
Range: **L11861 – L12030** (170 lines)

**Functions:**
- `step7_concat` — L11862

---

### 第八步：生成 ASS 字幕
Range: **L12031 – L12818** (788 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L12154-12818 (665 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L12032
- `_word_timings_for_subtitle_align` — L12058
- `_align_segments_via_asr` — L12099
- `step8_subtitles` — L12142
- `_read_output_json` — L12550
- `_qa_file_pass` — L12561
- `_ass_has_dialogue` — L12568
- `_write_adsd_delivery_qa` — L12578
- `_write_bgm_only_qa` — L12707

---

### 第九步：最终合成
Range: **L12819 – L13059** (241 lines)

**Functions:**
- `step9_render` — L12820

---

### 第十步：推送 Telegram
Range: **L13060 – L14674** (1615 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L14160-14481 (322 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L14482-14486 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L14487-14550 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L14551-14596 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L14597-14674 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L13429
- `PANTONE_FALLBACK` — L13456
- `FESTIVAL_DATE_TAG` — L13569

**Functions:**
- `_generate_caption` — L13061
- `_overlay_title_on_cover` — L13299
- `_prepare_tg_photo` — L13409
- `_get_pantone_for_date` — L13459
- `_llm_bottom_note` — L13484
- `_get_bottom_note` — L13513
- `_get_date_tag` — L13591
- `_shrink_to_b64` — L13613
- `_llm_check_scenes_anomalies` — L13629
- `_llm_check_cover_unique` — L13682
- `_llm_check_cover_quality` — L13712
- `_try_almanac_cover` — L13754
- `_generate_cover_image` — L13925
- `_async_kickoff_cover_caption` — L14167
- `_await_async_cover_caption` — L14197
- `step10_deliver` — L14221

---

### 主流程
Range: **L14675 – L14838** (164 lines)

**Functions:**
- `_print_execution_plan` — L14676
- `main` — L14724

---
