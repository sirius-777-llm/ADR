# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (16625 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-1915 (1794 lines · 56 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L1916-4033 (2118 lines · 28 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L4034-5137 (1104 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L5138-5689 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L5690-9279 (3590 lines · 75 fn · 6 sub)
- [`第 6.5 步：动态化（可选，--with-motion 开启）`](#第-6-5-步-动态化-可选---with-motion-开启) — L9280-13562 (4283 lines · 100 fn · 4 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L13563-13794 (232 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L13795-14586 (792 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L14587-14832 (246 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L14833-16447 (1615 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L16448-16625 (178 lines · 2 fn · 0 sub)

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
Range: **L1916 – L4033** (2118 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L3319-4033 (715 lines)

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
- `_parse_risk_score` — L2987
- `_check_high_risk_hard_abort` — L3016
- `_maybe_neutralize_topic` — L3043
- `step1_script` — L3082
- `_write_ads_retention_qa` — L3977

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L4034 – L5137** (1104 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L4109
- `_ADSD_POLICY_REWRITE_TERMS` — L4115
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L4206

**Functions:**
- `_openai_tts_fallback` — L4035
- `_edge_tts_fallback` — L4081
- `_sanitize_for_external_api` — L4124
- `_is_content_policy_error` — L4133
- `_rewrite_adsd_tts_text_for_policy` — L4147
- `_record_adsd_tts_rewrite` — L4187
- `_build_silence_mp3` — L4212
- `_audio_duration_seconds` — L4225
- `_text_to_audio_master_voice_timed` — L4237
- `_text_to_audio_master_voice` — L4362
- `step2_master_voice` — L4465
- `_tts_turn_to_audio` — L4593
- `_asr_verify_dialogue_audio` — L4657
- `_asr_verify_dialogue_turns` — L4719
- `_normalize_cn_number_token` — L4761
- `_compact_zh_text` — L4783
- `_write_adsd_asr_text_qa` — L4790
- `_write_adsd_speaker_focus_qa` — L4829
- `_write_adsd_gender_voice_qa` — L4889
- `step2_dialogue_voice` — L4942

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L5138 – L5689** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L5145-5267 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L5268-5302 (35 lines)
- _第二层：字符数插值_ — L5303-5327 (25 lines)
- _第三层：silencedetect 物理校准_ — L5328-5689 (362 lines)

**Functions:**
- `_detect_silences` — L5146
- `_calibrate_boundaries` — L5181
- `_enforce_monotonic` — L5215
- `_manual_override_segments` — L5227
- `_calc_sentence_boundaries` — L5248
- `step345_timeline` — L5359
- `_analyze_bgm_energy_cuts` — L5418
- `_snap_bgm_only_boundaries` — L5481
- `step345_bgm_only_timeline` — L5541

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L5690 – L9279** (3590 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L6793-6843 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L6844-6984 (141 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L6985-7385 (401 lines)
- _Speaker IP Card (2026-05-21)_ — L7386-9112 (1727 lines)
- _审批流程_ — L9113-9169 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L9170-9279 (110 lines)

**Top-level constants:**
- `CHARACTER_META_GRID_COSTUMES` — L6799
- `CHARACTER_META_GRID_POSES` — L6800
- `CHARACTER_META_GRID_SCENES` — L6801
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L6804

**Functions:**
- `_extract_img_url` — L5691
- `_extract_img_urls` — L5713
- `_extract_video_url` — L5746
- `_count_bands` — L5771
- `_detect_contact_sheet_like_image` — L5783
- `_guess_upload_mime` — L5837
- `_upload_to_weryai` — L5860
- `_send_for_approval` — L5892
- `_wait_approval` — L5956
- `_render_still_segment` — L5968
- `_scene_text_visual_alignment` — L5999
- `_write_text_visual_alignment_qa` — L6035
- `_scene_motion_action_plan` — L6058
- `_ensure_motion_action_plan` — L6112
- `_motion_action_block` — L6121
- `_motion_plan_for_qa` — L6149
- `_write_motion_action_plan_qa` — L6159
- `_write_motion_bridge_refs_qa` — L6189
- `_motion_bridge_ref_prompt` — L6196
- `generate_motion_bridge_refs_gpt_image2` — L6229
- `generate_image` — L6342
- `generate_storyboard_images_gpt_image2` — L6389
- `_storyboard_grid_aspect` — L6574
- `_storyboard_grid_cols_rows` — L6581
- `_storyboard_grid_prompt` — L6603
- `_storyboard_grid_prompt_limit` — L6641
- `_is_prompt_limit_response` — L6645
- `_production_storyboard_prompt` — L6651
- `_write_production_storyboard_page_qa` — L6685
- `_character_sheet_prompt` — L6695
- `_is_audit_blocked` — L6821
- `_paraphrase_sensitive_dialogue` — L6834
- `_topic_cache_dir` — L6848
- `_topic_cache_path` — L6854
- `_load_topic_decomposition_cache` — L6867
- `_save_topic_decomposition_cache` — L6885
- `_llm_topic_decomposition` — L6891
- `_director_route_block` — L7038
- `_llm_infer_meta_grid_template` — L7108
- `_resolve_meta_grid_template` — L7165
- `_infer_meta_grid_costume` — L7208
- `_infer_meta_grid_pose` — L7257
- `_adsd_meta_grid_call_prompt` — L7304
- `_meta_grid_panel_index` — L7346
- `_migrate_speaker_ip` — L7392
- `_speaker_ips_dir` — L7417
- `_list_speaker_ips` — L7424
- `_match_speaker_ip` — L7438
- `_build_speaker_ip_context_for_script` — L7458
- `_ip_usage_stats` — L7514
- `_recommend_related_ips` — L7532
- `_save_speaker_ip` — L7557
- `_record_speaker_usage_history` — L7566
- `_format_speaker_usage_history_for_prompt` — L7613
- `_llm_infer_ip_skeleton` — L7631
- `_llm_pick_voice_asset_for_ip` — L7676
- `_auto_incubate_missing_ips` — L7724
- `_character_meta_grid_cache_dir` — L7808
- `_character_meta_grid_cache_path` — L7816
- `_character_meta_grid_path` — L7822
- `generate_character_meta_grid_gpt_image2` — L7828
- `_generate_all_character_meta_grids` — L7958
- `_write_character_sheet_qa` — L7999
- `generate_character_sheet_gpt_image2` — L8009
- `generate_production_storyboard_page_gpt_image2` — L8109
- `_qa_clean_storyboard_panel` — L8172
- `_crop_storyboard_grid_panels` — L8353
- `generate_storyboard_grid_gpt_image2` — L8400
- `_gpt_image2_direct_annotated_aspect` — L8631
- `_gpt_image2_direct_annotated_prompt` — L8638
- `generate_gpt_image2_direct_annotated_storyboards` — L8668
- `_llm_bgm_description` — L8769
- `_bgm_contains_vocals` — L8808
- `generate_bgm` — L8842
- `step6_parallel` — L8959

---

### 第 6.5 步：动态化（可选，--with-motion 开启）
Range: **L9280 – L13562** (4283 lines)

**Sub-sections:**
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L13299-13341 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L13342-13379 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回主音轨_ — L13380-13517 (138 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L13518-13562 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L9283
- `_motion_tasks_file` — L9350
- `_motion_qa_file` — L9354
- `_append_motion_qa` — L9358
- `_finalize_motion_qa` — L9382
- `_lip_sync_tasks_file` — L9466
- `_load_motion_tasks` — L9470
- `_save_motion_task` — L9480
- `_remove_motion_task` — L9488
- `_load_lip_sync_tasks` — L9495
- `_save_lip_sync_task` — L9505
- `_remove_lip_sync_task` — L9512
- `_video_visual_motion_qa` — L9519
- `_motion_output_qa` — L9591
- `_has_audio_stream` — L9636
- `_normalize_motion_video` — L9647
- `_motion_poll_and_download` — L9697
- `_build_motion_video_prompt` — L9748
- `_short_board_text` — L9778
- `_wrap_board_text` — L9785
- `_storyboard_font` — L9816
- `_draw_storyboard_arrow` — L9831
- `_build_annotated_storyboard_reference` — L9845
- `_plain_caption_text` — L9946
- `_werydance_caption_request` — L9954
- `_werydance_caption_instruction` — L9981
- `_werydance_negative_prompt` — L9993
- `_motion_reference_prompt` — L10011
- `_motion_audio_dub_prompt` — L10034
- `_motion_audio_dub_poll_and_download` — L10068
- `_try_motion_audio_dub_video` — L10133
- `_try_motion_reference_video` — L10268
- `_motion_one_scene` — L10384
- `_grid_multiref_tasks_file` — L10513
- `_previs_page_tasks_file` — L10517
- `_load_grid_multiref_tasks` — L10521
- `_load_previs_page_tasks` — L10531
- `_save_grid_multiref_task` — L10541
- `_save_previs_page_task` — L10548
- `_remove_grid_multiref_task` — L10555
- `_remove_previs_page_task` — L10562
- `_poll_video_task_download` — L10569
- `_grid_multiref_group_size` — L10618
- `_grid_multiref_duration` — L10626
- `_grid_multiref_segment_max_stretch` — L10642
- `_grid_multiref_prompt` — L10650
- `_write_grid_multiref_motion_qa` — L10698
- `_write_previs_page_motion_qa` — L10708
- `_write_storyboard_trailer_qa` — L10718
- `_write_character_trailer_qa` — L10728
- `_write_grid_multiref_segment_qa` — L10738
- `_motion_compare_record` — L10748
- `_write_storyboard_motion_compare_qa` — L10770
- `_scene_segment_duration` — L10806
- `_apply_grid_multiref_segments` — L10825
- `_previs_page_duration` — L11019
- `_previs_page_group_prompt` — L11029
- `_previs_page_groups` — L11055
- `_storyboard_trailer_duration` — L11070
- `_storyboard_trailer_prompt` — L11080
- `_character_trailer_max_shots` — L11108
- `_character_trailer_shot_duration` — L11116
- `_character_trailer_prompt` — L11130
- `_concat_character_trailer_segments` — L11145
- `_generate_character_trailer_motion` — L11184
- `_multi_trailer_prompt_for_group` — L11292
- `_generate_multi_trailer_segments` — L11315
- `_generate_storyboard_trailer_motion` — L11426
- `_generate_previs_page_motion_segments` — L11501
- `_generate_grid_multiref_motion_segments` — L11613
- `_grid_multiref_concat_groups` — L11783
- `_grid_multiref_concat_groups_partial` — L11800
- `_grid_multiref_concat_paths` — L11818
- `_lip_sync_slot_duration` — L11849
- `_adsd_lip_sync_prompt` — L11856
- `_adsd_broll_motion_prompt` — L11902
- `_adsd_action_b_motion_prompt` — L11944
- `_adsd_silent_b_motion_prompt` — L11990
- `_adsd_narrated_b_audio_dub_prompt` — L12025
- `_adsd_almighty_audio_dub_prompt` — L12069
- `_postprocess_lip_sync_segment` — L12110
- `_detect_audio_leading_silence` — L12178
- `_postprocess_audio_dub_segment` — L12200
- `_lips_change_repair_segment` — L12311
- `_load_lips_change_requested_turns` — L12396
- `_parse_turn_set` — L12413
- `_load_motion_voice_repair_turns` — L12435
- `_voice_assets_file` — L12447
- `_load_voice_assets` — L12454
- `_select_voice_asset_reference` — L12473
- `_lip_sync_poll_download_and_process` — L12539
- `_lip_sync_one_scene` — L12607
- `step66_adsd_lip_sync` — L12931
- `step65_motion` — L13189
- `step65_grid_multiref_motion_qa` — L13271
- `_sanitize_scene_for_state` — L13300
- `_save_pipeline_state` — L13319
- `_retime_after_audio_dub` — L13343
- `_build_voice_clone_hybrid_audio` — L13381
- `_build_dynamic_bgm` — L13519

---

### 第七步：拼接视频轨
Range: **L13563 – L13794** (232 lines)

**Functions:**
- `step7_concat` — L13564

---

### 第八步：生成 ASS 字幕
Range: **L13795 – L14586** (792 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L13918-14586 (669 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L13796
- `_word_timings_for_subtitle_align` — L13822
- `_align_segments_via_asr` — L13863
- `step8_subtitles` — L13906
- `_read_output_json` — L14318
- `_qa_file_pass` — L14329
- `_ass_has_dialogue` — L14336
- `_write_adsd_delivery_qa` — L14346
- `_write_bgm_only_qa` — L14475

---

### 第九步：最终合成
Range: **L14587 – L14832** (246 lines)

**Functions:**
- `step9_render` — L14588

---

### 第十步：推送 Telegram
Range: **L14833 – L16447** (1615 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L15933-16254 (322 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L16255-16259 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L16260-16323 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L16324-16369 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L16370-16447 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L15202
- `PANTONE_FALLBACK` — L15229
- `FESTIVAL_DATE_TAG` — L15342

**Functions:**
- `_generate_caption` — L14834
- `_overlay_title_on_cover` — L15072
- `_prepare_tg_photo` — L15182
- `_get_pantone_for_date` — L15232
- `_llm_bottom_note` — L15257
- `_get_bottom_note` — L15286
- `_get_date_tag` — L15364
- `_shrink_to_b64` — L15386
- `_llm_check_scenes_anomalies` — L15402
- `_llm_check_cover_unique` — L15455
- `_llm_check_cover_quality` — L15485
- `_try_almanac_cover` — L15527
- `_generate_cover_image` — L15698
- `_async_kickoff_cover_caption` — L15940
- `_await_async_cover_caption` — L15970
- `step10_deliver` — L15994

---

### 主流程
Range: **L16448 – L16625** (178 lines)

**Functions:**
- `_print_execution_plan` — L16449
- `main` — L16497

---
