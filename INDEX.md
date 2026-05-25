# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (16495 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-1915 (1794 lines · 56 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L1916-3928 (2013 lines · 25 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L3929-5032 (1104 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L5033-5584 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L5585-9174 (3590 lines · 75 fn · 6 sub)
- [`第 6.5 步：动态化（可选，--with-motion 开启）`](#第-6-5-步-动态化-可选---with-motion-开启) — L9175-13432 (4258 lines · 100 fn · 4 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L13433-13664 (232 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L13665-14456 (792 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L14457-14702 (246 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L14703-16317 (1615 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L16318-16495 (178 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L1915** (1794 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L298-427 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L428-1043 (616 lines)
- _工具函数_ — L1044-1393 (350 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1394-1915 (522 lines)

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
- `VOICE_ASSET_AUDIO_DUB_EXPERIMENT` — L795
- `VOICE_ASSET_AUDIO_DUB_PARTIAL_OK` — L803
- `MOTION_VISUAL_QA` — L807
- `MOTION_VOICE_REPAIR` — L815
- `MOTION_VOICE_STRICT_LOCK` — L820
- `WERYDANCE_CAPTIONS` — L825
- `ADSD_ONSITE_POV_MODE` — L837
- `ADSD_LIPS_CHANGE_REPAIR` — L842
- `ADSD_LIPS_CHANGE_ALL` — L847
- `ADS_REPORTER_MODE` — L858
- `ADS_STORYBOARD_FLOW_DEFAULT` — L875
- `ADS_RETENTION_MODE` — L888
- `ADSD_MODE_NAME` — L894
- `EMOTION_STYLE` — L1023
- `EMOTION_STYLE_BRIGHT` — L1035
- `_TG_DASHBOARD_STAGES` — L1057
- `_TG_NOISY_PATTERNS` — L1072
- `_TG_IMMEDIATE_PATTERNS` — L1090
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1323
- `_TOPIC_MODIFIERS` — L1747
- `_TONE_PANTONE_OVERRIDE` — L1764

**Functions:**
- `_is_action_scene` — L310
- `_needs_storyboard_flow_character_sheet` — L321
- `_wuxia_action_panel_prompt` — L350
- `_action_motion_fragment` — L372
- `_infer_emotion_from_text` — L387
- `_emotion_expression_phrase` — L402
- `_infer_needs_lip_sync` — L409
- `_infer_turn_type` — L436
- `_is_action_shout` — L461
- `_resolve_turn_type` — L487
- `_is_silent_b` — L502
- `_is_narrated_b` — L506
- `_is_a_roll` — L510
- `_is_action_b` — L514
- `_voice_asset_id_for_speaker` — L518
- `_llm_assign_voice_assets` — L546
- `_apply_llm_voice_assignment` — L670
- `log` — L1045
- `_tg_send_raw` — L1113
- `_tg_matches` — L1129
- `_tg_summarize` — L1133
- `_tg_dashboard_stage_for` — L1140
- `_tg_progress_bar` — L1148
- `_tg_dashboard_text` — L1154
- `_tg_dashboard_update` — L1172
- `_tg_maybe_digest` — L1209
- `tg` — L1224
- `_wait_image_submit_slot` — L1273
- `_wait_motion_submit_slot` — L1286
- `_is_rate_limited_error` — L1299
- `_is_rate_limited_response` — L1309
- `_inject_image2_quality_suffix` — L1331
- `submit_text_to_image` — L1345
- `req_post` — L1375
- `req_get` — L1389
- `_tg_probe_send` — L1397
- `_tg_probe_delete` — L1417
- `_tg_upload_with_probe_gap` — L1430
- `poll` — L1470
- `poll_podcast` — L1495
- `poll_task_status` — L1517
- `poll_storyboard_task` — L1539
- `chat` — L1565
- `pick_image_model` — L1593
- `detect_topic_meta` — L1618
- `_topic_culture_guard` — L1668
- `_write_cultural_visual_qa` — L1694
- `is_1919_global_topic` — L1741
- `_strip_topic_modifiers` — L1752
- `apply_1919_global_guardrails` — L1770
- `build_1919_global_cover_prompt` — L1799
- `build_shot_blueprint` — L1828
- `ffprobe_duration` — L1854
- `ffprobe_video_size` — L1865
- `_video_decode_probe` — L1886
- `ffmpeg` — L1904

---

### 第一步：双导演生成剧本
Range: **L1916 – L3928** (2013 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L3214-3928 (715 lines)

**Functions:**
- `_extract_json_array` — L1917
- `_extract_json_object` — L1927
- `_voice_for_speaker` — L1937
- `_adsd_gender_from_voice` — L1973
- `_adsd_infer_gender_from_speaker` — L1981
- `_adsd_gender_lock_phrase` — L1990
- `_adsd_visual_subject_has_gender_conflict` — L2005
- `_adsd_default_roles` — L2017
- `_adsd_allows_media_role` — L2022
- `_adsd_role_candidates` — L2030
- `_adsd_dialogue_shape` — L2053
- `_finalize_adsd_turns` — L2062
- `_parse_adsd_override_turns` — L2096
- `_parse_timecode_seconds` — L2187
- `_clean_override_line_text` — L2196
- `_parse_override_script_text` — L2202
- `_adsd_pov_contract` — L2236
- `_load_audit_blacklist_block` — L2249
- `_generate_adsd_dialogue_turns` — L2287
- `_broll_rhythm_reviewer` — L2710
- `_sweep_speaker_field` — L2817
- `_adsd_immersion_qa_rewrite_turns` — L2877
- `_adsd_visual_contract` — L2935
- `step1_script` — L2987
- `_write_ads_retention_qa` — L3872

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L3929 – L5032** (1104 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L4004
- `_ADSD_POLICY_REWRITE_TERMS` — L4010
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L4101

**Functions:**
- `_openai_tts_fallback` — L3930
- `_edge_tts_fallback` — L3976
- `_sanitize_for_external_api` — L4019
- `_is_content_policy_error` — L4028
- `_rewrite_adsd_tts_text_for_policy` — L4042
- `_record_adsd_tts_rewrite` — L4082
- `_build_silence_mp3` — L4107
- `_audio_duration_seconds` — L4120
- `_text_to_audio_master_voice_timed` — L4132
- `_text_to_audio_master_voice` — L4257
- `step2_master_voice` — L4360
- `_tts_turn_to_audio` — L4488
- `_asr_verify_dialogue_audio` — L4552
- `_asr_verify_dialogue_turns` — L4614
- `_normalize_cn_number_token` — L4656
- `_compact_zh_text` — L4678
- `_write_adsd_asr_text_qa` — L4685
- `_write_adsd_speaker_focus_qa` — L4724
- `_write_adsd_gender_voice_qa` — L4784
- `step2_dialogue_voice` — L4837

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L5033 – L5584** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L5040-5162 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L5163-5197 (35 lines)
- _第二层：字符数插值_ — L5198-5222 (25 lines)
- _第三层：silencedetect 物理校准_ — L5223-5584 (362 lines)

**Functions:**
- `_detect_silences` — L5041
- `_calibrate_boundaries` — L5076
- `_enforce_monotonic` — L5110
- `_manual_override_segments` — L5122
- `_calc_sentence_boundaries` — L5143
- `step345_timeline` — L5254
- `_analyze_bgm_energy_cuts` — L5313
- `_snap_bgm_only_boundaries` — L5376
- `step345_bgm_only_timeline` — L5436

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L5585 – L9174** (3590 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L6688-6738 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L6739-6879 (141 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L6880-7280 (401 lines)
- _Speaker IP Card (2026-05-21)_ — L7281-9007 (1727 lines)
- _审批流程_ — L9008-9064 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L9065-9174 (110 lines)

**Top-level constants:**
- `CHARACTER_META_GRID_COSTUMES` — L6694
- `CHARACTER_META_GRID_POSES` — L6695
- `CHARACTER_META_GRID_SCENES` — L6696
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L6699

**Functions:**
- `_extract_img_url` — L5586
- `_extract_img_urls` — L5608
- `_extract_video_url` — L5641
- `_count_bands` — L5666
- `_detect_contact_sheet_like_image` — L5678
- `_guess_upload_mime` — L5732
- `_upload_to_weryai` — L5755
- `_send_for_approval` — L5787
- `_wait_approval` — L5851
- `_render_still_segment` — L5863
- `_scene_text_visual_alignment` — L5894
- `_write_text_visual_alignment_qa` — L5930
- `_scene_motion_action_plan` — L5953
- `_ensure_motion_action_plan` — L6007
- `_motion_action_block` — L6016
- `_motion_plan_for_qa` — L6044
- `_write_motion_action_plan_qa` — L6054
- `_write_motion_bridge_refs_qa` — L6084
- `_motion_bridge_ref_prompt` — L6091
- `generate_motion_bridge_refs_gpt_image2` — L6124
- `generate_image` — L6237
- `generate_storyboard_images_gpt_image2` — L6284
- `_storyboard_grid_aspect` — L6469
- `_storyboard_grid_cols_rows` — L6476
- `_storyboard_grid_prompt` — L6498
- `_storyboard_grid_prompt_limit` — L6536
- `_is_prompt_limit_response` — L6540
- `_production_storyboard_prompt` — L6546
- `_write_production_storyboard_page_qa` — L6580
- `_character_sheet_prompt` — L6590
- `_is_audit_blocked` — L6716
- `_paraphrase_sensitive_dialogue` — L6729
- `_topic_cache_dir` — L6743
- `_topic_cache_path` — L6749
- `_load_topic_decomposition_cache` — L6762
- `_save_topic_decomposition_cache` — L6780
- `_llm_topic_decomposition` — L6786
- `_director_route_block` — L6933
- `_llm_infer_meta_grid_template` — L7003
- `_resolve_meta_grid_template` — L7060
- `_infer_meta_grid_costume` — L7103
- `_infer_meta_grid_pose` — L7152
- `_adsd_meta_grid_call_prompt` — L7199
- `_meta_grid_panel_index` — L7241
- `_migrate_speaker_ip` — L7287
- `_speaker_ips_dir` — L7312
- `_list_speaker_ips` — L7319
- `_match_speaker_ip` — L7333
- `_build_speaker_ip_context_for_script` — L7353
- `_ip_usage_stats` — L7409
- `_recommend_related_ips` — L7427
- `_save_speaker_ip` — L7452
- `_record_speaker_usage_history` — L7461
- `_format_speaker_usage_history_for_prompt` — L7508
- `_llm_infer_ip_skeleton` — L7526
- `_llm_pick_voice_asset_for_ip` — L7571
- `_auto_incubate_missing_ips` — L7619
- `_character_meta_grid_cache_dir` — L7703
- `_character_meta_grid_cache_path` — L7711
- `_character_meta_grid_path` — L7717
- `generate_character_meta_grid_gpt_image2` — L7723
- `_generate_all_character_meta_grids` — L7853
- `_write_character_sheet_qa` — L7894
- `generate_character_sheet_gpt_image2` — L7904
- `generate_production_storyboard_page_gpt_image2` — L8004
- `_qa_clean_storyboard_panel` — L8067
- `_crop_storyboard_grid_panels` — L8248
- `generate_storyboard_grid_gpt_image2` — L8295
- `_gpt_image2_direct_annotated_aspect` — L8526
- `_gpt_image2_direct_annotated_prompt` — L8533
- `generate_gpt_image2_direct_annotated_storyboards` — L8563
- `_llm_bgm_description` — L8664
- `_bgm_contains_vocals` — L8703
- `generate_bgm` — L8737
- `step6_parallel` — L8854

---

### 第 6.5 步：动态化（可选，--with-motion 开启）
Range: **L9175 – L13432** (4258 lines)

**Sub-sections:**
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L13169-13211 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L13212-13249 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回主音轨_ — L13250-13387 (138 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L13388-13432 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L9178
- `_motion_tasks_file` — L9245
- `_motion_qa_file` — L9249
- `_append_motion_qa` — L9253
- `_finalize_motion_qa` — L9277
- `_lip_sync_tasks_file` — L9361
- `_load_motion_tasks` — L9365
- `_save_motion_task` — L9375
- `_remove_motion_task` — L9383
- `_load_lip_sync_tasks` — L9390
- `_save_lip_sync_task` — L9400
- `_remove_lip_sync_task` — L9407
- `_video_visual_motion_qa` — L9414
- `_motion_output_qa` — L9486
- `_has_audio_stream` — L9531
- `_normalize_motion_video` — L9542
- `_motion_poll_and_download` — L9592
- `_build_motion_video_prompt` — L9643
- `_short_board_text` — L9673
- `_wrap_board_text` — L9680
- `_storyboard_font` — L9711
- `_draw_storyboard_arrow` — L9726
- `_build_annotated_storyboard_reference` — L9740
- `_plain_caption_text` — L9841
- `_werydance_caption_request` — L9849
- `_werydance_caption_instruction` — L9876
- `_werydance_negative_prompt` — L9888
- `_motion_reference_prompt` — L9906
- `_motion_audio_dub_prompt` — L9929
- `_motion_audio_dub_poll_and_download` — L9963
- `_try_motion_audio_dub_video` — L10028
- `_try_motion_reference_video` — L10163
- `_motion_one_scene` — L10279
- `_grid_multiref_tasks_file` — L10408
- `_previs_page_tasks_file` — L10412
- `_load_grid_multiref_tasks` — L10416
- `_load_previs_page_tasks` — L10426
- `_save_grid_multiref_task` — L10436
- `_save_previs_page_task` — L10443
- `_remove_grid_multiref_task` — L10450
- `_remove_previs_page_task` — L10457
- `_poll_video_task_download` — L10464
- `_grid_multiref_group_size` — L10513
- `_grid_multiref_duration` — L10521
- `_grid_multiref_segment_max_stretch` — L10537
- `_grid_multiref_prompt` — L10545
- `_write_grid_multiref_motion_qa` — L10593
- `_write_previs_page_motion_qa` — L10603
- `_write_storyboard_trailer_qa` — L10613
- `_write_character_trailer_qa` — L10623
- `_write_grid_multiref_segment_qa` — L10633
- `_motion_compare_record` — L10643
- `_write_storyboard_motion_compare_qa` — L10665
- `_scene_segment_duration` — L10701
- `_apply_grid_multiref_segments` — L10720
- `_previs_page_duration` — L10914
- `_previs_page_group_prompt` — L10924
- `_previs_page_groups` — L10950
- `_storyboard_trailer_duration` — L10965
- `_storyboard_trailer_prompt` — L10975
- `_character_trailer_max_shots` — L11003
- `_character_trailer_shot_duration` — L11011
- `_character_trailer_prompt` — L11025
- `_concat_character_trailer_segments` — L11040
- `_generate_character_trailer_motion` — L11079
- `_multi_trailer_prompt_for_group` — L11187
- `_generate_multi_trailer_segments` — L11210
- `_generate_storyboard_trailer_motion` — L11321
- `_generate_previs_page_motion_segments` — L11396
- `_generate_grid_multiref_motion_segments` — L11508
- `_grid_multiref_concat_groups` — L11678
- `_grid_multiref_concat_groups_partial` — L11695
- `_grid_multiref_concat_paths` — L11713
- `_lip_sync_slot_duration` — L11744
- `_adsd_lip_sync_prompt` — L11751
- `_adsd_broll_motion_prompt` — L11797
- `_adsd_action_b_motion_prompt` — L11839
- `_adsd_silent_b_motion_prompt` — L11885
- `_adsd_narrated_b_audio_dub_prompt` — L11920
- `_adsd_almighty_audio_dub_prompt` — L11964
- `_postprocess_lip_sync_segment` — L12005
- `_detect_audio_leading_silence` — L12073
- `_postprocess_audio_dub_segment` — L12095
- `_lips_change_repair_segment` — L12206
- `_load_lips_change_requested_turns` — L12291
- `_parse_turn_set` — L12308
- `_load_motion_voice_repair_turns` — L12330
- `_voice_assets_file` — L12342
- `_load_voice_assets` — L12349
- `_select_voice_asset_reference` — L12368
- `_lip_sync_poll_download_and_process` — L12434
- `_lip_sync_one_scene` — L12502
- `step66_adsd_lip_sync` — L12826
- `step65_motion` — L13059
- `step65_grid_multiref_motion_qa` — L13141
- `_sanitize_scene_for_state` — L13170
- `_save_pipeline_state` — L13189
- `_retime_after_audio_dub` — L13213
- `_build_voice_clone_hybrid_audio` — L13251
- `_build_dynamic_bgm` — L13389

---

### 第七步：拼接视频轨
Range: **L13433 – L13664** (232 lines)

**Functions:**
- `step7_concat` — L13434

---

### 第八步：生成 ASS 字幕
Range: **L13665 – L14456** (792 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L13788-14456 (669 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L13666
- `_word_timings_for_subtitle_align` — L13692
- `_align_segments_via_asr` — L13733
- `step8_subtitles` — L13776
- `_read_output_json` — L14188
- `_qa_file_pass` — L14199
- `_ass_has_dialogue` — L14206
- `_write_adsd_delivery_qa` — L14216
- `_write_bgm_only_qa` — L14345

---

### 第九步：最终合成
Range: **L14457 – L14702** (246 lines)

**Functions:**
- `step9_render` — L14458

---

### 第十步：推送 Telegram
Range: **L14703 – L16317** (1615 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L15803-16124 (322 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L16125-16129 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L16130-16193 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L16194-16239 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L16240-16317 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L15072
- `PANTONE_FALLBACK` — L15099
- `FESTIVAL_DATE_TAG` — L15212

**Functions:**
- `_generate_caption` — L14704
- `_overlay_title_on_cover` — L14942
- `_prepare_tg_photo` — L15052
- `_get_pantone_for_date` — L15102
- `_llm_bottom_note` — L15127
- `_get_bottom_note` — L15156
- `_get_date_tag` — L15234
- `_shrink_to_b64` — L15256
- `_llm_check_scenes_anomalies` — L15272
- `_llm_check_cover_unique` — L15325
- `_llm_check_cover_quality` — L15355
- `_try_almanac_cover` — L15397
- `_generate_cover_image` — L15568
- `_async_kickoff_cover_caption` — L15810
- `_await_async_cover_caption` — L15840
- `step10_deliver` — L15864

---

### 主流程
Range: **L16318 – L16495** (178 lines)

**Functions:**
- `_print_execution_plan` — L16319
- `main` — L16367

---
