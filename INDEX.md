# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (16091 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-1915 (1794 lines · 56 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L1916-3681 (1766 lines · 23 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L3682-4783 (1102 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L4784-5335 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L5336-8775 (3440 lines · 73 fn · 6 sub)
- [`第 6.5 步：动态化（可选，--with-motion 开启）`](#第-6-5-步-动态化-可选---with-motion-开启) — L8776-13028 (4253 lines · 100 fn · 4 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L13029-13260 (232 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L13261-14052 (792 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L14053-14298 (246 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L14299-15913 (1615 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L15914-16091 (178 lines · 2 fn · 0 sub)

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
Range: **L5336 – L8775** (3440 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L6439-6489 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L6490-6597 (108 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L6598-6892 (295 lines)
- _Speaker IP Card (2026-05-21)_ — L6893-8608 (1716 lines)
- _审批流程_ — L8609-8665 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L8666-8775 (110 lines)

**Top-level constants:**
- `CHARACTER_META_GRID_COSTUMES` — L6445
- `CHARACTER_META_GRID_POSES` — L6446
- `CHARACTER_META_GRID_SCENES` — L6447
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L6450

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
- `_scene_text_visual_alignment` — L5645
- `_write_text_visual_alignment_qa` — L5681
- `_scene_motion_action_plan` — L5704
- `_ensure_motion_action_plan` — L5758
- `_motion_action_block` — L5767
- `_motion_plan_for_qa` — L5795
- `_write_motion_action_plan_qa` — L5805
- `_write_motion_bridge_refs_qa` — L5835
- `_motion_bridge_ref_prompt` — L5842
- `generate_motion_bridge_refs_gpt_image2` — L5875
- `generate_image` — L5988
- `generate_storyboard_images_gpt_image2` — L6035
- `_storyboard_grid_aspect` — L6220
- `_storyboard_grid_cols_rows` — L6227
- `_storyboard_grid_prompt` — L6249
- `_storyboard_grid_prompt_limit` — L6287
- `_is_prompt_limit_response` — L6291
- `_production_storyboard_prompt` — L6297
- `_write_production_storyboard_page_qa` — L6331
- `_character_sheet_prompt` — L6341
- `_is_audit_blocked` — L6467
- `_paraphrase_sensitive_dialogue` — L6480
- `_topic_cache_dir` — L6494
- `_topic_cache_path` — L6500
- `_load_topic_decomposition_cache` — L6505
- `_save_topic_decomposition_cache` — L6515
- `_llm_topic_decomposition` — L6520
- `_llm_infer_meta_grid_template` — L6655
- `_resolve_meta_grid_template` — L6712
- `_infer_meta_grid_costume` — L6755
- `_infer_meta_grid_pose` — L6804
- `_adsd_meta_grid_call_prompt` — L6851
- `_migrate_speaker_ip` — L6899
- `_speaker_ips_dir` — L6924
- `_list_speaker_ips` — L6931
- `_match_speaker_ip` — L6945
- `_build_speaker_ip_context_for_script` — L6965
- `_ip_usage_stats` — L7021
- `_recommend_related_ips` — L7039
- `_save_speaker_ip` — L7064
- `_record_speaker_usage_history` — L7073
- `_format_speaker_usage_history_for_prompt` — L7120
- `_llm_infer_ip_skeleton` — L7138
- `_llm_pick_voice_asset_for_ip` — L7183
- `_auto_incubate_missing_ips` — L7231
- `_character_meta_grid_cache_dir` — L7315
- `_character_meta_grid_cache_path` — L7323
- `_character_meta_grid_path` — L7329
- `generate_character_meta_grid_gpt_image2` — L7335
- `_generate_all_character_meta_grids` — L7454
- `_write_character_sheet_qa` — L7495
- `generate_character_sheet_gpt_image2` — L7505
- `generate_production_storyboard_page_gpt_image2` — L7605
- `_qa_clean_storyboard_panel` — L7668
- `_crop_storyboard_grid_panels` — L7849
- `generate_storyboard_grid_gpt_image2` — L7896
- `_gpt_image2_direct_annotated_aspect` — L8127
- `_gpt_image2_direct_annotated_prompt` — L8134
- `generate_gpt_image2_direct_annotated_storyboards` — L8164
- `_llm_bgm_description` — L8265
- `_bgm_contains_vocals` — L8304
- `generate_bgm` — L8338
- `step6_parallel` — L8455

---

### 第 6.5 步：动态化（可选，--with-motion 开启）
Range: **L8776 – L13028** (4253 lines)

**Sub-sections:**
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L12765-12807 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L12808-12845 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回主音轨_ — L12846-12983 (138 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L12984-13028 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L8779
- `_motion_tasks_file` — L8846
- `_motion_qa_file` — L8850
- `_append_motion_qa` — L8854
- `_finalize_motion_qa` — L8878
- `_lip_sync_tasks_file` — L8962
- `_load_motion_tasks` — L8966
- `_save_motion_task` — L8976
- `_remove_motion_task` — L8984
- `_load_lip_sync_tasks` — L8991
- `_save_lip_sync_task` — L9001
- `_remove_lip_sync_task` — L9008
- `_video_visual_motion_qa` — L9015
- `_motion_output_qa` — L9087
- `_has_audio_stream` — L9132
- `_normalize_motion_video` — L9143
- `_motion_poll_and_download` — L9193
- `_build_motion_video_prompt` — L9244
- `_short_board_text` — L9274
- `_wrap_board_text` — L9281
- `_storyboard_font` — L9312
- `_draw_storyboard_arrow` — L9327
- `_build_annotated_storyboard_reference` — L9341
- `_plain_caption_text` — L9442
- `_werydance_caption_request` — L9450
- `_werydance_caption_instruction` — L9477
- `_werydance_negative_prompt` — L9489
- `_motion_reference_prompt` — L9507
- `_motion_audio_dub_prompt` — L9530
- `_motion_audio_dub_poll_and_download` — L9564
- `_try_motion_audio_dub_video` — L9629
- `_try_motion_reference_video` — L9764
- `_motion_one_scene` — L9880
- `_grid_multiref_tasks_file` — L10009
- `_previs_page_tasks_file` — L10013
- `_load_grid_multiref_tasks` — L10017
- `_load_previs_page_tasks` — L10027
- `_save_grid_multiref_task` — L10037
- `_save_previs_page_task` — L10044
- `_remove_grid_multiref_task` — L10051
- `_remove_previs_page_task` — L10058
- `_poll_video_task_download` — L10065
- `_grid_multiref_group_size` — L10114
- `_grid_multiref_duration` — L10122
- `_grid_multiref_segment_max_stretch` — L10138
- `_grid_multiref_prompt` — L10146
- `_write_grid_multiref_motion_qa` — L10194
- `_write_previs_page_motion_qa` — L10204
- `_write_storyboard_trailer_qa` — L10214
- `_write_character_trailer_qa` — L10224
- `_write_grid_multiref_segment_qa` — L10234
- `_motion_compare_record` — L10244
- `_write_storyboard_motion_compare_qa` — L10266
- `_scene_segment_duration` — L10302
- `_apply_grid_multiref_segments` — L10321
- `_previs_page_duration` — L10515
- `_previs_page_group_prompt` — L10525
- `_previs_page_groups` — L10551
- `_storyboard_trailer_duration` — L10566
- `_storyboard_trailer_prompt` — L10576
- `_character_trailer_max_shots` — L10604
- `_character_trailer_shot_duration` — L10612
- `_character_trailer_prompt` — L10626
- `_concat_character_trailer_segments` — L10641
- `_generate_character_trailer_motion` — L10680
- `_multi_trailer_prompt_for_group` — L10788
- `_generate_multi_trailer_segments` — L10811
- `_generate_storyboard_trailer_motion` — L10922
- `_generate_previs_page_motion_segments` — L10997
- `_generate_grid_multiref_motion_segments` — L11109
- `_grid_multiref_concat_groups` — L11279
- `_grid_multiref_concat_groups_partial` — L11296
- `_grid_multiref_concat_paths` — L11314
- `_lip_sync_slot_duration` — L11345
- `_adsd_lip_sync_prompt` — L11352
- `_adsd_broll_motion_prompt` — L11398
- `_adsd_action_b_motion_prompt` — L11440
- `_adsd_silent_b_motion_prompt` — L11486
- `_adsd_narrated_b_audio_dub_prompt` — L11521
- `_adsd_almighty_audio_dub_prompt` — L11565
- `_postprocess_lip_sync_segment` — L11606
- `_detect_audio_leading_silence` — L11674
- `_postprocess_audio_dub_segment` — L11696
- `_lips_change_repair_segment` — L11807
- `_load_lips_change_requested_turns` — L11892
- `_parse_turn_set` — L11909
- `_load_motion_voice_repair_turns` — L11931
- `_voice_assets_file` — L11943
- `_load_voice_assets` — L11950
- `_select_voice_asset_reference` — L11969
- `_lip_sync_poll_download_and_process` — L12035
- `_lip_sync_one_scene` — L12099
- `step66_adsd_lip_sync` — L12422
- `step65_motion` — L12655
- `step65_grid_multiref_motion_qa` — L12737
- `_sanitize_scene_for_state` — L12766
- `_save_pipeline_state` — L12785
- `_retime_after_audio_dub` — L12809
- `_build_voice_clone_hybrid_audio` — L12847
- `_build_dynamic_bgm` — L12985

---

### 第七步：拼接视频轨
Range: **L13029 – L13260** (232 lines)

**Functions:**
- `step7_concat` — L13030

---

### 第八步：生成 ASS 字幕
Range: **L13261 – L14052** (792 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L13384-14052 (669 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L13262
- `_word_timings_for_subtitle_align` — L13288
- `_align_segments_via_asr` — L13329
- `step8_subtitles` — L13372
- `_read_output_json` — L13784
- `_qa_file_pass` — L13795
- `_ass_has_dialogue` — L13802
- `_write_adsd_delivery_qa` — L13812
- `_write_bgm_only_qa` — L13941

---

### 第九步：最终合成
Range: **L14053 – L14298** (246 lines)

**Functions:**
- `step9_render` — L14054

---

### 第十步：推送 Telegram
Range: **L14299 – L15913** (1615 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L15399-15720 (322 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L15721-15725 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L15726-15789 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L15790-15835 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L15836-15913 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L14668
- `PANTONE_FALLBACK` — L14695
- `FESTIVAL_DATE_TAG` — L14808

**Functions:**
- `_generate_caption` — L14300
- `_overlay_title_on_cover` — L14538
- `_prepare_tg_photo` — L14648
- `_get_pantone_for_date` — L14698
- `_llm_bottom_note` — L14723
- `_get_bottom_note` — L14752
- `_get_date_tag` — L14830
- `_shrink_to_b64` — L14852
- `_llm_check_scenes_anomalies` — L14868
- `_llm_check_cover_unique` — L14921
- `_llm_check_cover_quality` — L14951
- `_try_almanac_cover` — L14993
- `_generate_cover_image` — L15164
- `_async_kickoff_cover_caption` — L15406
- `_await_async_cover_caption` — L15436
- `step10_deliver` — L15460

---

### 主流程
Range: **L15914 – L16091** (178 lines)

**Functions:**
- `_print_execution_plan` — L15915
- `main` — L15963

---
