# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (15896 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-1912 (1791 lines · 56 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L1913-3611 (1699 lines · 22 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L3612-4713 (1102 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L4714-5265 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L5266-8676 (3411 lines · 73 fn · 6 sub)
- [`第 6.5 步：动态化（可选，--with-motion 开启）`](#第-6-5-步-动态化-可选---with-motion-开启) — L8677-12881 (4205 lines · 100 fn · 4 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L12882-13070 (189 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L13071-13862 (792 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L13863-14103 (241 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L14104-15718 (1615 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L15719-15896 (178 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L1912** (1791 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L298-427 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L428-1040 (613 lines)
- _工具函数_ — L1041-1390 (350 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1391-1912 (522 lines)

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
- `VOICE_ASSET_AUDIO_DUB_EXPERIMENT` — L792
- `VOICE_ASSET_AUDIO_DUB_PARTIAL_OK` — L800
- `MOTION_VISUAL_QA` — L804
- `MOTION_VOICE_REPAIR` — L812
- `MOTION_VOICE_STRICT_LOCK` — L817
- `WERYDANCE_CAPTIONS` — L822
- `ADSD_ONSITE_POV_MODE` — L834
- `ADSD_LIPS_CHANGE_REPAIR` — L839
- `ADSD_LIPS_CHANGE_ALL` — L844
- `ADS_REPORTER_MODE` — L855
- `ADS_STORYBOARD_FLOW_DEFAULT` — L872
- `ADS_RETENTION_MODE` — L885
- `ADSD_MODE_NAME` — L891
- `EMOTION_STYLE` — L1020
- `EMOTION_STYLE_BRIGHT` — L1032
- `_TG_DASHBOARD_STAGES` — L1054
- `_TG_NOISY_PATTERNS` — L1069
- `_TG_IMMEDIATE_PATTERNS` — L1087
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1320
- `_TOPIC_MODIFIERS` — L1744
- `_TONE_PANTONE_OVERRIDE` — L1761

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
- `_resolve_turn_type` — L484
- `_is_silent_b` — L499
- `_is_narrated_b` — L503
- `_is_a_roll` — L507
- `_is_action_b` — L511
- `_voice_asset_id_for_speaker` — L515
- `_llm_assign_voice_assets` — L543
- `_apply_llm_voice_assignment` — L667
- `log` — L1042
- `_tg_send_raw` — L1110
- `_tg_matches` — L1126
- `_tg_summarize` — L1130
- `_tg_dashboard_stage_for` — L1137
- `_tg_progress_bar` — L1145
- `_tg_dashboard_text` — L1151
- `_tg_dashboard_update` — L1169
- `_tg_maybe_digest` — L1206
- `tg` — L1221
- `_wait_image_submit_slot` — L1270
- `_wait_motion_submit_slot` — L1283
- `_is_rate_limited_error` — L1296
- `_is_rate_limited_response` — L1306
- `_inject_image2_quality_suffix` — L1328
- `submit_text_to_image` — L1342
- `req_post` — L1372
- `req_get` — L1386
- `_tg_probe_send` — L1394
- `_tg_probe_delete` — L1414
- `_tg_upload_with_probe_gap` — L1427
- `poll` — L1467
- `poll_podcast` — L1492
- `poll_task_status` — L1514
- `poll_storyboard_task` — L1536
- `chat` — L1562
- `pick_image_model` — L1590
- `detect_topic_meta` — L1615
- `_topic_culture_guard` — L1665
- `_write_cultural_visual_qa` — L1691
- `is_1919_global_topic` — L1738
- `_strip_topic_modifiers` — L1749
- `apply_1919_global_guardrails` — L1767
- `build_1919_global_cover_prompt` — L1796
- `build_shot_blueprint` — L1825
- `ffprobe_duration` — L1851
- `ffprobe_video_size` — L1862
- `_video_decode_probe` — L1883
- `ffmpeg` — L1901

---

### 第一步：双导演生成剧本
Range: **L1913 – L3611** (1699 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L2905-3611 (707 lines)

**Functions:**
- `_extract_json_array` — L1914
- `_extract_json_object` — L1924
- `_voice_for_speaker` — L1934
- `_adsd_gender_from_voice` — L1970
- `_adsd_infer_gender_from_speaker` — L1978
- `_adsd_gender_lock_phrase` — L1987
- `_adsd_visual_subject_has_gender_conflict` — L2002
- `_adsd_default_roles` — L2014
- `_adsd_allows_media_role` — L2019
- `_adsd_role_candidates` — L2027
- `_adsd_dialogue_shape` — L2050
- `_finalize_adsd_turns` — L2059
- `_parse_adsd_override_turns` — L2093
- `_parse_timecode_seconds` — L2184
- `_clean_override_line_text` — L2193
- `_parse_override_script_text` — L2199
- `_adsd_pov_contract` — L2233
- `_generate_adsd_dialogue_turns` — L2243
- `_adsd_immersion_qa_rewrite_turns` — L2568
- `_adsd_visual_contract` — L2626
- `step1_script` — L2678
- `_write_ads_retention_qa` — L3555

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L3612 – L4713** (1102 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L3687
- `_ADSD_POLICY_REWRITE_TERMS` — L3693
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L3784

**Functions:**
- `_openai_tts_fallback` — L3613
- `_edge_tts_fallback` — L3659
- `_sanitize_for_external_api` — L3702
- `_is_content_policy_error` — L3711
- `_rewrite_adsd_tts_text_for_policy` — L3725
- `_record_adsd_tts_rewrite` — L3765
- `_build_silence_mp3` — L3790
- `_audio_duration_seconds` — L3803
- `_text_to_audio_master_voice_timed` — L3815
- `_text_to_audio_master_voice` — L3940
- `step2_master_voice` — L4043
- `_tts_turn_to_audio` — L4171
- `_asr_verify_dialogue_audio` — L4233
- `_asr_verify_dialogue_turns` — L4295
- `_normalize_cn_number_token` — L4337
- `_compact_zh_text` — L4359
- `_write_adsd_asr_text_qa` — L4366
- `_write_adsd_speaker_focus_qa` — L4405
- `_write_adsd_gender_voice_qa` — L4465
- `step2_dialogue_voice` — L4518

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L4714 – L5265** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L4721-4843 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L4844-4878 (35 lines)
- _第二层：字符数插值_ — L4879-4903 (25 lines)
- _第三层：silencedetect 物理校准_ — L4904-5265 (362 lines)

**Functions:**
- `_detect_silences` — L4722
- `_calibrate_boundaries` — L4757
- `_enforce_monotonic` — L4791
- `_manual_override_segments` — L4803
- `_calc_sentence_boundaries` — L4824
- `step345_timeline` — L4935
- `_analyze_bgm_energy_cuts` — L4994
- `_snap_bgm_only_boundaries` — L5057
- `step345_bgm_only_timeline` — L5117

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L5266 – L8676** (3411 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L6352-6402 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L6403-6510 (108 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L6511-6793 (283 lines)
- _Speaker IP Card (2026-05-21)_ — L6794-8509 (1716 lines)
- _审批流程_ — L8510-8566 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L8567-8676 (110 lines)

**Top-level constants:**
- `CHARACTER_META_GRID_COSTUMES` — L6358
- `CHARACTER_META_GRID_POSES` — L6359
- `CHARACTER_META_GRID_SCENES` — L6360
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L6363

**Functions:**
- `_extract_img_url` — L5267
- `_extract_img_urls` — L5289
- `_extract_video_url` — L5322
- `_count_bands` — L5347
- `_detect_contact_sheet_like_image` — L5359
- `_guess_upload_mime` — L5413
- `_upload_to_weryai` — L5436
- `_send_for_approval` — L5468
- `_wait_approval` — L5532
- `_render_still_segment` — L5544
- `_scene_text_visual_alignment` — L5558
- `_write_text_visual_alignment_qa` — L5594
- `_scene_motion_action_plan` — L5617
- `_ensure_motion_action_plan` — L5671
- `_motion_action_block` — L5680
- `_motion_plan_for_qa` — L5708
- `_write_motion_action_plan_qa` — L5718
- `_write_motion_bridge_refs_qa` — L5748
- `_motion_bridge_ref_prompt` — L5755
- `generate_motion_bridge_refs_gpt_image2` — L5788
- `generate_image` — L5901
- `generate_storyboard_images_gpt_image2` — L5948
- `_storyboard_grid_aspect` — L6133
- `_storyboard_grid_cols_rows` — L6140
- `_storyboard_grid_prompt` — L6162
- `_storyboard_grid_prompt_limit` — L6200
- `_is_prompt_limit_response` — L6204
- `_production_storyboard_prompt` — L6210
- `_write_production_storyboard_page_qa` — L6244
- `_character_sheet_prompt` — L6254
- `_is_audit_blocked` — L6380
- `_paraphrase_sensitive_dialogue` — L6393
- `_topic_cache_dir` — L6407
- `_topic_cache_path` — L6413
- `_load_topic_decomposition_cache` — L6418
- `_save_topic_decomposition_cache` — L6428
- `_llm_topic_decomposition` — L6433
- `_llm_infer_meta_grid_template` — L6568
- `_resolve_meta_grid_template` — L6625
- `_infer_meta_grid_costume` — L6668
- `_infer_meta_grid_pose` — L6717
- `_adsd_meta_grid_call_prompt` — L6764
- `_migrate_speaker_ip` — L6800
- `_speaker_ips_dir` — L6825
- `_list_speaker_ips` — L6832
- `_match_speaker_ip` — L6846
- `_build_speaker_ip_context_for_script` — L6866
- `_ip_usage_stats` — L6922
- `_recommend_related_ips` — L6940
- `_save_speaker_ip` — L6965
- `_record_speaker_usage_history` — L6974
- `_format_speaker_usage_history_for_prompt` — L7021
- `_llm_infer_ip_skeleton` — L7039
- `_llm_pick_voice_asset_for_ip` — L7084
- `_auto_incubate_missing_ips` — L7132
- `_character_meta_grid_cache_dir` — L7216
- `_character_meta_grid_cache_path` — L7224
- `_character_meta_grid_path` — L7230
- `generate_character_meta_grid_gpt_image2` — L7236
- `_generate_all_character_meta_grids` — L7355
- `_write_character_sheet_qa` — L7396
- `generate_character_sheet_gpt_image2` — L7406
- `generate_production_storyboard_page_gpt_image2` — L7506
- `_qa_clean_storyboard_panel` — L7569
- `_crop_storyboard_grid_panels` — L7750
- `generate_storyboard_grid_gpt_image2` — L7797
- `_gpt_image2_direct_annotated_aspect` — L8028
- `_gpt_image2_direct_annotated_prompt` — L8035
- `generate_gpt_image2_direct_annotated_storyboards` — L8065
- `_llm_bgm_description` — L8166
- `_bgm_contains_vocals` — L8205
- `generate_bgm` — L8239
- `step6_parallel` — L8356

---

### 第 6.5 步：动态化（可选，--with-motion 开启）
Range: **L8677 – L12881** (4205 lines)

**Sub-sections:**
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L12623-12665 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L12666-12703 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回主音轨_ — L12704-12836 (133 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L12837-12881 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L8680
- `_motion_tasks_file` — L8747
- `_motion_qa_file` — L8751
- `_append_motion_qa` — L8755
- `_finalize_motion_qa` — L8779
- `_lip_sync_tasks_file` — L8863
- `_load_motion_tasks` — L8867
- `_save_motion_task` — L8877
- `_remove_motion_task` — L8885
- `_load_lip_sync_tasks` — L8892
- `_save_lip_sync_task` — L8902
- `_remove_lip_sync_task` — L8909
- `_video_visual_motion_qa` — L8916
- `_motion_output_qa` — L8988
- `_has_audio_stream` — L9033
- `_normalize_motion_video` — L9044
- `_motion_poll_and_download` — L9094
- `_build_motion_video_prompt` — L9145
- `_short_board_text` — L9175
- `_wrap_board_text` — L9182
- `_storyboard_font` — L9213
- `_draw_storyboard_arrow` — L9228
- `_build_annotated_storyboard_reference` — L9242
- `_plain_caption_text` — L9343
- `_werydance_caption_request` — L9351
- `_werydance_caption_instruction` — L9378
- `_werydance_negative_prompt` — L9390
- `_motion_reference_prompt` — L9404
- `_motion_audio_dub_prompt` — L9427
- `_motion_audio_dub_poll_and_download` — L9461
- `_try_motion_audio_dub_video` — L9526
- `_try_motion_reference_video` — L9661
- `_motion_one_scene` — L9777
- `_grid_multiref_tasks_file` — L9906
- `_previs_page_tasks_file` — L9910
- `_load_grid_multiref_tasks` — L9914
- `_load_previs_page_tasks` — L9924
- `_save_grid_multiref_task` — L9934
- `_save_previs_page_task` — L9941
- `_remove_grid_multiref_task` — L9948
- `_remove_previs_page_task` — L9955
- `_poll_video_task_download` — L9962
- `_grid_multiref_group_size` — L10011
- `_grid_multiref_duration` — L10019
- `_grid_multiref_segment_max_stretch` — L10035
- `_grid_multiref_prompt` — L10043
- `_write_grid_multiref_motion_qa` — L10091
- `_write_previs_page_motion_qa` — L10101
- `_write_storyboard_trailer_qa` — L10111
- `_write_character_trailer_qa` — L10121
- `_write_grid_multiref_segment_qa` — L10131
- `_motion_compare_record` — L10141
- `_write_storyboard_motion_compare_qa` — L10163
- `_scene_segment_duration` — L10199
- `_apply_grid_multiref_segments` — L10218
- `_previs_page_duration` — L10412
- `_previs_page_group_prompt` — L10422
- `_previs_page_groups` — L10448
- `_storyboard_trailer_duration` — L10463
- `_storyboard_trailer_prompt` — L10473
- `_character_trailer_max_shots` — L10501
- `_character_trailer_shot_duration` — L10509
- `_character_trailer_prompt` — L10523
- `_concat_character_trailer_segments` — L10538
- `_generate_character_trailer_motion` — L10577
- `_multi_trailer_prompt_for_group` — L10685
- `_generate_multi_trailer_segments` — L10708
- `_generate_storyboard_trailer_motion` — L10819
- `_generate_previs_page_motion_segments` — L10894
- `_generate_grid_multiref_motion_segments` — L11006
- `_grid_multiref_concat_groups` — L11176
- `_grid_multiref_concat_groups_partial` — L11193
- `_grid_multiref_concat_paths` — L11211
- `_lip_sync_slot_duration` — L11242
- `_adsd_lip_sync_prompt` — L11249
- `_adsd_broll_motion_prompt` — L11295
- `_adsd_action_b_motion_prompt` — L11337
- `_adsd_silent_b_motion_prompt` — L11374
- `_adsd_narrated_b_audio_dub_prompt` — L11409
- `_adsd_almighty_audio_dub_prompt` — L11453
- `_postprocess_lip_sync_segment` — L11494
- `_detect_audio_leading_silence` — L11562
- `_postprocess_audio_dub_segment` — L11584
- `_lips_change_repair_segment` — L11690
- `_load_lips_change_requested_turns` — L11775
- `_parse_turn_set` — L11792
- `_load_motion_voice_repair_turns` — L11814
- `_voice_assets_file` — L11826
- `_load_voice_assets` — L11833
- `_select_voice_asset_reference` — L11852
- `_lip_sync_poll_download_and_process` — L11918
- `_lip_sync_one_scene` — L11982
- `step66_adsd_lip_sync` — L12280
- `step65_motion` — L12513
- `step65_grid_multiref_motion_qa` — L12595
- `_sanitize_scene_for_state` — L12624
- `_save_pipeline_state` — L12643
- `_retime_after_audio_dub` — L12667
- `_build_voice_clone_hybrid_audio` — L12705
- `_build_dynamic_bgm` — L12838

---

### 第七步：拼接视频轨
Range: **L12882 – L13070** (189 lines)

**Functions:**
- `step7_concat` — L12883

---

### 第八步：生成 ASS 字幕
Range: **L13071 – L13862** (792 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L13194-13862 (669 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L13072
- `_word_timings_for_subtitle_align` — L13098
- `_align_segments_via_asr` — L13139
- `step8_subtitles` — L13182
- `_read_output_json` — L13594
- `_qa_file_pass` — L13605
- `_ass_has_dialogue` — L13612
- `_write_adsd_delivery_qa` — L13622
- `_write_bgm_only_qa` — L13751

---

### 第九步：最终合成
Range: **L13863 – L14103** (241 lines)

**Functions:**
- `step9_render` — L13864

---

### 第十步：推送 Telegram
Range: **L14104 – L15718** (1615 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L15204-15525 (322 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L15526-15530 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L15531-15594 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L15595-15640 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L15641-15718 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L14473
- `PANTONE_FALLBACK` — L14500
- `FESTIVAL_DATE_TAG` — L14613

**Functions:**
- `_generate_caption` — L14105
- `_overlay_title_on_cover` — L14343
- `_prepare_tg_photo` — L14453
- `_get_pantone_for_date` — L14503
- `_llm_bottom_note` — L14528
- `_get_bottom_note` — L14557
- `_get_date_tag` — L14635
- `_shrink_to_b64` — L14657
- `_llm_check_scenes_anomalies` — L14673
- `_llm_check_cover_unique` — L14726
- `_llm_check_cover_quality` — L14756
- `_try_almanac_cover` — L14798
- `_generate_cover_image` — L14969
- `_async_kickoff_cover_caption` — L15211
- `_await_async_cover_caption` — L15241
- `step10_deliver` — L15265

---

### 主流程
Range: **L15719 – L15896** (178 lines)

**Functions:**
- `_print_execution_plan` — L15720
- `main` — L15768

---
