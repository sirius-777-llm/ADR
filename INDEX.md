# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (13368 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-1699 (1578 lines · 48 fn · 3 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L1700-3139 (1440 lines · 22 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L3140-4209 (1070 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L4210-4761 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L4762-6993 (2232 lines · 42 fn · 2 sub)
- [`第 6.5 步：动态化（可选，--with-motion 开启）`](#第-6-5-步-动态化-可选---with-motion-开启) — L6994-10592 (3599 lines · 91 fn · 0 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L10593-10762 (170 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L10763-11416 (654 lines · 7 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L11417-11655 (239 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L11656-13242 (1587 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L13243-13368 (126 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L1699** (1578 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L298-852 (555 lines)
- _工具函数_ — L853-1177 (325 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1178-1699 (522 lines)

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
- `VOICE_ASSET_AUDIO_DUB_EXPERIMENT` — L604
- `VOICE_ASSET_AUDIO_DUB_PARTIAL_OK` — L612
- `MOTION_VISUAL_QA` — L616
- `MOTION_VOICE_REPAIR` — L624
- `MOTION_VOICE_STRICT_LOCK` — L629
- `WERYDANCE_CAPTIONS` — L634
- `ADSD_ONSITE_POV_MODE` — L646
- `ADSD_LIPS_CHANGE_REPAIR` — L651
- `ADSD_LIPS_CHANGE_ALL` — L656
- `ADS_REPORTER_MODE` — L667
- `ADS_STORYBOARD_FLOW_DEFAULT` — L684
- `ADS_RETENTION_MODE` — L697
- `ADSD_MODE_NAME` — L703
- `EMOTION_STYLE` — L832
- `EMOTION_STYLE_BRIGHT` — L844
- `_TG_DASHBOARD_STAGES` — L866
- `_TG_NOISY_PATTERNS` — L881
- `_TG_IMMEDIATE_PATTERNS` — L899
- `_TOPIC_MODIFIERS` — L1531
- `_TONE_PANTONE_OVERRIDE` — L1548

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
- `_apply_llm_voice_assignment` — L566
- `log` — L854
- `_tg_send_raw` — L922
- `_tg_matches` — L938
- `_tg_summarize` — L942
- `_tg_dashboard_stage_for` — L949
- `_tg_progress_bar` — L957
- `_tg_dashboard_text` — L963
- `_tg_dashboard_update` — L981
- `_tg_maybe_digest` — L1018
- `tg` — L1033
- `_wait_image_submit_slot` — L1082
- `_wait_motion_submit_slot` — L1095
- `_is_rate_limited_error` — L1108
- `_is_rate_limited_response` — L1118
- `submit_text_to_image` — L1130
- `req_post` — L1159
- `req_get` — L1173
- `_tg_probe_send` — L1181
- `_tg_probe_delete` — L1201
- `_tg_upload_with_probe_gap` — L1214
- `poll` — L1254
- `poll_podcast` — L1279
- `poll_task_status` — L1301
- `poll_storyboard_task` — L1323
- `chat` — L1349
- `pick_image_model` — L1377
- `detect_topic_meta` — L1402
- `_topic_culture_guard` — L1452
- `_write_cultural_visual_qa` — L1478
- `is_1919_global_topic` — L1525
- `_strip_topic_modifiers` — L1536
- `apply_1919_global_guardrails` — L1554
- `build_1919_global_cover_prompt` — L1583
- `build_shot_blueprint` — L1612
- `ffprobe_duration` — L1638
- `ffprobe_video_size` — L1649
- `_video_decode_probe` — L1670
- `ffmpeg` — L1688

---

### 第一步：双导演生成剧本
Range: **L1700 – L3139** (1440 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L2433-3139 (707 lines)

**Functions:**
- `_extract_json_array` — L1701
- `_extract_json_object` — L1711
- `_voice_for_speaker` — L1721
- `_adsd_gender_from_voice` — L1757
- `_adsd_infer_gender_from_speaker` — L1765
- `_adsd_gender_lock_phrase` — L1774
- `_adsd_visual_subject_has_gender_conflict` — L1789
- `_adsd_default_roles` — L1801
- `_adsd_allows_media_role` — L1806
- `_adsd_role_candidates` — L1814
- `_adsd_dialogue_shape` — L1830
- `_finalize_adsd_turns` — L1839
- `_parse_adsd_override_turns` — L1862
- `_parse_timecode_seconds` — L1925
- `_clean_override_line_text` — L1934
- `_parse_override_script_text` — L1940
- `_adsd_pov_contract` — L1974
- `_generate_adsd_dialogue_turns` — L1984
- `_adsd_immersion_qa_rewrite_turns` — L2100
- `_adsd_visual_contract` — L2154
- `step1_script` — L2206
- `_write_ads_retention_qa` — L3083

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L3140 – L4209** (1070 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L3215
- `_ADSD_POLICY_REWRITE_TERMS` — L3221
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L3312

**Functions:**
- `_openai_tts_fallback` — L3141
- `_edge_tts_fallback` — L3187
- `_sanitize_for_external_api` — L3230
- `_is_content_policy_error` — L3239
- `_rewrite_adsd_tts_text_for_policy` — L3253
- `_record_adsd_tts_rewrite` — L3293
- `_build_silence_mp3` — L3318
- `_audio_duration_seconds` — L3331
- `_text_to_audio_master_voice_timed` — L3343
- `_text_to_audio_master_voice` — L3468
- `step2_master_voice` — L3571
- `_tts_turn_to_audio` — L3699
- `_asr_verify_dialogue_audio` — L3761
- `_asr_verify_dialogue_turns` — L3803
- `_normalize_cn_number_token` — L3845
- `_compact_zh_text` — L3867
- `_write_adsd_asr_text_qa` — L3874
- `_write_adsd_speaker_focus_qa` — L3913
- `_write_adsd_gender_voice_qa` — L3973
- `step2_dialogue_voice` — L4026

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L4210 – L4761** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L4217-4339 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L4340-4374 (35 lines)
- _第二层：字符数插值_ — L4375-4399 (25 lines)
- _第三层：silencedetect 物理校准_ — L4400-4761 (362 lines)

**Functions:**
- `_detect_silences` — L4218
- `_calibrate_boundaries` — L4253
- `_enforce_monotonic` — L4287
- `_manual_override_segments` — L4299
- `_calc_sentence_boundaries` — L4320
- `step345_timeline` — L4431
- `_analyze_bgm_energy_cuts` — L4490
- `_snap_bgm_only_boundaries` — L4553
- `step345_bgm_only_timeline` — L4613

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L4762 – L6993** (2232 lines)

**Sub-sections:**
- _审批流程_ — L6827-6883 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L6884-6993 (110 lines)

**Functions:**
- `_extract_img_url` — L4763
- `_extract_img_urls` — L4785
- `_extract_video_url` — L4818
- `_count_bands` — L4843
- `_detect_contact_sheet_like_image` — L4855
- `_guess_upload_mime` — L4909
- `_upload_to_weryai` — L4932
- `_send_for_approval` — L4964
- `_wait_approval` — L5028
- `_render_still_segment` — L5040
- `_scene_text_visual_alignment` — L5054
- `_write_text_visual_alignment_qa` — L5090
- `_scene_motion_action_plan` — L5113
- `_ensure_motion_action_plan` — L5167
- `_motion_action_block` — L5176
- `_motion_plan_for_qa` — L5198
- `_write_motion_action_plan_qa` — L5208
- `_write_motion_bridge_refs_qa` — L5238
- `_motion_bridge_ref_prompt` — L5245
- `generate_motion_bridge_refs_gpt_image2` — L5278
- `generate_image` — L5391
- `generate_storyboard_images_gpt_image2` — L5438
- `_storyboard_grid_aspect` — L5623
- `_storyboard_grid_cols_rows` — L5630
- `_storyboard_grid_prompt` — L5652
- `_storyboard_grid_prompt_limit` — L5683
- `_is_prompt_limit_response` — L5687
- `_production_storyboard_prompt` — L5693
- `_write_production_storyboard_page_qa` — L5727
- `_character_sheet_prompt` — L5737
- `_write_character_sheet_qa` — L5835
- `generate_character_sheet_gpt_image2` — L5845
- `generate_production_storyboard_page_gpt_image2` — L5945
- `_qa_clean_storyboard_panel` — L6008
- `_crop_storyboard_grid_panels` — L6189
- `generate_storyboard_grid_gpt_image2` — L6236
- `_gpt_image2_direct_annotated_aspect` — L6467
- `_gpt_image2_direct_annotated_prompt` — L6474
- `generate_gpt_image2_direct_annotated_storyboards` — L6504
- `_llm_bgm_description` — L6605
- `generate_bgm` — L6644
- `step6_parallel` — L6735

---

### 第 6.5 步：动态化（可选，--with-motion 开启）
Range: **L6994 – L10592** (3599 lines)

**Functions:**
- `_generate_motion_prompts` — L6997
- `_motion_tasks_file` — L7064
- `_motion_qa_file` — L7068
- `_append_motion_qa` — L7072
- `_finalize_motion_qa` — L7096
- `_lip_sync_tasks_file` — L7180
- `_load_motion_tasks` — L7184
- `_save_motion_task` — L7194
- `_remove_motion_task` — L7202
- `_load_lip_sync_tasks` — L7209
- `_save_lip_sync_task` — L7219
- `_remove_lip_sync_task` — L7226
- `_video_visual_motion_qa` — L7233
- `_motion_output_qa` — L7305
- `_has_audio_stream` — L7350
- `_normalize_motion_video` — L7361
- `_motion_poll_and_download` — L7411
- `_build_motion_video_prompt` — L7462
- `_short_board_text` — L7492
- `_wrap_board_text` — L7499
- `_storyboard_font` — L7530
- `_draw_storyboard_arrow` — L7545
- `_build_annotated_storyboard_reference` — L7559
- `_plain_caption_text` — L7660
- `_werydance_caption_request` — L7668
- `_werydance_caption_instruction` — L7695
- `_werydance_negative_prompt` — L7707
- `_motion_reference_prompt` — L7713
- `_motion_audio_dub_prompt` — L7736
- `_motion_audio_dub_poll_and_download` — L7770
- `_try_motion_audio_dub_video` — L7835
- `_try_motion_reference_video` — L7970
- `_motion_one_scene` — L8086
- `_grid_multiref_tasks_file` — L8215
- `_previs_page_tasks_file` — L8219
- `_load_grid_multiref_tasks` — L8223
- `_load_previs_page_tasks` — L8233
- `_save_grid_multiref_task` — L8243
- `_save_previs_page_task` — L8250
- `_remove_grid_multiref_task` — L8257
- `_remove_previs_page_task` — L8264
- `_poll_video_task_download` — L8271
- `_grid_multiref_group_size` — L8320
- `_grid_multiref_duration` — L8328
- `_grid_multiref_segment_max_stretch` — L8344
- `_grid_multiref_prompt` — L8352
- `_write_grid_multiref_motion_qa` — L8400
- `_write_previs_page_motion_qa` — L8410
- `_write_storyboard_trailer_qa` — L8420
- `_write_character_trailer_qa` — L8430
- `_write_grid_multiref_segment_qa` — L8440
- `_motion_compare_record` — L8450
- `_write_storyboard_motion_compare_qa` — L8472
- `_scene_segment_duration` — L8508
- `_apply_grid_multiref_segments` — L8527
- `_previs_page_duration` — L8721
- `_previs_page_group_prompt` — L8731
- `_previs_page_groups` — L8757
- `_storyboard_trailer_duration` — L8772
- `_storyboard_trailer_prompt` — L8782
- `_character_trailer_max_shots` — L8810
- `_character_trailer_shot_duration` — L8818
- `_character_trailer_prompt` — L8832
- `_concat_character_trailer_segments` — L8847
- `_generate_character_trailer_motion` — L8886
- `_multi_trailer_prompt_for_group` — L8994
- `_generate_multi_trailer_segments` — L9017
- `_generate_storyboard_trailer_motion` — L9128
- `_generate_previs_page_motion_segments` — L9203
- `_generate_grid_multiref_motion_segments` — L9315
- `_grid_multiref_concat_groups` — L9485
- `_grid_multiref_concat_groups_partial` — L9502
- `_grid_multiref_concat_paths` — L9520
- `_lip_sync_slot_duration` — L9551
- `_adsd_lip_sync_prompt` — L9558
- `_adsd_broll_motion_prompt` — L9597
- `_adsd_almighty_audio_dub_prompt` — L9634
- `_postprocess_lip_sync_segment` — L9669
- `_postprocess_audio_dub_segment` — L9737
- `_lips_change_repair_segment` — L9813
- `_load_lips_change_requested_turns` — L9898
- `_parse_turn_set` — L9915
- `_load_motion_voice_repair_turns` — L9937
- `_voice_assets_file` — L9949
- `_load_voice_assets` — L9956
- `_select_voice_asset_reference` — L9975
- `_lip_sync_poll_download_and_process` — L10041
- `_lip_sync_one_scene` — L10105
- `step66_adsd_lip_sync` — L10305
- `step65_motion` — L10483
- `step65_grid_multiref_motion_qa` — L10565

---

### 第七步：拼接视频轨
Range: **L10593 – L10762** (170 lines)

**Functions:**
- `step7_concat` — L10594

---

### 第八步：生成 ASS 字幕
Range: **L10763 – L11416** (654 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L10802-11416 (615 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L10764
- `step8_subtitles` — L10790
- `_read_output_json` — L11158
- `_qa_file_pass` — L11169
- `_ass_has_dialogue` — L11176
- `_write_adsd_delivery_qa` — L11186
- `_write_bgm_only_qa` — L11305

---

### 第九步：最终合成
Range: **L11417 – L11655** (239 lines)

**Functions:**
- `step9_render` — L11418

---

### 第十步：推送 Telegram
Range: **L11656 – L13242** (1587 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L12756-13071 (316 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L13072-13076 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L13077-13118 (42 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L13119-13164 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L13165-13242 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L12025
- `PANTONE_FALLBACK` — L12052
- `FESTIVAL_DATE_TAG` — L12165

**Functions:**
- `_generate_caption` — L11657
- `_overlay_title_on_cover` — L11895
- `_prepare_tg_photo` — L12005
- `_get_pantone_for_date` — L12055
- `_llm_bottom_note` — L12080
- `_get_bottom_note` — L12109
- `_get_date_tag` — L12187
- `_shrink_to_b64` — L12209
- `_llm_check_scenes_anomalies` — L12225
- `_llm_check_cover_unique` — L12278
- `_llm_check_cover_quality` — L12308
- `_try_almanac_cover` — L12350
- `_generate_cover_image` — L12521
- `_async_kickoff_cover_caption` — L12763
- `_await_async_cover_caption` — L12793
- `step10_deliver` — L12817

---

### 主流程
Range: **L13243 – L13368** (126 lines)

**Functions:**
- `_print_execution_plan` — L13244
- `main` — L13292

---
