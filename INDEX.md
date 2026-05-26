# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (16885 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-1982 (1861 lines · 58 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L1983-4143 (2161 lines · 29 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L4144-5247 (1104 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L5248-5799 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L5800-9539 (3740 lines · 80 fn · 6 sub)
- [`第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）`](#第-6-5-步-动态化-hads-vads-默认-on---no-motion-关) — L9540-13822 (4283 lines · 100 fn · 4 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L13823-14054 (232 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L14055-14846 (792 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L14847-15092 (246 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L15093-16707 (1615 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L16708-16885 (178 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L1982** (1861 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L308-437 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L438-1110 (673 lines)
- _工具函数_ — L1111-1460 (350 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1461-1982 (522 lines)

**Top-level constants:**
- `HEADERS` — L135
- `VIDEO_FORMAT` — L143
- `ADS_DIALOGUE_MODE_EARLY_CHECK` — L150
- `WITH_MOTION` — L157
- `BGM_ONLY_REQUESTED` — L161
- `ADS_DIALOGUE_MODE` — L168
- `GPT_IMAGE2_STORYBOARD` — L177
- `STORYBOARD_REFERENCE_MOTION` — L181
- `STORYBOARD_ANNOTATED_MOTION` — L185
- `GPT_IMAGE2_DIRECT_ANNOTATED_STORYBOARD` — L189
- `GPT_IMAGE2_STORYBOARD_GRID` — L194
- `ADSD_STORYBOARD_GRID` — L202
- `ADS_CHARACTER_SHEET_REQUESTED` — L208
- `STORYBOARD_GRID_MULTIREF_MOTION` — L212
- `STORYBOARD_GRID_MULTIREF_SEGMENTS` — L216
- `STORYBOARD_GRID_MULTIREF_MAIN` — L222
- `PREVIS_PAGE_MOTION` — L228
- `STORYBOARD_TRAILER_MODE` — L232
- `MOTION_ACTION_STORYBOARD` — L237
- `MOTION_BRIDGE_REFS` — L241
- `CHARACTER_TRAILER_MODE` — L245
- `STORYBOARD_TRAILER_MAIN` — L253
- `ADSD_LIP_SYNC_EXPERIMENT` — L266
- `ADSD_RICH_MOTION_PROMPT` — L274
- `ADSD_LLM_VOICE_ASSIGN` — L282
- `ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT` — L286
- `ADSD_CONSECUTIVE_SPEAKER_BATCHING` — L300
- `ADSD_GENDER_FALLBACK_VOICE_ASSET` — L311
- `SILENT_B_SPEAKERS` — L443
- `_PODCAST_TO_VOICE_ASSET_MAP` — L806
- `_VOICE_ASSET_FORBIDDEN_FLAGS` — L824
- `VOICE_ASSET_AUDIO_DUB_EXPERIMENT` — L862
- `VOICE_ASSET_AUDIO_DUB_PARTIAL_OK` — L870
- `MOTION_VISUAL_QA` — L874
- `MOTION_VOICE_REPAIR` — L882
- `MOTION_VOICE_STRICT_LOCK` — L887
- `WERYDANCE_CAPTIONS` — L892
- `ADSD_ONSITE_POV_MODE` — L904
- `ADSD_LIPS_CHANGE_REPAIR` — L909
- `ADSD_LIPS_CHANGE_ALL` — L914
- `ADS_REPORTER_MODE` — L925
- `ADS_STORYBOARD_FLOW_DEFAULT` — L942
- `ADS_RETENTION_MODE` — L955
- `ADSD_MODE_NAME` — L961
- `EMOTION_STYLE` — L1090
- `EMOTION_STYLE_BRIGHT` — L1102
- `_TG_DASHBOARD_STAGES` — L1124
- `_TG_NOISY_PATTERNS` — L1139
- `_TG_IMMEDIATE_PATTERNS` — L1157
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1390
- `_TOPIC_MODIFIERS` — L1814
- `_TONE_PANTONE_OVERRIDE` — L1831

**Functions:**
- `_is_action_scene` — L320
- `_needs_storyboard_flow_character_sheet` — L331
- `_wuxia_action_panel_prompt` — L360
- `_action_motion_fragment` — L382
- `_infer_emotion_from_text` — L397
- `_emotion_expression_phrase` — L412
- `_infer_needs_lip_sync` — L419
- `_infer_turn_type` — L446
- `_is_action_shout` — L471
- `_resolve_turn_type` — L497
- `_is_silent_b` — L512
- `_is_narrated_b` — L516
- `_is_a_roll` — L520
- `_is_action_b` — L524
- `_voice_asset_id_for_speaker` — L528
- `_llm_assign_voice_assets` — L556
- `_apply_llm_voice_assignment` — L680
- `_voice_asset_is_speech_safe` — L831
- `_podcast_id_to_voice_asset` — L837
- `log` — L1112
- `_tg_send_raw` — L1180
- `_tg_matches` — L1196
- `_tg_summarize` — L1200
- `_tg_dashboard_stage_for` — L1207
- `_tg_progress_bar` — L1215
- `_tg_dashboard_text` — L1221
- `_tg_dashboard_update` — L1239
- `_tg_maybe_digest` — L1276
- `tg` — L1291
- `_wait_image_submit_slot` — L1340
- `_wait_motion_submit_slot` — L1353
- `_is_rate_limited_error` — L1366
- `_is_rate_limited_response` — L1376
- `_inject_image2_quality_suffix` — L1398
- `submit_text_to_image` — L1412
- `req_post` — L1442
- `req_get` — L1456
- `_tg_probe_send` — L1464
- `_tg_probe_delete` — L1484
- `_tg_upload_with_probe_gap` — L1497
- `poll` — L1537
- `poll_podcast` — L1562
- `poll_task_status` — L1584
- `poll_storyboard_task` — L1606
- `chat` — L1632
- `pick_image_model` — L1660
- `detect_topic_meta` — L1685
- `_topic_culture_guard` — L1735
- `_write_cultural_visual_qa` — L1761
- `is_1919_global_topic` — L1808
- `_strip_topic_modifiers` — L1819
- `apply_1919_global_guardrails` — L1837
- `build_1919_global_cover_prompt` — L1866
- `build_shot_blueprint` — L1895
- `ffprobe_duration` — L1921
- `ffprobe_video_size` — L1932
- `_video_decode_probe` — L1953
- `ffmpeg` — L1971

---

### 第一步：双导演生成剧本
Range: **L1983 – L4143** (2161 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L3415-4143 (729 lines)

**Functions:**
- `_extract_json_array` — L1984
- `_extract_json_object` — L1994
- `_voice_for_speaker` — L2004
- `_adsd_gender_from_voice` — L2040
- `_adsd_infer_gender_from_speaker` — L2048
- `_adsd_gender_lock_phrase` — L2057
- `_adsd_visual_subject_has_gender_conflict` — L2072
- `_adsd_default_roles` — L2084
- `_adsd_allows_media_role` — L2089
- `_adsd_role_candidates` — L2097
- `_adsd_dialogue_shape` — L2120
- `_finalize_adsd_turns` — L2129
- `_parse_adsd_override_turns` — L2163
- `_parse_timecode_seconds` — L2254
- `_clean_override_line_text` — L2263
- `_parse_override_script_text` — L2269
- `_adsd_pov_contract` — L2303
- `_load_audit_blacklist_block` — L2316
- `_generate_adsd_dialogue_turns` — L2354
- `_broll_rhythm_reviewer` — L2777
- `_sweep_speaker_field` — L2884
- `_should_run_immersion_qa` — L2944
- `_adsd_immersion_qa_rewrite_turns` — L2967
- `_adsd_visual_contract` — L3031
- `_parse_risk_score` — L3083
- `_check_high_risk_hard_abort` — L3112
- `_maybe_neutralize_topic` — L3139
- `step1_script` — L3178
- `_write_ads_retention_qa` — L4087

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L4144 – L5247** (1104 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L4219
- `_ADSD_POLICY_REWRITE_TERMS` — L4225
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L4316

**Functions:**
- `_openai_tts_fallback` — L4145
- `_edge_tts_fallback` — L4191
- `_sanitize_for_external_api` — L4234
- `_is_content_policy_error` — L4243
- `_rewrite_adsd_tts_text_for_policy` — L4257
- `_record_adsd_tts_rewrite` — L4297
- `_build_silence_mp3` — L4322
- `_audio_duration_seconds` — L4335
- `_text_to_audio_master_voice_timed` — L4347
- `_text_to_audio_master_voice` — L4472
- `step2_master_voice` — L4575
- `_tts_turn_to_audio` — L4703
- `_asr_verify_dialogue_audio` — L4767
- `_asr_verify_dialogue_turns` — L4829
- `_normalize_cn_number_token` — L4871
- `_compact_zh_text` — L4893
- `_write_adsd_asr_text_qa` — L4900
- `_write_adsd_speaker_focus_qa` — L4939
- `_write_adsd_gender_voice_qa` — L4999
- `step2_dialogue_voice` — L5052

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L5248 – L5799** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L5255-5377 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L5378-5412 (35 lines)
- _第二层：字符数插值_ — L5413-5437 (25 lines)
- _第三层：silencedetect 物理校准_ — L5438-5799 (362 lines)

**Functions:**
- `_detect_silences` — L5256
- `_calibrate_boundaries` — L5291
- `_enforce_monotonic` — L5325
- `_manual_override_segments` — L5337
- `_calc_sentence_boundaries` — L5358
- `step345_timeline` — L5469
- `_analyze_bgm_energy_cuts` — L5528
- `_snap_bgm_only_boundaries` — L5591
- `step345_bgm_only_timeline` — L5651

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L5800 – L9539** (3740 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L6989-7039 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L7040-7180 (141 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L7181-7615 (435 lines)
- _Speaker IP Card (2026-05-21)_ — L7616-9372 (1757 lines)
- _审批流程_ — L9373-9429 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L9430-9539 (110 lines)

**Top-level constants:**
- `CHARACTER_META_GRID_COSTUMES` — L6995
- `CHARACTER_META_GRID_POSES` — L6996
- `CHARACTER_META_GRID_SCENES` — L6997
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L7000

**Functions:**
- `_extract_img_url` — L5801
- `_extract_img_urls` — L5823
- `_extract_video_url` — L5856
- `_count_bands` — L5881
- `_detect_contact_sheet_like_image` — L5893
- `_file_sha256` — L5954
- `_load_upload_cache` — L5967
- `_save_upload_cache` — L5976
- `_cached_upload_url` — L5984
- `_store_upload_url` — L6001
- `_guess_upload_mime` — L6011
- `_upload_to_weryai` — L6034
- `_send_for_approval` — L6088
- `_wait_approval` — L6152
- `_render_still_segment` — L6164
- `_scene_text_visual_alignment` — L6195
- `_write_text_visual_alignment_qa` — L6231
- `_scene_motion_action_plan` — L6254
- `_ensure_motion_action_plan` — L6308
- `_motion_action_block` — L6317
- `_motion_plan_for_qa` — L6345
- `_write_motion_action_plan_qa` — L6355
- `_write_motion_bridge_refs_qa` — L6385
- `_motion_bridge_ref_prompt` — L6392
- `generate_motion_bridge_refs_gpt_image2` — L6425
- `generate_image` — L6538
- `generate_storyboard_images_gpt_image2` — L6585
- `_storyboard_grid_aspect` — L6770
- `_storyboard_grid_cols_rows` — L6777
- `_storyboard_grid_prompt` — L6799
- `_storyboard_grid_prompt_limit` — L6837
- `_is_prompt_limit_response` — L6841
- `_production_storyboard_prompt` — L6847
- `_write_production_storyboard_page_qa` — L6881
- `_character_sheet_prompt` — L6891
- `_is_audit_blocked` — L7017
- `_paraphrase_sensitive_dialogue` — L7030
- `_topic_cache_dir` — L7044
- `_topic_cache_path` — L7050
- `_load_topic_decomposition_cache` — L7063
- `_save_topic_decomposition_cache` — L7081
- `_llm_topic_decomposition` — L7087
- `_director_route_block` — L7234
- `_llm_infer_meta_grid_template` — L7304
- `_resolve_meta_grid_template` — L7361
- `_infer_meta_grid_costume` — L7404
- `_infer_meta_grid_pose` — L7453
- `_adsd_meta_grid_call_prompt` — L7500
- `_meta_grid_panel_index` — L7542
- `_migrate_speaker_ip` — L7622
- `_speaker_ips_dir` — L7647
- `_list_speaker_ips` — L7654
- `_match_speaker_ip` — L7668
- `_build_speaker_ip_context_for_script` — L7688
- `_ip_usage_stats` — L7744
- `_recommend_related_ips` — L7762
- `_save_speaker_ip` — L7787
- `_record_speaker_usage_history` — L7796
- `_format_speaker_usage_history_for_prompt` — L7843
- `_llm_infer_ip_skeleton` — L7861
- `_llm_pick_voice_asset_for_ip` — L7906
- `_auto_incubate_missing_ips` — L7954
- `_character_meta_grid_cache_dir` — L8038
- `_character_meta_grid_cache_path` — L8046
- `_character_meta_grid_path` — L8054
- `generate_character_meta_grid_gpt_image2` — L8060
- `_generate_all_character_meta_grids` — L8218
- `_write_character_sheet_qa` — L8259
- `generate_character_sheet_gpt_image2` — L8269
- `generate_production_storyboard_page_gpt_image2` — L8369
- `_qa_clean_storyboard_panel` — L8432
- `_crop_storyboard_grid_panels` — L8613
- `generate_storyboard_grid_gpt_image2` — L8660
- `_gpt_image2_direct_annotated_aspect` — L8891
- `_gpt_image2_direct_annotated_prompt` — L8898
- `generate_gpt_image2_direct_annotated_storyboards` — L8928
- `_llm_bgm_description` — L9029
- `_bgm_contains_vocals` — L9068
- `generate_bgm` — L9102
- `step6_parallel` — L9219

---

### 第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）
Range: **L9540 – L13822** (4283 lines)

**Sub-sections:**
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L13559-13601 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L13602-13639 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回主音轨_ — L13640-13777 (138 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L13778-13822 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L9543
- `_motion_tasks_file` — L9610
- `_motion_qa_file` — L9614
- `_append_motion_qa` — L9618
- `_finalize_motion_qa` — L9642
- `_lip_sync_tasks_file` — L9726
- `_load_motion_tasks` — L9730
- `_save_motion_task` — L9740
- `_remove_motion_task` — L9748
- `_load_lip_sync_tasks` — L9755
- `_save_lip_sync_task` — L9765
- `_remove_lip_sync_task` — L9772
- `_video_visual_motion_qa` — L9779
- `_motion_output_qa` — L9851
- `_has_audio_stream` — L9896
- `_normalize_motion_video` — L9907
- `_motion_poll_and_download` — L9957
- `_build_motion_video_prompt` — L10008
- `_short_board_text` — L10038
- `_wrap_board_text` — L10045
- `_storyboard_font` — L10076
- `_draw_storyboard_arrow` — L10091
- `_build_annotated_storyboard_reference` — L10105
- `_plain_caption_text` — L10206
- `_werydance_caption_request` — L10214
- `_werydance_caption_instruction` — L10241
- `_werydance_negative_prompt` — L10253
- `_motion_reference_prompt` — L10271
- `_motion_audio_dub_prompt` — L10294
- `_motion_audio_dub_poll_and_download` — L10328
- `_try_motion_audio_dub_video` — L10393
- `_try_motion_reference_video` — L10528
- `_motion_one_scene` — L10644
- `_grid_multiref_tasks_file` — L10773
- `_previs_page_tasks_file` — L10777
- `_load_grid_multiref_tasks` — L10781
- `_load_previs_page_tasks` — L10791
- `_save_grid_multiref_task` — L10801
- `_save_previs_page_task` — L10808
- `_remove_grid_multiref_task` — L10815
- `_remove_previs_page_task` — L10822
- `_poll_video_task_download` — L10829
- `_grid_multiref_group_size` — L10878
- `_grid_multiref_duration` — L10886
- `_grid_multiref_segment_max_stretch` — L10902
- `_grid_multiref_prompt` — L10910
- `_write_grid_multiref_motion_qa` — L10958
- `_write_previs_page_motion_qa` — L10968
- `_write_storyboard_trailer_qa` — L10978
- `_write_character_trailer_qa` — L10988
- `_write_grid_multiref_segment_qa` — L10998
- `_motion_compare_record` — L11008
- `_write_storyboard_motion_compare_qa` — L11030
- `_scene_segment_duration` — L11066
- `_apply_grid_multiref_segments` — L11085
- `_previs_page_duration` — L11279
- `_previs_page_group_prompt` — L11289
- `_previs_page_groups` — L11315
- `_storyboard_trailer_duration` — L11330
- `_storyboard_trailer_prompt` — L11340
- `_character_trailer_max_shots` — L11368
- `_character_trailer_shot_duration` — L11376
- `_character_trailer_prompt` — L11390
- `_concat_character_trailer_segments` — L11405
- `_generate_character_trailer_motion` — L11444
- `_multi_trailer_prompt_for_group` — L11552
- `_generate_multi_trailer_segments` — L11575
- `_generate_storyboard_trailer_motion` — L11686
- `_generate_previs_page_motion_segments` — L11761
- `_generate_grid_multiref_motion_segments` — L11873
- `_grid_multiref_concat_groups` — L12043
- `_grid_multiref_concat_groups_partial` — L12060
- `_grid_multiref_concat_paths` — L12078
- `_lip_sync_slot_duration` — L12109
- `_adsd_lip_sync_prompt` — L12116
- `_adsd_broll_motion_prompt` — L12162
- `_adsd_action_b_motion_prompt` — L12204
- `_adsd_silent_b_motion_prompt` — L12250
- `_adsd_narrated_b_audio_dub_prompt` — L12285
- `_adsd_almighty_audio_dub_prompt` — L12329
- `_postprocess_lip_sync_segment` — L12370
- `_detect_audio_leading_silence` — L12438
- `_postprocess_audio_dub_segment` — L12460
- `_lips_change_repair_segment` — L12571
- `_load_lips_change_requested_turns` — L12656
- `_parse_turn_set` — L12673
- `_load_motion_voice_repair_turns` — L12695
- `_voice_assets_file` — L12707
- `_load_voice_assets` — L12714
- `_select_voice_asset_reference` — L12733
- `_lip_sync_poll_download_and_process` — L12799
- `_lip_sync_one_scene` — L12867
- `step66_adsd_lip_sync` — L13191
- `step65_motion` — L13449
- `step65_grid_multiref_motion_qa` — L13531
- `_sanitize_scene_for_state` — L13560
- `_save_pipeline_state` — L13579
- `_retime_after_audio_dub` — L13603
- `_build_voice_clone_hybrid_audio` — L13641
- `_build_dynamic_bgm` — L13779

---

### 第七步：拼接视频轨
Range: **L13823 – L14054** (232 lines)

**Functions:**
- `step7_concat` — L13824

---

### 第八步：生成 ASS 字幕
Range: **L14055 – L14846** (792 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L14178-14846 (669 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L14056
- `_word_timings_for_subtitle_align` — L14082
- `_align_segments_via_asr` — L14123
- `step8_subtitles` — L14166
- `_read_output_json` — L14578
- `_qa_file_pass` — L14589
- `_ass_has_dialogue` — L14596
- `_write_adsd_delivery_qa` — L14606
- `_write_bgm_only_qa` — L14735

---

### 第九步：最终合成
Range: **L14847 – L15092** (246 lines)

**Functions:**
- `step9_render` — L14848

---

### 第十步：推送 Telegram
Range: **L15093 – L16707** (1615 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L16193-16514 (322 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L16515-16519 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L16520-16583 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L16584-16629 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L16630-16707 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L15462
- `PANTONE_FALLBACK` — L15489
- `FESTIVAL_DATE_TAG` — L15602

**Functions:**
- `_generate_caption` — L15094
- `_overlay_title_on_cover` — L15332
- `_prepare_tg_photo` — L15442
- `_get_pantone_for_date` — L15492
- `_llm_bottom_note` — L15517
- `_get_bottom_note` — L15546
- `_get_date_tag` — L15624
- `_shrink_to_b64` — L15646
- `_llm_check_scenes_anomalies` — L15662
- `_llm_check_cover_unique` — L15715
- `_llm_check_cover_quality` — L15745
- `_try_almanac_cover` — L15787
- `_generate_cover_image` — L15958
- `_async_kickoff_cover_caption` — L16200
- `_await_async_cover_caption` — L16230
- `step10_deliver` — L16254

---

### 主流程
Range: **L16708 – L16885** (178 lines)

**Functions:**
- `_print_execution_plan` — L16709
- `main` — L16757

---
