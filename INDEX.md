# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (16487 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-1915 (1794 lines · 56 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L1916-3922 (2007 lines · 25 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L3923-5024 (1102 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L5025-5576 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L5577-9166 (3590 lines · 75 fn · 6 sub)
- [`第 6.5 步：动态化（可选，--with-motion 开启）`](#第-6-5-步-动态化-可选---with-motion-开启) — L9167-13424 (4258 lines · 100 fn · 4 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L13425-13656 (232 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L13657-14448 (792 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L14449-14694 (246 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L14695-16309 (1615 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L16310-16487 (178 lines · 2 fn · 0 sub)

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
Range: **L1916 – L3922** (2007 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L3208-3922 (715 lines)

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
- `_adsd_immersion_qa_rewrite_turns` — L2871
- `_adsd_visual_contract` — L2929
- `step1_script` — L2981
- `_write_ads_retention_qa` — L3866

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L3923 – L5024** (1102 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L3998
- `_ADSD_POLICY_REWRITE_TERMS` — L4004
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L4095

**Functions:**
- `_openai_tts_fallback` — L3924
- `_edge_tts_fallback` — L3970
- `_sanitize_for_external_api` — L4013
- `_is_content_policy_error` — L4022
- `_rewrite_adsd_tts_text_for_policy` — L4036
- `_record_adsd_tts_rewrite` — L4076
- `_build_silence_mp3` — L4101
- `_audio_duration_seconds` — L4114
- `_text_to_audio_master_voice_timed` — L4126
- `_text_to_audio_master_voice` — L4251
- `step2_master_voice` — L4354
- `_tts_turn_to_audio` — L4482
- `_asr_verify_dialogue_audio` — L4544
- `_asr_verify_dialogue_turns` — L4606
- `_normalize_cn_number_token` — L4648
- `_compact_zh_text` — L4670
- `_write_adsd_asr_text_qa` — L4677
- `_write_adsd_speaker_focus_qa` — L4716
- `_write_adsd_gender_voice_qa` — L4776
- `step2_dialogue_voice` — L4829

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L5025 – L5576** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L5032-5154 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L5155-5189 (35 lines)
- _第二层：字符数插值_ — L5190-5214 (25 lines)
- _第三层：silencedetect 物理校准_ — L5215-5576 (362 lines)

**Functions:**
- `_detect_silences` — L5033
- `_calibrate_boundaries` — L5068
- `_enforce_monotonic` — L5102
- `_manual_override_segments` — L5114
- `_calc_sentence_boundaries` — L5135
- `step345_timeline` — L5246
- `_analyze_bgm_energy_cuts` — L5305
- `_snap_bgm_only_boundaries` — L5368
- `step345_bgm_only_timeline` — L5428

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L5577 – L9166** (3590 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L6680-6730 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L6731-6871 (141 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L6872-7272 (401 lines)
- _Speaker IP Card (2026-05-21)_ — L7273-8999 (1727 lines)
- _审批流程_ — L9000-9056 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L9057-9166 (110 lines)

**Top-level constants:**
- `CHARACTER_META_GRID_COSTUMES` — L6686
- `CHARACTER_META_GRID_POSES` — L6687
- `CHARACTER_META_GRID_SCENES` — L6688
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L6691

**Functions:**
- `_extract_img_url` — L5578
- `_extract_img_urls` — L5600
- `_extract_video_url` — L5633
- `_count_bands` — L5658
- `_detect_contact_sheet_like_image` — L5670
- `_guess_upload_mime` — L5724
- `_upload_to_weryai` — L5747
- `_send_for_approval` — L5779
- `_wait_approval` — L5843
- `_render_still_segment` — L5855
- `_scene_text_visual_alignment` — L5886
- `_write_text_visual_alignment_qa` — L5922
- `_scene_motion_action_plan` — L5945
- `_ensure_motion_action_plan` — L5999
- `_motion_action_block` — L6008
- `_motion_plan_for_qa` — L6036
- `_write_motion_action_plan_qa` — L6046
- `_write_motion_bridge_refs_qa` — L6076
- `_motion_bridge_ref_prompt` — L6083
- `generate_motion_bridge_refs_gpt_image2` — L6116
- `generate_image` — L6229
- `generate_storyboard_images_gpt_image2` — L6276
- `_storyboard_grid_aspect` — L6461
- `_storyboard_grid_cols_rows` — L6468
- `_storyboard_grid_prompt` — L6490
- `_storyboard_grid_prompt_limit` — L6528
- `_is_prompt_limit_response` — L6532
- `_production_storyboard_prompt` — L6538
- `_write_production_storyboard_page_qa` — L6572
- `_character_sheet_prompt` — L6582
- `_is_audit_blocked` — L6708
- `_paraphrase_sensitive_dialogue` — L6721
- `_topic_cache_dir` — L6735
- `_topic_cache_path` — L6741
- `_load_topic_decomposition_cache` — L6754
- `_save_topic_decomposition_cache` — L6772
- `_llm_topic_decomposition` — L6778
- `_director_route_block` — L6925
- `_llm_infer_meta_grid_template` — L6995
- `_resolve_meta_grid_template` — L7052
- `_infer_meta_grid_costume` — L7095
- `_infer_meta_grid_pose` — L7144
- `_adsd_meta_grid_call_prompt` — L7191
- `_meta_grid_panel_index` — L7233
- `_migrate_speaker_ip` — L7279
- `_speaker_ips_dir` — L7304
- `_list_speaker_ips` — L7311
- `_match_speaker_ip` — L7325
- `_build_speaker_ip_context_for_script` — L7345
- `_ip_usage_stats` — L7401
- `_recommend_related_ips` — L7419
- `_save_speaker_ip` — L7444
- `_record_speaker_usage_history` — L7453
- `_format_speaker_usage_history_for_prompt` — L7500
- `_llm_infer_ip_skeleton` — L7518
- `_llm_pick_voice_asset_for_ip` — L7563
- `_auto_incubate_missing_ips` — L7611
- `_character_meta_grid_cache_dir` — L7695
- `_character_meta_grid_cache_path` — L7703
- `_character_meta_grid_path` — L7709
- `generate_character_meta_grid_gpt_image2` — L7715
- `_generate_all_character_meta_grids` — L7845
- `_write_character_sheet_qa` — L7886
- `generate_character_sheet_gpt_image2` — L7896
- `generate_production_storyboard_page_gpt_image2` — L7996
- `_qa_clean_storyboard_panel` — L8059
- `_crop_storyboard_grid_panels` — L8240
- `generate_storyboard_grid_gpt_image2` — L8287
- `_gpt_image2_direct_annotated_aspect` — L8518
- `_gpt_image2_direct_annotated_prompt` — L8525
- `generate_gpt_image2_direct_annotated_storyboards` — L8555
- `_llm_bgm_description` — L8656
- `_bgm_contains_vocals` — L8695
- `generate_bgm` — L8729
- `step6_parallel` — L8846

---

### 第 6.5 步：动态化（可选，--with-motion 开启）
Range: **L9167 – L13424** (4258 lines)

**Sub-sections:**
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L13161-13203 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L13204-13241 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回主音轨_ — L13242-13379 (138 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L13380-13424 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L9170
- `_motion_tasks_file` — L9237
- `_motion_qa_file` — L9241
- `_append_motion_qa` — L9245
- `_finalize_motion_qa` — L9269
- `_lip_sync_tasks_file` — L9353
- `_load_motion_tasks` — L9357
- `_save_motion_task` — L9367
- `_remove_motion_task` — L9375
- `_load_lip_sync_tasks` — L9382
- `_save_lip_sync_task` — L9392
- `_remove_lip_sync_task` — L9399
- `_video_visual_motion_qa` — L9406
- `_motion_output_qa` — L9478
- `_has_audio_stream` — L9523
- `_normalize_motion_video` — L9534
- `_motion_poll_and_download` — L9584
- `_build_motion_video_prompt` — L9635
- `_short_board_text` — L9665
- `_wrap_board_text` — L9672
- `_storyboard_font` — L9703
- `_draw_storyboard_arrow` — L9718
- `_build_annotated_storyboard_reference` — L9732
- `_plain_caption_text` — L9833
- `_werydance_caption_request` — L9841
- `_werydance_caption_instruction` — L9868
- `_werydance_negative_prompt` — L9880
- `_motion_reference_prompt` — L9898
- `_motion_audio_dub_prompt` — L9921
- `_motion_audio_dub_poll_and_download` — L9955
- `_try_motion_audio_dub_video` — L10020
- `_try_motion_reference_video` — L10155
- `_motion_one_scene` — L10271
- `_grid_multiref_tasks_file` — L10400
- `_previs_page_tasks_file` — L10404
- `_load_grid_multiref_tasks` — L10408
- `_load_previs_page_tasks` — L10418
- `_save_grid_multiref_task` — L10428
- `_save_previs_page_task` — L10435
- `_remove_grid_multiref_task` — L10442
- `_remove_previs_page_task` — L10449
- `_poll_video_task_download` — L10456
- `_grid_multiref_group_size` — L10505
- `_grid_multiref_duration` — L10513
- `_grid_multiref_segment_max_stretch` — L10529
- `_grid_multiref_prompt` — L10537
- `_write_grid_multiref_motion_qa` — L10585
- `_write_previs_page_motion_qa` — L10595
- `_write_storyboard_trailer_qa` — L10605
- `_write_character_trailer_qa` — L10615
- `_write_grid_multiref_segment_qa` — L10625
- `_motion_compare_record` — L10635
- `_write_storyboard_motion_compare_qa` — L10657
- `_scene_segment_duration` — L10693
- `_apply_grid_multiref_segments` — L10712
- `_previs_page_duration` — L10906
- `_previs_page_group_prompt` — L10916
- `_previs_page_groups` — L10942
- `_storyboard_trailer_duration` — L10957
- `_storyboard_trailer_prompt` — L10967
- `_character_trailer_max_shots` — L10995
- `_character_trailer_shot_duration` — L11003
- `_character_trailer_prompt` — L11017
- `_concat_character_trailer_segments` — L11032
- `_generate_character_trailer_motion` — L11071
- `_multi_trailer_prompt_for_group` — L11179
- `_generate_multi_trailer_segments` — L11202
- `_generate_storyboard_trailer_motion` — L11313
- `_generate_previs_page_motion_segments` — L11388
- `_generate_grid_multiref_motion_segments` — L11500
- `_grid_multiref_concat_groups` — L11670
- `_grid_multiref_concat_groups_partial` — L11687
- `_grid_multiref_concat_paths` — L11705
- `_lip_sync_slot_duration` — L11736
- `_adsd_lip_sync_prompt` — L11743
- `_adsd_broll_motion_prompt` — L11789
- `_adsd_action_b_motion_prompt` — L11831
- `_adsd_silent_b_motion_prompt` — L11877
- `_adsd_narrated_b_audio_dub_prompt` — L11912
- `_adsd_almighty_audio_dub_prompt` — L11956
- `_postprocess_lip_sync_segment` — L11997
- `_detect_audio_leading_silence` — L12065
- `_postprocess_audio_dub_segment` — L12087
- `_lips_change_repair_segment` — L12198
- `_load_lips_change_requested_turns` — L12283
- `_parse_turn_set` — L12300
- `_load_motion_voice_repair_turns` — L12322
- `_voice_assets_file` — L12334
- `_load_voice_assets` — L12341
- `_select_voice_asset_reference` — L12360
- `_lip_sync_poll_download_and_process` — L12426
- `_lip_sync_one_scene` — L12494
- `step66_adsd_lip_sync` — L12818
- `step65_motion` — L13051
- `step65_grid_multiref_motion_qa` — L13133
- `_sanitize_scene_for_state` — L13162
- `_save_pipeline_state` — L13181
- `_retime_after_audio_dub` — L13205
- `_build_voice_clone_hybrid_audio` — L13243
- `_build_dynamic_bgm` — L13381

---

### 第七步：拼接视频轨
Range: **L13425 – L13656** (232 lines)

**Functions:**
- `step7_concat` — L13426

---

### 第八步：生成 ASS 字幕
Range: **L13657 – L14448** (792 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L13780-14448 (669 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L13658
- `_word_timings_for_subtitle_align` — L13684
- `_align_segments_via_asr` — L13725
- `step8_subtitles` — L13768
- `_read_output_json` — L14180
- `_qa_file_pass` — L14191
- `_ass_has_dialogue` — L14198
- `_write_adsd_delivery_qa` — L14208
- `_write_bgm_only_qa` — L14337

---

### 第九步：最终合成
Range: **L14449 – L14694** (246 lines)

**Functions:**
- `step9_render` — L14450

---

### 第十步：推送 Telegram
Range: **L14695 – L16309** (1615 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L15795-16116 (322 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L16117-16121 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L16122-16185 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L16186-16231 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L16232-16309 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L15064
- `PANTONE_FALLBACK` — L15091
- `FESTIVAL_DATE_TAG` — L15204

**Functions:**
- `_generate_caption` — L14696
- `_overlay_title_on_cover` — L14934
- `_prepare_tg_photo` — L15044
- `_get_pantone_for_date` — L15094
- `_llm_bottom_note` — L15119
- `_get_bottom_note` — L15148
- `_get_date_tag` — L15226
- `_shrink_to_b64` — L15248
- `_llm_check_scenes_anomalies` — L15264
- `_llm_check_cover_unique` — L15317
- `_llm_check_cover_quality` — L15347
- `_try_almanac_cover` — L15389
- `_generate_cover_image` — L15560
- `_async_kickoff_cover_caption` — L15802
- `_await_async_cover_caption` — L15832
- `step10_deliver` — L15856

---

### 主流程
Range: **L16310 – L16487** (178 lines)

**Functions:**
- `_print_execution_plan` — L16311
- `main` — L16359

---
