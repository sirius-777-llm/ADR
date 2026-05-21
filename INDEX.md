# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (15790 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-1883 (1762 lines · 55 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L1884-3540 (1657 lines · 22 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L3541-4642 (1102 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L4643-5194 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L5195-8590 (3396 lines · 73 fn · 6 sub)
- [`第 6.5 步：动态化（可选，--with-motion 开启）`](#第-6-5-步-动态化-可选---with-motion-开启) — L8591-12794 (4204 lines · 100 fn · 4 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L12795-12964 (170 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L12965-13756 (792 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L13757-13997 (241 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L13998-15612 (1615 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L15613-15790 (178 lines · 2 fn · 0 sub)

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
Range: **L1884 – L3540** (1657 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L2834-3540 (707 lines)

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
- `_adsd_immersion_qa_rewrite_turns` — L2497
- `_adsd_visual_contract` — L2555
- `step1_script` — L2607
- `_write_ads_retention_qa` — L3484

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L3541 – L4642** (1102 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L3616
- `_ADSD_POLICY_REWRITE_TERMS` — L3622
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L3713

**Functions:**
- `_openai_tts_fallback` — L3542
- `_edge_tts_fallback` — L3588
- `_sanitize_for_external_api` — L3631
- `_is_content_policy_error` — L3640
- `_rewrite_adsd_tts_text_for_policy` — L3654
- `_record_adsd_tts_rewrite` — L3694
- `_build_silence_mp3` — L3719
- `_audio_duration_seconds` — L3732
- `_text_to_audio_master_voice_timed` — L3744
- `_text_to_audio_master_voice` — L3869
- `step2_master_voice` — L3972
- `_tts_turn_to_audio` — L4100
- `_asr_verify_dialogue_audio` — L4162
- `_asr_verify_dialogue_turns` — L4224
- `_normalize_cn_number_token` — L4266
- `_compact_zh_text` — L4288
- `_write_adsd_asr_text_qa` — L4295
- `_write_adsd_speaker_focus_qa` — L4334
- `_write_adsd_gender_voice_qa` — L4394
- `step2_dialogue_voice` — L4447

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L4643 – L5194** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L4650-4772 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L4773-4807 (35 lines)
- _第二层：字符数插值_ — L4808-4832 (25 lines)
- _第三层：silencedetect 物理校准_ — L4833-5194 (362 lines)

**Functions:**
- `_detect_silences` — L4651
- `_calibrate_boundaries` — L4686
- `_enforce_monotonic` — L4720
- `_manual_override_segments` — L4732
- `_calc_sentence_boundaries` — L4753
- `step345_timeline` — L4864
- `_analyze_bgm_energy_cuts` — L4923
- `_snap_bgm_only_boundaries` — L4986
- `step345_bgm_only_timeline` — L5046

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L5195 – L8590** (3396 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L6281-6331 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L6332-6432 (101 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L6433-6715 (283 lines)
- _Speaker IP Card (2026-05-21)_ — L6716-8423 (1708 lines)
- _审批流程_ — L8424-8480 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L8481-8590 (110 lines)

**Top-level constants:**
- `CHARACTER_META_GRID_COSTUMES` — L6287
- `CHARACTER_META_GRID_POSES` — L6288
- `CHARACTER_META_GRID_SCENES` — L6289
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L6292

**Functions:**
- `_extract_img_url` — L5196
- `_extract_img_urls` — L5218
- `_extract_video_url` — L5251
- `_count_bands` — L5276
- `_detect_contact_sheet_like_image` — L5288
- `_guess_upload_mime` — L5342
- `_upload_to_weryai` — L5365
- `_send_for_approval` — L5397
- `_wait_approval` — L5461
- `_render_still_segment` — L5473
- `_scene_text_visual_alignment` — L5487
- `_write_text_visual_alignment_qa` — L5523
- `_scene_motion_action_plan` — L5546
- `_ensure_motion_action_plan` — L5600
- `_motion_action_block` — L5609
- `_motion_plan_for_qa` — L5637
- `_write_motion_action_plan_qa` — L5647
- `_write_motion_bridge_refs_qa` — L5677
- `_motion_bridge_ref_prompt` — L5684
- `generate_motion_bridge_refs_gpt_image2` — L5717
- `generate_image` — L5830
- `generate_storyboard_images_gpt_image2` — L5877
- `_storyboard_grid_aspect` — L6062
- `_storyboard_grid_cols_rows` — L6069
- `_storyboard_grid_prompt` — L6091
- `_storyboard_grid_prompt_limit` — L6129
- `_is_prompt_limit_response` — L6133
- `_production_storyboard_prompt` — L6139
- `_write_production_storyboard_page_qa` — L6173
- `_character_sheet_prompt` — L6183
- `_is_audit_blocked` — L6309
- `_paraphrase_sensitive_dialogue` — L6322
- `_topic_cache_dir` — L6336
- `_topic_cache_path` — L6342
- `_load_topic_decomposition_cache` — L6347
- `_save_topic_decomposition_cache` — L6357
- `_llm_topic_decomposition` — L6362
- `_llm_infer_meta_grid_template` — L6490
- `_resolve_meta_grid_template` — L6547
- `_infer_meta_grid_costume` — L6590
- `_infer_meta_grid_pose` — L6639
- `_adsd_meta_grid_call_prompt` — L6686
- `_migrate_speaker_ip` — L6722
- `_speaker_ips_dir` — L6747
- `_list_speaker_ips` — L6754
- `_match_speaker_ip` — L6768
- `_build_speaker_ip_context_for_script` — L6788
- `_ip_usage_stats` — L6844
- `_recommend_related_ips` — L6862
- `_save_speaker_ip` — L6887
- `_record_speaker_usage_history` — L6896
- `_format_speaker_usage_history_for_prompt` — L6943
- `_llm_infer_ip_skeleton` — L6961
- `_llm_pick_voice_asset_for_ip` — L7006
- `_auto_incubate_missing_ips` — L7054
- `_character_meta_grid_cache_dir` — L7130
- `_character_meta_grid_cache_path` — L7138
- `_character_meta_grid_path` — L7144
- `generate_character_meta_grid_gpt_image2` — L7150
- `_generate_all_character_meta_grids` — L7269
- `_write_character_sheet_qa` — L7310
- `generate_character_sheet_gpt_image2` — L7320
- `generate_production_storyboard_page_gpt_image2` — L7420
- `_qa_clean_storyboard_panel` — L7483
- `_crop_storyboard_grid_panels` — L7664
- `generate_storyboard_grid_gpt_image2` — L7711
- `_gpt_image2_direct_annotated_aspect` — L7942
- `_gpt_image2_direct_annotated_prompt` — L7949
- `generate_gpt_image2_direct_annotated_storyboards` — L7979
- `_llm_bgm_description` — L8080
- `_bgm_contains_vocals` — L8119
- `generate_bgm` — L8153
- `step6_parallel` — L8270

---

### 第 6.5 步：动态化（可选，--with-motion 开启）
Range: **L8591 – L12794** (4204 lines)

**Sub-sections:**
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L12536-12578 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L12579-12616 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回主音轨_ — L12617-12749 (133 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L12750-12794 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L8594
- `_motion_tasks_file` — L8661
- `_motion_qa_file` — L8665
- `_append_motion_qa` — L8669
- `_finalize_motion_qa` — L8693
- `_lip_sync_tasks_file` — L8777
- `_load_motion_tasks` — L8781
- `_save_motion_task` — L8791
- `_remove_motion_task` — L8799
- `_load_lip_sync_tasks` — L8806
- `_save_lip_sync_task` — L8816
- `_remove_lip_sync_task` — L8823
- `_video_visual_motion_qa` — L8830
- `_motion_output_qa` — L8902
- `_has_audio_stream` — L8947
- `_normalize_motion_video` — L8958
- `_motion_poll_and_download` — L9008
- `_build_motion_video_prompt` — L9059
- `_short_board_text` — L9089
- `_wrap_board_text` — L9096
- `_storyboard_font` — L9127
- `_draw_storyboard_arrow` — L9142
- `_build_annotated_storyboard_reference` — L9156
- `_plain_caption_text` — L9257
- `_werydance_caption_request` — L9265
- `_werydance_caption_instruction` — L9292
- `_werydance_negative_prompt` — L9304
- `_motion_reference_prompt` — L9318
- `_motion_audio_dub_prompt` — L9341
- `_motion_audio_dub_poll_and_download` — L9375
- `_try_motion_audio_dub_video` — L9440
- `_try_motion_reference_video` — L9575
- `_motion_one_scene` — L9691
- `_grid_multiref_tasks_file` — L9820
- `_previs_page_tasks_file` — L9824
- `_load_grid_multiref_tasks` — L9828
- `_load_previs_page_tasks` — L9838
- `_save_grid_multiref_task` — L9848
- `_save_previs_page_task` — L9855
- `_remove_grid_multiref_task` — L9862
- `_remove_previs_page_task` — L9869
- `_poll_video_task_download` — L9876
- `_grid_multiref_group_size` — L9925
- `_grid_multiref_duration` — L9933
- `_grid_multiref_segment_max_stretch` — L9949
- `_grid_multiref_prompt` — L9957
- `_write_grid_multiref_motion_qa` — L10005
- `_write_previs_page_motion_qa` — L10015
- `_write_storyboard_trailer_qa` — L10025
- `_write_character_trailer_qa` — L10035
- `_write_grid_multiref_segment_qa` — L10045
- `_motion_compare_record` — L10055
- `_write_storyboard_motion_compare_qa` — L10077
- `_scene_segment_duration` — L10113
- `_apply_grid_multiref_segments` — L10132
- `_previs_page_duration` — L10326
- `_previs_page_group_prompt` — L10336
- `_previs_page_groups` — L10362
- `_storyboard_trailer_duration` — L10377
- `_storyboard_trailer_prompt` — L10387
- `_character_trailer_max_shots` — L10415
- `_character_trailer_shot_duration` — L10423
- `_character_trailer_prompt` — L10437
- `_concat_character_trailer_segments` — L10452
- `_generate_character_trailer_motion` — L10491
- `_multi_trailer_prompt_for_group` — L10599
- `_generate_multi_trailer_segments` — L10622
- `_generate_storyboard_trailer_motion` — L10733
- `_generate_previs_page_motion_segments` — L10808
- `_generate_grid_multiref_motion_segments` — L10920
- `_grid_multiref_concat_groups` — L11090
- `_grid_multiref_concat_groups_partial` — L11107
- `_grid_multiref_concat_paths` — L11125
- `_lip_sync_slot_duration` — L11156
- `_adsd_lip_sync_prompt` — L11163
- `_adsd_broll_motion_prompt` — L11209
- `_adsd_action_b_motion_prompt` — L11251
- `_adsd_silent_b_motion_prompt` — L11288
- `_adsd_narrated_b_audio_dub_prompt` — L11323
- `_adsd_almighty_audio_dub_prompt` — L11367
- `_postprocess_lip_sync_segment` — L11408
- `_detect_audio_leading_silence` — L11476
- `_postprocess_audio_dub_segment` — L11498
- `_lips_change_repair_segment` — L11604
- `_load_lips_change_requested_turns` — L11689
- `_parse_turn_set` — L11706
- `_load_motion_voice_repair_turns` — L11728
- `_voice_assets_file` — L11740
- `_load_voice_assets` — L11747
- `_select_voice_asset_reference` — L11766
- `_lip_sync_poll_download_and_process` — L11832
- `_lip_sync_one_scene` — L11896
- `step66_adsd_lip_sync` — L12193
- `step65_motion` — L12426
- `step65_grid_multiref_motion_qa` — L12508
- `_sanitize_scene_for_state` — L12537
- `_save_pipeline_state` — L12556
- `_retime_after_audio_dub` — L12580
- `_build_voice_clone_hybrid_audio` — L12618
- `_build_dynamic_bgm` — L12751

---

### 第七步：拼接视频轨
Range: **L12795 – L12964** (170 lines)

**Functions:**
- `step7_concat` — L12796

---

### 第八步：生成 ASS 字幕
Range: **L12965 – L13756** (792 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L13088-13756 (669 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L12966
- `_word_timings_for_subtitle_align` — L12992
- `_align_segments_via_asr` — L13033
- `step8_subtitles` — L13076
- `_read_output_json` — L13488
- `_qa_file_pass` — L13499
- `_ass_has_dialogue` — L13506
- `_write_adsd_delivery_qa` — L13516
- `_write_bgm_only_qa` — L13645

---

### 第九步：最终合成
Range: **L13757 – L13997** (241 lines)

**Functions:**
- `step9_render` — L13758

---

### 第十步：推送 Telegram
Range: **L13998 – L15612** (1615 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L15098-15419 (322 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L15420-15424 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L15425-15488 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L15489-15534 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L15535-15612 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L14367
- `PANTONE_FALLBACK` — L14394
- `FESTIVAL_DATE_TAG` — L14507

**Functions:**
- `_generate_caption` — L13999
- `_overlay_title_on_cover` — L14237
- `_prepare_tg_photo` — L14347
- `_get_pantone_for_date` — L14397
- `_llm_bottom_note` — L14422
- `_get_bottom_note` — L14451
- `_get_date_tag` — L14529
- `_shrink_to_b64` — L14551
- `_llm_check_scenes_anomalies` — L14567
- `_llm_check_cover_unique` — L14620
- `_llm_check_cover_quality` — L14650
- `_try_almanac_cover` — L14692
- `_generate_cover_image` — L14863
- `_async_kickoff_cover_caption` — L15105
- `_await_async_cover_caption` — L15135
- `step10_deliver` — L15159

---

### 主流程
Range: **L15613 – L15790** (178 lines)

**Functions:**
- `_print_execution_plan` — L15614
- `main` — L15662

---
