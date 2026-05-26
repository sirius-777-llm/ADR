# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (16669 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-1941 (1820 lines · 57 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L1942-4077 (2136 lines · 28 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L4078-5181 (1104 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L5182-5733 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L5734-9323 (3590 lines · 75 fn · 6 sub)
- [`第 6.5 步：动态化（可选，--with-motion 开启）`](#第-6-5-步-动态化-可选---with-motion-开启) — L9324-13606 (4283 lines · 100 fn · 4 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L13607-13838 (232 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L13839-14630 (792 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L14631-14876 (246 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L14877-16491 (1615 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L16492-16669 (178 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L1941** (1820 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L298-427 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L428-1069 (642 lines)
- _工具函数_ — L1070-1419 (350 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1420-1941 (522 lines)

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
- `VOICE_ASSET_AUDIO_DUB_EXPERIMENT` — L821
- `VOICE_ASSET_AUDIO_DUB_PARTIAL_OK` — L829
- `MOTION_VISUAL_QA` — L833
- `MOTION_VOICE_REPAIR` — L841
- `MOTION_VOICE_STRICT_LOCK` — L846
- `WERYDANCE_CAPTIONS` — L851
- `ADSD_ONSITE_POV_MODE` — L863
- `ADSD_LIPS_CHANGE_REPAIR` — L868
- `ADSD_LIPS_CHANGE_ALL` — L873
- `ADS_REPORTER_MODE` — L884
- `ADS_STORYBOARD_FLOW_DEFAULT` — L901
- `ADS_RETENTION_MODE` — L914
- `ADSD_MODE_NAME` — L920
- `EMOTION_STYLE` — L1049
- `EMOTION_STYLE_BRIGHT` — L1061
- `_TG_DASHBOARD_STAGES` — L1083
- `_TG_NOISY_PATTERNS` — L1098
- `_TG_IMMEDIATE_PATTERNS` — L1116
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1349
- `_TOPIC_MODIFIERS` — L1773
- `_TONE_PANTONE_OVERRIDE` — L1790

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
- `_podcast_id_to_voice_asset` — L812
- `log` — L1071
- `_tg_send_raw` — L1139
- `_tg_matches` — L1155
- `_tg_summarize` — L1159
- `_tg_dashboard_stage_for` — L1166
- `_tg_progress_bar` — L1174
- `_tg_dashboard_text` — L1180
- `_tg_dashboard_update` — L1198
- `_tg_maybe_digest` — L1235
- `tg` — L1250
- `_wait_image_submit_slot` — L1299
- `_wait_motion_submit_slot` — L1312
- `_is_rate_limited_error` — L1325
- `_is_rate_limited_response` — L1335
- `_inject_image2_quality_suffix` — L1357
- `submit_text_to_image` — L1371
- `req_post` — L1401
- `req_get` — L1415
- `_tg_probe_send` — L1423
- `_tg_probe_delete` — L1443
- `_tg_upload_with_probe_gap` — L1456
- `poll` — L1496
- `poll_podcast` — L1521
- `poll_task_status` — L1543
- `poll_storyboard_task` — L1565
- `chat` — L1591
- `pick_image_model` — L1619
- `detect_topic_meta` — L1644
- `_topic_culture_guard` — L1694
- `_write_cultural_visual_qa` — L1720
- `is_1919_global_topic` — L1767
- `_strip_topic_modifiers` — L1778
- `apply_1919_global_guardrails` — L1796
- `build_1919_global_cover_prompt` — L1825
- `build_shot_blueprint` — L1854
- `ffprobe_duration` — L1880
- `ffprobe_video_size` — L1891
- `_video_decode_probe` — L1912
- `ffmpeg` — L1930

---

### 第一步：双导演生成剧本
Range: **L1942 – L4077** (2136 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L3345-4077 (733 lines)

**Functions:**
- `_extract_json_array` — L1943
- `_extract_json_object` — L1953
- `_voice_for_speaker` — L1963
- `_adsd_gender_from_voice` — L1999
- `_adsd_infer_gender_from_speaker` — L2007
- `_adsd_gender_lock_phrase` — L2016
- `_adsd_visual_subject_has_gender_conflict` — L2031
- `_adsd_default_roles` — L2043
- `_adsd_allows_media_role` — L2048
- `_adsd_role_candidates` — L2056
- `_adsd_dialogue_shape` — L2079
- `_finalize_adsd_turns` — L2088
- `_parse_adsd_override_turns` — L2122
- `_parse_timecode_seconds` — L2213
- `_clean_override_line_text` — L2222
- `_parse_override_script_text` — L2228
- `_adsd_pov_contract` — L2262
- `_load_audit_blacklist_block` — L2275
- `_generate_adsd_dialogue_turns` — L2313
- `_broll_rhythm_reviewer` — L2736
- `_sweep_speaker_field` — L2843
- `_adsd_immersion_qa_rewrite_turns` — L2903
- `_adsd_visual_contract` — L2961
- `_parse_risk_score` — L3013
- `_check_high_risk_hard_abort` — L3042
- `_maybe_neutralize_topic` — L3069
- `step1_script` — L3108
- `_write_ads_retention_qa` — L4021

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L4078 – L5181** (1104 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L4153
- `_ADSD_POLICY_REWRITE_TERMS` — L4159
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L4250

**Functions:**
- `_openai_tts_fallback` — L4079
- `_edge_tts_fallback` — L4125
- `_sanitize_for_external_api` — L4168
- `_is_content_policy_error` — L4177
- `_rewrite_adsd_tts_text_for_policy` — L4191
- `_record_adsd_tts_rewrite` — L4231
- `_build_silence_mp3` — L4256
- `_audio_duration_seconds` — L4269
- `_text_to_audio_master_voice_timed` — L4281
- `_text_to_audio_master_voice` — L4406
- `step2_master_voice` — L4509
- `_tts_turn_to_audio` — L4637
- `_asr_verify_dialogue_audio` — L4701
- `_asr_verify_dialogue_turns` — L4763
- `_normalize_cn_number_token` — L4805
- `_compact_zh_text` — L4827
- `_write_adsd_asr_text_qa` — L4834
- `_write_adsd_speaker_focus_qa` — L4873
- `_write_adsd_gender_voice_qa` — L4933
- `step2_dialogue_voice` — L4986

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L5182 – L5733** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L5189-5311 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L5312-5346 (35 lines)
- _第二层：字符数插值_ — L5347-5371 (25 lines)
- _第三层：silencedetect 物理校准_ — L5372-5733 (362 lines)

**Functions:**
- `_detect_silences` — L5190
- `_calibrate_boundaries` — L5225
- `_enforce_monotonic` — L5259
- `_manual_override_segments` — L5271
- `_calc_sentence_boundaries` — L5292
- `step345_timeline` — L5403
- `_analyze_bgm_energy_cuts` — L5462
- `_snap_bgm_only_boundaries` — L5525
- `step345_bgm_only_timeline` — L5585

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L5734 – L9323** (3590 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L6837-6887 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L6888-7028 (141 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L7029-7429 (401 lines)
- _Speaker IP Card (2026-05-21)_ — L7430-9156 (1727 lines)
- _审批流程_ — L9157-9213 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L9214-9323 (110 lines)

**Top-level constants:**
- `CHARACTER_META_GRID_COSTUMES` — L6843
- `CHARACTER_META_GRID_POSES` — L6844
- `CHARACTER_META_GRID_SCENES` — L6845
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L6848

**Functions:**
- `_extract_img_url` — L5735
- `_extract_img_urls` — L5757
- `_extract_video_url` — L5790
- `_count_bands` — L5815
- `_detect_contact_sheet_like_image` — L5827
- `_guess_upload_mime` — L5881
- `_upload_to_weryai` — L5904
- `_send_for_approval` — L5936
- `_wait_approval` — L6000
- `_render_still_segment` — L6012
- `_scene_text_visual_alignment` — L6043
- `_write_text_visual_alignment_qa` — L6079
- `_scene_motion_action_plan` — L6102
- `_ensure_motion_action_plan` — L6156
- `_motion_action_block` — L6165
- `_motion_plan_for_qa` — L6193
- `_write_motion_action_plan_qa` — L6203
- `_write_motion_bridge_refs_qa` — L6233
- `_motion_bridge_ref_prompt` — L6240
- `generate_motion_bridge_refs_gpt_image2` — L6273
- `generate_image` — L6386
- `generate_storyboard_images_gpt_image2` — L6433
- `_storyboard_grid_aspect` — L6618
- `_storyboard_grid_cols_rows` — L6625
- `_storyboard_grid_prompt` — L6647
- `_storyboard_grid_prompt_limit` — L6685
- `_is_prompt_limit_response` — L6689
- `_production_storyboard_prompt` — L6695
- `_write_production_storyboard_page_qa` — L6729
- `_character_sheet_prompt` — L6739
- `_is_audit_blocked` — L6865
- `_paraphrase_sensitive_dialogue` — L6878
- `_topic_cache_dir` — L6892
- `_topic_cache_path` — L6898
- `_load_topic_decomposition_cache` — L6911
- `_save_topic_decomposition_cache` — L6929
- `_llm_topic_decomposition` — L6935
- `_director_route_block` — L7082
- `_llm_infer_meta_grid_template` — L7152
- `_resolve_meta_grid_template` — L7209
- `_infer_meta_grid_costume` — L7252
- `_infer_meta_grid_pose` — L7301
- `_adsd_meta_grid_call_prompt` — L7348
- `_meta_grid_panel_index` — L7390
- `_migrate_speaker_ip` — L7436
- `_speaker_ips_dir` — L7461
- `_list_speaker_ips` — L7468
- `_match_speaker_ip` — L7482
- `_build_speaker_ip_context_for_script` — L7502
- `_ip_usage_stats` — L7558
- `_recommend_related_ips` — L7576
- `_save_speaker_ip` — L7601
- `_record_speaker_usage_history` — L7610
- `_format_speaker_usage_history_for_prompt` — L7657
- `_llm_infer_ip_skeleton` — L7675
- `_llm_pick_voice_asset_for_ip` — L7720
- `_auto_incubate_missing_ips` — L7768
- `_character_meta_grid_cache_dir` — L7852
- `_character_meta_grid_cache_path` — L7860
- `_character_meta_grid_path` — L7866
- `generate_character_meta_grid_gpt_image2` — L7872
- `_generate_all_character_meta_grids` — L8002
- `_write_character_sheet_qa` — L8043
- `generate_character_sheet_gpt_image2` — L8053
- `generate_production_storyboard_page_gpt_image2` — L8153
- `_qa_clean_storyboard_panel` — L8216
- `_crop_storyboard_grid_panels` — L8397
- `generate_storyboard_grid_gpt_image2` — L8444
- `_gpt_image2_direct_annotated_aspect` — L8675
- `_gpt_image2_direct_annotated_prompt` — L8682
- `generate_gpt_image2_direct_annotated_storyboards` — L8712
- `_llm_bgm_description` — L8813
- `_bgm_contains_vocals` — L8852
- `generate_bgm` — L8886
- `step6_parallel` — L9003

---

### 第 6.5 步：动态化（可选，--with-motion 开启）
Range: **L9324 – L13606** (4283 lines)

**Sub-sections:**
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L13343-13385 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L13386-13423 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回主音轨_ — L13424-13561 (138 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L13562-13606 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L9327
- `_motion_tasks_file` — L9394
- `_motion_qa_file` — L9398
- `_append_motion_qa` — L9402
- `_finalize_motion_qa` — L9426
- `_lip_sync_tasks_file` — L9510
- `_load_motion_tasks` — L9514
- `_save_motion_task` — L9524
- `_remove_motion_task` — L9532
- `_load_lip_sync_tasks` — L9539
- `_save_lip_sync_task` — L9549
- `_remove_lip_sync_task` — L9556
- `_video_visual_motion_qa` — L9563
- `_motion_output_qa` — L9635
- `_has_audio_stream` — L9680
- `_normalize_motion_video` — L9691
- `_motion_poll_and_download` — L9741
- `_build_motion_video_prompt` — L9792
- `_short_board_text` — L9822
- `_wrap_board_text` — L9829
- `_storyboard_font` — L9860
- `_draw_storyboard_arrow` — L9875
- `_build_annotated_storyboard_reference` — L9889
- `_plain_caption_text` — L9990
- `_werydance_caption_request` — L9998
- `_werydance_caption_instruction` — L10025
- `_werydance_negative_prompt` — L10037
- `_motion_reference_prompt` — L10055
- `_motion_audio_dub_prompt` — L10078
- `_motion_audio_dub_poll_and_download` — L10112
- `_try_motion_audio_dub_video` — L10177
- `_try_motion_reference_video` — L10312
- `_motion_one_scene` — L10428
- `_grid_multiref_tasks_file` — L10557
- `_previs_page_tasks_file` — L10561
- `_load_grid_multiref_tasks` — L10565
- `_load_previs_page_tasks` — L10575
- `_save_grid_multiref_task` — L10585
- `_save_previs_page_task` — L10592
- `_remove_grid_multiref_task` — L10599
- `_remove_previs_page_task` — L10606
- `_poll_video_task_download` — L10613
- `_grid_multiref_group_size` — L10662
- `_grid_multiref_duration` — L10670
- `_grid_multiref_segment_max_stretch` — L10686
- `_grid_multiref_prompt` — L10694
- `_write_grid_multiref_motion_qa` — L10742
- `_write_previs_page_motion_qa` — L10752
- `_write_storyboard_trailer_qa` — L10762
- `_write_character_trailer_qa` — L10772
- `_write_grid_multiref_segment_qa` — L10782
- `_motion_compare_record` — L10792
- `_write_storyboard_motion_compare_qa` — L10814
- `_scene_segment_duration` — L10850
- `_apply_grid_multiref_segments` — L10869
- `_previs_page_duration` — L11063
- `_previs_page_group_prompt` — L11073
- `_previs_page_groups` — L11099
- `_storyboard_trailer_duration` — L11114
- `_storyboard_trailer_prompt` — L11124
- `_character_trailer_max_shots` — L11152
- `_character_trailer_shot_duration` — L11160
- `_character_trailer_prompt` — L11174
- `_concat_character_trailer_segments` — L11189
- `_generate_character_trailer_motion` — L11228
- `_multi_trailer_prompt_for_group` — L11336
- `_generate_multi_trailer_segments` — L11359
- `_generate_storyboard_trailer_motion` — L11470
- `_generate_previs_page_motion_segments` — L11545
- `_generate_grid_multiref_motion_segments` — L11657
- `_grid_multiref_concat_groups` — L11827
- `_grid_multiref_concat_groups_partial` — L11844
- `_grid_multiref_concat_paths` — L11862
- `_lip_sync_slot_duration` — L11893
- `_adsd_lip_sync_prompt` — L11900
- `_adsd_broll_motion_prompt` — L11946
- `_adsd_action_b_motion_prompt` — L11988
- `_adsd_silent_b_motion_prompt` — L12034
- `_adsd_narrated_b_audio_dub_prompt` — L12069
- `_adsd_almighty_audio_dub_prompt` — L12113
- `_postprocess_lip_sync_segment` — L12154
- `_detect_audio_leading_silence` — L12222
- `_postprocess_audio_dub_segment` — L12244
- `_lips_change_repair_segment` — L12355
- `_load_lips_change_requested_turns` — L12440
- `_parse_turn_set` — L12457
- `_load_motion_voice_repair_turns` — L12479
- `_voice_assets_file` — L12491
- `_load_voice_assets` — L12498
- `_select_voice_asset_reference` — L12517
- `_lip_sync_poll_download_and_process` — L12583
- `_lip_sync_one_scene` — L12651
- `step66_adsd_lip_sync` — L12975
- `step65_motion` — L13233
- `step65_grid_multiref_motion_qa` — L13315
- `_sanitize_scene_for_state` — L13344
- `_save_pipeline_state` — L13363
- `_retime_after_audio_dub` — L13387
- `_build_voice_clone_hybrid_audio` — L13425
- `_build_dynamic_bgm` — L13563

---

### 第七步：拼接视频轨
Range: **L13607 – L13838** (232 lines)

**Functions:**
- `step7_concat` — L13608

---

### 第八步：生成 ASS 字幕
Range: **L13839 – L14630** (792 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L13962-14630 (669 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L13840
- `_word_timings_for_subtitle_align` — L13866
- `_align_segments_via_asr` — L13907
- `step8_subtitles` — L13950
- `_read_output_json` — L14362
- `_qa_file_pass` — L14373
- `_ass_has_dialogue` — L14380
- `_write_adsd_delivery_qa` — L14390
- `_write_bgm_only_qa` — L14519

---

### 第九步：最终合成
Range: **L14631 – L14876** (246 lines)

**Functions:**
- `step9_render` — L14632

---

### 第十步：推送 Telegram
Range: **L14877 – L16491** (1615 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L15977-16298 (322 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L16299-16303 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L16304-16367 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L16368-16413 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L16414-16491 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L15246
- `PANTONE_FALLBACK` — L15273
- `FESTIVAL_DATE_TAG` — L15386

**Functions:**
- `_generate_caption` — L14878
- `_overlay_title_on_cover` — L15116
- `_prepare_tg_photo` — L15226
- `_get_pantone_for_date` — L15276
- `_llm_bottom_note` — L15301
- `_get_bottom_note` — L15330
- `_get_date_tag` — L15408
- `_shrink_to_b64` — L15430
- `_llm_check_scenes_anomalies` — L15446
- `_llm_check_cover_unique` — L15499
- `_llm_check_cover_quality` — L15529
- `_try_almanac_cover` — L15571
- `_generate_cover_image` — L15742
- `_async_kickoff_cover_caption` — L15984
- `_await_async_cover_caption` — L16014
- `step10_deliver` — L16038

---

### 主流程
Range: **L16492 – L16669** (178 lines)

**Functions:**
- `_print_execution_plan` — L16493
- `main` — L16541

---
