# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (14741 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-1869 (1748 lines · 54 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L1870-3480 (1611 lines · 22 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L3481-4582 (1102 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L4583-5134 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L5135-7654 (2520 lines · 52 fn · 3 sub)
- [`第 6.5 步：动态化（可选，--with-motion 开启）`](#第-6-5-步-动态化-可选---with-motion-开启) — L7655-11763 (4109 lines · 99 fn · 4 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L11764-11933 (170 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L11934-12721 (788 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L12722-12962 (241 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L12963-14577 (1615 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L14578-14741 (164 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L1869** (1748 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L298-423 (126 lines)
- _三类 turn 区分 (silent_b PR)_ — L424-997 (574 lines)
- _工具函数_ — L998-1347 (350 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1348-1869 (522 lines)

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
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1277
- `_TOPIC_MODIFIERS` — L1701
- `_TONE_PANTONE_OVERRIDE` — L1718

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
- `_inject_image2_quality_suffix` — L1285
- `submit_text_to_image` — L1299
- `req_post` — L1329
- `req_get` — L1343
- `_tg_probe_send` — L1351
- `_tg_probe_delete` — L1371
- `_tg_upload_with_probe_gap` — L1384
- `poll` — L1424
- `poll_podcast` — L1449
- `poll_task_status` — L1471
- `poll_storyboard_task` — L1493
- `chat` — L1519
- `pick_image_model` — L1547
- `detect_topic_meta` — L1572
- `_topic_culture_guard` — L1622
- `_write_cultural_visual_qa` — L1648
- `is_1919_global_topic` — L1695
- `_strip_topic_modifiers` — L1706
- `apply_1919_global_guardrails` — L1724
- `build_1919_global_cover_prompt` — L1753
- `build_shot_blueprint` — L1782
- `ffprobe_duration` — L1808
- `ffprobe_video_size` — L1819
- `_video_decode_probe` — L1840
- `ffmpeg` — L1858

---

### 第一步：双导演生成剧本
Range: **L1870 – L3480** (1611 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L2774-3480 (707 lines)

**Functions:**
- `_extract_json_array` — L1871
- `_extract_json_object` — L1881
- `_voice_for_speaker` — L1891
- `_adsd_gender_from_voice` — L1927
- `_adsd_infer_gender_from_speaker` — L1935
- `_adsd_gender_lock_phrase` — L1944
- `_adsd_visual_subject_has_gender_conflict` — L1959
- `_adsd_default_roles` — L1971
- `_adsd_allows_media_role` — L1976
- `_adsd_role_candidates` — L1984
- `_adsd_dialogue_shape` — L2000
- `_finalize_adsd_turns` — L2009
- `_parse_adsd_override_turns` — L2043
- `_parse_timecode_seconds` — L2134
- `_clean_override_line_text` — L2143
- `_parse_override_script_text` — L2149
- `_adsd_pov_contract` — L2183
- `_generate_adsd_dialogue_turns` — L2193
- `_adsd_immersion_qa_rewrite_turns` — L2437
- `_adsd_visual_contract` — L2495
- `step1_script` — L2547
- `_write_ads_retention_qa` — L3424

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L3481 – L4582** (1102 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L3556
- `_ADSD_POLICY_REWRITE_TERMS` — L3562
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L3653

**Functions:**
- `_openai_tts_fallback` — L3482
- `_edge_tts_fallback` — L3528
- `_sanitize_for_external_api` — L3571
- `_is_content_policy_error` — L3580
- `_rewrite_adsd_tts_text_for_policy` — L3594
- `_record_adsd_tts_rewrite` — L3634
- `_build_silence_mp3` — L3659
- `_audio_duration_seconds` — L3672
- `_text_to_audio_master_voice_timed` — L3684
- `_text_to_audio_master_voice` — L3809
- `step2_master_voice` — L3912
- `_tts_turn_to_audio` — L4040
- `_asr_verify_dialogue_audio` — L4102
- `_asr_verify_dialogue_turns` — L4164
- `_normalize_cn_number_token` — L4206
- `_compact_zh_text` — L4228
- `_write_adsd_asr_text_qa` — L4235
- `_write_adsd_speaker_focus_qa` — L4274
- `_write_adsd_gender_voice_qa` — L4334
- `step2_dialogue_voice` — L4387

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L4583 – L5134** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L4590-4712 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L4713-4747 (35 lines)
- _第二层：字符数插值_ — L4748-4772 (25 lines)
- _第三层：silencedetect 物理校准_ — L4773-5134 (362 lines)

**Functions:**
- `_detect_silences` — L4591
- `_calibrate_boundaries` — L4626
- `_enforce_monotonic` — L4660
- `_manual_override_segments` — L4672
- `_calc_sentence_boundaries` — L4693
- `step345_timeline` — L4804
- `_analyze_bgm_energy_cuts` — L4863
- `_snap_bgm_only_boundaries` — L4926
- `step345_bgm_only_timeline` — L4986

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L5135 – L7654** (2520 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L6208-7487 (1280 lines)
- _审批流程_ — L7488-7544 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L7545-7654 (110 lines)

**Top-level constants:**
- `CHARACTER_META_GRID_COSTUMES` — L6214
- `CHARACTER_META_GRID_POSES` — L6215
- `CHARACTER_META_GRID_SCENES` — L6216
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L6219

**Functions:**
- `_extract_img_url` — L5136
- `_extract_img_urls` — L5158
- `_extract_video_url` — L5191
- `_count_bands` — L5216
- `_detect_contact_sheet_like_image` — L5228
- `_guess_upload_mime` — L5282
- `_upload_to_weryai` — L5305
- `_send_for_approval` — L5337
- `_wait_approval` — L5401
- `_render_still_segment` — L5413
- `_scene_text_visual_alignment` — L5427
- `_write_text_visual_alignment_qa` — L5463
- `_scene_motion_action_plan` — L5486
- `_ensure_motion_action_plan` — L5540
- `_motion_action_block` — L5549
- `_motion_plan_for_qa` — L5571
- `_write_motion_action_plan_qa` — L5581
- `_write_motion_bridge_refs_qa` — L5611
- `_motion_bridge_ref_prompt` — L5618
- `generate_motion_bridge_refs_gpt_image2` — L5651
- `generate_image` — L5764
- `generate_storyboard_images_gpt_image2` — L5811
- `_storyboard_grid_aspect` — L5996
- `_storyboard_grid_cols_rows` — L6003
- `_storyboard_grid_prompt` — L6025
- `_storyboard_grid_prompt_limit` — L6056
- `_is_prompt_limit_response` — L6060
- `_production_storyboard_prompt` — L6066
- `_write_production_storyboard_page_qa` — L6100
- `_character_sheet_prompt` — L6110
- `_is_audit_blocked` — L6236
- `_paraphrase_sensitive_dialogue` — L6249
- `_infer_meta_grid_costume` — L6259
- `_infer_meta_grid_pose` — L6271
- `_adsd_meta_grid_call_prompt` — L6286
- `_character_meta_grid_cache_dir` — L6302
- `_character_meta_grid_cache_path` — L6310
- `_character_meta_grid_path` — L6316
- `generate_character_meta_grid_gpt_image2` — L6322
- `_generate_all_character_meta_grids` — L6403
- `_write_character_sheet_qa` — L6444
- `generate_character_sheet_gpt_image2` — L6454
- `generate_production_storyboard_page_gpt_image2` — L6554
- `_qa_clean_storyboard_panel` — L6617
- `_crop_storyboard_grid_panels` — L6798
- `generate_storyboard_grid_gpt_image2` — L6845
- `_gpt_image2_direct_annotated_aspect` — L7076
- `_gpt_image2_direct_annotated_prompt` — L7083
- `generate_gpt_image2_direct_annotated_storyboards` — L7113
- `_llm_bgm_description` — L7214
- `generate_bgm` — L7253
- `step6_parallel` — L7344

---

### 第 6.5 步：动态化（可选，--with-motion 开启）
Range: **L7655 – L11763** (4109 lines)

**Sub-sections:**
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L11505-11547 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L11548-11585 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回主音轨_ — L11586-11718 (133 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L11719-11763 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L7658
- `_motion_tasks_file` — L7725
- `_motion_qa_file` — L7729
- `_append_motion_qa` — L7733
- `_finalize_motion_qa` — L7757
- `_lip_sync_tasks_file` — L7841
- `_load_motion_tasks` — L7845
- `_save_motion_task` — L7855
- `_remove_motion_task` — L7863
- `_load_lip_sync_tasks` — L7870
- `_save_lip_sync_task` — L7880
- `_remove_lip_sync_task` — L7887
- `_video_visual_motion_qa` — L7894
- `_motion_output_qa` — L7966
- `_has_audio_stream` — L8011
- `_normalize_motion_video` — L8022
- `_motion_poll_and_download` — L8072
- `_build_motion_video_prompt` — L8123
- `_short_board_text` — L8153
- `_wrap_board_text` — L8160
- `_storyboard_font` — L8191
- `_draw_storyboard_arrow` — L8206
- `_build_annotated_storyboard_reference` — L8220
- `_plain_caption_text` — L8321
- `_werydance_caption_request` — L8329
- `_werydance_caption_instruction` — L8356
- `_werydance_negative_prompt` — L8368
- `_motion_reference_prompt` — L8382
- `_motion_audio_dub_prompt` — L8405
- `_motion_audio_dub_poll_and_download` — L8439
- `_try_motion_audio_dub_video` — L8504
- `_try_motion_reference_video` — L8639
- `_motion_one_scene` — L8755
- `_grid_multiref_tasks_file` — L8884
- `_previs_page_tasks_file` — L8888
- `_load_grid_multiref_tasks` — L8892
- `_load_previs_page_tasks` — L8902
- `_save_grid_multiref_task` — L8912
- `_save_previs_page_task` — L8919
- `_remove_grid_multiref_task` — L8926
- `_remove_previs_page_task` — L8933
- `_poll_video_task_download` — L8940
- `_grid_multiref_group_size` — L8989
- `_grid_multiref_duration` — L8997
- `_grid_multiref_segment_max_stretch` — L9013
- `_grid_multiref_prompt` — L9021
- `_write_grid_multiref_motion_qa` — L9069
- `_write_previs_page_motion_qa` — L9079
- `_write_storyboard_trailer_qa` — L9089
- `_write_character_trailer_qa` — L9099
- `_write_grid_multiref_segment_qa` — L9109
- `_motion_compare_record` — L9119
- `_write_storyboard_motion_compare_qa` — L9141
- `_scene_segment_duration` — L9177
- `_apply_grid_multiref_segments` — L9196
- `_previs_page_duration` — L9390
- `_previs_page_group_prompt` — L9400
- `_previs_page_groups` — L9426
- `_storyboard_trailer_duration` — L9441
- `_storyboard_trailer_prompt` — L9451
- `_character_trailer_max_shots` — L9479
- `_character_trailer_shot_duration` — L9487
- `_character_trailer_prompt` — L9501
- `_concat_character_trailer_segments` — L9516
- `_generate_character_trailer_motion` — L9555
- `_multi_trailer_prompt_for_group` — L9663
- `_generate_multi_trailer_segments` — L9686
- `_generate_storyboard_trailer_motion` — L9797
- `_generate_previs_page_motion_segments` — L9872
- `_generate_grid_multiref_motion_segments` — L9984
- `_grid_multiref_concat_groups` — L10154
- `_grid_multiref_concat_groups_partial` — L10171
- `_grid_multiref_concat_paths` — L10189
- `_lip_sync_slot_duration` — L10220
- `_adsd_lip_sync_prompt` — L10227
- `_adsd_broll_motion_prompt` — L10273
- `_adsd_silent_b_motion_prompt` — L10315
- `_adsd_narrated_b_audio_dub_prompt` — L10350
- `_adsd_almighty_audio_dub_prompt` — L10394
- `_postprocess_lip_sync_segment` — L10429
- `_detect_audio_leading_silence` — L10497
- `_postprocess_audio_dub_segment` — L10519
- `_lips_change_repair_segment` — L10625
- `_load_lips_change_requested_turns` — L10710
- `_parse_turn_set` — L10727
- `_load_motion_voice_repair_turns` — L10749
- `_voice_assets_file` — L10761
- `_load_voice_assets` — L10768
- `_select_voice_asset_reference` — L10787
- `_lip_sync_poll_download_and_process` — L10853
- `_lip_sync_one_scene` — L10917
- `step66_adsd_lip_sync` — L11179
- `step65_motion` — L11395
- `step65_grid_multiref_motion_qa` — L11477
- `_sanitize_scene_for_state` — L11506
- `_save_pipeline_state` — L11525
- `_retime_after_audio_dub` — L11549
- `_build_voice_clone_hybrid_audio` — L11587
- `_build_dynamic_bgm` — L11720

---

### 第七步：拼接视频轨
Range: **L11764 – L11933** (170 lines)

**Functions:**
- `step7_concat` — L11765

---

### 第八步：生成 ASS 字幕
Range: **L11934 – L12721** (788 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L12057-12721 (665 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L11935
- `_word_timings_for_subtitle_align` — L11961
- `_align_segments_via_asr` — L12002
- `step8_subtitles` — L12045
- `_read_output_json` — L12453
- `_qa_file_pass` — L12464
- `_ass_has_dialogue` — L12471
- `_write_adsd_delivery_qa` — L12481
- `_write_bgm_only_qa` — L12610

---

### 第九步：最终合成
Range: **L12722 – L12962** (241 lines)

**Functions:**
- `step9_render` — L12723

---

### 第十步：推送 Telegram
Range: **L12963 – L14577** (1615 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L14063-14384 (322 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L14385-14389 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L14390-14453 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L14454-14499 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L14500-14577 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L13332
- `PANTONE_FALLBACK` — L13359
- `FESTIVAL_DATE_TAG` — L13472

**Functions:**
- `_generate_caption` — L12964
- `_overlay_title_on_cover` — L13202
- `_prepare_tg_photo` — L13312
- `_get_pantone_for_date` — L13362
- `_llm_bottom_note` — L13387
- `_get_bottom_note` — L13416
- `_get_date_tag` — L13494
- `_shrink_to_b64` — L13516
- `_llm_check_scenes_anomalies` — L13532
- `_llm_check_cover_unique` — L13585
- `_llm_check_cover_quality` — L13615
- `_try_almanac_cover` — L13657
- `_generate_cover_image` — L13828
- `_async_kickoff_cover_caption` — L14070
- `_await_async_cover_caption` — L14100
- `step10_deliver` — L14124

---

### 主流程
Range: **L14578 – L14741** (164 lines)

**Functions:**
- `_print_execution_plan` — L14579
- `main` — L14627

---
