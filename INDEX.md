# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (16553 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-1915 (1794 lines · 56 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L1916-3986 (2071 lines · 26 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L3987-5090 (1104 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L5091-5642 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L5643-9232 (3590 lines · 75 fn · 6 sub)
- [`第 6.5 步：动态化（可选，--with-motion 开启）`](#第-6-5-步-动态化-可选---with-motion-开启) — L9233-13490 (4258 lines · 100 fn · 4 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L13491-13722 (232 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L13723-14514 (792 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L14515-14760 (246 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L14761-16375 (1615 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L16376-16553 (178 lines · 2 fn · 0 sub)

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
Range: **L1916 – L3986** (2071 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L3272-3986 (715 lines)

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
- `_maybe_neutralize_topic` — L2987
- `step1_script` — L3038
- `_write_ads_retention_qa` — L3930

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L3987 – L5090** (1104 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L4062
- `_ADSD_POLICY_REWRITE_TERMS` — L4068
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L4159

**Functions:**
- `_openai_tts_fallback` — L3988
- `_edge_tts_fallback` — L4034
- `_sanitize_for_external_api` — L4077
- `_is_content_policy_error` — L4086
- `_rewrite_adsd_tts_text_for_policy` — L4100
- `_record_adsd_tts_rewrite` — L4140
- `_build_silence_mp3` — L4165
- `_audio_duration_seconds` — L4178
- `_text_to_audio_master_voice_timed` — L4190
- `_text_to_audio_master_voice` — L4315
- `step2_master_voice` — L4418
- `_tts_turn_to_audio` — L4546
- `_asr_verify_dialogue_audio` — L4610
- `_asr_verify_dialogue_turns` — L4672
- `_normalize_cn_number_token` — L4714
- `_compact_zh_text` — L4736
- `_write_adsd_asr_text_qa` — L4743
- `_write_adsd_speaker_focus_qa` — L4782
- `_write_adsd_gender_voice_qa` — L4842
- `step2_dialogue_voice` — L4895

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L5091 – L5642** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L5098-5220 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L5221-5255 (35 lines)
- _第二层：字符数插值_ — L5256-5280 (25 lines)
- _第三层：silencedetect 物理校准_ — L5281-5642 (362 lines)

**Functions:**
- `_detect_silences` — L5099
- `_calibrate_boundaries` — L5134
- `_enforce_monotonic` — L5168
- `_manual_override_segments` — L5180
- `_calc_sentence_boundaries` — L5201
- `step345_timeline` — L5312
- `_analyze_bgm_energy_cuts` — L5371
- `_snap_bgm_only_boundaries` — L5434
- `step345_bgm_only_timeline` — L5494

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L5643 – L9232** (3590 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L6746-6796 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L6797-6937 (141 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L6938-7338 (401 lines)
- _Speaker IP Card (2026-05-21)_ — L7339-9065 (1727 lines)
- _审批流程_ — L9066-9122 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L9123-9232 (110 lines)

**Top-level constants:**
- `CHARACTER_META_GRID_COSTUMES` — L6752
- `CHARACTER_META_GRID_POSES` — L6753
- `CHARACTER_META_GRID_SCENES` — L6754
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L6757

**Functions:**
- `_extract_img_url` — L5644
- `_extract_img_urls` — L5666
- `_extract_video_url` — L5699
- `_count_bands` — L5724
- `_detect_contact_sheet_like_image` — L5736
- `_guess_upload_mime` — L5790
- `_upload_to_weryai` — L5813
- `_send_for_approval` — L5845
- `_wait_approval` — L5909
- `_render_still_segment` — L5921
- `_scene_text_visual_alignment` — L5952
- `_write_text_visual_alignment_qa` — L5988
- `_scene_motion_action_plan` — L6011
- `_ensure_motion_action_plan` — L6065
- `_motion_action_block` — L6074
- `_motion_plan_for_qa` — L6102
- `_write_motion_action_plan_qa` — L6112
- `_write_motion_bridge_refs_qa` — L6142
- `_motion_bridge_ref_prompt` — L6149
- `generate_motion_bridge_refs_gpt_image2` — L6182
- `generate_image` — L6295
- `generate_storyboard_images_gpt_image2` — L6342
- `_storyboard_grid_aspect` — L6527
- `_storyboard_grid_cols_rows` — L6534
- `_storyboard_grid_prompt` — L6556
- `_storyboard_grid_prompt_limit` — L6594
- `_is_prompt_limit_response` — L6598
- `_production_storyboard_prompt` — L6604
- `_write_production_storyboard_page_qa` — L6638
- `_character_sheet_prompt` — L6648
- `_is_audit_blocked` — L6774
- `_paraphrase_sensitive_dialogue` — L6787
- `_topic_cache_dir` — L6801
- `_topic_cache_path` — L6807
- `_load_topic_decomposition_cache` — L6820
- `_save_topic_decomposition_cache` — L6838
- `_llm_topic_decomposition` — L6844
- `_director_route_block` — L6991
- `_llm_infer_meta_grid_template` — L7061
- `_resolve_meta_grid_template` — L7118
- `_infer_meta_grid_costume` — L7161
- `_infer_meta_grid_pose` — L7210
- `_adsd_meta_grid_call_prompt` — L7257
- `_meta_grid_panel_index` — L7299
- `_migrate_speaker_ip` — L7345
- `_speaker_ips_dir` — L7370
- `_list_speaker_ips` — L7377
- `_match_speaker_ip` — L7391
- `_build_speaker_ip_context_for_script` — L7411
- `_ip_usage_stats` — L7467
- `_recommend_related_ips` — L7485
- `_save_speaker_ip` — L7510
- `_record_speaker_usage_history` — L7519
- `_format_speaker_usage_history_for_prompt` — L7566
- `_llm_infer_ip_skeleton` — L7584
- `_llm_pick_voice_asset_for_ip` — L7629
- `_auto_incubate_missing_ips` — L7677
- `_character_meta_grid_cache_dir` — L7761
- `_character_meta_grid_cache_path` — L7769
- `_character_meta_grid_path` — L7775
- `generate_character_meta_grid_gpt_image2` — L7781
- `_generate_all_character_meta_grids` — L7911
- `_write_character_sheet_qa` — L7952
- `generate_character_sheet_gpt_image2` — L7962
- `generate_production_storyboard_page_gpt_image2` — L8062
- `_qa_clean_storyboard_panel` — L8125
- `_crop_storyboard_grid_panels` — L8306
- `generate_storyboard_grid_gpt_image2` — L8353
- `_gpt_image2_direct_annotated_aspect` — L8584
- `_gpt_image2_direct_annotated_prompt` — L8591
- `generate_gpt_image2_direct_annotated_storyboards` — L8621
- `_llm_bgm_description` — L8722
- `_bgm_contains_vocals` — L8761
- `generate_bgm` — L8795
- `step6_parallel` — L8912

---

### 第 6.5 步：动态化（可选，--with-motion 开启）
Range: **L9233 – L13490** (4258 lines)

**Sub-sections:**
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L13227-13269 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L13270-13307 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回主音轨_ — L13308-13445 (138 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L13446-13490 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L9236
- `_motion_tasks_file` — L9303
- `_motion_qa_file` — L9307
- `_append_motion_qa` — L9311
- `_finalize_motion_qa` — L9335
- `_lip_sync_tasks_file` — L9419
- `_load_motion_tasks` — L9423
- `_save_motion_task` — L9433
- `_remove_motion_task` — L9441
- `_load_lip_sync_tasks` — L9448
- `_save_lip_sync_task` — L9458
- `_remove_lip_sync_task` — L9465
- `_video_visual_motion_qa` — L9472
- `_motion_output_qa` — L9544
- `_has_audio_stream` — L9589
- `_normalize_motion_video` — L9600
- `_motion_poll_and_download` — L9650
- `_build_motion_video_prompt` — L9701
- `_short_board_text` — L9731
- `_wrap_board_text` — L9738
- `_storyboard_font` — L9769
- `_draw_storyboard_arrow` — L9784
- `_build_annotated_storyboard_reference` — L9798
- `_plain_caption_text` — L9899
- `_werydance_caption_request` — L9907
- `_werydance_caption_instruction` — L9934
- `_werydance_negative_prompt` — L9946
- `_motion_reference_prompt` — L9964
- `_motion_audio_dub_prompt` — L9987
- `_motion_audio_dub_poll_and_download` — L10021
- `_try_motion_audio_dub_video` — L10086
- `_try_motion_reference_video` — L10221
- `_motion_one_scene` — L10337
- `_grid_multiref_tasks_file` — L10466
- `_previs_page_tasks_file` — L10470
- `_load_grid_multiref_tasks` — L10474
- `_load_previs_page_tasks` — L10484
- `_save_grid_multiref_task` — L10494
- `_save_previs_page_task` — L10501
- `_remove_grid_multiref_task` — L10508
- `_remove_previs_page_task` — L10515
- `_poll_video_task_download` — L10522
- `_grid_multiref_group_size` — L10571
- `_grid_multiref_duration` — L10579
- `_grid_multiref_segment_max_stretch` — L10595
- `_grid_multiref_prompt` — L10603
- `_write_grid_multiref_motion_qa` — L10651
- `_write_previs_page_motion_qa` — L10661
- `_write_storyboard_trailer_qa` — L10671
- `_write_character_trailer_qa` — L10681
- `_write_grid_multiref_segment_qa` — L10691
- `_motion_compare_record` — L10701
- `_write_storyboard_motion_compare_qa` — L10723
- `_scene_segment_duration` — L10759
- `_apply_grid_multiref_segments` — L10778
- `_previs_page_duration` — L10972
- `_previs_page_group_prompt` — L10982
- `_previs_page_groups` — L11008
- `_storyboard_trailer_duration` — L11023
- `_storyboard_trailer_prompt` — L11033
- `_character_trailer_max_shots` — L11061
- `_character_trailer_shot_duration` — L11069
- `_character_trailer_prompt` — L11083
- `_concat_character_trailer_segments` — L11098
- `_generate_character_trailer_motion` — L11137
- `_multi_trailer_prompt_for_group` — L11245
- `_generate_multi_trailer_segments` — L11268
- `_generate_storyboard_trailer_motion` — L11379
- `_generate_previs_page_motion_segments` — L11454
- `_generate_grid_multiref_motion_segments` — L11566
- `_grid_multiref_concat_groups` — L11736
- `_grid_multiref_concat_groups_partial` — L11753
- `_grid_multiref_concat_paths` — L11771
- `_lip_sync_slot_duration` — L11802
- `_adsd_lip_sync_prompt` — L11809
- `_adsd_broll_motion_prompt` — L11855
- `_adsd_action_b_motion_prompt` — L11897
- `_adsd_silent_b_motion_prompt` — L11943
- `_adsd_narrated_b_audio_dub_prompt` — L11978
- `_adsd_almighty_audio_dub_prompt` — L12022
- `_postprocess_lip_sync_segment` — L12063
- `_detect_audio_leading_silence` — L12131
- `_postprocess_audio_dub_segment` — L12153
- `_lips_change_repair_segment` — L12264
- `_load_lips_change_requested_turns` — L12349
- `_parse_turn_set` — L12366
- `_load_motion_voice_repair_turns` — L12388
- `_voice_assets_file` — L12400
- `_load_voice_assets` — L12407
- `_select_voice_asset_reference` — L12426
- `_lip_sync_poll_download_and_process` — L12492
- `_lip_sync_one_scene` — L12560
- `step66_adsd_lip_sync` — L12884
- `step65_motion` — L13117
- `step65_grid_multiref_motion_qa` — L13199
- `_sanitize_scene_for_state` — L13228
- `_save_pipeline_state` — L13247
- `_retime_after_audio_dub` — L13271
- `_build_voice_clone_hybrid_audio` — L13309
- `_build_dynamic_bgm` — L13447

---

### 第七步：拼接视频轨
Range: **L13491 – L13722** (232 lines)

**Functions:**
- `step7_concat` — L13492

---

### 第八步：生成 ASS 字幕
Range: **L13723 – L14514** (792 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L13846-14514 (669 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L13724
- `_word_timings_for_subtitle_align` — L13750
- `_align_segments_via_asr` — L13791
- `step8_subtitles` — L13834
- `_read_output_json` — L14246
- `_qa_file_pass` — L14257
- `_ass_has_dialogue` — L14264
- `_write_adsd_delivery_qa` — L14274
- `_write_bgm_only_qa` — L14403

---

### 第九步：最终合成
Range: **L14515 – L14760** (246 lines)

**Functions:**
- `step9_render` — L14516

---

### 第十步：推送 Telegram
Range: **L14761 – L16375** (1615 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L15861-16182 (322 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L16183-16187 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L16188-16251 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L16252-16297 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L16298-16375 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L15130
- `PANTONE_FALLBACK` — L15157
- `FESTIVAL_DATE_TAG` — L15270

**Functions:**
- `_generate_caption` — L14762
- `_overlay_title_on_cover` — L15000
- `_prepare_tg_photo` — L15110
- `_get_pantone_for_date` — L15160
- `_llm_bottom_note` — L15185
- `_get_bottom_note` — L15214
- `_get_date_tag` — L15292
- `_shrink_to_b64` — L15314
- `_llm_check_scenes_anomalies` — L15330
- `_llm_check_cover_unique` — L15383
- `_llm_check_cover_quality` — L15413
- `_try_almanac_cover` — L15455
- `_generate_cover_image` — L15626
- `_async_kickoff_cover_caption` — L15868
- `_await_async_cover_caption` — L15898
- `step10_deliver` — L15922

---

### 主流程
Range: **L16376 – L16553** (178 lines)

**Functions:**
- `_print_execution_plan` — L16377
- `main` — L16425

---
