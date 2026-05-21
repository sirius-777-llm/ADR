# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (15987 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-1915 (1794 lines · 56 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L1916-3681 (1766 lines · 23 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L3682-4783 (1102 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L4784-5335 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L5336-8758 (3423 lines · 73 fn · 6 sub)
- [`第 6.5 步：动态化（可选，--with-motion 开启）`](#第-6-5-步-动态化-可选---with-motion-开启) — L8759-12967 (4209 lines · 100 fn · 4 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L12968-13156 (189 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L13157-13948 (792 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L13949-14194 (246 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L14195-15809 (1615 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L15810-15987 (178 lines · 2 fn · 0 sub)

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
Range: **L1916 – L3681** (1766 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L2975-3681 (707 lines)

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
- `_sweep_speaker_field` — L2584
- `_adsd_immersion_qa_rewrite_turns` — L2638
- `_adsd_visual_contract` — L2696
- `step1_script` — L2748
- `_write_ads_retention_qa` — L3625

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L3682 – L4783** (1102 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L3757
- `_ADSD_POLICY_REWRITE_TERMS` — L3763
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L3854

**Functions:**
- `_openai_tts_fallback` — L3683
- `_edge_tts_fallback` — L3729
- `_sanitize_for_external_api` — L3772
- `_is_content_policy_error` — L3781
- `_rewrite_adsd_tts_text_for_policy` — L3795
- `_record_adsd_tts_rewrite` — L3835
- `_build_silence_mp3` — L3860
- `_audio_duration_seconds` — L3873
- `_text_to_audio_master_voice_timed` — L3885
- `_text_to_audio_master_voice` — L4010
- `step2_master_voice` — L4113
- `_tts_turn_to_audio` — L4241
- `_asr_verify_dialogue_audio` — L4303
- `_asr_verify_dialogue_turns` — L4365
- `_normalize_cn_number_token` — L4407
- `_compact_zh_text` — L4429
- `_write_adsd_asr_text_qa` — L4436
- `_write_adsd_speaker_focus_qa` — L4475
- `_write_adsd_gender_voice_qa` — L4535
- `step2_dialogue_voice` — L4588

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L4784 – L5335** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L4791-4913 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L4914-4948 (35 lines)
- _第二层：字符数插值_ — L4949-4973 (25 lines)
- _第三层：silencedetect 物理校准_ — L4974-5335 (362 lines)

**Functions:**
- `_detect_silences` — L4792
- `_calibrate_boundaries` — L4827
- `_enforce_monotonic` — L4861
- `_manual_override_segments` — L4873
- `_calc_sentence_boundaries` — L4894
- `step345_timeline` — L5005
- `_analyze_bgm_energy_cuts` — L5064
- `_snap_bgm_only_boundaries` — L5127
- `step345_bgm_only_timeline` — L5187

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L5336 – L8758** (3423 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L6422-6472 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L6473-6580 (108 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L6581-6875 (295 lines)
- _Speaker IP Card (2026-05-21)_ — L6876-8591 (1716 lines)
- _审批流程_ — L8592-8648 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L8649-8758 (110 lines)

**Top-level constants:**
- `CHARACTER_META_GRID_COSTUMES` — L6428
- `CHARACTER_META_GRID_POSES` — L6429
- `CHARACTER_META_GRID_SCENES` — L6430
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L6433

**Functions:**
- `_extract_img_url` — L5337
- `_extract_img_urls` — L5359
- `_extract_video_url` — L5392
- `_count_bands` — L5417
- `_detect_contact_sheet_like_image` — L5429
- `_guess_upload_mime` — L5483
- `_upload_to_weryai` — L5506
- `_send_for_approval` — L5538
- `_wait_approval` — L5602
- `_render_still_segment` — L5614
- `_scene_text_visual_alignment` — L5628
- `_write_text_visual_alignment_qa` — L5664
- `_scene_motion_action_plan` — L5687
- `_ensure_motion_action_plan` — L5741
- `_motion_action_block` — L5750
- `_motion_plan_for_qa` — L5778
- `_write_motion_action_plan_qa` — L5788
- `_write_motion_bridge_refs_qa` — L5818
- `_motion_bridge_ref_prompt` — L5825
- `generate_motion_bridge_refs_gpt_image2` — L5858
- `generate_image` — L5971
- `generate_storyboard_images_gpt_image2` — L6018
- `_storyboard_grid_aspect` — L6203
- `_storyboard_grid_cols_rows` — L6210
- `_storyboard_grid_prompt` — L6232
- `_storyboard_grid_prompt_limit` — L6270
- `_is_prompt_limit_response` — L6274
- `_production_storyboard_prompt` — L6280
- `_write_production_storyboard_page_qa` — L6314
- `_character_sheet_prompt` — L6324
- `_is_audit_blocked` — L6450
- `_paraphrase_sensitive_dialogue` — L6463
- `_topic_cache_dir` — L6477
- `_topic_cache_path` — L6483
- `_load_topic_decomposition_cache` — L6488
- `_save_topic_decomposition_cache` — L6498
- `_llm_topic_decomposition` — L6503
- `_llm_infer_meta_grid_template` — L6638
- `_resolve_meta_grid_template` — L6695
- `_infer_meta_grid_costume` — L6738
- `_infer_meta_grid_pose` — L6787
- `_adsd_meta_grid_call_prompt` — L6834
- `_migrate_speaker_ip` — L6882
- `_speaker_ips_dir` — L6907
- `_list_speaker_ips` — L6914
- `_match_speaker_ip` — L6928
- `_build_speaker_ip_context_for_script` — L6948
- `_ip_usage_stats` — L7004
- `_recommend_related_ips` — L7022
- `_save_speaker_ip` — L7047
- `_record_speaker_usage_history` — L7056
- `_format_speaker_usage_history_for_prompt` — L7103
- `_llm_infer_ip_skeleton` — L7121
- `_llm_pick_voice_asset_for_ip` — L7166
- `_auto_incubate_missing_ips` — L7214
- `_character_meta_grid_cache_dir` — L7298
- `_character_meta_grid_cache_path` — L7306
- `_character_meta_grid_path` — L7312
- `generate_character_meta_grid_gpt_image2` — L7318
- `_generate_all_character_meta_grids` — L7437
- `_write_character_sheet_qa` — L7478
- `generate_character_sheet_gpt_image2` — L7488
- `generate_production_storyboard_page_gpt_image2` — L7588
- `_qa_clean_storyboard_panel` — L7651
- `_crop_storyboard_grid_panels` — L7832
- `generate_storyboard_grid_gpt_image2` — L7879
- `_gpt_image2_direct_annotated_aspect` — L8110
- `_gpt_image2_direct_annotated_prompt` — L8117
- `generate_gpt_image2_direct_annotated_storyboards` — L8147
- `_llm_bgm_description` — L8248
- `_bgm_contains_vocals` — L8287
- `generate_bgm` — L8321
- `step6_parallel` — L8438

---

### 第 6.5 步：动态化（可选，--with-motion 开启）
Range: **L8759 – L12967** (4209 lines)

**Sub-sections:**
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L12709-12751 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L12752-12789 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回主音轨_ — L12790-12922 (133 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L12923-12967 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L8762
- `_motion_tasks_file` — L8829
- `_motion_qa_file` — L8833
- `_append_motion_qa` — L8837
- `_finalize_motion_qa` — L8861
- `_lip_sync_tasks_file` — L8945
- `_load_motion_tasks` — L8949
- `_save_motion_task` — L8959
- `_remove_motion_task` — L8967
- `_load_lip_sync_tasks` — L8974
- `_save_lip_sync_task` — L8984
- `_remove_lip_sync_task` — L8991
- `_video_visual_motion_qa` — L8998
- `_motion_output_qa` — L9070
- `_has_audio_stream` — L9115
- `_normalize_motion_video` — L9126
- `_motion_poll_and_download` — L9176
- `_build_motion_video_prompt` — L9227
- `_short_board_text` — L9257
- `_wrap_board_text` — L9264
- `_storyboard_font` — L9295
- `_draw_storyboard_arrow` — L9310
- `_build_annotated_storyboard_reference` — L9324
- `_plain_caption_text` — L9425
- `_werydance_caption_request` — L9433
- `_werydance_caption_instruction` — L9460
- `_werydance_negative_prompt` — L9472
- `_motion_reference_prompt` — L9490
- `_motion_audio_dub_prompt` — L9513
- `_motion_audio_dub_poll_and_download` — L9547
- `_try_motion_audio_dub_video` — L9612
- `_try_motion_reference_video` — L9747
- `_motion_one_scene` — L9863
- `_grid_multiref_tasks_file` — L9992
- `_previs_page_tasks_file` — L9996
- `_load_grid_multiref_tasks` — L10000
- `_load_previs_page_tasks` — L10010
- `_save_grid_multiref_task` — L10020
- `_save_previs_page_task` — L10027
- `_remove_grid_multiref_task` — L10034
- `_remove_previs_page_task` — L10041
- `_poll_video_task_download` — L10048
- `_grid_multiref_group_size` — L10097
- `_grid_multiref_duration` — L10105
- `_grid_multiref_segment_max_stretch` — L10121
- `_grid_multiref_prompt` — L10129
- `_write_grid_multiref_motion_qa` — L10177
- `_write_previs_page_motion_qa` — L10187
- `_write_storyboard_trailer_qa` — L10197
- `_write_character_trailer_qa` — L10207
- `_write_grid_multiref_segment_qa` — L10217
- `_motion_compare_record` — L10227
- `_write_storyboard_motion_compare_qa` — L10249
- `_scene_segment_duration` — L10285
- `_apply_grid_multiref_segments` — L10304
- `_previs_page_duration` — L10498
- `_previs_page_group_prompt` — L10508
- `_previs_page_groups` — L10534
- `_storyboard_trailer_duration` — L10549
- `_storyboard_trailer_prompt` — L10559
- `_character_trailer_max_shots` — L10587
- `_character_trailer_shot_duration` — L10595
- `_character_trailer_prompt` — L10609
- `_concat_character_trailer_segments` — L10624
- `_generate_character_trailer_motion` — L10663
- `_multi_trailer_prompt_for_group` — L10771
- `_generate_multi_trailer_segments` — L10794
- `_generate_storyboard_trailer_motion` — L10905
- `_generate_previs_page_motion_segments` — L10980
- `_generate_grid_multiref_motion_segments` — L11092
- `_grid_multiref_concat_groups` — L11262
- `_grid_multiref_concat_groups_partial` — L11279
- `_grid_multiref_concat_paths` — L11297
- `_lip_sync_slot_duration` — L11328
- `_adsd_lip_sync_prompt` — L11335
- `_adsd_broll_motion_prompt` — L11381
- `_adsd_action_b_motion_prompt` — L11423
- `_adsd_silent_b_motion_prompt` — L11460
- `_adsd_narrated_b_audio_dub_prompt` — L11495
- `_adsd_almighty_audio_dub_prompt` — L11539
- `_postprocess_lip_sync_segment` — L11580
- `_detect_audio_leading_silence` — L11648
- `_postprocess_audio_dub_segment` — L11670
- `_lips_change_repair_segment` — L11776
- `_load_lips_change_requested_turns` — L11861
- `_parse_turn_set` — L11878
- `_load_motion_voice_repair_turns` — L11900
- `_voice_assets_file` — L11912
- `_load_voice_assets` — L11919
- `_select_voice_asset_reference` — L11938
- `_lip_sync_poll_download_and_process` — L12004
- `_lip_sync_one_scene` — L12068
- `step66_adsd_lip_sync` — L12366
- `step65_motion` — L12599
- `step65_grid_multiref_motion_qa` — L12681
- `_sanitize_scene_for_state` — L12710
- `_save_pipeline_state` — L12729
- `_retime_after_audio_dub` — L12753
- `_build_voice_clone_hybrid_audio` — L12791
- `_build_dynamic_bgm` — L12924

---

### 第七步：拼接视频轨
Range: **L12968 – L13156** (189 lines)

**Functions:**
- `step7_concat` — L12969

---

### 第八步：生成 ASS 字幕
Range: **L13157 – L13948** (792 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L13280-13948 (669 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L13158
- `_word_timings_for_subtitle_align` — L13184
- `_align_segments_via_asr` — L13225
- `step8_subtitles` — L13268
- `_read_output_json` — L13680
- `_qa_file_pass` — L13691
- `_ass_has_dialogue` — L13698
- `_write_adsd_delivery_qa` — L13708
- `_write_bgm_only_qa` — L13837

---

### 第九步：最终合成
Range: **L13949 – L14194** (246 lines)

**Functions:**
- `step9_render` — L13950

---

### 第十步：推送 Telegram
Range: **L14195 – L15809** (1615 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L15295-15616 (322 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L15617-15621 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L15622-15685 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L15686-15731 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L15732-15809 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L14564
- `PANTONE_FALLBACK` — L14591
- `FESTIVAL_DATE_TAG` — L14704

**Functions:**
- `_generate_caption` — L14196
- `_overlay_title_on_cover` — L14434
- `_prepare_tg_photo` — L14544
- `_get_pantone_for_date` — L14594
- `_llm_bottom_note` — L14619
- `_get_bottom_note` — L14648
- `_get_date_tag` — L14726
- `_shrink_to_b64` — L14748
- `_llm_check_scenes_anomalies` — L14764
- `_llm_check_cover_unique` — L14817
- `_llm_check_cover_quality` — L14847
- `_try_almanac_cover` — L14889
- `_generate_cover_image` — L15060
- `_async_kickoff_cover_caption` — L15302
- `_await_async_cover_caption` — L15332
- `step10_deliver` — L15356

---

### 主流程
Range: **L15810 – L15987** (178 lines)

**Functions:**
- `_print_execution_plan` — L15811
- `main` — L15859

---
