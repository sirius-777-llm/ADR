# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (16890 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-1987 (1866 lines · 58 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L1988-4148 (2161 lines · 29 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L4149-5252 (1104 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L5253-5804 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L5805-9544 (3740 lines · 80 fn · 6 sub)
- [`第 6.5 步：动态化（可选，--with-motion 开启）`](#第-6-5-步-动态化-可选---with-motion-开启) — L9545-13827 (4283 lines · 100 fn · 4 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L13828-14059 (232 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L14060-14851 (792 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L14852-15097 (246 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L15098-16712 (1615 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L16713-16890 (178 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L1987** (1866 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L313-442 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L443-1115 (673 lines)
- _工具函数_ — L1116-1465 (350 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1466-1987 (522 lines)

**Top-level constants:**
- `HEADERS` — L135
- `VIDEO_FORMAT` — L143
- `ADS_DIALOGUE_MODE_EARLY_CHECK` — L150
- `WITH_MOTION` — L158
- `BGM_ONLY_REQUESTED` — L166
- `ADS_DIALOGUE_MODE` — L173
- `GPT_IMAGE2_STORYBOARD` — L182
- `STORYBOARD_REFERENCE_MOTION` — L186
- `STORYBOARD_ANNOTATED_MOTION` — L190
- `GPT_IMAGE2_DIRECT_ANNOTATED_STORYBOARD` — L194
- `GPT_IMAGE2_STORYBOARD_GRID` — L199
- `ADSD_STORYBOARD_GRID` — L207
- `ADS_CHARACTER_SHEET_REQUESTED` — L213
- `STORYBOARD_GRID_MULTIREF_MOTION` — L217
- `STORYBOARD_GRID_MULTIREF_SEGMENTS` — L221
- `STORYBOARD_GRID_MULTIREF_MAIN` — L227
- `PREVIS_PAGE_MOTION` — L233
- `STORYBOARD_TRAILER_MODE` — L237
- `MOTION_ACTION_STORYBOARD` — L242
- `MOTION_BRIDGE_REFS` — L246
- `CHARACTER_TRAILER_MODE` — L250
- `STORYBOARD_TRAILER_MAIN` — L258
- `ADSD_LIP_SYNC_EXPERIMENT` — L271
- `ADSD_RICH_MOTION_PROMPT` — L279
- `ADSD_LLM_VOICE_ASSIGN` — L287
- `ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT` — L291
- `ADSD_CONSECUTIVE_SPEAKER_BATCHING` — L305
- `ADSD_GENDER_FALLBACK_VOICE_ASSET` — L316
- `SILENT_B_SPEAKERS` — L448
- `_PODCAST_TO_VOICE_ASSET_MAP` — L811
- `_VOICE_ASSET_FORBIDDEN_FLAGS` — L829
- `VOICE_ASSET_AUDIO_DUB_EXPERIMENT` — L867
- `VOICE_ASSET_AUDIO_DUB_PARTIAL_OK` — L875
- `MOTION_VISUAL_QA` — L879
- `MOTION_VOICE_REPAIR` — L887
- `MOTION_VOICE_STRICT_LOCK` — L892
- `WERYDANCE_CAPTIONS` — L897
- `ADSD_ONSITE_POV_MODE` — L909
- `ADSD_LIPS_CHANGE_REPAIR` — L914
- `ADSD_LIPS_CHANGE_ALL` — L919
- `ADS_REPORTER_MODE` — L930
- `ADS_STORYBOARD_FLOW_DEFAULT` — L947
- `ADS_RETENTION_MODE` — L960
- `ADSD_MODE_NAME` — L966
- `EMOTION_STYLE` — L1095
- `EMOTION_STYLE_BRIGHT` — L1107
- `_TG_DASHBOARD_STAGES` — L1129
- `_TG_NOISY_PATTERNS` — L1144
- `_TG_IMMEDIATE_PATTERNS` — L1162
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1395
- `_TOPIC_MODIFIERS` — L1819
- `_TONE_PANTONE_OVERRIDE` — L1836

**Functions:**
- `_is_action_scene` — L325
- `_needs_storyboard_flow_character_sheet` — L336
- `_wuxia_action_panel_prompt` — L365
- `_action_motion_fragment` — L387
- `_infer_emotion_from_text` — L402
- `_emotion_expression_phrase` — L417
- `_infer_needs_lip_sync` — L424
- `_infer_turn_type` — L451
- `_is_action_shout` — L476
- `_resolve_turn_type` — L502
- `_is_silent_b` — L517
- `_is_narrated_b` — L521
- `_is_a_roll` — L525
- `_is_action_b` — L529
- `_voice_asset_id_for_speaker` — L533
- `_llm_assign_voice_assets` — L561
- `_apply_llm_voice_assignment` — L685
- `_voice_asset_is_speech_safe` — L836
- `_podcast_id_to_voice_asset` — L842
- `log` — L1117
- `_tg_send_raw` — L1185
- `_tg_matches` — L1201
- `_tg_summarize` — L1205
- `_tg_dashboard_stage_for` — L1212
- `_tg_progress_bar` — L1220
- `_tg_dashboard_text` — L1226
- `_tg_dashboard_update` — L1244
- `_tg_maybe_digest` — L1281
- `tg` — L1296
- `_wait_image_submit_slot` — L1345
- `_wait_motion_submit_slot` — L1358
- `_is_rate_limited_error` — L1371
- `_is_rate_limited_response` — L1381
- `_inject_image2_quality_suffix` — L1403
- `submit_text_to_image` — L1417
- `req_post` — L1447
- `req_get` — L1461
- `_tg_probe_send` — L1469
- `_tg_probe_delete` — L1489
- `_tg_upload_with_probe_gap` — L1502
- `poll` — L1542
- `poll_podcast` — L1567
- `poll_task_status` — L1589
- `poll_storyboard_task` — L1611
- `chat` — L1637
- `pick_image_model` — L1665
- `detect_topic_meta` — L1690
- `_topic_culture_guard` — L1740
- `_write_cultural_visual_qa` — L1766
- `is_1919_global_topic` — L1813
- `_strip_topic_modifiers` — L1824
- `apply_1919_global_guardrails` — L1842
- `build_1919_global_cover_prompt` — L1871
- `build_shot_blueprint` — L1900
- `ffprobe_duration` — L1926
- `ffprobe_video_size` — L1937
- `_video_decode_probe` — L1958
- `ffmpeg` — L1976

---

### 第一步：双导演生成剧本
Range: **L1988 – L4148** (2161 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L3420-4148 (729 lines)

**Functions:**
- `_extract_json_array` — L1989
- `_extract_json_object` — L1999
- `_voice_for_speaker` — L2009
- `_adsd_gender_from_voice` — L2045
- `_adsd_infer_gender_from_speaker` — L2053
- `_adsd_gender_lock_phrase` — L2062
- `_adsd_visual_subject_has_gender_conflict` — L2077
- `_adsd_default_roles` — L2089
- `_adsd_allows_media_role` — L2094
- `_adsd_role_candidates` — L2102
- `_adsd_dialogue_shape` — L2125
- `_finalize_adsd_turns` — L2134
- `_parse_adsd_override_turns` — L2168
- `_parse_timecode_seconds` — L2259
- `_clean_override_line_text` — L2268
- `_parse_override_script_text` — L2274
- `_adsd_pov_contract` — L2308
- `_load_audit_blacklist_block` — L2321
- `_generate_adsd_dialogue_turns` — L2359
- `_broll_rhythm_reviewer` — L2782
- `_sweep_speaker_field` — L2889
- `_should_run_immersion_qa` — L2949
- `_adsd_immersion_qa_rewrite_turns` — L2972
- `_adsd_visual_contract` — L3036
- `_parse_risk_score` — L3088
- `_check_high_risk_hard_abort` — L3117
- `_maybe_neutralize_topic` — L3144
- `step1_script` — L3183
- `_write_ads_retention_qa` — L4092

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L4149 – L5252** (1104 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L4224
- `_ADSD_POLICY_REWRITE_TERMS` — L4230
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L4321

**Functions:**
- `_openai_tts_fallback` — L4150
- `_edge_tts_fallback` — L4196
- `_sanitize_for_external_api` — L4239
- `_is_content_policy_error` — L4248
- `_rewrite_adsd_tts_text_for_policy` — L4262
- `_record_adsd_tts_rewrite` — L4302
- `_build_silence_mp3` — L4327
- `_audio_duration_seconds` — L4340
- `_text_to_audio_master_voice_timed` — L4352
- `_text_to_audio_master_voice` — L4477
- `step2_master_voice` — L4580
- `_tts_turn_to_audio` — L4708
- `_asr_verify_dialogue_audio` — L4772
- `_asr_verify_dialogue_turns` — L4834
- `_normalize_cn_number_token` — L4876
- `_compact_zh_text` — L4898
- `_write_adsd_asr_text_qa` — L4905
- `_write_adsd_speaker_focus_qa` — L4944
- `_write_adsd_gender_voice_qa` — L5004
- `step2_dialogue_voice` — L5057

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L5253 – L5804** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L5260-5382 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L5383-5417 (35 lines)
- _第二层：字符数插值_ — L5418-5442 (25 lines)
- _第三层：silencedetect 物理校准_ — L5443-5804 (362 lines)

**Functions:**
- `_detect_silences` — L5261
- `_calibrate_boundaries` — L5296
- `_enforce_monotonic` — L5330
- `_manual_override_segments` — L5342
- `_calc_sentence_boundaries` — L5363
- `step345_timeline` — L5474
- `_analyze_bgm_energy_cuts` — L5533
- `_snap_bgm_only_boundaries` — L5596
- `step345_bgm_only_timeline` — L5656

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L5805 – L9544** (3740 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L6994-7044 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L7045-7185 (141 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L7186-7620 (435 lines)
- _Speaker IP Card (2026-05-21)_ — L7621-9377 (1757 lines)
- _审批流程_ — L9378-9434 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L9435-9544 (110 lines)

**Top-level constants:**
- `CHARACTER_META_GRID_COSTUMES` — L7000
- `CHARACTER_META_GRID_POSES` — L7001
- `CHARACTER_META_GRID_SCENES` — L7002
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L7005

**Functions:**
- `_extract_img_url` — L5806
- `_extract_img_urls` — L5828
- `_extract_video_url` — L5861
- `_count_bands` — L5886
- `_detect_contact_sheet_like_image` — L5898
- `_file_sha256` — L5959
- `_load_upload_cache` — L5972
- `_save_upload_cache` — L5981
- `_cached_upload_url` — L5989
- `_store_upload_url` — L6006
- `_guess_upload_mime` — L6016
- `_upload_to_weryai` — L6039
- `_send_for_approval` — L6093
- `_wait_approval` — L6157
- `_render_still_segment` — L6169
- `_scene_text_visual_alignment` — L6200
- `_write_text_visual_alignment_qa` — L6236
- `_scene_motion_action_plan` — L6259
- `_ensure_motion_action_plan` — L6313
- `_motion_action_block` — L6322
- `_motion_plan_for_qa` — L6350
- `_write_motion_action_plan_qa` — L6360
- `_write_motion_bridge_refs_qa` — L6390
- `_motion_bridge_ref_prompt` — L6397
- `generate_motion_bridge_refs_gpt_image2` — L6430
- `generate_image` — L6543
- `generate_storyboard_images_gpt_image2` — L6590
- `_storyboard_grid_aspect` — L6775
- `_storyboard_grid_cols_rows` — L6782
- `_storyboard_grid_prompt` — L6804
- `_storyboard_grid_prompt_limit` — L6842
- `_is_prompt_limit_response` — L6846
- `_production_storyboard_prompt` — L6852
- `_write_production_storyboard_page_qa` — L6886
- `_character_sheet_prompt` — L6896
- `_is_audit_blocked` — L7022
- `_paraphrase_sensitive_dialogue` — L7035
- `_topic_cache_dir` — L7049
- `_topic_cache_path` — L7055
- `_load_topic_decomposition_cache` — L7068
- `_save_topic_decomposition_cache` — L7086
- `_llm_topic_decomposition` — L7092
- `_director_route_block` — L7239
- `_llm_infer_meta_grid_template` — L7309
- `_resolve_meta_grid_template` — L7366
- `_infer_meta_grid_costume` — L7409
- `_infer_meta_grid_pose` — L7458
- `_adsd_meta_grid_call_prompt` — L7505
- `_meta_grid_panel_index` — L7547
- `_migrate_speaker_ip` — L7627
- `_speaker_ips_dir` — L7652
- `_list_speaker_ips` — L7659
- `_match_speaker_ip` — L7673
- `_build_speaker_ip_context_for_script` — L7693
- `_ip_usage_stats` — L7749
- `_recommend_related_ips` — L7767
- `_save_speaker_ip` — L7792
- `_record_speaker_usage_history` — L7801
- `_format_speaker_usage_history_for_prompt` — L7848
- `_llm_infer_ip_skeleton` — L7866
- `_llm_pick_voice_asset_for_ip` — L7911
- `_auto_incubate_missing_ips` — L7959
- `_character_meta_grid_cache_dir` — L8043
- `_character_meta_grid_cache_path` — L8051
- `_character_meta_grid_path` — L8059
- `generate_character_meta_grid_gpt_image2` — L8065
- `_generate_all_character_meta_grids` — L8223
- `_write_character_sheet_qa` — L8264
- `generate_character_sheet_gpt_image2` — L8274
- `generate_production_storyboard_page_gpt_image2` — L8374
- `_qa_clean_storyboard_panel` — L8437
- `_crop_storyboard_grid_panels` — L8618
- `generate_storyboard_grid_gpt_image2` — L8665
- `_gpt_image2_direct_annotated_aspect` — L8896
- `_gpt_image2_direct_annotated_prompt` — L8903
- `generate_gpt_image2_direct_annotated_storyboards` — L8933
- `_llm_bgm_description` — L9034
- `_bgm_contains_vocals` — L9073
- `generate_bgm` — L9107
- `step6_parallel` — L9224

---

### 第 6.5 步：动态化（可选，--with-motion 开启）
Range: **L9545 – L13827** (4283 lines)

**Sub-sections:**
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L13564-13606 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L13607-13644 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回主音轨_ — L13645-13782 (138 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L13783-13827 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L9548
- `_motion_tasks_file` — L9615
- `_motion_qa_file` — L9619
- `_append_motion_qa` — L9623
- `_finalize_motion_qa` — L9647
- `_lip_sync_tasks_file` — L9731
- `_load_motion_tasks` — L9735
- `_save_motion_task` — L9745
- `_remove_motion_task` — L9753
- `_load_lip_sync_tasks` — L9760
- `_save_lip_sync_task` — L9770
- `_remove_lip_sync_task` — L9777
- `_video_visual_motion_qa` — L9784
- `_motion_output_qa` — L9856
- `_has_audio_stream` — L9901
- `_normalize_motion_video` — L9912
- `_motion_poll_and_download` — L9962
- `_build_motion_video_prompt` — L10013
- `_short_board_text` — L10043
- `_wrap_board_text` — L10050
- `_storyboard_font` — L10081
- `_draw_storyboard_arrow` — L10096
- `_build_annotated_storyboard_reference` — L10110
- `_plain_caption_text` — L10211
- `_werydance_caption_request` — L10219
- `_werydance_caption_instruction` — L10246
- `_werydance_negative_prompt` — L10258
- `_motion_reference_prompt` — L10276
- `_motion_audio_dub_prompt` — L10299
- `_motion_audio_dub_poll_and_download` — L10333
- `_try_motion_audio_dub_video` — L10398
- `_try_motion_reference_video` — L10533
- `_motion_one_scene` — L10649
- `_grid_multiref_tasks_file` — L10778
- `_previs_page_tasks_file` — L10782
- `_load_grid_multiref_tasks` — L10786
- `_load_previs_page_tasks` — L10796
- `_save_grid_multiref_task` — L10806
- `_save_previs_page_task` — L10813
- `_remove_grid_multiref_task` — L10820
- `_remove_previs_page_task` — L10827
- `_poll_video_task_download` — L10834
- `_grid_multiref_group_size` — L10883
- `_grid_multiref_duration` — L10891
- `_grid_multiref_segment_max_stretch` — L10907
- `_grid_multiref_prompt` — L10915
- `_write_grid_multiref_motion_qa` — L10963
- `_write_previs_page_motion_qa` — L10973
- `_write_storyboard_trailer_qa` — L10983
- `_write_character_trailer_qa` — L10993
- `_write_grid_multiref_segment_qa` — L11003
- `_motion_compare_record` — L11013
- `_write_storyboard_motion_compare_qa` — L11035
- `_scene_segment_duration` — L11071
- `_apply_grid_multiref_segments` — L11090
- `_previs_page_duration` — L11284
- `_previs_page_group_prompt` — L11294
- `_previs_page_groups` — L11320
- `_storyboard_trailer_duration` — L11335
- `_storyboard_trailer_prompt` — L11345
- `_character_trailer_max_shots` — L11373
- `_character_trailer_shot_duration` — L11381
- `_character_trailer_prompt` — L11395
- `_concat_character_trailer_segments` — L11410
- `_generate_character_trailer_motion` — L11449
- `_multi_trailer_prompt_for_group` — L11557
- `_generate_multi_trailer_segments` — L11580
- `_generate_storyboard_trailer_motion` — L11691
- `_generate_previs_page_motion_segments` — L11766
- `_generate_grid_multiref_motion_segments` — L11878
- `_grid_multiref_concat_groups` — L12048
- `_grid_multiref_concat_groups_partial` — L12065
- `_grid_multiref_concat_paths` — L12083
- `_lip_sync_slot_duration` — L12114
- `_adsd_lip_sync_prompt` — L12121
- `_adsd_broll_motion_prompt` — L12167
- `_adsd_action_b_motion_prompt` — L12209
- `_adsd_silent_b_motion_prompt` — L12255
- `_adsd_narrated_b_audio_dub_prompt` — L12290
- `_adsd_almighty_audio_dub_prompt` — L12334
- `_postprocess_lip_sync_segment` — L12375
- `_detect_audio_leading_silence` — L12443
- `_postprocess_audio_dub_segment` — L12465
- `_lips_change_repair_segment` — L12576
- `_load_lips_change_requested_turns` — L12661
- `_parse_turn_set` — L12678
- `_load_motion_voice_repair_turns` — L12700
- `_voice_assets_file` — L12712
- `_load_voice_assets` — L12719
- `_select_voice_asset_reference` — L12738
- `_lip_sync_poll_download_and_process` — L12804
- `_lip_sync_one_scene` — L12872
- `step66_adsd_lip_sync` — L13196
- `step65_motion` — L13454
- `step65_grid_multiref_motion_qa` — L13536
- `_sanitize_scene_for_state` — L13565
- `_save_pipeline_state` — L13584
- `_retime_after_audio_dub` — L13608
- `_build_voice_clone_hybrid_audio` — L13646
- `_build_dynamic_bgm` — L13784

---

### 第七步：拼接视频轨
Range: **L13828 – L14059** (232 lines)

**Functions:**
- `step7_concat` — L13829

---

### 第八步：生成 ASS 字幕
Range: **L14060 – L14851** (792 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L14183-14851 (669 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L14061
- `_word_timings_for_subtitle_align` — L14087
- `_align_segments_via_asr` — L14128
- `step8_subtitles` — L14171
- `_read_output_json` — L14583
- `_qa_file_pass` — L14594
- `_ass_has_dialogue` — L14601
- `_write_adsd_delivery_qa` — L14611
- `_write_bgm_only_qa` — L14740

---

### 第九步：最终合成
Range: **L14852 – L15097** (246 lines)

**Functions:**
- `step9_render` — L14853

---

### 第十步：推送 Telegram
Range: **L15098 – L16712** (1615 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L16198-16519 (322 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L16520-16524 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L16525-16588 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L16589-16634 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L16635-16712 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L15467
- `PANTONE_FALLBACK` — L15494
- `FESTIVAL_DATE_TAG` — L15607

**Functions:**
- `_generate_caption` — L15099
- `_overlay_title_on_cover` — L15337
- `_prepare_tg_photo` — L15447
- `_get_pantone_for_date` — L15497
- `_llm_bottom_note` — L15522
- `_get_bottom_note` — L15551
- `_get_date_tag` — L15629
- `_shrink_to_b64` — L15651
- `_llm_check_scenes_anomalies` — L15667
- `_llm_check_cover_unique` — L15720
- `_llm_check_cover_quality` — L15750
- `_try_almanac_cover` — L15792
- `_generate_cover_image` — L15963
- `_async_kickoff_cover_caption` — L16205
- `_await_async_cover_caption` — L16235
- `step10_deliver` — L16259

---

### 主流程
Range: **L16713 – L16890** (178 lines)

**Functions:**
- `_print_execution_plan` — L16714
- `main` — L16762

---
