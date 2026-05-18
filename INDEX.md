# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (13053 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-1506 (1385 lines · 45 fn · 3 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L1507-2930 (1424 lines · 22 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L2931-4000 (1070 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L4001-4552 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L4553-6778 (2226 lines · 42 fn · 2 sub)
- [`第 6.5 步：动态化（可选，--with-motion 开启）`](#第-6-5-步-动态化-可选---with-motion-开启) — L6779-10347 (3569 lines · 91 fn · 0 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L10348-10517 (170 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L10518-11171 (654 lines · 7 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L11172-11410 (239 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L11411-12927 (1517 lines · 16 fn · 4 sub)
- [`主流程`](#主流程) — L12928-13053 (126 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L1506** (1385 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L290-659 (370 lines)
- _工具函数_ — L660-984 (325 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L985-1506 (522 lines)

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
- `VOICE_ASSET_AUDIO_DUB_EXPERIMENT` — L411
- `VOICE_ASSET_AUDIO_DUB_PARTIAL_OK` — L419
- `MOTION_VISUAL_QA` — L423
- `MOTION_VOICE_REPAIR` — L431
- `MOTION_VOICE_STRICT_LOCK` — L436
- `WERYDANCE_CAPTIONS` — L441
- `ADSD_ONSITE_POV_MODE` — L453
- `ADSD_LIPS_CHANGE_REPAIR` — L458
- `ADSD_LIPS_CHANGE_ALL` — L463
- `ADS_REPORTER_MODE` — L474
- `ADS_STORYBOARD_FLOW_DEFAULT` — L491
- `ADS_RETENTION_MODE` — L504
- `ADSD_MODE_NAME` — L510
- `EMOTION_STYLE` — L639
- `EMOTION_STYLE_BRIGHT` — L651
- `_TG_DASHBOARD_STAGES` — L673
- `_TG_NOISY_PATTERNS` — L688
- `_TG_IMMEDIATE_PATTERNS` — L706
- `_TOPIC_MODIFIERS` — L1338
- `_TONE_PANTONE_OVERRIDE` — L1355

**Functions:**
- `_is_action_scene` — L302
- `_wuxia_action_panel_prompt` — L309
- `_action_motion_fragment` — L331
- `_infer_emotion_from_text` — L346
- `_emotion_expression_phrase` — L361
- `_infer_needs_lip_sync` — L368
- `_voice_asset_id_for_speaker` — L387
- `log` — L661
- `_tg_send_raw` — L729
- `_tg_matches` — L745
- `_tg_summarize` — L749
- `_tg_dashboard_stage_for` — L756
- `_tg_progress_bar` — L764
- `_tg_dashboard_text` — L770
- `_tg_dashboard_update` — L788
- `_tg_maybe_digest` — L825
- `tg` — L840
- `_wait_image_submit_slot` — L889
- `_wait_motion_submit_slot` — L902
- `_is_rate_limited_error` — L915
- `_is_rate_limited_response` — L925
- `submit_text_to_image` — L937
- `req_post` — L966
- `req_get` — L980
- `_tg_probe_send` — L988
- `_tg_probe_delete` — L1008
- `_tg_upload_with_probe_gap` — L1021
- `poll` — L1061
- `poll_podcast` — L1086
- `poll_task_status` — L1108
- `poll_storyboard_task` — L1130
- `chat` — L1156
- `pick_image_model` — L1184
- `detect_topic_meta` — L1209
- `_topic_culture_guard` — L1259
- `_write_cultural_visual_qa` — L1285
- `is_1919_global_topic` — L1332
- `_strip_topic_modifiers` — L1343
- `apply_1919_global_guardrails` — L1361
- `build_1919_global_cover_prompt` — L1390
- `build_shot_blueprint` — L1419
- `ffprobe_duration` — L1445
- `ffprobe_video_size` — L1456
- `_video_decode_probe` — L1477
- `ffmpeg` — L1495

---

### 第一步：双导演生成剧本
Range: **L1507 – L2930** (1424 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L2240-2930 (691 lines)

**Functions:**
- `_extract_json_array` — L1508
- `_extract_json_object` — L1518
- `_voice_for_speaker` — L1528
- `_adsd_gender_from_voice` — L1564
- `_adsd_infer_gender_from_speaker` — L1572
- `_adsd_gender_lock_phrase` — L1581
- `_adsd_visual_subject_has_gender_conflict` — L1596
- `_adsd_default_roles` — L1608
- `_adsd_allows_media_role` — L1613
- `_adsd_role_candidates` — L1621
- `_adsd_dialogue_shape` — L1637
- `_finalize_adsd_turns` — L1646
- `_parse_adsd_override_turns` — L1669
- `_parse_timecode_seconds` — L1732
- `_clean_override_line_text` — L1741
- `_parse_override_script_text` — L1747
- `_adsd_pov_contract` — L1781
- `_generate_adsd_dialogue_turns` — L1791
- `_adsd_immersion_qa_rewrite_turns` — L1907
- `_adsd_visual_contract` — L1961
- `step1_script` — L2013
- `_write_ads_retention_qa` — L2874

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L2931 – L4000** (1070 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L3006
- `_ADSD_POLICY_REWRITE_TERMS` — L3012
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L3103

**Functions:**
- `_openai_tts_fallback` — L2932
- `_edge_tts_fallback` — L2978
- `_sanitize_for_external_api` — L3021
- `_is_content_policy_error` — L3030
- `_rewrite_adsd_tts_text_for_policy` — L3044
- `_record_adsd_tts_rewrite` — L3084
- `_build_silence_mp3` — L3109
- `_audio_duration_seconds` — L3122
- `_text_to_audio_master_voice_timed` — L3134
- `_text_to_audio_master_voice` — L3259
- `step2_master_voice` — L3362
- `_tts_turn_to_audio` — L3490
- `_asr_verify_dialogue_audio` — L3552
- `_asr_verify_dialogue_turns` — L3594
- `_normalize_cn_number_token` — L3636
- `_compact_zh_text` — L3658
- `_write_adsd_asr_text_qa` — L3665
- `_write_adsd_speaker_focus_qa` — L3704
- `_write_adsd_gender_voice_qa` — L3764
- `step2_dialogue_voice` — L3817

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L4001 – L4552** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L4008-4130 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L4131-4165 (35 lines)
- _第二层：字符数插值_ — L4166-4190 (25 lines)
- _第三层：silencedetect 物理校准_ — L4191-4552 (362 lines)

**Functions:**
- `_detect_silences` — L4009
- `_calibrate_boundaries` — L4044
- `_enforce_monotonic` — L4078
- `_manual_override_segments` — L4090
- `_calc_sentence_boundaries` — L4111
- `step345_timeline` — L4222
- `_analyze_bgm_energy_cuts` — L4281
- `_snap_bgm_only_boundaries` — L4344
- `step345_bgm_only_timeline` — L4404

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L4553 – L6778** (2226 lines)

**Sub-sections:**
- _审批流程_ — L6612-6668 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L6669-6778 (110 lines)

**Functions:**
- `_extract_img_url` — L4554
- `_extract_img_urls` — L4576
- `_extract_video_url` — L4609
- `_count_bands` — L4634
- `_detect_contact_sheet_like_image` — L4646
- `_guess_upload_mime` — L4700
- `_upload_to_weryai` — L4723
- `_send_for_approval` — L4755
- `_wait_approval` — L4819
- `_render_still_segment` — L4831
- `_scene_text_visual_alignment` — L4845
- `_write_text_visual_alignment_qa` — L4881
- `_scene_motion_action_plan` — L4904
- `_ensure_motion_action_plan` — L4958
- `_motion_action_block` — L4967
- `_motion_plan_for_qa` — L4989
- `_write_motion_action_plan_qa` — L4999
- `_write_motion_bridge_refs_qa` — L5029
- `_motion_bridge_ref_prompt` — L5036
- `generate_motion_bridge_refs_gpt_image2` — L5069
- `generate_image` — L5182
- `generate_storyboard_images_gpt_image2` — L5229
- `_storyboard_grid_aspect` — L5414
- `_storyboard_grid_cols_rows` — L5421
- `_storyboard_grid_prompt` — L5443
- `_storyboard_grid_prompt_limit` — L5474
- `_is_prompt_limit_response` — L5478
- `_production_storyboard_prompt` — L5484
- `_write_production_storyboard_page_qa` — L5518
- `_character_sheet_prompt` — L5528
- `_write_character_sheet_qa` — L5626
- `generate_character_sheet_gpt_image2` — L5636
- `generate_production_storyboard_page_gpt_image2` — L5730
- `_qa_clean_storyboard_panel` — L5793
- `_crop_storyboard_grid_panels` — L5974
- `generate_storyboard_grid_gpt_image2` — L6021
- `_gpt_image2_direct_annotated_aspect` — L6252
- `_gpt_image2_direct_annotated_prompt` — L6259
- `generate_gpt_image2_direct_annotated_storyboards` — L6289
- `_llm_bgm_description` — L6390
- `generate_bgm` — L6429
- `step6_parallel` — L6520

---

### 第 6.5 步：动态化（可选，--with-motion 开启）
Range: **L6779 – L10347** (3569 lines)

**Functions:**
- `_generate_motion_prompts` — L6782
- `_motion_tasks_file` — L6849
- `_motion_qa_file` — L6853
- `_append_motion_qa` — L6857
- `_finalize_motion_qa` — L6881
- `_lip_sync_tasks_file` — L6965
- `_load_motion_tasks` — L6969
- `_save_motion_task` — L6979
- `_remove_motion_task` — L6987
- `_load_lip_sync_tasks` — L6994
- `_save_lip_sync_task` — L7004
- `_remove_lip_sync_task` — L7011
- `_video_visual_motion_qa` — L7018
- `_motion_output_qa` — L7090
- `_has_audio_stream` — L7135
- `_normalize_motion_video` — L7146
- `_motion_poll_and_download` — L7196
- `_build_motion_video_prompt` — L7247
- `_short_board_text` — L7277
- `_wrap_board_text` — L7284
- `_storyboard_font` — L7315
- `_draw_storyboard_arrow` — L7330
- `_build_annotated_storyboard_reference` — L7344
- `_plain_caption_text` — L7445
- `_werydance_caption_request` — L7453
- `_werydance_caption_instruction` — L7480
- `_werydance_negative_prompt` — L7492
- `_motion_reference_prompt` — L7498
- `_motion_audio_dub_prompt` — L7521
- `_motion_audio_dub_poll_and_download` — L7555
- `_try_motion_audio_dub_video` — L7620
- `_try_motion_reference_video` — L7755
- `_motion_one_scene` — L7871
- `_grid_multiref_tasks_file` — L8000
- `_previs_page_tasks_file` — L8004
- `_load_grid_multiref_tasks` — L8008
- `_load_previs_page_tasks` — L8018
- `_save_grid_multiref_task` — L8028
- `_save_previs_page_task` — L8035
- `_remove_grid_multiref_task` — L8042
- `_remove_previs_page_task` — L8049
- `_poll_video_task_download` — L8056
- `_grid_multiref_group_size` — L8105
- `_grid_multiref_duration` — L8113
- `_grid_multiref_segment_max_stretch` — L8129
- `_grid_multiref_prompt` — L8137
- `_write_grid_multiref_motion_qa` — L8173
- `_write_previs_page_motion_qa` — L8183
- `_write_storyboard_trailer_qa` — L8193
- `_write_character_trailer_qa` — L8203
- `_write_grid_multiref_segment_qa` — L8213
- `_motion_compare_record` — L8223
- `_write_storyboard_motion_compare_qa` — L8245
- `_scene_segment_duration` — L8281
- `_apply_grid_multiref_segments` — L8300
- `_previs_page_duration` — L8494
- `_previs_page_group_prompt` — L8504
- `_previs_page_groups` — L8530
- `_storyboard_trailer_duration` — L8545
- `_storyboard_trailer_prompt` — L8555
- `_character_trailer_max_shots` — L8583
- `_character_trailer_shot_duration` — L8591
- `_character_trailer_prompt` — L8605
- `_concat_character_trailer_segments` — L8620
- `_generate_character_trailer_motion` — L8659
- `_multi_trailer_prompt_for_group` — L8767
- `_generate_multi_trailer_segments` — L8790
- `_generate_storyboard_trailer_motion` — L8901
- `_generate_previs_page_motion_segments` — L8976
- `_generate_grid_multiref_motion_segments` — L9088
- `_grid_multiref_concat_groups` — L9240
- `_grid_multiref_concat_groups_partial` — L9257
- `_grid_multiref_concat_paths` — L9275
- `_lip_sync_slot_duration` — L9306
- `_adsd_lip_sync_prompt` — L9313
- `_adsd_broll_motion_prompt` — L9352
- `_adsd_almighty_audio_dub_prompt` — L9389
- `_postprocess_lip_sync_segment` — L9424
- `_postprocess_audio_dub_segment` — L9492
- `_lips_change_repair_segment` — L9568
- `_load_lips_change_requested_turns` — L9653
- `_parse_turn_set` — L9670
- `_load_motion_voice_repair_turns` — L9692
- `_voice_assets_file` — L9704
- `_load_voice_assets` — L9711
- `_select_voice_asset_reference` — L9730
- `_lip_sync_poll_download_and_process` — L9796
- `_lip_sync_one_scene` — L9860
- `step66_adsd_lip_sync` — L10060
- `step65_motion` — L10238
- `step65_grid_multiref_motion_qa` — L10320

---

### 第七步：拼接视频轨
Range: **L10348 – L10517** (170 lines)

**Functions:**
- `step7_concat` — L10349

---

### 第八步：生成 ASS 字幕
Range: **L10518 – L11171** (654 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L10557-11171 (615 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L10519
- `step8_subtitles` — L10545
- `_read_output_json` — L10913
- `_qa_file_pass` — L10924
- `_ass_has_dialogue` — L10931
- `_write_adsd_delivery_qa` — L10941
- `_write_bgm_only_qa` — L11060

---

### 第九步：最终合成
Range: **L11172 – L11410** (239 lines)

**Functions:**
- `step9_render` — L11173

---

### 第十步：推送 Telegram
Range: **L11411 – L12927** (1517 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L12511-12826 (316 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L12827-12831 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L12832-12873 (42 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L12874-12927 (54 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L11780
- `PANTONE_FALLBACK` — L11807
- `FESTIVAL_DATE_TAG` — L11920

**Functions:**
- `_generate_caption` — L11412
- `_overlay_title_on_cover` — L11650
- `_prepare_tg_photo` — L11760
- `_get_pantone_for_date` — L11810
- `_llm_bottom_note` — L11835
- `_get_bottom_note` — L11864
- `_get_date_tag` — L11942
- `_shrink_to_b64` — L11964
- `_llm_check_scenes_anomalies` — L11980
- `_llm_check_cover_unique` — L12033
- `_llm_check_cover_quality` — L12063
- `_try_almanac_cover` — L12105
- `_generate_cover_image` — L12276
- `_async_kickoff_cover_caption` — L12518
- `_await_async_cover_caption` — L12548
- `step10_deliver` — L12572

---

### 主流程
Range: **L12928 – L13053** (126 lines)

**Functions:**
- `_print_execution_plan` — L12929
- `main` — L12977

---
