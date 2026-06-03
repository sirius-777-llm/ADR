#!/usr/bin/env python3
"""B57 · 全自动 voice 参考一致性审计器 (ffmpeg + numpy, 无重依赖)

多音色顽疾真根因 = 参考音频脏: 库内多数 voice_asset 从 youtube diarization 自动切 4 条 ref,
cluster 偶尔切错混入别的说话人 (罗翔 ref_03/04 实测是 imposter). 本工具用纯声学特征
(MFCC + F0 + 频谱质心) 做离群检测, 揪出疑似 imposter 参考, 取代人工听辨。

核心方法 (v2):
  1. 全库所有 clip 提特征 → 全局稳健归一化 (median/MAD), 让欧氏距离落到**绝对**尺度
     (同说话人 ~3-4, 不同说话人 ~6-10 — 实测罗翔清洗对 3.32);
  2. 每个 asset 内部按**绝对阈值 T 单链聚类**: 全在一簇 → clean; 裂成多簇(簇间 >T)
     = 真有不同说话人混入 → 少数簇标 imposter; 2v2 → even_split 交人工。
  绝对阈值是关键: per-asset 相对间隙会把自然变异误判, 全局绝对尺度只在真跨说话人时触发。

约束: 本机只有 numpy + ffmpeg。策略 (codex review-spec): report-first, 高置信才自动隔离, 永不盲删。

用法:
  python3 tools/audit_voice_consistency.py                      # 审全库 (跳过 verified), 只读报告
  python3 tools/audit_voice_consistency.py --calibrate          # 打印全局距离分布帮选阈值 T
  python3 tools/audit_voice_consistency.py --golden             # 罗翔 4 条黄金回归测试
  python3 tools/audit_voice_consistency.py --asset external_xxx
  python3 tools/audit_voice_consistency.py --md                 # markdown 全量
  python3 tools/audit_voice_consistency.py --apply              # 高置信自动隔离 (先 backup, 保留 ≥2)
"""
import argparse
import json
import os
import subprocess
import sys
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "voice_assets" / "voice_assets.json"
REF_ROOT = ROOT / "voice_assets" / "references"
QUARANTINE = ROOT / "voice_assets" / "_quarantine"
REPORT_PATH = ROOT / "voice_assets" / "voice_consistency_audit.json"

SR = 16000
N_FFT = 512
N_MEL = 26
N_MFCC = 13
FRAME = int(0.025 * SR)
HOP = int(0.010 * SR)
SILENCE_RMS = 0.005
MIN_SECONDS = 0.5
DEFAULT_T = 6.0          # 全局尺度下的"跨说话人"绝对距离阈值 (校准得出)

# ---------- 特征提取 (向量化纯 numpy) ----------

def decode(path: str) -> np.ndarray | None:
    try:
        cmd = ["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1",
               "-ar", str(SR), "-f", "s16le", "-"]
        raw = subprocess.run(cmd, capture_output=True, timeout=60).stdout
        if not raw:
            return None
        return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    except Exception:
        return None


def _mel_filterbank() -> np.ndarray:
    def hz2mel(f): return 2595.0 * np.log10(1 + f / 700.0)
    def mel2hz(m): return 700.0 * (10 ** (m / 2595.0) - 1)
    mels = np.linspace(hz2mel(0), hz2mel(8000), N_MEL + 2)
    hz = mel2hz(mels)
    bins = np.floor((N_FFT + 1) * hz / SR).astype(int)
    fb = np.zeros((N_MEL, N_FFT // 2 + 1))
    for i in range(1, N_MEL + 1):
        l, c, r = bins[i - 1], bins[i], bins[i + 1]
        for k in range(l, c):
            if c > l:
                fb[i - 1, k] = (k - l) / (c - l)
        for k in range(c, r):
            if r > c:
                fb[i - 1, k] = (r - k) / (r - c)
    return fb


def _dct_basis() -> np.ndarray:
    n = np.arange(N_MEL)
    return np.array([np.cos(np.pi * i * (2 * n + 1) / (2 * N_MEL)) for i in range(N_MFCC)])


_FB = _mel_filterbank()
_DCT = _dct_basis()
_FREQS = np.fft.rfftfreq(N_FFT, 1.0 / SR)


def extract_features(x: np.ndarray) -> np.ndarray | None:
    if x is None or len(x) < SR * MIN_SECONDS:
        return None
    x = np.append(x[0], x[1:] - 0.97 * x[:-1])
    n_frames = 1 + (len(x) - FRAME) // HOP
    if n_frames < 3:
        return None
    idx = np.arange(FRAME)[None, :] + HOP * np.arange(n_frames)[:, None]
    frames = x[idx] * np.hanning(FRAME)[None, :]
    rms = np.sqrt(np.mean(frames ** 2, axis=1))
    voiced = rms > SILENCE_RMS
    if voiced.sum() < 3:
        voiced = rms > (np.median(rms) * 0.5)
    if voiced.sum() < 3:
        return None
    fr = frames[voiced]
    mag = np.abs(np.fft.rfft(fr, N_FFT, axis=1)) + 1e-9
    spec = mag ** 2
    mel = np.log((spec @ _FB.T) + 1e-9)
    mfcc = (mel @ _DCT.T)[:, 1:N_MFCC]                          # 丢 c0 (能量)
    centroid = (spec * _FREQS[None, :]).sum(1) / (spec.sum(1) + 1e-9)
    ceps = np.fft.irfft(np.log(mag), N_FFT, axis=1)
    qmin, qmax = int(SR / 400), int(SR / 80)
    qpeak = np.argmax(ceps[:, qmin:qmax], axis=1) + qmin
    f0 = SR / np.maximum(qpeak, 1)
    return np.concatenate([
        mfcc.mean(0), mfcc.std(0),
        [np.median(centroid), centroid.std(), np.median(f0), f0.std()],
    ])


# ---------- 单链聚类 (绝对阈值) ----------

def _components(D: np.ndarray, t: float) -> list[list[int]]:
    """距离 <t 即同簇 (单链/连通分量, union-find)。"""
    n = D.shape[0]
    parent = list(range(n))
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for i in range(n):
        for j in range(i + 1, n):
            if D[i, j] < t:
                parent[find(i)] = find(j)
    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    return sorted(groups.values(), key=len, reverse=True)


# ---------- 变体过滤 (raw / speech_band 同段不同处理) ----------

def _canonical_clips(clip_paths: list[str]) -> list[str]:
    """同一段的 _speech_band 变体若有非变体兄弟则丢弃, 避免按处理方式误聚类。"""
    by_canon = {}
    for p in clip_paths:
        base = os.path.basename(p)
        canon = base.replace("_speech_band", "").replace("_raw", "")
        by_canon.setdefault(canon, []).append(p)
    out = []
    for canon, variants in by_canon.items():
        non_band = [v for v in variants if "speech_band" not in os.path.basename(v)]
        out.append((non_band or variants)[0])
    return sorted(out)


# ---------- 单 asset 审计 ----------

def audit_asset(asset_id, clip_paths, feats_by_path, gmed, gscale, t) -> dict:
    clip_paths = _canonical_clips(clip_paths)
    valid, bad, feats = [], [], []
    for p in clip_paths:
        f = feats_by_path.get(p)
        if f is None:
            bad.append(p)
        else:
            valid.append(p); feats.append(f)
    n = len(valid)
    result = {"asset_id": asset_id, "n_clips": len(clip_paths), "n_valid": n,
              "bad_clips": [os.path.basename(b) for b in bad], "clips": [], "verdict": ""}
    if n < 3:
        result["verdict"] = "insufficient"
        result["clips"] = [{"clip": os.path.basename(p), "path": p, "suspect": False, "confidence": 0.0} for p in valid]
        return result

    Z = (np.array(feats) - gmed) / gscale                       # 全局归一化
    D = np.sqrt(((Z[:, None, :] - Z[None, :, :]) ** 2).sum(-1))
    dup = [(os.path.basename(valid[i]), os.path.basename(valid[j]))
           for i in range(n) for j in range(i + 1, n) if D[i, j] < 0.05]
    if dup:
        result["duplicate_pairs"] = dup

    comps = _components(D, t)                                    # 绝对阈值单链聚类
    core = set(comps[0])                                         # 最大簇 = 推定真说话人
    suspects = [i for i in range(n) if i not in core]
    # 置信: 离群片到核心最近距离相对阈值的余量
    def conf_of(i):
        dmin = min(D[i, j] for j in core)
        return float(min(1.0, (dmin - t) / t)) if dmin > t else 0.0

    for i in range(n):
        result["clips"].append({
            "clip": os.path.basename(valid[i]), "path": valid[i],
            "nn_dist": round(float(min(D[i, j] for j in range(n) if j != i)), 2),
            "in_core": i in core, "suspect": i not in core,
            "confidence": round(conf_of(i), 3) if i not in core else 0.0,
        })

    result["core_clips"] = [os.path.basename(valid[i]) for i in sorted(core)]
    result["n_clusters"] = len(comps)
    n_susp = len(suspects)
    if n_susp == 0:
        result["verdict"] = "clean"
    elif len(core) > n_susp:
        result["verdict"] = "polluted"          # 多数核心 + 少数离群 → 可自动隔离
    elif len(core) == n_susp:
        result["verdict"] = "even_split"         # 2v2 → 交人工 (谁真需外部信息)
    else:
        result["verdict"] = "ambiguous"
    return result


# ---------- 注册表 ----------

def load_registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def asset_clip_paths(asset: dict) -> list[str]:
    out = []
    for r in (asset.get("reference_audios") or []):
        p = r.get("path") if isinstance(r, dict) else r
        if p:
            out.append(str(ROOT / p) if not os.path.isabs(p) else p)
    return out


def is_verified(asset: dict) -> bool:
    q = str(asset.get("qa_status", "")).lower()
    return "verified" in q or "clean" in q


# ---------- 收集 + 全局归一化 ----------

def collect_targets(args) -> list[tuple[str, list[str]]]:
    if args.golden:
        return [("luo_xiang(golden)", sorted(str(p) for p in (REF_ROOT / "luo_xiang").glob("*.wav")))]
    if args.clips_dir:
        d = Path(args.clips_dir)
        return [(d.name, sorted(str(p) for p in d.glob("*.wav")) + sorted(str(p) for p in d.glob("*.mp3")))]
    reg = load_registry()
    out = []
    for a in reg.get("assets", []):
        aid = a.get("voice_id", "")
        if args.asset and aid != args.asset:
            continue
        if not args.asset and not args.golden and not args.include_verified and is_verified(a):
            continue
        clips = asset_clip_paths(a)
        if clips:
            out.append((aid, clips))
    return out


def extract_all(targets) -> dict:
    feats = {}
    allp = {p for _, clips in targets for p in clips}
    for p in allp:
        feats[p] = extract_features(decode(p))
    return feats


def global_stats(feats_by_path: dict):
    M = np.array([f for f in feats_by_path.values() if f is not None])
    med = np.median(M, axis=0)
    mad = np.median(np.abs(M - med), axis=0) * 1.4826
    scale = np.where(mad < 1e-6, M.std(0) + 1e-9, mad)
    return med, scale, M


# ---------- 输出 ----------

def print_summary(results, md=False):
    rank = {"polluted": 0, "even_split": 1, "ambiguous": 2, "insufficient": 3, "clean": 4}
    icon = {"polluted": "🔴", "even_split": "🟠", "ambiguous": "🟡", "insufficient": "⚪", "clean": "🟢"}
    results = sorted(results, key=lambda r: (rank.get(r["verdict"], 9), -r["n_valid"]))
    cnt = {v: sum(1 for r in results if r["verdict"] == v) for v in rank}
    print(f"\n=== voice 参考一致性审计: {len(results)} asset · 🔴污染 {cnt['polluted']} · 🟠对半 {cnt['even_split']} · 🟡可疑 {cnt['ambiguous']} · 🟢干净 {cnt['clean']} ===")
    for r in results:
        if r["verdict"] == "clean" and not md:
            continue
        line = f"{icon.get(r['verdict'],'?')} {r['asset_id']:42s} {r['verdict']:13s} 有效{r['n_valid']}/{r['n_clips']}"
        if r.get("bad_clips"):
            line += f" 坏{len(r['bad_clips'])}"
        print(line)
        for c in r["clips"]:
            if c.get("suspect"):
                print(f"      ⮑ imposter? {c['clip']:22s} nn={c.get('nn_dist')} conf={c['confidence']}")
        if r.get("duplicate_pairs"):
            print(f"      ⮑ 重复片: {r['duplicate_pairs']}")


def main():
    ap = argparse.ArgumentParser(description="B57 voice 参考一致性审计器")
    ap.add_argument("--asset")
    ap.add_argument("--clips-dir")
    ap.add_argument("--golden", action="store_true", help="罗翔 4 条黄金回归测试")
    ap.add_argument("--calibrate", action="store_true", help="打印全局距离分布帮选阈值")
    ap.add_argument("--t", type=float, default=DEFAULT_T, help=f"跨说话人绝对距离阈值 (默认 {DEFAULT_T})")
    ap.add_argument("--min-confidence", type=float, default=0.5)
    ap.add_argument("--include-verified", action="store_true")
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    targets = collect_targets(args)
    feats = extract_all(targets)
    gmed, gscale, M = global_stats(feats)

    if args.calibrate:
        # 全库 within-asset nearest-neighbor 距离分布 (同说话人主导) + 全 pairwise
        nn, allpair = [], []
        for aid, clips in targets:
            clips = _canonical_clips(clips)
            fs = [feats[p] for p in clips if feats.get(p) is not None]
            if len(fs) < 2:
                continue
            Z = (np.array(fs) - gmed) / gscale
            D = np.sqrt(((Z[:, None, :] - Z[None, :, :]) ** 2).sum(-1))
            for i in range(len(fs)):
                nn.append(min(D[i, j] for j in range(len(fs)) if j != i))
                for j in range(i + 1, len(fs)):
                    allpair.append(D[i, j])
        nn, allpair = np.array(nn), np.array(allpair)
        print(f"\n=== 全局校准 ({len(targets)} asset) ===")
        print(f"within-asset 最近邻距离 (同说话人主导): "
              f"p50={np.percentile(nn,50):.2f} p75={np.percentile(nn,75):.2f} p90={np.percentile(nn,90):.2f} max={nn.max():.2f}")
        print(f"within-asset 全两两距离: "
              f"p25={np.percentile(allpair,25):.2f} p50={np.percentile(allpair,50):.2f} p75={np.percentile(allpair,75):.2f} p90={np.percentile(allpair,90):.2f}")
        print("建议 T ≈ 最近邻 p90 与两两 p75 之间 (同人上界与跨人下界的谷)")
        return 0

    results = [audit_asset(aid, clips, feats, gmed, gscale, args.t) for aid, clips in targets]
    REPORT_PATH.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print_summary(results, md=args.md)
    print(f"\n报告: {REPORT_PATH}  (T={args.t})")
    print("ℹ️ 定位=自动分诊: 🔴/🟠/🟡 是**待人工耳听确认**队列 (把听全库降成听可疑子集), 不自动删。"
          "\n   能稳抓'孤立离群'(3+1 常见 diarization 误切); 同性近音色 2v2(如罗翔 03/04)粗特征解不了→标交人工。"
          "\n   彻底精度需训练声纹 embedding(onnxruntime+wespeaker), 列为后续升级。")
    if args.apply:
        print("[--apply] 自动隔离在 review-code 通过后启用 (本次仅报告)。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
