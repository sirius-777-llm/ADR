# ADR Code Index

Auto-generated. Source: `run_adr_v8.py` (13018 lines). Regenerate: `python3 tools/generate_index.py`.

## Sections

- [`Module-level (header + global config)`](#module-level--header---global-config) — L1-121 (121 lines · 1 fn · 1 sub)
- [`配置`](#配置) — L122-1491 (1370 lines · 45 fn · 3 sub)
- [`第一步：双导演生成剧本`](#第一步-双导演生成剧本) — L1492-2915 (1424 lines · 22 fn · 1 sub)
- [`第二步：逐句生成音轨（WeryAI Podcast，线程池并发）`](#第二步-逐句生成音轨-weryai-podcast-线程池并发) — L2916-3985 (1070 lines · 20 fn · 0 sub)
- [`第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）`](#第三步---第四步---第五步-时间轴计算-whisper---同步优先剪辑节奏) — L3986-4537 (552 lines · 9 fn · 4 sub)
- [`第六步：并行生成图片 + BGM + 视频片段`](#第六步-并行生成图片---bgm---视频片段) — L4538-6760 (2223 lines · 42 fn · 2 sub)
- [`第 6.5 步：动态化（可选，--with-motion 开启）`](#第-6-5-步-动态化-可选---with-motion-开启) — L6761-10312 (3552 lines · 91 fn · 0 sub)
- [`第七步：拼接视频轨`](#第七步-拼接视频轨) — L10313-10482 (170 lines · 1 fn · 0 sub)
- [`第八步：生成 ASS 字幕`](#第八步-生成-ass-字幕) — L10483-11136 (654 lines · 7 fn · 1 sub)
- [`第九步：最终合成`](#第九步-最终合成) — L11137-11375 (239 lines · 1 fn · 0 sub)
- [`第十步：推送 Telegram`](#第十步-推送-telegram) — L11376-12892 (1517 lines · 16 fn · 4 sub)
- [`主流程`](#主流程) — L12893-13018 (126 lines · 2 fn · 0 sub)

---

### Module-level (header + global config)
Range: **L1 – L121** (121 lines)

**Sub-sections:**
- _老黄历数据模块_ — L29-121 (93 lines)

**Functions:**
- `get_almanac_data` — L57

---

### 配置
Range: **L122 – L1491** (1370 lines)

**Sub-sections:**
- _音色库智能匹配（P3）_ — L290-644 (355 lines)
- _工具函数_ — L645-969 (325 lines)
- _TG 上传 probe-gap 检测共用 helper_ — L970-1491 (522 lines)

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
- `ADSD_ALMIGHTY_AUDIO_DUB_EXPERIMENT` — L268
- `ADSD_CONSECUTIVE_SPEAKER_BATCHING` — L282
- `ADSD_GENDER_FALLBACK_VOICE_ASSET` — L293
- `VOICE_ASSET_AUDIO_DUB_EXPERIMENT` — L411
- `VOICE_ASSET_AUDIO_DUB_PARTIAL_OK` — L419
- `MOTION_VISUAL_QA` — L423
- `MOTION_VOICE_REPAIR` — L431
- `MOTION_VOICE_STRICT_LOCK` — L436
- `WERYDANCE_CAPTIONS` — L441
- `ADSD_ONSITE_POV_MODE` — L453
- `ADSD_LIPS_CHANGE_REPAIR` — L458
- `ADSD_LIPS_CHANGE_ALL` — L463
- `ADS_REPORTER_MODE` — L474
- `ADS_RETENTION_MODE` — L489
- `ADSD_MODE_NAME` — L495
- `EMOTION_STYLE` — L624
- `EMOTION_STYLE_BRIGHT` — L636
- `_TG_DASHBOARD_STAGES` — L658
- `_TG_NOISY_PATTERNS` — L673
- `_TG_IMMEDIATE_PATTERNS` — L691
- `_TOPIC_MODIFIERS` — L1323
- `_TONE_PANTONE_OVERRIDE` — L1340

**Functions:**
- `_is_action_scene` — L302
- `_wuxia_action_panel_prompt` — L309
- `_action_motion_fragment` — L331
- `_infer_emotion_from_text` — L346
- `_emotion_expression_phrase` — L361
- `_infer_needs_lip_sync` — L368
- `_voice_asset_id_for_speaker` — L387
- `log` — L646
- `_tg_send_raw` — L714
- `_tg_matches` — L730
- `_tg_summarize` — L734
- `_tg_dashboard_stage_for` — L741
- `_tg_progress_bar` — L749
- `_tg_dashboard_text` — L755
- `_tg_dashboard_update` — L773
- `_tg_maybe_digest` — L810
- `tg` — L825
- `_wait_image_submit_slot` — L874
- `_wait_motion_submit_slot` — L887
- `_is_rate_limited_error` — L900
- `_is_rate_limited_response` — L910
- `submit_text_to_image` — L922
- `req_post` — L951
- `req_get` — L965
- `_tg_probe_send` — L973
- `_tg_probe_delete` — L993
- `_tg_upload_with_probe_gap` — L1006
- `poll` — L1046
- `poll_podcast` — L1071
- `poll_task_status` — L1093
- `poll_storyboard_task` — L1115
- `chat` — L1141
- `pick_image_model` — L1169
- `detect_topic_meta` — L1194
- `_topic_culture_guard` — L1244
- `_write_cultural_visual_qa` — L1270
- `is_1919_global_topic` — L1317
- `_strip_topic_modifiers` — L1328
- `apply_1919_global_guardrails` — L1346
- `build_1919_global_cover_prompt` — L1375
- `build_shot_blueprint` — L1404
- `ffprobe_duration` — L1430
- `ffprobe_video_size` — L1441
- `_video_decode_probe` — L1462
- `ffmpeg` — L1480

---

### 第一步：双导演生成剧本
Range: **L1492 – L2915** (1424 lines)

**Sub-sections:**
- _外部脚本注入（可选开关）_ — L2225-2915 (691 lines)

**Functions:**
- `_extract_json_array` — L1493
- `_extract_json_object` — L1503
- `_voice_for_speaker` — L1513
- `_adsd_gender_from_voice` — L1549
- `_adsd_infer_gender_from_speaker` — L1557
- `_adsd_gender_lock_phrase` — L1566
- `_adsd_visual_subject_has_gender_conflict` — L1581
- `_adsd_default_roles` — L1593
- `_adsd_allows_media_role` — L1598
- `_adsd_role_candidates` — L1606
- `_adsd_dialogue_shape` — L1622
- `_finalize_adsd_turns` — L1631
- `_parse_adsd_override_turns` — L1654
- `_parse_timecode_seconds` — L1717
- `_clean_override_line_text` — L1726
- `_parse_override_script_text` — L1732
- `_adsd_pov_contract` — L1766
- `_generate_adsd_dialogue_turns` — L1776
- `_adsd_immersion_qa_rewrite_turns` — L1892
- `_adsd_visual_contract` — L1946
- `step1_script` — L1998
- `_write_ads_retention_qa` — L2859

---

### 第二步：逐句生成音轨（WeryAI Podcast，线程池并发）
Range: **L2916 – L3985** (1070 lines)

**Top-level constants:**
- `_SENSITIVE_TERMS` — L2991
- `_ADSD_POLICY_REWRITE_TERMS` — L2997
- `_TEXT_TO_AUDIO_DEFAULT_VOICE` — L3088

**Functions:**
- `_openai_tts_fallback` — L2917
- `_edge_tts_fallback` — L2963
- `_sanitize_for_external_api` — L3006
- `_is_content_policy_error` — L3015
- `_rewrite_adsd_tts_text_for_policy` — L3029
- `_record_adsd_tts_rewrite` — L3069
- `_build_silence_mp3` — L3094
- `_audio_duration_seconds` — L3107
- `_text_to_audio_master_voice_timed` — L3119
- `_text_to_audio_master_voice` — L3244
- `step2_master_voice` — L3347
- `_tts_turn_to_audio` — L3475
- `_asr_verify_dialogue_audio` — L3537
- `_asr_verify_dialogue_turns` — L3579
- `_normalize_cn_number_token` — L3621
- `_compact_zh_text` — L3643
- `_write_adsd_asr_text_qa` — L3650
- `_write_adsd_speaker_focus_qa` — L3689
- `_write_adsd_gender_voice_qa` — L3749
- `step2_dialogue_voice` — L3802

---

### 第三步 + 第四步 + 第五步：时间轴计算（Whisper + 同步优先剪辑节奏）
Range: **L3986 – L4537** (552 lines)

**Sub-sections:**
- _silencedetect 校准工具_ — L3993-4115 (123 lines)
- _第一层：Whisper 构建语速曲线_ — L4116-4150 (35 lines)
- _第二层：字符数插值_ — L4151-4175 (25 lines)
- _第三层：silencedetect 物理校准_ — L4176-4537 (362 lines)

**Functions:**
- `_detect_silences` — L3994
- `_calibrate_boundaries` — L4029
- `_enforce_monotonic` — L4063
- `_manual_override_segments` — L4075
- `_calc_sentence_boundaries` — L4096
- `step345_timeline` — L4207
- `_analyze_bgm_energy_cuts` — L4266
- `_snap_bgm_only_boundaries` — L4329
- `step345_bgm_only_timeline` — L4389

---

### 第六步：并行生成图片 + BGM + 视频片段
Range: **L4538 – L6760** (2223 lines)

**Sub-sections:**
- _审批流程_ — L6594-6650 (57 lines)
- _并行等待审批结果，被拒的后台重做再审_ — L6651-6760 (110 lines)

**Functions:**
- `_extract_img_url` — L4539
- `_extract_img_urls` — L4561
- `_extract_video_url` — L4594
- `_count_bands` — L4619
- `_detect_contact_sheet_like_image` — L4631
- `_guess_upload_mime` — L4685
- `_upload_to_weryai` — L4708
- `_send_for_approval` — L4740
- `_wait_approval` — L4804
- `_render_still_segment` — L4816
- `_scene_text_visual_alignment` — L4830
- `_write_text_visual_alignment_qa` — L4866
- `_scene_motion_action_plan` — L4889
- `_ensure_motion_action_plan` — L4940
- `_motion_action_block` — L4949
- `_motion_plan_for_qa` — L4971
- `_write_motion_action_plan_qa` — L4981
- `_write_motion_bridge_refs_qa` — L5011
- `_motion_bridge_ref_prompt` — L5018
- `generate_motion_bridge_refs_gpt_image2` — L5051
- `generate_image` — L5164
- `generate_storyboard_images_gpt_image2` — L5211
- `_storyboard_grid_aspect` — L5396
- `_storyboard_grid_cols_rows` — L5403
- `_storyboard_grid_prompt` — L5425
- `_storyboard_grid_prompt_limit` — L5456
- `_is_prompt_limit_response` — L5460
- `_production_storyboard_prompt` — L5466
- `_write_production_storyboard_page_qa` — L5500
- `_character_sheet_prompt` — L5510
- `_write_character_sheet_qa` — L5608
- `generate_character_sheet_gpt_image2` — L5618
- `generate_production_storyboard_page_gpt_image2` — L5712
- `_qa_clean_storyboard_panel` — L5775
- `_crop_storyboard_grid_panels` — L5956
- `generate_storyboard_grid_gpt_image2` — L6003
- `_gpt_image2_direct_annotated_aspect` — L6234
- `_gpt_image2_direct_annotated_prompt` — L6241
- `generate_gpt_image2_direct_annotated_storyboards` — L6271
- `_llm_bgm_description` — L6372
- `generate_bgm` — L6411
- `step6_parallel` — L6502

---

### 第 6.5 步：动态化（可选，--with-motion 开启）
Range: **L6761 – L10312** (3552 lines)

**Functions:**
- `_generate_motion_prompts` — L6764
- `_motion_tasks_file` — L6831
- `_motion_qa_file` — L6835
- `_append_motion_qa` — L6839
- `_finalize_motion_qa` — L6863
- `_lip_sync_tasks_file` — L6947
- `_load_motion_tasks` — L6951
- `_save_motion_task` — L6961
- `_remove_motion_task` — L6969
- `_load_lip_sync_tasks` — L6976
- `_save_lip_sync_task` — L6986
- `_remove_lip_sync_task` — L6993
- `_video_visual_motion_qa` — L7000
- `_motion_output_qa` — L7072
- `_has_audio_stream` — L7117
- `_normalize_motion_video` — L7128
- `_motion_poll_and_download` — L7178
- `_build_motion_video_prompt` — L7229
- `_short_board_text` — L7259
- `_wrap_board_text` — L7266
- `_storyboard_font` — L7297
- `_draw_storyboard_arrow` — L7312
- `_build_annotated_storyboard_reference` — L7326
- `_plain_caption_text` — L7427
- `_werydance_caption_request` — L7435
- `_werydance_caption_instruction` — L7462
- `_werydance_negative_prompt` — L7474
- `_motion_reference_prompt` — L7480
- `_motion_audio_dub_prompt` — L7503
- `_motion_audio_dub_poll_and_download` — L7537
- `_try_motion_audio_dub_video` — L7602
- `_try_motion_reference_video` — L7737
- `_motion_one_scene` — L7853
- `_grid_multiref_tasks_file` — L7982
- `_previs_page_tasks_file` — L7986
- `_load_grid_multiref_tasks` — L7990
- `_load_previs_page_tasks` — L8000
- `_save_grid_multiref_task` — L8010
- `_save_previs_page_task` — L8017
- `_remove_grid_multiref_task` — L8024
- `_remove_previs_page_task` — L8031
- `_poll_video_task_download` — L8038
- `_grid_multiref_group_size` — L8087
- `_grid_multiref_duration` — L8095
- `_grid_multiref_segment_max_stretch` — L8111
- `_grid_multiref_prompt` — L8119
- `_write_grid_multiref_motion_qa` — L8138
- `_write_previs_page_motion_qa` — L8148
- `_write_storyboard_trailer_qa` — L8158
- `_write_character_trailer_qa` — L8168
- `_write_grid_multiref_segment_qa` — L8178
- `_motion_compare_record` — L8188
- `_write_storyboard_motion_compare_qa` — L8210
- `_scene_segment_duration` — L8246
- `_apply_grid_multiref_segments` — L8265
- `_previs_page_duration` — L8459
- `_previs_page_group_prompt` — L8469
- `_previs_page_groups` — L8495
- `_storyboard_trailer_duration` — L8510
- `_storyboard_trailer_prompt` — L8520
- `_character_trailer_max_shots` — L8548
- `_character_trailer_shot_duration` — L8556
- `_character_trailer_prompt` — L8570
- `_concat_character_trailer_segments` — L8585
- `_generate_character_trailer_motion` — L8624
- `_multi_trailer_prompt_for_group` — L8732
- `_generate_multi_trailer_segments` — L8755
- `_generate_storyboard_trailer_motion` — L8866
- `_generate_previs_page_motion_segments` — L8941
- `_generate_grid_multiref_motion_segments` — L9053
- `_grid_multiref_concat_groups` — L9205
- `_grid_multiref_concat_groups_partial` — L9222
- `_grid_multiref_concat_paths` — L9240
- `_lip_sync_slot_duration` — L9271
- `_adsd_lip_sync_prompt` — L9278
- `_adsd_broll_motion_prompt` — L9317
- `_adsd_almighty_audio_dub_prompt` — L9354
- `_postprocess_lip_sync_segment` — L9389
- `_postprocess_audio_dub_segment` — L9457
- `_lips_change_repair_segment` — L9533
- `_load_lips_change_requested_turns` — L9618
- `_parse_turn_set` — L9635
- `_load_motion_voice_repair_turns` — L9657
- `_voice_assets_file` — L9669
- `_load_voice_assets` — L9676
- `_select_voice_asset_reference` — L9695
- `_lip_sync_poll_download_and_process` — L9761
- `_lip_sync_one_scene` — L9825
- `step66_adsd_lip_sync` — L10025
- `step65_motion` — L10203
- `step65_grid_multiref_motion_qa` — L10285

---

### 第七步：拼接视频轨
Range: **L10313 – L10482** (170 lines)

**Functions:**
- `step7_concat` — L10314

---

### 第八步：生成 ASS 字幕
Range: **L10483 – L11136** (654 lines)

**Sub-sections:**
- _字幕分段：LLM 智能语义断句_ — L10522-11136 (615 lines)

**Functions:**
- `_werydance_caption_covered_turns` — L10484
- `step8_subtitles` — L10510
- `_read_output_json` — L10878
- `_qa_file_pass` — L10889
- `_ass_has_dialogue` — L10896
- `_write_adsd_delivery_qa` — L10906
- `_write_bgm_only_qa` — L11025

---

### 第九步：最终合成
Range: **L11137 – L11375** (239 lines)

**Functions:**
- `step9_render` — L11138

---

### 第十步：推送 Telegram
Range: **L11376 – L12892** (1517 lines)

**Sub-sections:**
- _异步封面 + caption（与 step6-9 并发）_ — L12476-12791 (316 lines)
- _SSL 假阴性防护：见模块级 _tg_probe_send / _tg_probe_delete_ — L12792-12796 (5 lines)
- _尝试 1：requests（timeout 放大到 600s），前后 probe 跳号检测_ — L12797-12838 (42 lines)
- _尝试 2：curl fallback（更稳定，不受 httpx/urllib3 限制），同样跳号检测_ — L12839-12892 (54 lines)

**Top-level constants:**
- `PANTONE_JIEQI` — L11745
- `PANTONE_FALLBACK` — L11772
- `FESTIVAL_DATE_TAG` — L11885

**Functions:**
- `_generate_caption` — L11377
- `_overlay_title_on_cover` — L11615
- `_prepare_tg_photo` — L11725
- `_get_pantone_for_date` — L11775
- `_llm_bottom_note` — L11800
- `_get_bottom_note` — L11829
- `_get_date_tag` — L11907
- `_shrink_to_b64` — L11929
- `_llm_check_scenes_anomalies` — L11945
- `_llm_check_cover_unique` — L11998
- `_llm_check_cover_quality` — L12028
- `_try_almanac_cover` — L12070
- `_generate_cover_image` — L12241
- `_async_kickoff_cover_caption` — L12483
- `_await_async_cover_caption` — L12513
- `step10_deliver` — L12537

---

### 主流程
Range: **L12893 – L13018** (126 lines)

**Functions:**
- `_print_execution_plan` — L12894
- `main` — L12942

---
