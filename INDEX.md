# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (16875 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-1972 (1851 lines · 58 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L1973-4133 (2161 lines · 29 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L4134-5237 (1104 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L5238-5789 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L5790-9529 (3740 lines · 80 fn · 6 sub)
- [`第 6.5 步：动态化（可选，--with-motion 开启）`](#第-6-5-步-动态化-可选---with-motion-开启) — L9530-13812 (4283 lines · 100 fn · 4 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L13813-14044 (232 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L14045-14836 (792 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L14837-15082 (246 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L15083-16697 (1615 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L16698-16875 (178 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L1972** (1851 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L298-427 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L428-1100 (673 lines)
- _工具函数_ — L1101-1450 (350 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1451-1972 (522 lines)

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
- `_PODCAST_TO_VOICE_ASSET_MAP` — L796
- `_VOICE_ASSET_FORBIDDEN_FLAGS` — L814
- `VOICE_ASSET_AUDIO_DUB_EXPERIMENT` — L852
- `VOICE_ASSET_AUDIO_DUB_PARTIAL_OK` — L860
- `MOTION_VISUAL_QA` — L864
- `MOTION_VOICE_REPAIR` — L872
- `MOTION_VOICE_STRICT_LOCK` — L877
- `WERYDANCE_CAPTIONS` — L882
- `ADSD_ONSITE_POV_MODE` — L894
- `ADSD_LIPS_CHANGE_REPAIR` — L899
- `ADSD_LIPS_CHANGE_ALL` — L904
- `ADS_REPORTER_MODE` — L915
- `ADS_STORYBOARD_FLOW_DEFAULT` — L932
- `ADS_RETENTION_MODE` — L945
- `ADSD_MODE_NAME` — L951
- `EMOTION_STYLE` — L1080
- `EMOTION_STYLE_BRIGHT` — L1092
- `_TG_DASHBOARD_STAGES` — L1114
- `_TG_NOISY_PATTERNS` — L1129
- `_TG_IMMEDIATE_PATTERNS` — L1147
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1380
- `_TOPIC_MODIFIERS` — L1804
- `_TONE_PANTONE_OVERRIDE` — L1821

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
- `_voice_asset_is_speech_safe` — L821
- `_podcast_id_to_voice_asset` — L827
- `log` — L1102
- `_tg_send_raw` — L1170
- `_tg_matches` — L1186
- `_tg_summarize` — L1190
- `_tg_dashboard_stage_for` — L1197
- `_tg_progress_bar` — L1205
- `_tg_dashboard_text` — L1211
- `_tg_dashboard_update` — L1229
- `_tg_maybe_digest` — L1266
- `tg` — L1281
- `_wait_image_submit_slot` — L1330
- `_wait_motion_submit_slot` — L1343
- `_is_rate_limited_error` — L1356
- `_is_rate_limited_response` — L1366
- `_inject_image2_quality_suffix` — L1388
- `submit_text_to_image` — L1402
- `req_post` — L1432
- `req_get` — L1446
- `_tg_probe_send` — L1454
- `_tg_probe_delete` — L1474
- `_tg_upload_with_probe_gap` — L1487
- `poll` — L1527
- `poll_podcast` — L1552
- `poll_task_status` — L1574
- `poll_storyboard_task` — L1596
- `chat` — L1622
- `pick_image_model` — L1650
- `detect_topic_meta` — L1675
- `_topic_culture_guard` — L1725
- `_write_cultural_visual_qa` — L1751
- `is_1919_global_topic` — L1798
- `_strip_topic_modifiers` — L1809
- `apply_1919_global_guardrails` — L1827
- `build_1919_global_cover_prompt` — L1856
- `build_shot_blueprint` — L1885
- `ffprobe_duration` — L1911
- `ffprobe_video_size` — L1922
- `_video_decode_probe` — L1943
- `ffmpeg` — L1961

---

### 第一步：双导演生成剧本
Range: **L1973 – L4133** (2161 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L3405-4133 (729 lines)

**Functions:**
- `_extract_json_array` — L1974
- `_extract_json_object` — L1984
- `_voice_for_speaker` — L1994
- `_adsd_gender_from_voice` — L2030
- `_adsd_infer_gender_from_speaker` — L2038
- `_adsd_gender_lock_phrase` — L2047
- `_adsd_visual_subject_has_gender_conflict` — L2062
- `_adsd_default_roles` — L2074
- `_adsd_allows_media_role` — L2079
- `_adsd_role_candidates` — L2087
- `_adsd_dialogue_shape` — L2110
- `_finalize_adsd_turns` — L2119
- `_parse_adsd_override_turns` — L2153
- `_parse_timecode_seconds` — L2244
- `_clean_override_line_text` — L2253
- `_parse_override_script_text` — L2259
- `_adsd_pov_contract` — L2293
- `_load_audit_blacklist_block` — L2306
- `_generate_adsd_dialogue_turns` — L2344
- `_broll_rhythm_reviewer` — L2767
- `_sweep_speaker_field` — L2874
- `_should_run_immersion_qa` — L2934
- `_adsd_immersion_qa_rewrite_turns` — L2957
- `_adsd_visual_contract` — L3021
- `_parse_risk_score` — L3073
- `_check_high_risk_hard_abort` — L3102
- `_maybe_neutralize_topic` — L3129
- `step1_script` — L3168
- `_write_ads_retention_qa` — L4077

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L4134 – L5237** (1104 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L4209
- `_ADSD_POLICY_REWRITE_TERMS` — L4215
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L4306

**Functions:**
- `_openai_tts_fallback` — L4135
- `_edge_tts_fallback` — L4181
- `_sanitize_for_external_api` — L4224
- `_is_content_policy_error` — L4233
- `_rewrite_adsd_tts_text_for_policy` — L4247
- `_record_adsd_tts_rewrite` — L4287
- `_build_silence_mp3` — L4312
- `_audio_duration_seconds` — L4325
- `_text_to_audio_master_voice_timed` — L4337
- `_text_to_audio_master_voice` — L4462
- `step2_master_voice` — L4565
- `_tts_turn_to_audio` — L4693
- `_asr_verify_dialogue_audio` — L4757
- `_asr_verify_dialogue_turns` — L4819
- `_normalize_cn_number_token` — L4861
- `_compact_zh_text` — L4883
- `_write_adsd_asr_text_qa` — L4890
- `_write_adsd_speaker_focus_qa` — L4929
- `_write_adsd_gender_voice_qa` — L4989
- `step2_dialogue_voice` — L5042

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L5238 – L5789** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L5245-5367 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L5368-5402 (35 lines)
- _第二层：字符数插值_ — L5403-5427 (25 lines)
- _第三层：silencedetect 物理校准_ — L5428-5789 (362 lines)

**Functions:**
- `_detect_silences` — L5246
- `_calibrate_boundaries` — L5281
- `_enforce_monotonic` — L5315
- `_manual_override_segments` — L5327
- `_calc_sentence_boundaries` — L5348
- `step345_timeline` — L5459
- `_analyze_bgm_energy_cuts` — L5518
- `_snap_bgm_only_boundaries` — L5581
- `step345_bgm_only_timeline` — L5641

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L5790 – L9529** (3740 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L6979-7029 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L7030-7170 (141 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L7171-7605 (435 lines)
- _Speaker IP Card (2026-05-21)_ — L7606-9362 (1757 lines)
- _审批流程_ — L9363-9419 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L9420-9529 (110 lines)

**Top-level constants:**
- `CHARACTER_META_GRID_COSTUMES` — L6985
- `CHARACTER_META_GRID_POSES` — L6986
- `CHARACTER_META_GRID_SCENES` — L6987
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L6990

**Functions:**
- `_extract_img_url` — L5791
- `_extract_img_urls` — L5813
- `_extract_video_url` — L5846
- `_count_bands` — L5871
- `_detect_contact_sheet_like_image` — L5883
- `_file_sha256` — L5944
- `_load_upload_cache` — L5957
- `_save_upload_cache` — L5966
- `_cached_upload_url` — L5974
- `_store_upload_url` — L5991
- `_guess_upload_mime` — L6001
- `_upload_to_weryai` — L6024
- `_send_for_approval` — L6078
- `_wait_approval` — L6142
- `_render_still_segment` — L6154
- `_scene_text_visual_alignment` — L6185
- `_write_text_visual_alignment_qa` — L6221
- `_scene_motion_action_plan` — L6244
- `_ensure_motion_action_plan` — L6298
- `_motion_action_block` — L6307
- `_motion_plan_for_qa` — L6335
- `_write_motion_action_plan_qa` — L6345
- `_write_motion_bridge_refs_qa` — L6375
- `_motion_bridge_ref_prompt` — L6382
- `generate_motion_bridge_refs_gpt_image2` — L6415
- `generate_image` — L6528
- `generate_storyboard_images_gpt_image2` — L6575
- `_storyboard_grid_aspect` — L6760
- `_storyboard_grid_cols_rows` — L6767
- `_storyboard_grid_prompt` — L6789
- `_storyboard_grid_prompt_limit` — L6827
- `_is_prompt_limit_response` — L6831
- `_production_storyboard_prompt` — L6837
- `_write_production_storyboard_page_qa` — L6871
- `_character_sheet_prompt` — L6881
- `_is_audit_blocked` — L7007
- `_paraphrase_sensitive_dialogue` — L7020
- `_topic_cache_dir` — L7034
- `_topic_cache_path` — L7040
- `_load_topic_decomposition_cache` — L7053
- `_save_topic_decomposition_cache` — L7071
- `_llm_topic_decomposition` — L7077
- `_director_route_block` — L7224
- `_llm_infer_meta_grid_template` — L7294
- `_resolve_meta_grid_template` — L7351
- `_infer_meta_grid_costume` — L7394
- `_infer_meta_grid_pose` — L7443
- `_adsd_meta_grid_call_prompt` — L7490
- `_meta_grid_panel_index` — L7532
- `_migrate_speaker_ip` — L7612
- `_speaker_ips_dir` — L7637
- `_list_speaker_ips` — L7644
- `_match_speaker_ip` — L7658
- `_build_speaker_ip_context_for_script` — L7678
- `_ip_usage_stats` — L7734
- `_recommend_related_ips` — L7752
- `_save_speaker_ip` — L7777
- `_record_speaker_usage_history` — L7786
- `_format_speaker_usage_history_for_prompt` — L7833
- `_llm_infer_ip_skeleton` — L7851
- `_llm_pick_voice_asset_for_ip` — L7896
- `_auto_incubate_missing_ips` — L7944
- `_character_meta_grid_cache_dir` — L8028
- `_character_meta_grid_cache_path` — L8036
- `_character_meta_grid_path` — L8044
- `generate_character_meta_grid_gpt_image2` — L8050
- `_generate_all_character_meta_grids` — L8208
- `_write_character_sheet_qa` — L8249
- `generate_character_sheet_gpt_image2` — L8259
- `generate_production_storyboard_page_gpt_image2` — L8359
- `_qa_clean_storyboard_panel` — L8422
- `_crop_storyboard_grid_panels` — L8603
- `generate_storyboard_grid_gpt_image2` — L8650
- `_gpt_image2_direct_annotated_aspect` — L8881
- `_gpt_image2_direct_annotated_prompt` — L8888
- `generate_gpt_image2_direct_annotated_storyboards` — L8918
- `_llm_bgm_description` — L9019
- `_bgm_contains_vocals` — L9058
- `generate_bgm` — L9092
- `step6_parallel` — L9209

---

### 第 6.5 步：动态化（可选，--with-motion 开启）
Range: **L9530 – L13812** (4283 lines)

**Sub-sections:**
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L13549-13591 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L13592-13629 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回主音轨_ — L13630-13767 (138 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L13768-13812 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L9533
- `_motion_tasks_file` — L9600
- `_motion_qa_file` — L9604
- `_append_motion_qa` — L9608
- `_finalize_motion_qa` — L9632
- `_lip_sync_tasks_file` — L9716
- `_load_motion_tasks` — L9720
- `_save_motion_task` — L9730
- `_remove_motion_task` — L9738
- `_load_lip_sync_tasks` — L9745
- `_save_lip_sync_task` — L9755
- `_remove_lip_sync_task` — L9762
- `_video_visual_motion_qa` — L9769
- `_motion_output_qa` — L9841
- `_has_audio_stream` — L9886
- `_normalize_motion_video` — L9897
- `_motion_poll_and_download` — L9947
- `_build_motion_video_prompt` — L9998
- `_short_board_text` — L10028
- `_wrap_board_text` — L10035
- `_storyboard_font` — L10066
- `_draw_storyboard_arrow` — L10081
- `_build_annotated_storyboard_reference` — L10095
- `_plain_caption_text` — L10196
- `_werydance_caption_request` — L10204
- `_werydance_caption_instruction` — L10231
- `_werydance_negative_prompt` — L10243
- `_motion_reference_prompt` — L10261
- `_motion_audio_dub_prompt` — L10284
- `_motion_audio_dub_poll_and_download` — L10318
- `_try_motion_audio_dub_video` — L10383
- `_try_motion_reference_video` — L10518
- `_motion_one_scene` — L10634
- `_grid_multiref_tasks_file` — L10763
- `_previs_page_tasks_file` — L10767
- `_load_grid_multiref_tasks` — L10771
- `_load_previs_page_tasks` — L10781
- `_save_grid_multiref_task` — L10791
- `_save_previs_page_task` — L10798
- `_remove_grid_multiref_task` — L10805
- `_remove_previs_page_task` — L10812
- `_poll_video_task_download` — L10819
- `_grid_multiref_group_size` — L10868
- `_grid_multiref_duration` — L10876
- `_grid_multiref_segment_max_stretch` — L10892
- `_grid_multiref_prompt` — L10900
- `_write_grid_multiref_motion_qa` — L10948
- `_write_previs_page_motion_qa` — L10958
- `_write_storyboard_trailer_qa` — L10968
- `_write_character_trailer_qa` — L10978
- `_write_grid_multiref_segment_qa` — L10988
- `_motion_compare_record` — L10998
- `_write_storyboard_motion_compare_qa` — L11020
- `_scene_segment_duration` — L11056
- `_apply_grid_multiref_segments` — L11075
- `_previs_page_duration` — L11269
- `_previs_page_group_prompt` — L11279
- `_previs_page_groups` — L11305
- `_storyboard_trailer_duration` — L11320
- `_storyboard_trailer_prompt` — L11330
- `_character_trailer_max_shots` — L11358
- `_character_trailer_shot_duration` — L11366
- `_character_trailer_prompt` — L11380
- `_concat_character_trailer_segments` — L11395
- `_generate_character_trailer_motion` — L11434
- `_multi_trailer_prompt_for_group` — L11542
- `_generate_multi_trailer_segments` — L11565
- `_generate_storyboard_trailer_motion` — L11676
- `_generate_previs_page_motion_segments` — L11751
- `_generate_grid_multiref_motion_segments` — L11863
- `_grid_multiref_concat_groups` — L12033
- `_grid_multiref_concat_groups_partial` — L12050
- `_grid_multiref_concat_paths` — L12068
- `_lip_sync_slot_duration` — L12099
- `_adsd_lip_sync_prompt` — L12106
- `_adsd_broll_motion_prompt` — L12152
- `_adsd_action_b_motion_prompt` — L12194
- `_adsd_silent_b_motion_prompt` — L12240
- `_adsd_narrated_b_audio_dub_prompt` — L12275
- `_adsd_almighty_audio_dub_prompt` — L12319
- `_postprocess_lip_sync_segment` — L12360
- `_detect_audio_leading_silence` — L12428
- `_postprocess_audio_dub_segment` — L12450
- `_lips_change_repair_segment` — L12561
- `_load_lips_change_requested_turns` — L12646
- `_parse_turn_set` — L12663
- `_load_motion_voice_repair_turns` — L12685
- `_voice_assets_file` — L12697
- `_load_voice_assets` — L12704
- `_select_voice_asset_reference` — L12723
- `_lip_sync_poll_download_and_process` — L12789
- `_lip_sync_one_scene` — L12857
- `step66_adsd_lip_sync` — L13181
- `step65_motion` — L13439
- `step65_grid_multiref_motion_qa` — L13521
- `_sanitize_scene_for_state` — L13550
- `_save_pipeline_state` — L13569
- `_retime_after_audio_dub` — L13593
- `_build_voice_clone_hybrid_audio` — L13631
- `_build_dynamic_bgm` — L13769

---

### 第七步：拼接视频轨
Range: **L13813 – L14044** (232 lines)

**Functions:**
- `step7_concat` — L13814

---

### 第八步：生成 ASS 字幕
Range: **L14045 – L14836** (792 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L14168-14836 (669 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L14046
- `_word_timings_for_subtitle_align` — L14072
- `_align_segments_via_asr` — L14113
- `step8_subtitles` — L14156
- `_read_output_json` — L14568
- `_qa_file_pass` — L14579
- `_ass_has_dialogue` — L14586
- `_write_adsd_delivery_qa` — L14596
- `_write_bgm_only_qa` — L14725

---

### 第九步：最终合成
Range: **L14837 – L15082** (246 lines)

**Functions:**
- `step9_render` — L14838

---

### 第十步：推送 Telegram
Range: **L15083 – L16697** (1615 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L16183-16504 (322 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L16505-16509 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L16510-16573 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L16574-16619 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L16620-16697 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L15452
- `PANTONE_FALLBACK` — L15479
- `FESTIVAL_DATE_TAG` — L15592

**Functions:**
- `_generate_caption` — L15084
- `_overlay_title_on_cover` — L15322
- `_prepare_tg_photo` — L15432
- `_get_pantone_for_date` — L15482
- `_llm_bottom_note` — L15507
- `_get_bottom_note` — L15536
- `_get_date_tag` — L15614
- `_shrink_to_b64` — L15636
- `_llm_check_scenes_anomalies` — L15652
- `_llm_check_cover_unique` — L15705
- `_llm_check_cover_quality` — L15735
- `_try_almanac_cover` — L15777
- `_generate_cover_image` — L15948
- `_async_kickoff_cover_caption` — L16190
- `_await_async_cover_caption` — L16220
- `step10_deliver` — L16244

---

### 主流程
Range: **L16698 – L16875** (178 lines)

**Functions:**
- `_print_execution_plan` — L16699
- `main` — L16747

---
