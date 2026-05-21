# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (15583 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-1883 (1762 lines · 55 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L1884-3528 (1645 lines · 22 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L3529-4630 (1102 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L4631-5182 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L5183-8391 (3209 lines · 70 fn · 6 sub)
- [`第 6.5 步：动态化（可选，--with-motion 开启）`](#第-6-5-步-动态化-可选---with-motion-开启) — L8392-12595 (4204 lines · 100 fn · 4 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L12596-12765 (170 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L12766-13557 (792 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L13558-13798 (241 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L13799-15413 (1615 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L15414-15583 (170 lines · 2 fn · 0 sub)

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
Range: **L1884 – L3528** (1645 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L2822-3528 (707 lines)

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
- `_adsd_immersion_qa_rewrite_turns` — L2485
- `_adsd_visual_contract` — L2543
- `step1_script` — L2595
- `_write_ads_retention_qa` — L3472

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L3529 – L4630** (1102 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L3604
- `_ADSD_POLICY_REWRITE_TERMS` — L3610
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L3701

**Functions:**
- `_openai_tts_fallback` — L3530
- `_edge_tts_fallback` — L3576
- `_sanitize_for_external_api` — L3619
- `_is_content_policy_error` — L3628
- `_rewrite_adsd_tts_text_for_policy` — L3642
- `_record_adsd_tts_rewrite` — L3682
- `_build_silence_mp3` — L3707
- `_audio_duration_seconds` — L3720
- `_text_to_audio_master_voice_timed` — L3732
- `_text_to_audio_master_voice` — L3857
- `step2_master_voice` — L3960
- `_tts_turn_to_audio` — L4088
- `_asr_verify_dialogue_audio` — L4150
- `_asr_verify_dialogue_turns` — L4212
- `_normalize_cn_number_token` — L4254
- `_compact_zh_text` — L4276
- `_write_adsd_asr_text_qa` — L4283
- `_write_adsd_speaker_focus_qa` — L4322
- `_write_adsd_gender_voice_qa` — L4382
- `step2_dialogue_voice` — L4435

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L4631 – L5182** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L4638-4760 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L4761-4795 (35 lines)
- _第二层：字符数插值_ — L4796-4820 (25 lines)
- _第三层：silencedetect 物理校准_ — L4821-5182 (362 lines)

**Functions:**
- `_detect_silences` — L4639
- `_calibrate_boundaries` — L4674
- `_enforce_monotonic` — L4708
- `_manual_override_segments` — L4720
- `_calc_sentence_boundaries` — L4741
- `step345_timeline` — L4852
- `_analyze_bgm_energy_cuts` — L4911
- `_snap_bgm_only_boundaries` — L4974
- `step345_bgm_only_timeline` — L5034

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L5183 – L8391** (3209 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L6269-6319 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L6320-6420 (101 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L6421-6695 (275 lines)
- _Speaker IP Card (2026-05-21)_ — L6696-8224 (1529 lines)
- _审批流程_ — L8225-8281 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L8282-8391 (110 lines)

**Top-level constants:**
- `CHARACTER_META_GRID_COSTUMES` — L6275
- `CHARACTER_META_GRID_POSES` — L6276
- `CHARACTER_META_GRID_SCENES` — L6277
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L6280

**Functions:**
- `_extract_img_url` — L5184
- `_extract_img_urls` — L5206
- `_extract_video_url` — L5239
- `_count_bands` — L5264
- `_detect_contact_sheet_like_image` — L5276
- `_guess_upload_mime` — L5330
- `_upload_to_weryai` — L5353
- `_send_for_approval` — L5385
- `_wait_approval` — L5449
- `_render_still_segment` — L5461
- `_scene_text_visual_alignment` — L5475
- `_write_text_visual_alignment_qa` — L5511
- `_scene_motion_action_plan` — L5534
- `_ensure_motion_action_plan` — L5588
- `_motion_action_block` — L5597
- `_motion_plan_for_qa` — L5625
- `_write_motion_action_plan_qa` — L5635
- `_write_motion_bridge_refs_qa` — L5665
- `_motion_bridge_ref_prompt` — L5672
- `generate_motion_bridge_refs_gpt_image2` — L5705
- `generate_image` — L5818
- `generate_storyboard_images_gpt_image2` — L5865
- `_storyboard_grid_aspect` — L6050
- `_storyboard_grid_cols_rows` — L6057
- `_storyboard_grid_prompt` — L6079
- `_storyboard_grid_prompt_limit` — L6117
- `_is_prompt_limit_response` — L6121
- `_production_storyboard_prompt` — L6127
- `_write_production_storyboard_page_qa` — L6161
- `_character_sheet_prompt` — L6171
- `_is_audit_blocked` — L6297
- `_paraphrase_sensitive_dialogue` — L6310
- `_topic_cache_dir` — L6324
- `_topic_cache_path` — L6330
- `_load_topic_decomposition_cache` — L6335
- `_save_topic_decomposition_cache` — L6345
- `_llm_topic_decomposition` — L6350
- `_llm_infer_meta_grid_template` — L6478
- `_resolve_meta_grid_template` — L6535
- `_infer_meta_grid_costume` — L6578
- `_infer_meta_grid_pose` — L6623
- `_adsd_meta_grid_call_prompt` — L6666
- `_migrate_speaker_ip` — L6702
- `_speaker_ips_dir` — L6727
- `_list_speaker_ips` — L6734
- `_match_speaker_ip` — L6748
- `_build_speaker_ip_context_for_script` — L6768
- `_ip_usage_stats` — L6814
- `_recommend_related_ips` — L6832
- `_save_speaker_ip` — L6857
- `_record_speaker_usage_history` — L6866
- `_format_speaker_usage_history_for_prompt` — L6913
- `_character_meta_grid_cache_dir` — L6931
- `_character_meta_grid_cache_path` — L6939
- `_character_meta_grid_path` — L6945
- `generate_character_meta_grid_gpt_image2` — L6951
- `_generate_all_character_meta_grids` — L7070
- `_write_character_sheet_qa` — L7111
- `generate_character_sheet_gpt_image2` — L7121
- `generate_production_storyboard_page_gpt_image2` — L7221
- `_qa_clean_storyboard_panel` — L7284
- `_crop_storyboard_grid_panels` — L7465
- `generate_storyboard_grid_gpt_image2` — L7512
- `_gpt_image2_direct_annotated_aspect` — L7743
- `_gpt_image2_direct_annotated_prompt` — L7750
- `generate_gpt_image2_direct_annotated_storyboards` — L7780
- `_llm_bgm_description` — L7881
- `_bgm_contains_vocals` — L7920
- `generate_bgm` — L7954
- `step6_parallel` — L8071

---

### 第 6.5 步：动态化（可选，--with-motion 开启）
Range: **L8392 – L12595** (4204 lines)

**Sub-sections:**
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L12337-12379 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L12380-12417 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回主音轨_ — L12418-12550 (133 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L12551-12595 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L8395
- `_motion_tasks_file` — L8462
- `_motion_qa_file` — L8466
- `_append_motion_qa` — L8470
- `_finalize_motion_qa` — L8494
- `_lip_sync_tasks_file` — L8578
- `_load_motion_tasks` — L8582
- `_save_motion_task` — L8592
- `_remove_motion_task` — L8600
- `_load_lip_sync_tasks` — L8607
- `_save_lip_sync_task` — L8617
- `_remove_lip_sync_task` — L8624
- `_video_visual_motion_qa` — L8631
- `_motion_output_qa` — L8703
- `_has_audio_stream` — L8748
- `_normalize_motion_video` — L8759
- `_motion_poll_and_download` — L8809
- `_build_motion_video_prompt` — L8860
- `_short_board_text` — L8890
- `_wrap_board_text` — L8897
- `_storyboard_font` — L8928
- `_draw_storyboard_arrow` — L8943
- `_build_annotated_storyboard_reference` — L8957
- `_plain_caption_text` — L9058
- `_werydance_caption_request` — L9066
- `_werydance_caption_instruction` — L9093
- `_werydance_negative_prompt` — L9105
- `_motion_reference_prompt` — L9119
- `_motion_audio_dub_prompt` — L9142
- `_motion_audio_dub_poll_and_download` — L9176
- `_try_motion_audio_dub_video` — L9241
- `_try_motion_reference_video` — L9376
- `_motion_one_scene` — L9492
- `_grid_multiref_tasks_file` — L9621
- `_previs_page_tasks_file` — L9625
- `_load_grid_multiref_tasks` — L9629
- `_load_previs_page_tasks` — L9639
- `_save_grid_multiref_task` — L9649
- `_save_previs_page_task` — L9656
- `_remove_grid_multiref_task` — L9663
- `_remove_previs_page_task` — L9670
- `_poll_video_task_download` — L9677
- `_grid_multiref_group_size` — L9726
- `_grid_multiref_duration` — L9734
- `_grid_multiref_segment_max_stretch` — L9750
- `_grid_multiref_prompt` — L9758
- `_write_grid_multiref_motion_qa` — L9806
- `_write_previs_page_motion_qa` — L9816
- `_write_storyboard_trailer_qa` — L9826
- `_write_character_trailer_qa` — L9836
- `_write_grid_multiref_segment_qa` — L9846
- `_motion_compare_record` — L9856
- `_write_storyboard_motion_compare_qa` — L9878
- `_scene_segment_duration` — L9914
- `_apply_grid_multiref_segments` — L9933
- `_previs_page_duration` — L10127
- `_previs_page_group_prompt` — L10137
- `_previs_page_groups` — L10163
- `_storyboard_trailer_duration` — L10178
- `_storyboard_trailer_prompt` — L10188
- `_character_trailer_max_shots` — L10216
- `_character_trailer_shot_duration` — L10224
- `_character_trailer_prompt` — L10238
- `_concat_character_trailer_segments` — L10253
- `_generate_character_trailer_motion` — L10292
- `_multi_trailer_prompt_for_group` — L10400
- `_generate_multi_trailer_segments` — L10423
- `_generate_storyboard_trailer_motion` — L10534
- `_generate_previs_page_motion_segments` — L10609
- `_generate_grid_multiref_motion_segments` — L10721
- `_grid_multiref_concat_groups` — L10891
- `_grid_multiref_concat_groups_partial` — L10908
- `_grid_multiref_concat_paths` — L10926
- `_lip_sync_slot_duration` — L10957
- `_adsd_lip_sync_prompt` — L10964
- `_adsd_broll_motion_prompt` — L11010
- `_adsd_action_b_motion_prompt` — L11052
- `_adsd_silent_b_motion_prompt` — L11089
- `_adsd_narrated_b_audio_dub_prompt` — L11124
- `_adsd_almighty_audio_dub_prompt` — L11168
- `_postprocess_lip_sync_segment` — L11209
- `_detect_audio_leading_silence` — L11277
- `_postprocess_audio_dub_segment` — L11299
- `_lips_change_repair_segment` — L11405
- `_load_lips_change_requested_turns` — L11490
- `_parse_turn_set` — L11507
- `_load_motion_voice_repair_turns` — L11529
- `_voice_assets_file` — L11541
- `_load_voice_assets` — L11548
- `_select_voice_asset_reference` — L11567
- `_lip_sync_poll_download_and_process` — L11633
- `_lip_sync_one_scene` — L11697
- `step66_adsd_lip_sync` — L11994
- `step65_motion` — L12227
- `step65_grid_multiref_motion_qa` — L12309
- `_sanitize_scene_for_state` — L12338
- `_save_pipeline_state` — L12357
- `_retime_after_audio_dub` — L12381
- `_build_voice_clone_hybrid_audio` — L12419
- `_build_dynamic_bgm` — L12552

---

### 第七步：拼接视频轨
Range: **L12596 – L12765** (170 lines)

**Functions:**
- `step7_concat` — L12597

---

### 第八步：生成 ASS 字幕
Range: **L12766 – L13557** (792 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L12889-13557 (669 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L12767
- `_word_timings_for_subtitle_align` — L12793
- `_align_segments_via_asr` — L12834
- `step8_subtitles` — L12877
- `_read_output_json` — L13289
- `_qa_file_pass` — L13300
- `_ass_has_dialogue` — L13307
- `_write_adsd_delivery_qa` — L13317
- `_write_bgm_only_qa` — L13446

---

### 第九步：最终合成
Range: **L13558 – L13798** (241 lines)

**Functions:**
- `step9_render` — L13559

---

### 第十步：推送 Telegram
Range: **L13799 – L15413** (1615 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L14899-15220 (322 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L15221-15225 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L15226-15289 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L15290-15335 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L15336-15413 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L14168
- `PANTONE_FALLBACK` — L14195
- `FESTIVAL_DATE_TAG` — L14308

**Functions:**
- `_generate_caption` — L13800
- `_overlay_title_on_cover` — L14038
- `_prepare_tg_photo` — L14148
- `_get_pantone_for_date` — L14198
- `_llm_bottom_note` — L14223
- `_get_bottom_note` — L14252
- `_get_date_tag` — L14330
- `_shrink_to_b64` — L14352
- `_llm_check_scenes_anomalies` — L14368
- `_llm_check_cover_unique` — L14421
- `_llm_check_cover_quality` — L14451
- `_try_almanac_cover` — L14493
- `_generate_cover_image` — L14664
- `_async_kickoff_cover_caption` — L14906
- `_await_async_cover_caption` — L14936
- `step10_deliver` — L14960

---

### 主流程
Range: **L15414 – L15583** (170 lines)

**Functions:**
- `_print_execution_plan` — L15415
- `main` — L15463

---
