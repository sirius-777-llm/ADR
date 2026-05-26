# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (16678 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-1954 (1833 lines · 57 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L1955-4086 (2132 lines · 28 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L4087-5190 (1104 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L5191-5742 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L5743-9332 (3590 lines · 75 fn · 6 sub)
- [`第 6.5 步：动态化（可选，--with-motion 开启）`](#第-6-5-步-动态化-可选---with-motion-开启) — L9333-13615 (4283 lines · 100 fn · 4 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L13616-13847 (232 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L13848-14639 (792 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L14640-14885 (246 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L14886-16500 (1615 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L16501-16678 (178 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L1954** (1833 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L298-427 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L428-1082 (655 lines)
- _工具函数_ — L1083-1432 (350 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1433-1954 (522 lines)

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
- `_PODCAST_TO_VOICE_ASSET_MAP` — L797
- `VOICE_ASSET_AUDIO_DUB_EXPERIMENT` — L834
- `VOICE_ASSET_AUDIO_DUB_PARTIAL_OK` — L842
- `MOTION_VISUAL_QA` — L846
- `MOTION_VOICE_REPAIR` — L854
- `MOTION_VOICE_STRICT_LOCK` — L859
- `WERYDANCE_CAPTIONS` — L864
- `ADSD_ONSITE_POV_MODE` — L876
- `ADSD_LIPS_CHANGE_REPAIR` — L881
- `ADSD_LIPS_CHANGE_ALL` — L886
- `ADS_REPORTER_MODE` — L897
- `ADS_STORYBOARD_FLOW_DEFAULT` — L914
- `ADS_RETENTION_MODE` — L927
- `ADSD_MODE_NAME` — L933
- `EMOTION_STYLE` — L1062
- `EMOTION_STYLE_BRIGHT` — L1074
- `_TG_DASHBOARD_STAGES` — L1096
- `_TG_NOISY_PATTERNS` — L1111
- `_TG_IMMEDIATE_PATTERNS` — L1129
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1362
- `_TOPIC_MODIFIERS` — L1786
- `_TONE_PANTONE_OVERRIDE` — L1803

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
- `_podcast_id_to_voice_asset` — L814
- `log` — L1084
- `_tg_send_raw` — L1152
- `_tg_matches` — L1168
- `_tg_summarize` — L1172
- `_tg_dashboard_stage_for` — L1179
- `_tg_progress_bar` — L1187
- `_tg_dashboard_text` — L1193
- `_tg_dashboard_update` — L1211
- `_tg_maybe_digest` — L1248
- `tg` — L1263
- `_wait_image_submit_slot` — L1312
- `_wait_motion_submit_slot` — L1325
- `_is_rate_limited_error` — L1338
- `_is_rate_limited_response` — L1348
- `_inject_image2_quality_suffix` — L1370
- `submit_text_to_image` — L1384
- `req_post` — L1414
- `req_get` — L1428
- `_tg_probe_send` — L1436
- `_tg_probe_delete` — L1456
- `_tg_upload_with_probe_gap` — L1469
- `poll` — L1509
- `poll_podcast` — L1534
- `poll_task_status` — L1556
- `poll_storyboard_task` — L1578
- `chat` — L1604
- `pick_image_model` — L1632
- `detect_topic_meta` — L1657
- `_topic_culture_guard` — L1707
- `_write_cultural_visual_qa` — L1733
- `is_1919_global_topic` — L1780
- `_strip_topic_modifiers` — L1791
- `apply_1919_global_guardrails` — L1809
- `build_1919_global_cover_prompt` — L1838
- `build_shot_blueprint` — L1867
- `ffprobe_duration` — L1893
- `ffprobe_video_size` — L1904
- `_video_decode_probe` — L1925
- `ffmpeg` — L1943

---

### 第一步：双导演生成剧本
Range: **L1955 – L4086** (2132 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L3358-4086 (729 lines)

**Functions:**
- `_extract_json_array` — L1956
- `_extract_json_object` — L1966
- `_voice_for_speaker` — L1976
- `_adsd_gender_from_voice` — L2012
- `_adsd_infer_gender_from_speaker` — L2020
- `_adsd_gender_lock_phrase` — L2029
- `_adsd_visual_subject_has_gender_conflict` — L2044
- `_adsd_default_roles` — L2056
- `_adsd_allows_media_role` — L2061
- `_adsd_role_candidates` — L2069
- `_adsd_dialogue_shape` — L2092
- `_finalize_adsd_turns` — L2101
- `_parse_adsd_override_turns` — L2135
- `_parse_timecode_seconds` — L2226
- `_clean_override_line_text` — L2235
- `_parse_override_script_text` — L2241
- `_adsd_pov_contract` — L2275
- `_load_audit_blacklist_block` — L2288
- `_generate_adsd_dialogue_turns` — L2326
- `_broll_rhythm_reviewer` — L2749
- `_sweep_speaker_field` — L2856
- `_adsd_immersion_qa_rewrite_turns` — L2916
- `_adsd_visual_contract` — L2974
- `_parse_risk_score` — L3026
- `_check_high_risk_hard_abort` — L3055
- `_maybe_neutralize_topic` — L3082
- `step1_script` — L3121
- `_write_ads_retention_qa` — L4030

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L4087 – L5190** (1104 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L4162
- `_ADSD_POLICY_REWRITE_TERMS` — L4168
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L4259

**Functions:**
- `_openai_tts_fallback` — L4088
- `_edge_tts_fallback` — L4134
- `_sanitize_for_external_api` — L4177
- `_is_content_policy_error` — L4186
- `_rewrite_adsd_tts_text_for_policy` — L4200
- `_record_adsd_tts_rewrite` — L4240
- `_build_silence_mp3` — L4265
- `_audio_duration_seconds` — L4278
- `_text_to_audio_master_voice_timed` — L4290
- `_text_to_audio_master_voice` — L4415
- `step2_master_voice` — L4518
- `_tts_turn_to_audio` — L4646
- `_asr_verify_dialogue_audio` — L4710
- `_asr_verify_dialogue_turns` — L4772
- `_normalize_cn_number_token` — L4814
- `_compact_zh_text` — L4836
- `_write_adsd_asr_text_qa` — L4843
- `_write_adsd_speaker_focus_qa` — L4882
- `_write_adsd_gender_voice_qa` — L4942
- `step2_dialogue_voice` — L4995

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L5191 – L5742** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L5198-5320 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L5321-5355 (35 lines)
- _第二层：字符数插值_ — L5356-5380 (25 lines)
- _第三层：silencedetect 物理校准_ — L5381-5742 (362 lines)

**Functions:**
- `_detect_silences` — L5199
- `_calibrate_boundaries` — L5234
- `_enforce_monotonic` — L5268
- `_manual_override_segments` — L5280
- `_calc_sentence_boundaries` — L5301
- `step345_timeline` — L5412
- `_analyze_bgm_energy_cuts` — L5471
- `_snap_bgm_only_boundaries` — L5534
- `step345_bgm_only_timeline` — L5594

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L5743 – L9332** (3590 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L6846-6896 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L6897-7037 (141 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L7038-7438 (401 lines)
- _Speaker IP Card (2026-05-21)_ — L7439-9165 (1727 lines)
- _审批流程_ — L9166-9222 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L9223-9332 (110 lines)

**Top-level constants:**
- `CHARACTER_META_GRID_COSTUMES` — L6852
- `CHARACTER_META_GRID_POSES` — L6853
- `CHARACTER_META_GRID_SCENES` — L6854
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L6857

**Functions:**
- `_extract_img_url` — L5744
- `_extract_img_urls` — L5766
- `_extract_video_url` — L5799
- `_count_bands` — L5824
- `_detect_contact_sheet_like_image` — L5836
- `_guess_upload_mime` — L5890
- `_upload_to_weryai` — L5913
- `_send_for_approval` — L5945
- `_wait_approval` — L6009
- `_render_still_segment` — L6021
- `_scene_text_visual_alignment` — L6052
- `_write_text_visual_alignment_qa` — L6088
- `_scene_motion_action_plan` — L6111
- `_ensure_motion_action_plan` — L6165
- `_motion_action_block` — L6174
- `_motion_plan_for_qa` — L6202
- `_write_motion_action_plan_qa` — L6212
- `_write_motion_bridge_refs_qa` — L6242
- `_motion_bridge_ref_prompt` — L6249
- `generate_motion_bridge_refs_gpt_image2` — L6282
- `generate_image` — L6395
- `generate_storyboard_images_gpt_image2` — L6442
- `_storyboard_grid_aspect` — L6627
- `_storyboard_grid_cols_rows` — L6634
- `_storyboard_grid_prompt` — L6656
- `_storyboard_grid_prompt_limit` — L6694
- `_is_prompt_limit_response` — L6698
- `_production_storyboard_prompt` — L6704
- `_write_production_storyboard_page_qa` — L6738
- `_character_sheet_prompt` — L6748
- `_is_audit_blocked` — L6874
- `_paraphrase_sensitive_dialogue` — L6887
- `_topic_cache_dir` — L6901
- `_topic_cache_path` — L6907
- `_load_topic_decomposition_cache` — L6920
- `_save_topic_decomposition_cache` — L6938
- `_llm_topic_decomposition` — L6944
- `_director_route_block` — L7091
- `_llm_infer_meta_grid_template` — L7161
- `_resolve_meta_grid_template` — L7218
- `_infer_meta_grid_costume` — L7261
- `_infer_meta_grid_pose` — L7310
- `_adsd_meta_grid_call_prompt` — L7357
- `_meta_grid_panel_index` — L7399
- `_migrate_speaker_ip` — L7445
- `_speaker_ips_dir` — L7470
- `_list_speaker_ips` — L7477
- `_match_speaker_ip` — L7491
- `_build_speaker_ip_context_for_script` — L7511
- `_ip_usage_stats` — L7567
- `_recommend_related_ips` — L7585
- `_save_speaker_ip` — L7610
- `_record_speaker_usage_history` — L7619
- `_format_speaker_usage_history_for_prompt` — L7666
- `_llm_infer_ip_skeleton` — L7684
- `_llm_pick_voice_asset_for_ip` — L7729
- `_auto_incubate_missing_ips` — L7777
- `_character_meta_grid_cache_dir` — L7861
- `_character_meta_grid_cache_path` — L7869
- `_character_meta_grid_path` — L7875
- `generate_character_meta_grid_gpt_image2` — L7881
- `_generate_all_character_meta_grids` — L8011
- `_write_character_sheet_qa` — L8052
- `generate_character_sheet_gpt_image2` — L8062
- `generate_production_storyboard_page_gpt_image2` — L8162
- `_qa_clean_storyboard_panel` — L8225
- `_crop_storyboard_grid_panels` — L8406
- `generate_storyboard_grid_gpt_image2` — L8453
- `_gpt_image2_direct_annotated_aspect` — L8684
- `_gpt_image2_direct_annotated_prompt` — L8691
- `generate_gpt_image2_direct_annotated_storyboards` — L8721
- `_llm_bgm_description` — L8822
- `_bgm_contains_vocals` — L8861
- `generate_bgm` — L8895
- `step6_parallel` — L9012

---

### 第 6.5 步：动态化（可选，--with-motion 开启）
Range: **L9333 – L13615** (4283 lines)

**Sub-sections:**
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L13352-13394 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L13395-13432 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回主音轨_ — L13433-13570 (138 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L13571-13615 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L9336
- `_motion_tasks_file` — L9403
- `_motion_qa_file` — L9407
- `_append_motion_qa` — L9411
- `_finalize_motion_qa` — L9435
- `_lip_sync_tasks_file` — L9519
- `_load_motion_tasks` — L9523
- `_save_motion_task` — L9533
- `_remove_motion_task` — L9541
- `_load_lip_sync_tasks` — L9548
- `_save_lip_sync_task` — L9558
- `_remove_lip_sync_task` — L9565
- `_video_visual_motion_qa` — L9572
- `_motion_output_qa` — L9644
- `_has_audio_stream` — L9689
- `_normalize_motion_video` — L9700
- `_motion_poll_and_download` — L9750
- `_build_motion_video_prompt` — L9801
- `_short_board_text` — L9831
- `_wrap_board_text` — L9838
- `_storyboard_font` — L9869
- `_draw_storyboard_arrow` — L9884
- `_build_annotated_storyboard_reference` — L9898
- `_plain_caption_text` — L9999
- `_werydance_caption_request` — L10007
- `_werydance_caption_instruction` — L10034
- `_werydance_negative_prompt` — L10046
- `_motion_reference_prompt` — L10064
- `_motion_audio_dub_prompt` — L10087
- `_motion_audio_dub_poll_and_download` — L10121
- `_try_motion_audio_dub_video` — L10186
- `_try_motion_reference_video` — L10321
- `_motion_one_scene` — L10437
- `_grid_multiref_tasks_file` — L10566
- `_previs_page_tasks_file` — L10570
- `_load_grid_multiref_tasks` — L10574
- `_load_previs_page_tasks` — L10584
- `_save_grid_multiref_task` — L10594
- `_save_previs_page_task` — L10601
- `_remove_grid_multiref_task` — L10608
- `_remove_previs_page_task` — L10615
- `_poll_video_task_download` — L10622
- `_grid_multiref_group_size` — L10671
- `_grid_multiref_duration` — L10679
- `_grid_multiref_segment_max_stretch` — L10695
- `_grid_multiref_prompt` — L10703
- `_write_grid_multiref_motion_qa` — L10751
- `_write_previs_page_motion_qa` — L10761
- `_write_storyboard_trailer_qa` — L10771
- `_write_character_trailer_qa` — L10781
- `_write_grid_multiref_segment_qa` — L10791
- `_motion_compare_record` — L10801
- `_write_storyboard_motion_compare_qa` — L10823
- `_scene_segment_duration` — L10859
- `_apply_grid_multiref_segments` — L10878
- `_previs_page_duration` — L11072
- `_previs_page_group_prompt` — L11082
- `_previs_page_groups` — L11108
- `_storyboard_trailer_duration` — L11123
- `_storyboard_trailer_prompt` — L11133
- `_character_trailer_max_shots` — L11161
- `_character_trailer_shot_duration` — L11169
- `_character_trailer_prompt` — L11183
- `_concat_character_trailer_segments` — L11198
- `_generate_character_trailer_motion` — L11237
- `_multi_trailer_prompt_for_group` — L11345
- `_generate_multi_trailer_segments` — L11368
- `_generate_storyboard_trailer_motion` — L11479
- `_generate_previs_page_motion_segments` — L11554
- `_generate_grid_multiref_motion_segments` — L11666
- `_grid_multiref_concat_groups` — L11836
- `_grid_multiref_concat_groups_partial` — L11853
- `_grid_multiref_concat_paths` — L11871
- `_lip_sync_slot_duration` — L11902
- `_adsd_lip_sync_prompt` — L11909
- `_adsd_broll_motion_prompt` — L11955
- `_adsd_action_b_motion_prompt` — L11997
- `_adsd_silent_b_motion_prompt` — L12043
- `_adsd_narrated_b_audio_dub_prompt` — L12078
- `_adsd_almighty_audio_dub_prompt` — L12122
- `_postprocess_lip_sync_segment` — L12163
- `_detect_audio_leading_silence` — L12231
- `_postprocess_audio_dub_segment` — L12253
- `_lips_change_repair_segment` — L12364
- `_load_lips_change_requested_turns` — L12449
- `_parse_turn_set` — L12466
- `_load_motion_voice_repair_turns` — L12488
- `_voice_assets_file` — L12500
- `_load_voice_assets` — L12507
- `_select_voice_asset_reference` — L12526
- `_lip_sync_poll_download_and_process` — L12592
- `_lip_sync_one_scene` — L12660
- `step66_adsd_lip_sync` — L12984
- `step65_motion` — L13242
- `step65_grid_multiref_motion_qa` — L13324
- `_sanitize_scene_for_state` — L13353
- `_save_pipeline_state` — L13372
- `_retime_after_audio_dub` — L13396
- `_build_voice_clone_hybrid_audio` — L13434
- `_build_dynamic_bgm` — L13572

---

### 第七步：拼接视频轨
Range: **L13616 – L13847** (232 lines)

**Functions:**
- `step7_concat` — L13617

---

### 第八步：生成 ASS 字幕
Range: **L13848 – L14639** (792 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L13971-14639 (669 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L13849
- `_word_timings_for_subtitle_align` — L13875
- `_align_segments_via_asr` — L13916
- `step8_subtitles` — L13959
- `_read_output_json` — L14371
- `_qa_file_pass` — L14382
- `_ass_has_dialogue` — L14389
- `_write_adsd_delivery_qa` — L14399
- `_write_bgm_only_qa` — L14528

---

### 第九步：最终合成
Range: **L14640 – L14885** (246 lines)

**Functions:**
- `step9_render` — L14641

---

### 第十步：推送 Telegram
Range: **L14886 – L16500** (1615 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L15986-16307 (322 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L16308-16312 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L16313-16376 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L16377-16422 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L16423-16500 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L15255
- `PANTONE_FALLBACK` — L15282
- `FESTIVAL_DATE_TAG` — L15395

**Functions:**
- `_generate_caption` — L14887
- `_overlay_title_on_cover` — L15125
- `_prepare_tg_photo` — L15235
- `_get_pantone_for_date` — L15285
- `_llm_bottom_note` — L15310
- `_get_bottom_note` — L15339
- `_get_date_tag` — L15417
- `_shrink_to_b64` — L15439
- `_llm_check_scenes_anomalies` — L15455
- `_llm_check_cover_unique` — L15508
- `_llm_check_cover_quality` — L15538
- `_try_almanac_cover` — L15580
- `_generate_cover_image` — L15751
- `_async_kickoff_cover_caption` — L15993
- `_await_async_cover_caption` — L16023
- `step10_deliver` — L16047

---

### 主流程
Range: **L16501 – L16678** (178 lines)

**Functions:**
- `_print_execution_plan` — L16502
- `main` — L16550

---
