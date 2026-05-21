# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (14999 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-1874 (1753 lines · 54 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L1875-3488 (1614 lines · 22 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L3489-4590 (1102 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L4591-5142 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L5143-7902 (2760 lines · 60 fn · 4 sub)
- [`第 6.5 步：动态化（可选，--with-motion 开启）`](#第-6-5-步-动态化-可选---with-motion-开启) — L7903-12011 (4109 lines · 99 fn · 4 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L12012-12181 (170 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L12182-12973 (792 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L12974-13214 (241 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L13215-14829 (1615 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L14830-14999 (170 lines · 2 fn · 0 sub)

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
Range: **L5143 – L7902** (2760 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L6216-6320 (105 lines)
- _Speaker IP Card (2026-05-21)_ — L6321-7735 (1415 lines)
- _审批流程_ — L7736-7792 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L7793-7902 (110 lines)

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
- `_infer_meta_grid_costume` — L6267
- `_infer_meta_grid_pose` — L6279
- `_adsd_meta_grid_call_prompt` — L6294
- `_speaker_ips_dir` — L6324
- `_list_speaker_ips` — L6331
- `_match_speaker_ip` — L6345
- `_build_speaker_ip_context_for_script` — L6365
- `_save_speaker_ip` — L6411
- `_record_speaker_usage_history` — L6419
- `_format_speaker_usage_history_for_prompt` — L6461
- `_character_meta_grid_cache_dir` — L6479
- `_character_meta_grid_cache_path` — L6487
- `_character_meta_grid_path` — L6493
- `generate_character_meta_grid_gpt_image2` — L6499
- `_generate_all_character_meta_grids` — L6599
- `_write_character_sheet_qa` — L6640
- `generate_character_sheet_gpt_image2` — L6650
- `generate_production_storyboard_page_gpt_image2` — L6750
- `_qa_clean_storyboard_panel` — L6813
- `_crop_storyboard_grid_panels` — L6994
- `generate_storyboard_grid_gpt_image2` — L7041
- `_gpt_image2_direct_annotated_aspect` — L7272
- `_gpt_image2_direct_annotated_prompt` — L7279
- `generate_gpt_image2_direct_annotated_storyboards` — L7309
- `_llm_bgm_description` — L7410
- `_bgm_contains_vocals` — L7449
- `generate_bgm` — L7483
- `step6_parallel` — L7582

---

### 第 6.5 步：动态化（可选，--with-motion 开启）
Range: **L7903 – L12011** (4109 lines)

**Sub-sections:**
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L11753-11795 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L11796-11833 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回主音轨_ — L11834-11966 (133 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L11967-12011 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L7906
- `_motion_tasks_file` — L7973
- `_motion_qa_file` — L7977
- `_append_motion_qa` — L7981
- `_finalize_motion_qa` — L8005
- `_lip_sync_tasks_file` — L8089
- `_load_motion_tasks` — L8093
- `_save_motion_task` — L8103
- `_remove_motion_task` — L8111
- `_load_lip_sync_tasks` — L8118
- `_save_lip_sync_task` — L8128
- `_remove_lip_sync_task` — L8135
- `_video_visual_motion_qa` — L8142
- `_motion_output_qa` — L8214
- `_has_audio_stream` — L8259
- `_normalize_motion_video` — L8270
- `_motion_poll_and_download` — L8320
- `_build_motion_video_prompt` — L8371
- `_short_board_text` — L8401
- `_wrap_board_text` — L8408
- `_storyboard_font` — L8439
- `_draw_storyboard_arrow` — L8454
- `_build_annotated_storyboard_reference` — L8468
- `_plain_caption_text` — L8569
- `_werydance_caption_request` — L8577
- `_werydance_caption_instruction` — L8604
- `_werydance_negative_prompt` — L8616
- `_motion_reference_prompt` — L8630
- `_motion_audio_dub_prompt` — L8653
- `_motion_audio_dub_poll_and_download` — L8687
- `_try_motion_audio_dub_video` — L8752
- `_try_motion_reference_video` — L8887
- `_motion_one_scene` — L9003
- `_grid_multiref_tasks_file` — L9132
- `_previs_page_tasks_file` — L9136
- `_load_grid_multiref_tasks` — L9140
- `_load_previs_page_tasks` — L9150
- `_save_grid_multiref_task` — L9160
- `_save_previs_page_task` — L9167
- `_remove_grid_multiref_task` — L9174
- `_remove_previs_page_task` — L9181
- `_poll_video_task_download` — L9188
- `_grid_multiref_group_size` — L9237
- `_grid_multiref_duration` — L9245
- `_grid_multiref_segment_max_stretch` — L9261
- `_grid_multiref_prompt` — L9269
- `_write_grid_multiref_motion_qa` — L9317
- `_write_previs_page_motion_qa` — L9327
- `_write_storyboard_trailer_qa` — L9337
- `_write_character_trailer_qa` — L9347
- `_write_grid_multiref_segment_qa` — L9357
- `_motion_compare_record` — L9367
- `_write_storyboard_motion_compare_qa` — L9389
- `_scene_segment_duration` — L9425
- `_apply_grid_multiref_segments` — L9444
- `_previs_page_duration` — L9638
- `_previs_page_group_prompt` — L9648
- `_previs_page_groups` — L9674
- `_storyboard_trailer_duration` — L9689
- `_storyboard_trailer_prompt` — L9699
- `_character_trailer_max_shots` — L9727
- `_character_trailer_shot_duration` — L9735
- `_character_trailer_prompt` — L9749
- `_concat_character_trailer_segments` — L9764
- `_generate_character_trailer_motion` — L9803
- `_multi_trailer_prompt_for_group` — L9911
- `_generate_multi_trailer_segments` — L9934
- `_generate_storyboard_trailer_motion` — L10045
- `_generate_previs_page_motion_segments` — L10120
- `_generate_grid_multiref_motion_segments` — L10232
- `_grid_multiref_concat_groups` — L10402
- `_grid_multiref_concat_groups_partial` — L10419
- `_grid_multiref_concat_paths` — L10437
- `_lip_sync_slot_duration` — L10468
- `_adsd_lip_sync_prompt` — L10475
- `_adsd_broll_motion_prompt` — L10521
- `_adsd_silent_b_motion_prompt` — L10563
- `_adsd_narrated_b_audio_dub_prompt` — L10598
- `_adsd_almighty_audio_dub_prompt` — L10642
- `_postprocess_lip_sync_segment` — L10677
- `_detect_audio_leading_silence` — L10745
- `_postprocess_audio_dub_segment` — L10767
- `_lips_change_repair_segment` — L10873
- `_load_lips_change_requested_turns` — L10958
- `_parse_turn_set` — L10975
- `_load_motion_voice_repair_turns` — L10997
- `_voice_assets_file` — L11009
- `_load_voice_assets` — L11016
- `_select_voice_asset_reference` — L11035
- `_lip_sync_poll_download_and_process` — L11101
- `_lip_sync_one_scene` — L11165
- `step66_adsd_lip_sync` — L11427
- `step65_motion` — L11643
- `step65_grid_multiref_motion_qa` — L11725
- `_sanitize_scene_for_state` — L11754
- `_save_pipeline_state` — L11773
- `_retime_after_audio_dub` — L11797
- `_build_voice_clone_hybrid_audio` — L11835
- `_build_dynamic_bgm` — L11968

---

### 第七步：拼接视频轨
Range: **L12012 – L12181** (170 lines)

**Functions:**
- `step7_concat` — L12013

---

### 第八步：生成 ASS 字幕
Range: **L12182 – L12973** (792 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L12305-12973 (669 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L12183
- `_word_timings_for_subtitle_align` — L12209
- `_align_segments_via_asr` — L12250
- `step8_subtitles` — L12293
- `_read_output_json` — L12705
- `_qa_file_pass` — L12716
- `_ass_has_dialogue` — L12723
- `_write_adsd_delivery_qa` — L12733
- `_write_bgm_only_qa` — L12862

---

### 第九步：最终合成
Range: **L12974 – L13214** (241 lines)

**Functions:**
- `step9_render` — L12975

---

### 第十步：推送 Telegram
Range: **L13215 – L14829** (1615 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L14315-14636 (322 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L14637-14641 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L14642-14705 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L14706-14751 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L14752-14829 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L13584
- `PANTONE_FALLBACK` — L13611
- `FESTIVAL_DATE_TAG` — L13724

**Functions:**
- `_generate_caption` — L13216
- `_overlay_title_on_cover` — L13454
- `_prepare_tg_photo` — L13564
- `_get_pantone_for_date` — L13614
- `_llm_bottom_note` — L13639
- `_get_bottom_note` — L13668
- `_get_date_tag` — L13746
- `_shrink_to_b64` — L13768
- `_llm_check_scenes_anomalies` — L13784
- `_llm_check_cover_unique` — L13837
- `_llm_check_cover_quality` — L13867
- `_try_almanac_cover` — L13909
- `_generate_cover_image` — L14080
- `_async_kickoff_cover_caption` — L14322
- `_await_async_cover_caption` — L14352
- `step10_deliver` — L14376

---

### 主流程
Range: **L14830 – L14999** (170 lines)

**Functions:**
- `_print_execution_plan` — L14831
- `main` — L14879

---
