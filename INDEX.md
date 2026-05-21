# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (15515 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-1883 (1762 lines · 55 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L1884-3524 (1641 lines · 22 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L3525-4626 (1102 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L4627-5178 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L5179-8329 (3151 lines · 68 fn · 6 sub)
- [`第 6.5 步：动态化（可选，--with-motion 开启）`](#第-6-5-步-动态化-可选---with-motion-开启) — L8330-12527 (4198 lines · 100 fn · 4 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L12528-12697 (170 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L12698-13489 (792 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L13490-13730 (241 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L13731-15345 (1615 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L15346-15515 (170 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L1883** (1762 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L298-427 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L428-1011 (584 lines)
- _工具函数_ — L1012-1361 (350 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1362-1883 (522 lines)

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
- `SILENT_B_SPEAKERS` — L433
- `VOICE_ASSET_AUDIO_DUB_EXPERIMENT` — L763
- `VOICE_ASSET_AUDIO_DUB_PARTIAL_OK` — L771
- `MOTION_VISUAL_QA` — L775
- `MOTION_VOICE_REPAIR` — L783
- `MOTION_VOICE_STRICT_LOCK` — L788
- `WERYDANCE_CAPTIONS` — L793
- `ADSD_ONSITE_POV_MODE` — L805
- `ADSD_LIPS_CHANGE_REPAIR` — L810
- `ADSD_LIPS_CHANGE_ALL` — L815
- `ADS_REPORTER_MODE` — L826
- `ADS_STORYBOARD_FLOW_DEFAULT` — L843
- `ADS_RETENTION_MODE` — L856
- `ADSD_MODE_NAME` — L862
- `EMOTION_STYLE` — L991
- `EMOTION_STYLE_BRIGHT` — L1003
- `_TG_DASHBOARD_STAGES` — L1025
- `_TG_NOISY_PATTERNS` — L1040
- `_TG_IMMEDIATE_PATTERNS` — L1058
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1291
- `_TOPIC_MODIFIERS` — L1715
- `_TONE_PANTONE_OVERRIDE` — L1732

**Functions:**
- `_is_action_scene` — L310
- `_needs_storyboard_flow_character_sheet` — L321
- `_wuxia_action_panel_prompt` — L350
- `_action_motion_fragment` — L372
- `_infer_emotion_from_text` — L387
- `_emotion_expression_phrase` — L402
- `_infer_needs_lip_sync` — L409
- `_infer_turn_type` — L436
- `_resolve_turn_type` — L455
- `_is_silent_b` — L470
- `_is_narrated_b` — L474
- `_is_a_roll` — L478
- `_is_action_b` — L482
- `_voice_asset_id_for_speaker` — L486
- `_llm_assign_voice_assets` — L514
- `_apply_llm_voice_assignment` — L638
- `log` — L1013
- `_tg_send_raw` — L1081
- `_tg_matches` — L1097
- `_tg_summarize` — L1101
- `_tg_dashboard_stage_for` — L1108
- `_tg_progress_bar` — L1116
- `_tg_dashboard_text` — L1122
- `_tg_dashboard_update` — L1140
- `_tg_maybe_digest` — L1177
- `tg` — L1192
- `_wait_image_submit_slot` — L1241
- `_wait_motion_submit_slot` — L1254
- `_is_rate_limited_error` — L1267
- `_is_rate_limited_response` — L1277
- `_inject_image2_quality_suffix` — L1299
- `submit_text_to_image` — L1313
- `req_post` — L1343
- `req_get` — L1357
- `_tg_probe_send` — L1365
- `_tg_probe_delete` — L1385
- `_tg_upload_with_probe_gap` — L1398
- `poll` — L1438
- `poll_podcast` — L1463
- `poll_task_status` — L1485
- `poll_storyboard_task` — L1507
- `chat` — L1533
- `pick_image_model` — L1561
- `detect_topic_meta` — L1586
- `_topic_culture_guard` — L1636
- `_write_cultural_visual_qa` — L1662
- `is_1919_global_topic` — L1709
- `_strip_topic_modifiers` — L1720
- `apply_1919_global_guardrails` — L1738
- `build_1919_global_cover_prompt` — L1767
- `build_shot_blueprint` — L1796
- `ffprobe_duration` — L1822
- `ffprobe_video_size` — L1833
- `_video_decode_probe` — L1854
- `ffmpeg` — L1872

---

### 第一步：双导演生成剧本
Range: **L1884 – L3524** (1641 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L2818-3524 (707 lines)

**Functions:**
- `_extract_json_array` — L1885
- `_extract_json_object` — L1895
- `_voice_for_speaker` — L1905
- `_adsd_gender_from_voice` — L1941
- `_adsd_infer_gender_from_speaker` — L1949
- `_adsd_gender_lock_phrase` — L1958
- `_adsd_visual_subject_has_gender_conflict` — L1973
- `_adsd_default_roles` — L1985
- `_adsd_allows_media_role` — L1990
- `_adsd_role_candidates` — L1998
- `_adsd_dialogue_shape` — L2021
- `_finalize_adsd_turns` — L2030
- `_parse_adsd_override_turns` — L2064
- `_parse_timecode_seconds` — L2155
- `_clean_override_line_text` — L2164
- `_parse_override_script_text` — L2170
- `_adsd_pov_contract` — L2204
- `_generate_adsd_dialogue_turns` — L2214
- `_adsd_immersion_qa_rewrite_turns` — L2481
- `_adsd_visual_contract` — L2539
- `step1_script` — L2591
- `_write_ads_retention_qa` — L3468

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L3525 – L4626** (1102 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L3600
- `_ADSD_POLICY_REWRITE_TERMS` — L3606
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L3697

**Functions:**
- `_openai_tts_fallback` — L3526
- `_edge_tts_fallback` — L3572
- `_sanitize_for_external_api` — L3615
- `_is_content_policy_error` — L3624
- `_rewrite_adsd_tts_text_for_policy` — L3638
- `_record_adsd_tts_rewrite` — L3678
- `_build_silence_mp3` — L3703
- `_audio_duration_seconds` — L3716
- `_text_to_audio_master_voice_timed` — L3728
- `_text_to_audio_master_voice` — L3853
- `step2_master_voice` — L3956
- `_tts_turn_to_audio` — L4084
- `_asr_verify_dialogue_audio` — L4146
- `_asr_verify_dialogue_turns` — L4208
- `_normalize_cn_number_token` — L4250
- `_compact_zh_text` — L4272
- `_write_adsd_asr_text_qa` — L4279
- `_write_adsd_speaker_focus_qa` — L4318
- `_write_adsd_gender_voice_qa` — L4378
- `step2_dialogue_voice` — L4431

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L4627 – L5178** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L4634-4756 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L4757-4791 (35 lines)
- _第二层：字符数插值_ — L4792-4816 (25 lines)
- _第三层：silencedetect 物理校准_ — L4817-5178 (362 lines)

**Functions:**
- `_detect_silences` — L4635
- `_calibrate_boundaries` — L4670
- `_enforce_monotonic` — L4704
- `_manual_override_segments` — L4716
- `_calc_sentence_boundaries` — L4737
- `step345_timeline` — L4848
- `_analyze_bgm_energy_cuts` — L4907
- `_snap_bgm_only_boundaries` — L4970
- `step345_bgm_only_timeline` — L5030

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L5179 – L8329** (3151 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L6265-6315 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L6316-6416 (101 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L6417-6688 (272 lines)
- _Speaker IP Card (2026-05-21)_ — L6689-8162 (1474 lines)
- _审批流程_ — L8163-8219 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L8220-8329 (110 lines)

**Top-level constants:**
- `CHARACTER_META_GRID_COSTUMES` — L6271
- `CHARACTER_META_GRID_POSES` — L6272
- `CHARACTER_META_GRID_SCENES` — L6273
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L6276

**Functions:**
- `_extract_img_url` — L5180
- `_extract_img_urls` — L5202
- `_extract_video_url` — L5235
- `_count_bands` — L5260
- `_detect_contact_sheet_like_image` — L5272
- `_guess_upload_mime` — L5326
- `_upload_to_weryai` — L5349
- `_send_for_approval` — L5381
- `_wait_approval` — L5445
- `_render_still_segment` — L5457
- `_scene_text_visual_alignment` — L5471
- `_write_text_visual_alignment_qa` — L5507
- `_scene_motion_action_plan` — L5530
- `_ensure_motion_action_plan` — L5584
- `_motion_action_block` — L5593
- `_motion_plan_for_qa` — L5621
- `_write_motion_action_plan_qa` — L5631
- `_write_motion_bridge_refs_qa` — L5661
- `_motion_bridge_ref_prompt` — L5668
- `generate_motion_bridge_refs_gpt_image2` — L5701
- `generate_image` — L5814
- `generate_storyboard_images_gpt_image2` — L5861
- `_storyboard_grid_aspect` — L6046
- `_storyboard_grid_cols_rows` — L6053
- `_storyboard_grid_prompt` — L6075
- `_storyboard_grid_prompt_limit` — L6113
- `_is_prompt_limit_response` — L6117
- `_production_storyboard_prompt` — L6123
- `_write_production_storyboard_page_qa` — L6157
- `_character_sheet_prompt` — L6167
- `_is_audit_blocked` — L6293
- `_paraphrase_sensitive_dialogue` — L6306
- `_topic_cache_dir` — L6320
- `_topic_cache_path` — L6326
- `_load_topic_decomposition_cache` — L6331
- `_save_topic_decomposition_cache` — L6341
- `_llm_topic_decomposition` — L6346
- `_llm_infer_meta_grid_template` — L6474
- `_resolve_meta_grid_template` — L6531
- `_infer_meta_grid_costume` — L6574
- `_infer_meta_grid_pose` — L6619
- `_adsd_meta_grid_call_prompt` — L6662
- `_migrate_speaker_ip` — L6695
- `_speaker_ips_dir` — L6713
- `_list_speaker_ips` — L6720
- `_match_speaker_ip` — L6734
- `_build_speaker_ip_context_for_script` — L6754
- `_save_speaker_ip` — L6800
- `_record_speaker_usage_history` — L6809
- `_format_speaker_usage_history_for_prompt` — L6851
- `_character_meta_grid_cache_dir` — L6869
- `_character_meta_grid_cache_path` — L6877
- `_character_meta_grid_path` — L6883
- `generate_character_meta_grid_gpt_image2` — L6889
- `_generate_all_character_meta_grids` — L7008
- `_write_character_sheet_qa` — L7049
- `generate_character_sheet_gpt_image2` — L7059
- `generate_production_storyboard_page_gpt_image2` — L7159
- `_qa_clean_storyboard_panel` — L7222
- `_crop_storyboard_grid_panels` — L7403
- `generate_storyboard_grid_gpt_image2` — L7450
- `_gpt_image2_direct_annotated_aspect` — L7681
- `_gpt_image2_direct_annotated_prompt` — L7688
- `generate_gpt_image2_direct_annotated_storyboards` — L7718
- `_llm_bgm_description` — L7819
- `_bgm_contains_vocals` — L7858
- `generate_bgm` — L7892
- `step6_parallel` — L8009

---

### 第 6.5 步：动态化（可选，--with-motion 开启）
Range: **L8330 – L12527** (4198 lines)

**Sub-sections:**
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L12269-12311 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L12312-12349 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回主音轨_ — L12350-12482 (133 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L12483-12527 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L8333
- `_motion_tasks_file` — L8400
- `_motion_qa_file` — L8404
- `_append_motion_qa` — L8408
- `_finalize_motion_qa` — L8432
- `_lip_sync_tasks_file` — L8516
- `_load_motion_tasks` — L8520
- `_save_motion_task` — L8530
- `_remove_motion_task` — L8538
- `_load_lip_sync_tasks` — L8545
- `_save_lip_sync_task` — L8555
- `_remove_lip_sync_task` — L8562
- `_video_visual_motion_qa` — L8569
- `_motion_output_qa` — L8641
- `_has_audio_stream` — L8686
- `_normalize_motion_video` — L8697
- `_motion_poll_and_download` — L8747
- `_build_motion_video_prompt` — L8798
- `_short_board_text` — L8828
- `_wrap_board_text` — L8835
- `_storyboard_font` — L8866
- `_draw_storyboard_arrow` — L8881
- `_build_annotated_storyboard_reference` — L8895
- `_plain_caption_text` — L8996
- `_werydance_caption_request` — L9004
- `_werydance_caption_instruction` — L9031
- `_werydance_negative_prompt` — L9043
- `_motion_reference_prompt` — L9057
- `_motion_audio_dub_prompt` — L9080
- `_motion_audio_dub_poll_and_download` — L9114
- `_try_motion_audio_dub_video` — L9179
- `_try_motion_reference_video` — L9314
- `_motion_one_scene` — L9430
- `_grid_multiref_tasks_file` — L9559
- `_previs_page_tasks_file` — L9563
- `_load_grid_multiref_tasks` — L9567
- `_load_previs_page_tasks` — L9577
- `_save_grid_multiref_task` — L9587
- `_save_previs_page_task` — L9594
- `_remove_grid_multiref_task` — L9601
- `_remove_previs_page_task` — L9608
- `_poll_video_task_download` — L9615
- `_grid_multiref_group_size` — L9664
- `_grid_multiref_duration` — L9672
- `_grid_multiref_segment_max_stretch` — L9688
- `_grid_multiref_prompt` — L9696
- `_write_grid_multiref_motion_qa` — L9744
- `_write_previs_page_motion_qa` — L9754
- `_write_storyboard_trailer_qa` — L9764
- `_write_character_trailer_qa` — L9774
- `_write_grid_multiref_segment_qa` — L9784
- `_motion_compare_record` — L9794
- `_write_storyboard_motion_compare_qa` — L9816
- `_scene_segment_duration` — L9852
- `_apply_grid_multiref_segments` — L9871
- `_previs_page_duration` — L10065
- `_previs_page_group_prompt` — L10075
- `_previs_page_groups` — L10101
- `_storyboard_trailer_duration` — L10116
- `_storyboard_trailer_prompt` — L10126
- `_character_trailer_max_shots` — L10154
- `_character_trailer_shot_duration` — L10162
- `_character_trailer_prompt` — L10176
- `_concat_character_trailer_segments` — L10191
- `_generate_character_trailer_motion` — L10230
- `_multi_trailer_prompt_for_group` — L10338
- `_generate_multi_trailer_segments` — L10361
- `_generate_storyboard_trailer_motion` — L10472
- `_generate_previs_page_motion_segments` — L10547
- `_generate_grid_multiref_motion_segments` — L10659
- `_grid_multiref_concat_groups` — L10829
- `_grid_multiref_concat_groups_partial` — L10846
- `_grid_multiref_concat_paths` — L10864
- `_lip_sync_slot_duration` — L10895
- `_adsd_lip_sync_prompt` — L10902
- `_adsd_broll_motion_prompt` — L10948
- `_adsd_action_b_motion_prompt` — L10990
- `_adsd_silent_b_motion_prompt` — L11027
- `_adsd_narrated_b_audio_dub_prompt` — L11062
- `_adsd_almighty_audio_dub_prompt` — L11106
- `_postprocess_lip_sync_segment` — L11141
- `_detect_audio_leading_silence` — L11209
- `_postprocess_audio_dub_segment` — L11231
- `_lips_change_repair_segment` — L11337
- `_load_lips_change_requested_turns` — L11422
- `_parse_turn_set` — L11439
- `_load_motion_voice_repair_turns` — L11461
- `_voice_assets_file` — L11473
- `_load_voice_assets` — L11480
- `_select_voice_asset_reference` — L11499
- `_lip_sync_poll_download_and_process` — L11565
- `_lip_sync_one_scene` — L11629
- `step66_adsd_lip_sync` — L11926
- `step65_motion` — L12159
- `step65_grid_multiref_motion_qa` — L12241
- `_sanitize_scene_for_state` — L12270
- `_save_pipeline_state` — L12289
- `_retime_after_audio_dub` — L12313
- `_build_voice_clone_hybrid_audio` — L12351
- `_build_dynamic_bgm` — L12484

---

### 第七步：拼接视频轨
Range: **L12528 – L12697** (170 lines)

**Functions:**
- `step7_concat` — L12529

---

### 第八步：生成 ASS 字幕
Range: **L12698 – L13489** (792 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L12821-13489 (669 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L12699
- `_word_timings_for_subtitle_align` — L12725
- `_align_segments_via_asr` — L12766
- `step8_subtitles` — L12809
- `_read_output_json` — L13221
- `_qa_file_pass` — L13232
- `_ass_has_dialogue` — L13239
- `_write_adsd_delivery_qa` — L13249
- `_write_bgm_only_qa` — L13378

---

### 第九步：最终合成
Range: **L13490 – L13730** (241 lines)

**Functions:**
- `step9_render` — L13491

---

### 第十步：推送 Telegram
Range: **L13731 – L15345** (1615 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L14831-15152 (322 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L15153-15157 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L15158-15221 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L15222-15267 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L15268-15345 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L14100
- `PANTONE_FALLBACK` — L14127
- `FESTIVAL_DATE_TAG` — L14240

**Functions:**
- `_generate_caption` — L13732
- `_overlay_title_on_cover` — L13970
- `_prepare_tg_photo` — L14080
- `_get_pantone_for_date` — L14130
- `_llm_bottom_note` — L14155
- `_get_bottom_note` — L14184
- `_get_date_tag` — L14262
- `_shrink_to_b64` — L14284
- `_llm_check_scenes_anomalies` — L14300
- `_llm_check_cover_unique` — L14353
- `_llm_check_cover_quality` — L14383
- `_try_almanac_cover` — L14425
- `_generate_cover_image` — L14596
- `_async_kickoff_cover_caption` — L14838
- `_await_async_cover_caption` — L14868
- `step10_deliver` — L14892

---

### 主流程
Range: **L15346 – L15515** (170 lines)

**Functions:**
- `_print_execution_plan` — L15347
- `main` — L15395

---
