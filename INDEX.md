# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (17020 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-1997 (1876 lines · 58 fn · 4 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L1998-4231 (2234 lines · 30 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L4232-5353 (1122 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L5354-5905 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L5906-9655 (3750 lines · 81 fn · 6 sub)
- [`第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）`](#第-6-5-步-动态化-hads-vads-默认-on---no-motion-关) — L9656-13946 (4291 lines · 100 fn · 4 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L13947-14178 (232 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L14179-14981 (803 lines · 9 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L14982-15227 (246 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L15228-16842 (1615 lines · 16 fn · 5 sub)
- [`主流程`](#主流程) — L16843-17020 (178 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L1997** (1876 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L308-437 (130 lines)
- _四类 turn 区分 (silent_b PR + action_b 4b PR)_ — L438-1125 (688 lines)
- _工具函数_ — L1126-1475 (350 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L1476-1997 (522 lines)

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
- `EMOTION_STYLE` — L1105
- `EMOTION_STYLE_BRIGHT` — L1117
- `_TG_DASHBOARD_STAGES` — L1139
- `_TG_NOISY_PATTERNS` — L1154
- `_TG_IMMEDIATE_PATTERNS` — L1172
- `GPT_IMAGE2_QUALITY_SUFFIX` — L1405
- `_TOPIC_MODIFIERS` — L1829
- `_TONE_PANTONE_OVERRIDE` — L1846

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
- `_apply_llm_voice_assignment` — L685
- `_voice_asset_is_speech_safe` — L836
- `_podcast_id_to_voice_asset` — L842
- `log` — L1127
- `_tg_send_raw` — L1195
- `_tg_matches` — L1211
- `_tg_summarize` — L1215
- `_tg_dashboard_stage_for` — L1222
- `_tg_progress_bar` — L1230
- `_tg_dashboard_text` — L1236
- `_tg_dashboard_update` — L1254
- `_tg_maybe_digest` — L1291
- `tg` — L1306
- `_wait_image_submit_slot` — L1355
- `_wait_motion_submit_slot` — L1368
- `_is_rate_limited_error` — L1381
- `_is_rate_limited_response` — L1391
- `_inject_image2_quality_suffix` — L1413
- `submit_text_to_image` — L1427
- `req_post` — L1457
- `req_get` — L1471
- `_tg_probe_send` — L1479
- `_tg_probe_delete` — L1499
- `_tg_upload_with_probe_gap` — L1512
- `poll` — L1552
- `poll_podcast` — L1577
- `poll_task_status` — L1599
- `poll_storyboard_task` — L1621
- `chat` — L1647
- `pick_image_model` — L1675
- `detect_topic_meta` — L1700
- `_topic_culture_guard` — L1750
- `_write_cultural_visual_qa` — L1776
- `is_1919_global_topic` — L1823
- `_strip_topic_modifiers` — L1834
- `apply_1919_global_guardrails` — L1852
- `build_1919_global_cover_prompt` — L1881
- `build_shot_blueprint` — L1910
- `ffprobe_duration` — L1936
- `ffprobe_video_size` — L1947
- `_video_decode_probe` — L1968
- `ffmpeg` — L1986

---

### 第一步：双导演生成剧本
Range: **L1998 – L4231** (2234 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L3460-4231 (772 lines)

**Top-level constants:**
- `_ENSEMBLE_CAP_BY_ROUTE` — L2146

**Functions:**
- `_extract_json_array` — L1999
- `_extract_json_object` — L2009
- `_voice_for_speaker` — L2019
- `_adsd_gender_from_voice` — L2055
- `_adsd_infer_gender_from_speaker` — L2063
- `_adsd_gender_lock_phrase` — L2072
- `_adsd_visual_subject_has_gender_conflict` — L2087
- `_adsd_default_roles` — L2099
- `_adsd_allows_media_role` — L2104
- `_adsd_role_candidates` — L2112
- `_adsd_dialogue_shape` — L2135
- `_ensemble_speaker_cap` — L2157
- `_finalize_adsd_turns` — L2170
- `_parse_adsd_override_turns` — L2204
- `_parse_timecode_seconds` — L2295
- `_clean_override_line_text` — L2304
- `_parse_override_script_text` — L2310
- `_adsd_pov_contract` — L2344
- `_load_audit_blacklist_block` — L2357
- `_generate_adsd_dialogue_turns` — L2395
- `_broll_rhythm_reviewer` — L2822
- `_sweep_speaker_field` — L2929
- `_should_run_immersion_qa` — L2989
- `_adsd_immersion_qa_rewrite_turns` — L3012
- `_adsd_visual_contract` — L3076
- `_parse_risk_score` — L3128
- `_check_high_risk_hard_abort` — L3157
- `_maybe_neutralize_topic` — L3184
- `step1_script` — L3223
- `_write_ads_retention_qa` — L4175

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L4232 – L5353** (1122 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L4307
- `_ADSD_POLICY_REWRITE_TERMS` — L4313
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L4404

**Functions:**
- `_openai_tts_fallback` — L4233
- `_edge_tts_fallback` — L4279
- `_sanitize_for_external_api` — L4322
- `_is_content_policy_error` — L4331
- `_rewrite_adsd_tts_text_for_policy` — L4345
- `_record_adsd_tts_rewrite` — L4385
- `_build_silence_mp3` — L4410
- `_audio_duration_seconds` — L4423
- `_text_to_audio_master_voice_timed` — L4435
- `_text_to_audio_master_voice` — L4560
- `step2_master_voice` — L4663
- `_tts_turn_to_audio` — L4791
- `_asr_verify_dialogue_audio` — L4855
- `_asr_verify_dialogue_turns` — L4917
- `_normalize_cn_number_token` — L4959
- `_compact_zh_text` — L4981
- `_write_adsd_asr_text_qa` — L4988
- `_write_adsd_speaker_focus_qa` — L5027
- `_write_adsd_gender_voice_qa` — L5087
- `step2_dialogue_voice` — L5140

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L5354 – L5905** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L5361-5483 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L5484-5518 (35 lines)
- _第二层：字符数插值_ — L5519-5543 (25 lines)
- _第三层：silencedetect 物理校准_ — L5544-5905 (362 lines)

**Functions:**
- `_detect_silences` — L5362
- `_calibrate_boundaries` — L5397
- `_enforce_monotonic` — L5431
- `_manual_override_segments` — L5443
- `_calc_sentence_boundaries` — L5464
- `step345_timeline` — L5575
- `_analyze_bgm_energy_cuts` — L5634
- `_snap_bgm_only_boundaries` — L5697
- `step345_bgm_only_timeline` — L5757

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L5906 – L9655** (3750 lines)

**Sub-sections:**
- _人设符 PR (2026-05-20)_ — L7105-7155 (51 lines)
- _topic-level LLM decomposition + cache (2026-05-21)_ — L7156-7296 (141 lines)
- _era-aware meta_grid 模板系统 (2026-05-21)_ — L7297-7731 (435 lines)
- _Speaker IP Card (2026-05-21)_ — L7732-9488 (1757 lines)
- _审批流程_ — L9489-9545 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L9546-9655 (110 lines)

**Top-level constants:**
- `_CORE_TERMS_STOP_WORDS` — L6301
- `CHARACTER_META_GRID_COSTUMES` — L7111
- `CHARACTER_META_GRID_POSES` — L7112
- `CHARACTER_META_GRID_SCENES` — L7113
- `ADR_SENSITIVE_DIALOGUE_PHRASES` — L7116

**Functions:**
- `_extract_img_url` — L5907
- `_extract_img_urls` — L5929
- `_extract_video_url` — L5962
- `_count_bands` — L5987
- `_detect_contact_sheet_like_image` — L5999
- `_file_sha256` — L6060
- `_load_upload_cache` — L6073
- `_save_upload_cache` — L6082
- `_cached_upload_url` — L6090
- `_store_upload_url` — L6107
- `_guess_upload_mime` — L6117
- `_upload_to_weryai` — L6140
- `_send_for_approval` — L6194
- `_wait_approval` — L6258
- `_render_still_segment` — L6270
- `_extract_core_terms` — L6307
- `_scene_text_visual_alignment` — L6326
- `_write_text_visual_alignment_qa` — L6347
- `_scene_motion_action_plan` — L6370
- `_ensure_motion_action_plan` — L6424
- `_motion_action_block` — L6433
- `_motion_plan_for_qa` — L6461
- `_write_motion_action_plan_qa` — L6471
- `_write_motion_bridge_refs_qa` — L6501
- `_motion_bridge_ref_prompt` — L6508
- `generate_motion_bridge_refs_gpt_image2` — L6541
- `generate_image` — L6654
- `generate_storyboard_images_gpt_image2` — L6701
- `_storyboard_grid_aspect` — L6886
- `_storyboard_grid_cols_rows` — L6893
- `_storyboard_grid_prompt` — L6915
- `_storyboard_grid_prompt_limit` — L6953
- `_is_prompt_limit_response` — L6957
- `_production_storyboard_prompt` — L6963
- `_write_production_storyboard_page_qa` — L6997
- `_character_sheet_prompt` — L7007
- `_is_audit_blocked` — L7133
- `_paraphrase_sensitive_dialogue` — L7146
- `_topic_cache_dir` — L7160
- `_topic_cache_path` — L7166
- `_load_topic_decomposition_cache` — L7179
- `_save_topic_decomposition_cache` — L7197
- `_llm_topic_decomposition` — L7203
- `_director_route_block` — L7350
- `_llm_infer_meta_grid_template` — L7420
- `_resolve_meta_grid_template` — L7477
- `_infer_meta_grid_costume` — L7520
- `_infer_meta_grid_pose` — L7569
- `_adsd_meta_grid_call_prompt` — L7616
- `_meta_grid_panel_index` — L7658
- `_migrate_speaker_ip` — L7738
- `_speaker_ips_dir` — L7763
- `_list_speaker_ips` — L7770
- `_match_speaker_ip` — L7784
- `_build_speaker_ip_context_for_script` — L7804
- `_ip_usage_stats` — L7860
- `_recommend_related_ips` — L7878
- `_save_speaker_ip` — L7903
- `_record_speaker_usage_history` — L7912
- `_format_speaker_usage_history_for_prompt` — L7959
- `_llm_infer_ip_skeleton` — L7977
- `_llm_pick_voice_asset_for_ip` — L8022
- `_auto_incubate_missing_ips` — L8070
- `_character_meta_grid_cache_dir` — L8154
- `_character_meta_grid_cache_path` — L8162
- `_character_meta_grid_path` — L8170
- `generate_character_meta_grid_gpt_image2` — L8176
- `_generate_all_character_meta_grids` — L8334
- `_write_character_sheet_qa` — L8375
- `generate_character_sheet_gpt_image2` — L8385
- `generate_production_storyboard_page_gpt_image2` — L8485
- `_qa_clean_storyboard_panel` — L8548
- `_crop_storyboard_grid_panels` — L8729
- `generate_storyboard_grid_gpt_image2` — L8776
- `_gpt_image2_direct_annotated_aspect` — L9007
- `_gpt_image2_direct_annotated_prompt` — L9014
- `generate_gpt_image2_direct_annotated_storyboards` — L9044
- `_llm_bgm_description` — L9145
- `_bgm_contains_vocals` — L9184
- `generate_bgm` — L9218
- `step6_parallel` — L9335

---

### 第 6.5 步：动态化（HADS/VADS 默认 ON，--no-motion 关）
Range: **L9656 – L13946** (4291 lines)

**Sub-sections:**
- _pipeline state 持久化：让 tools/rerun_downstream.py 跳过 step1-66 局部重跑下游_ — L13683-13725 (43 lines)
- _audio_dub retiming：按 seg 真实长度重算 timeline，避免克隆语音被截_ — L13726-13763 (38 lines)
- _audio_dub voice-clone splice：把 A-roll seg 里的克隆音色拼回主音轨_ — L13764-13901 (138 lines)
- _silent_b BGM 动态浮起：silent_b 区间 BGM 音量 +40%（让 BGM 接管呼吸位）_ — L13902-13946 (45 lines)

**Functions:**
- `_generate_motion_prompts` — L9659
- `_motion_tasks_file` — L9726
- `_motion_qa_file` — L9730
- `_append_motion_qa` — L9734
- `_finalize_motion_qa` — L9758
- `_lip_sync_tasks_file` — L9842
- `_load_motion_tasks` — L9846
- `_save_motion_task` — L9856
- `_remove_motion_task` — L9864
- `_load_lip_sync_tasks` — L9871
- `_save_lip_sync_task` — L9881
- `_remove_lip_sync_task` — L9888
- `_video_visual_motion_qa` — L9895
- `_motion_output_qa` — L9967
- `_has_audio_stream` — L10012
- `_normalize_motion_video` — L10023
- `_motion_poll_and_download` — L10073
- `_build_motion_video_prompt` — L10124
- `_short_board_text` — L10154
- `_wrap_board_text` — L10161
- `_storyboard_font` — L10192
- `_draw_storyboard_arrow` — L10207
- `_build_annotated_storyboard_reference` — L10221
- `_plain_caption_text` — L10322
- `_werydance_caption_request` — L10330
- `_werydance_caption_instruction` — L10357
- `_werydance_negative_prompt` — L10369
- `_motion_reference_prompt` — L10387
- `_motion_audio_dub_prompt` — L10410
- `_motion_audio_dub_poll_and_download` — L10444
- `_try_motion_audio_dub_video` — L10509
- `_try_motion_reference_video` — L10644
- `_motion_one_scene` — L10760
- `_grid_multiref_tasks_file` — L10889
- `_previs_page_tasks_file` — L10893
- `_load_grid_multiref_tasks` — L10897
- `_load_previs_page_tasks` — L10907
- `_save_grid_multiref_task` — L10917
- `_save_previs_page_task` — L10924
- `_remove_grid_multiref_task` — L10931
- `_remove_previs_page_task` — L10938
- `_poll_video_task_download` — L10945
- `_grid_multiref_group_size` — L10994
- `_grid_multiref_duration` — L11002
- `_grid_multiref_segment_max_stretch` — L11018
- `_grid_multiref_prompt` — L11026
- `_write_grid_multiref_motion_qa` — L11074
- `_write_previs_page_motion_qa` — L11084
- `_write_storyboard_trailer_qa` — L11094
- `_write_character_trailer_qa` — L11104
- `_write_grid_multiref_segment_qa` — L11114
- `_motion_compare_record` — L11124
- `_write_storyboard_motion_compare_qa` — L11146
- `_scene_segment_duration` — L11182
- `_apply_grid_multiref_segments` — L11201
- `_previs_page_duration` — L11395
- `_previs_page_group_prompt` — L11405
- `_previs_page_groups` — L11431
- `_storyboard_trailer_duration` — L11446
- `_storyboard_trailer_prompt` — L11456
- `_character_trailer_max_shots` — L11484
- `_character_trailer_shot_duration` — L11492
- `_character_trailer_prompt` — L11506
- `_concat_character_trailer_segments` — L11521
- `_generate_character_trailer_motion` — L11560
- `_multi_trailer_prompt_for_group` — L11668
- `_generate_multi_trailer_segments` — L11691
- `_generate_storyboard_trailer_motion` — L11802
- `_generate_previs_page_motion_segments` — L11877
- `_generate_grid_multiref_motion_segments` — L11989
- `_grid_multiref_concat_groups` — L12159
- `_grid_multiref_concat_groups_partial` — L12176
- `_grid_multiref_concat_paths` — L12194
- `_lip_sync_slot_duration` — L12225
- `_adsd_lip_sync_prompt` — L12232
- `_adsd_broll_motion_prompt` — L12278
- `_adsd_action_b_motion_prompt` — L12320
- `_adsd_silent_b_motion_prompt` — L12366
- `_adsd_narrated_b_audio_dub_prompt` — L12401
- `_adsd_almighty_audio_dub_prompt` — L12445
- `_postprocess_lip_sync_segment` — L12486
- `_detect_audio_leading_silence` — L12558
- `_postprocess_audio_dub_segment` — L12580
- `_lips_change_repair_segment` — L12695
- `_load_lips_change_requested_turns` — L12780
- `_parse_turn_set` — L12797
- `_load_motion_voice_repair_turns` — L12819
- `_voice_assets_file` — L12831
- `_load_voice_assets` — L12838
- `_select_voice_asset_reference` — L12857
- `_lip_sync_poll_download_and_process` — L12923
- `_lip_sync_one_scene` — L12991
- `step66_adsd_lip_sync` — L13315
- `step65_motion` — L13573
- `step65_grid_multiref_motion_qa` — L13655
- `_sanitize_scene_for_state` — L13684
- `_save_pipeline_state` — L13703
- `_retime_after_audio_dub` — L13727
- `_build_voice_clone_hybrid_audio` — L13765
- `_build_dynamic_bgm` — L13903

---

### 第七步：拼接视频轨
Range: **L13947 – L14178** (232 lines)

**Functions:**
- `step7_concat` — L13948

---

### 第八步：生成 ASS 字幕
Range: **L14179 – L14981** (803 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L14302-14981 (680 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L14180
- `_word_timings_for_subtitle_align` — L14206
- `_align_segments_via_asr` — L14247
- `step8_subtitles` — L14290
- `_read_output_json` — L14702
- `_qa_file_pass` — L14713
- `_ass_has_dialogue` — L14720
- `_write_adsd_delivery_qa` — L14730
- `_write_bgm_only_qa` — L14870

---

### 第九步：最终合成
Range: **L14982 – L15227** (246 lines)

**Functions:**
- `step9_render` — L14983

---

### 第十步：推送 Telegram
Range: **L15228 – L16842** (1615 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L16328-16649 (322 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L16650-16654 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L16655-16718 (64 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L16719-16764 (46 lines)
- _尝试 3：小土伯/TG 文件兜底。视频上传链路 SSL 抖动时，压 lite/micro 后用 sendDocument 发文件。_ — L16765-16842 (78 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L15597
- `PANTONE_FALLBACK` — L15624
- `FESTIVAL_DATE_TAG` — L15737

**Functions:**
- `_generate_caption` — L15229
- `_overlay_title_on_cover` — L15467
- `_prepare_tg_photo` — L15577
- `_get_pantone_for_date` — L15627
- `_llm_bottom_note` — L15652
- `_get_bottom_note` — L15681
- `_get_date_tag` — L15759
- `_shrink_to_b64` — L15781
- `_llm_check_scenes_anomalies` — L15797
- `_llm_check_cover_unique` — L15850
- `_llm_check_cover_quality` — L15880
- `_try_almanac_cover` — L15922
- `_generate_cover_image` — L16093
- `_async_kickoff_cover_caption` — L16335
- `_await_async_cover_caption` — L16365
- `step10_deliver` — L16389

---

### 主流程
Range: **L16843 – L17020** (178 lines)

**Functions:**
- `_print_execution_plan` — L16844
- `main` — L16892

---
