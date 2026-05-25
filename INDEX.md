# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (16371 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-1915 (1794 lines · 56 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L1916-3830 (1915 lines · 24 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L3831-4932 (1102 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L4933-5484 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L5485-9050 (3566 lines · 75 fn · 6 sub)
- [`第 6.5 步：动态化（可选，--with-motion 开启）`](#第-6-5-步-动态化-可选---with-motion-开启) — L9051-13308 (4258 lines · 100 fn · 4 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L13309-13540 (232 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L13541-14332 (792 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L14333-14578 (246 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L14579-16193 (1615 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L16194-16371 (178 lines · 2 fn · 0 sub)

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
Range: **L1916 – L3830** (1915 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L3116-3830 (715 lines)

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
- `_generate_adsd_dialogue_turns` — L2246
- `_broll_rhythm_reviewer` — L2618
- `_sweep_speaker_field` — L2725
- `_adsd_immersion_qa_rewrite_turns` — L2779
- `_adsd_visual_contract` — L2837
- `step1_script` — L2889
- `_write_ads_retention_qa` — L3774

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L3831 – L4932** (1102 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L3906
- `_ADSD_POLICY_REWRITE_TERMS` — L3912
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L4003

**Functions:**
- `_openai_tts_fallback` — L3832
- `_edge_tts_fallback` — L3878
- `_sanitize_for_external_api` — L3921
- `_is_content_policy_error` — L3930
- `_rewrite_adsd_tts_text_for_policy` — L3944
- `_record_adsd_tts_rewrite` — L3984
- `_build_silence_mp3` — L4009
- `_audio_duration_seconds` — L4022
- `_text_to_audio_master_voice_timed` — L4034
- `_text_to_audio_master_voice` — L4159
- `step2_master_voice` — L4262
- `_tts_turn_to_audio` — L4390
- `_asr_verify_dialogue_audio` — L4452
- `_asr_verify_dialogue_turns` — L4514
- `_normalize_cn_number_token` — L4556
- `_compact_zh_text` — L4578
- `_write_adsd_asr_text_qa` — L4585
- `_write_adsd_speaker_focus_qa` — L4624
- `_write_adsd_gender_voice_qa` — L4684
- `step2_dialogue_voice` — L4737

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L4933 – L5484** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L4940-5062 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L5063-5097 (35 lines)
- _第二层：字符数插值_ — L5098-5122 (25 lines)
- _第三层：silencedetect 物理校准_ — L5123-5484 (362 lines)

**Functions:**
- `_detect_silences` — L4941
- `_calibrate_boundaries` — L4976
- `_enforce_monotonic` — L5010
- `_manual_override_segments` — L5022
- `_calc_sentence_boundaries` — L5043
- `step345_timeline` — L5154
- `_analyze_bgm_energy_cuts` — L5213
- `_snap_bgm_only_boundaries` — L5276
- `step345_bgm_only_timeline` — L5336

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L5485 – L9050** (3566 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L6588-6638 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L6639-6755 (117 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L6756-7156 (401 lines)
- _Speaker IP Card (2026-05-21)_ — L7157-8883 (1727 lines)
- _审批流程_ — L8884-8940 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L8941-9050 (110 lines)

**Top-level constants:**
- `CHARACTER_META_GRID_COSTUMES` — L6594
- `CHARACTER_META_GRID_POSES` — L6595
- `CHARACTER_META_GRID_SCENES` — L6596
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L6599

**Functions:**
- `_extract_img_url` — L5486
- `_extract_img_urls` — L5508
- `_extract_video_url` — L5541
- `_count_bands` — L5566
- `_detect_contact_sheet_like_image` — L5578
- `_guess_upload_mime` — L5632
- `_upload_to_weryai` — L5655
- `_send_for_approval` — L5687
- `_wait_approval` — L5751
- `_render_still_segment` — L5763
- `_scene_text_visual_alignment` — L5794
- `_write_text_visual_alignment_qa` — L5830
- `_scene_motion_action_plan` — L5853
- `_ensure_motion_action_plan` — L5907
- `_motion_action_block` — L5916
- `_motion_plan_for_qa` — L5944
- `_write_motion_action_plan_qa` — L5954
- `_write_motion_bridge_refs_qa` — L5984
- `_motion_bridge_ref_prompt` — L5991
- `generate_motion_bridge_refs_gpt_image2` — L6024
- `generate_image` — L6137
- `generate_storyboard_images_gpt_image2` — L6184
- `_storyboard_grid_aspect` — L6369
- `_storyboard_grid_cols_rows` — L6376
- `_storyboard_grid_prompt` — L6398
- `_storyboard_grid_prompt_limit` — L6436
- `_is_prompt_limit_response` — L6440
- `_production_storyboard_prompt` — L6446
- `_write_production_storyboard_page_qa` — L6480
- `_character_sheet_prompt` — L6490
- `_is_audit_blocked` — L6616
- `_paraphrase_sensitive_dialogue` — L6629
- `_topic_cache_dir` — L6643
- `_topic_cache_path` — L6649
- `_load_topic_decomposition_cache` — L6654
- `_save_topic_decomposition_cache` — L6664
- `_llm_topic_decomposition` — L6669
- `_director_route_block` — L6809
- `_llm_infer_meta_grid_template` — L6879
- `_resolve_meta_grid_template` — L6936
- `_infer_meta_grid_costume` — L6979
- `_infer_meta_grid_pose` — L7028
- `_adsd_meta_grid_call_prompt` — L7075
- `_meta_grid_panel_index` — L7117
- `_migrate_speaker_ip` — L7163
- `_speaker_ips_dir` — L7188
- `_list_speaker_ips` — L7195
- `_match_speaker_ip` — L7209
- `_build_speaker_ip_context_for_script` — L7229
- `_ip_usage_stats` — L7285
- `_recommend_related_ips` — L7303
- `_save_speaker_ip` — L7328
- `_record_speaker_usage_history` — L7337
- `_format_speaker_usage_history_for_prompt` — L7384
- `_llm_infer_ip_skeleton` — L7402
- `_llm_pick_voice_asset_for_ip` — L7447
- `_auto_incubate_missing_ips` — L7495
- `_character_meta_grid_cache_dir` — L7579
- `_character_meta_grid_cache_path` — L7587
- `_character_meta_grid_path` — L7593
- `generate_character_meta_grid_gpt_image2` — L7599
- `_generate_all_character_meta_grids` — L7729
- `_write_character_sheet_qa` — L7770
- `generate_character_sheet_gpt_image2` — L7780
- `generate_production_storyboard_page_gpt_image2` — L7880
- `_qa_clean_storyboard_panel` — L7943
- `_crop_storyboard_grid_panels` — L8124
- `generate_storyboard_grid_gpt_image2` — L8171
- `_gpt_image2_direct_annotated_aspect` — L8402
- `_gpt_image2_direct_annotated_prompt` — L8409
- `generate_gpt_image2_direct_annotated_storyboards` — L8439
- `_llm_bgm_description` — L8540
- `_bgm_contains_vocals` — L8579
- `generate_bgm` — L8613
- `step6_parallel` — L8730

---

### 第 6.5 步：动态化（可选，--with-motion 开启）
Range: **L9051 – L13308** (4258 lines)

**Sub-sections:**
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L13045-13087 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L13088-13125 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回主音轨_ — L13126-13263 (138 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L13264-13308 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L9054
- `_motion_tasks_file` — L9121
- `_motion_qa_file` — L9125
- `_append_motion_qa` — L9129
- `_finalize_motion_qa` — L9153
- `_lip_sync_tasks_file` — L9237
- `_load_motion_tasks` — L9241
- `_save_motion_task` — L9251
- `_remove_motion_task` — L9259
- `_load_lip_sync_tasks` — L9266
- `_save_lip_sync_task` — L9276
- `_remove_lip_sync_task` — L9283
- `_video_visual_motion_qa` — L9290
- `_motion_output_qa` — L9362
- `_has_audio_stream` — L9407
- `_normalize_motion_video` — L9418
- `_motion_poll_and_download` — L9468
- `_build_motion_video_prompt` — L9519
- `_short_board_text` — L9549
- `_wrap_board_text` — L9556
- `_storyboard_font` — L9587
- `_draw_storyboard_arrow` — L9602
- `_build_annotated_storyboard_reference` — L9616
- `_plain_caption_text` — L9717
- `_werydance_caption_request` — L9725
- `_werydance_caption_instruction` — L9752
- `_werydance_negative_prompt` — L9764
- `_motion_reference_prompt` — L9782
- `_motion_audio_dub_prompt` — L9805
- `_motion_audio_dub_poll_and_download` — L9839
- `_try_motion_audio_dub_video` — L9904
- `_try_motion_reference_video` — L10039
- `_motion_one_scene` — L10155
- `_grid_multiref_tasks_file` — L10284
- `_previs_page_tasks_file` — L10288
- `_load_grid_multiref_tasks` — L10292
- `_load_previs_page_tasks` — L10302
- `_save_grid_multiref_task` — L10312
- `_save_previs_page_task` — L10319
- `_remove_grid_multiref_task` — L10326
- `_remove_previs_page_task` — L10333
- `_poll_video_task_download` — L10340
- `_grid_multiref_group_size` — L10389
- `_grid_multiref_duration` — L10397
- `_grid_multiref_segment_max_stretch` — L10413
- `_grid_multiref_prompt` — L10421
- `_write_grid_multiref_motion_qa` — L10469
- `_write_previs_page_motion_qa` — L10479
- `_write_storyboard_trailer_qa` — L10489
- `_write_character_trailer_qa` — L10499
- `_write_grid_multiref_segment_qa` — L10509
- `_motion_compare_record` — L10519
- `_write_storyboard_motion_compare_qa` — L10541
- `_scene_segment_duration` — L10577
- `_apply_grid_multiref_segments` — L10596
- `_previs_page_duration` — L10790
- `_previs_page_group_prompt` — L10800
- `_previs_page_groups` — L10826
- `_storyboard_trailer_duration` — L10841
- `_storyboard_trailer_prompt` — L10851
- `_character_trailer_max_shots` — L10879
- `_character_trailer_shot_duration` — L10887
- `_character_trailer_prompt` — L10901
- `_concat_character_trailer_segments` — L10916
- `_generate_character_trailer_motion` — L10955
- `_multi_trailer_prompt_for_group` — L11063
- `_generate_multi_trailer_segments` — L11086
- `_generate_storyboard_trailer_motion` — L11197
- `_generate_previs_page_motion_segments` — L11272
- `_generate_grid_multiref_motion_segments` — L11384
- `_grid_multiref_concat_groups` — L11554
- `_grid_multiref_concat_groups_partial` — L11571
- `_grid_multiref_concat_paths` — L11589
- `_lip_sync_slot_duration` — L11620
- `_adsd_lip_sync_prompt` — L11627
- `_adsd_broll_motion_prompt` — L11673
- `_adsd_action_b_motion_prompt` — L11715
- `_adsd_silent_b_motion_prompt` — L11761
- `_adsd_narrated_b_audio_dub_prompt` — L11796
- `_adsd_almighty_audio_dub_prompt` — L11840
- `_postprocess_lip_sync_segment` — L11881
- `_detect_audio_leading_silence` — L11949
- `_postprocess_audio_dub_segment` — L11971
- `_lips_change_repair_segment` — L12082
- `_load_lips_change_requested_turns` — L12167
- `_parse_turn_set` — L12184
- `_load_motion_voice_repair_turns` — L12206
- `_voice_assets_file` — L12218
- `_load_voice_assets` — L12225
- `_select_voice_asset_reference` — L12244
- `_lip_sync_poll_download_and_process` — L12310
- `_lip_sync_one_scene` — L12378
- `step66_adsd_lip_sync` — L12702
- `step65_motion` — L12935
- `step65_grid_multiref_motion_qa` — L13017
- `_sanitize_scene_for_state` — L13046
- `_save_pipeline_state` — L13065
- `_retime_after_audio_dub` — L13089
- `_build_voice_clone_hybrid_audio` — L13127
- `_build_dynamic_bgm` — L13265

---

### 第七步：拼接视频轨
Range: **L13309 – L13540** (232 lines)

**Functions:**
- `step7_concat` — L13310

---

### 第八步：生成 ASS 字幕
Range: **L13541 – L14332** (792 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L13664-14332 (669 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L13542
- `_word_timings_for_subtitle_align` — L13568
- `_align_segments_via_asr` — L13609
- `step8_subtitles` — L13652
- `_read_output_json` — L14064
- `_qa_file_pass` — L14075
- `_ass_has_dialogue` — L14082
- `_write_adsd_delivery_qa` — L14092
- `_write_bgm_only_qa` — L14221

---

### 第九步：最终合成
Range: **L14333 – L14578** (246 lines)

**Functions:**
- `step9_render` — L14334

---

### 第十步：推送 Telegram
Range: **L14579 – L16193** (1615 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L15679-16000 (322 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L16001-16005 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L16006-16069 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L16070-16115 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L16116-16193 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L14948
- `PANTONE_FALLBACK` — L14975
- `FESTIVAL_DATE_TAG` — L15088

**Functions:**
- `_generate_caption` — L14580
- `_overlay_title_on_cover` — L14818
- `_prepare_tg_photo` — L14928
- `_get_pantone_for_date` — L14978
- `_llm_bottom_note` — L15003
- `_get_bottom_note` — L15032
- `_get_date_tag` — L15110
- `_shrink_to_b64` — L15132
- `_llm_check_scenes_anomalies` — L15148
- `_llm_check_cover_unique` — L15201
- `_llm_check_cover_quality` — L15231
- `_try_almanac_cover` — L15273
- `_generate_cover_image` — L15444
- `_async_kickoff_cover_caption` — L15686
- `_await_async_cover_caption` — L15716
- `step10_deliver` — L15740

---

### 主流程
Range: **L16194 – L16371** (178 lines)

**Functions:**
- `_print_execution_plan` — L16195
- `main` — L16243

---
