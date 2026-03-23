# AI Photographer

Termux + IP Webcam + YOLO で動くスマホ自動撮影システム。
Claude Code がカメラマン兼編集者として、撮影・物体検出・選別・クロップまで自動でやる。

## 仕組み

```
IP Webcam (MJPEG) → 動画録画 → YOLO後処理 → ベストフレーム選出 → Claude選別 → CALS保存
```

1. **録画** — IP Webcam のストリームを一時ファイルに保存（メモリ節約）
2. **YOLO解析** — 全フレームを物体検出、信頼度×中央寄り度でスコアリング
3. **窓選出** — 5秒ごとの時間窓でベストスコアのフレームを1枚採用
4. **Claude選別** — 似た写真の重複排除、ブレ・無意味な写真の除外
5. **クロップ保存** — CALS規格(1280x960)にリサイズ、日付フォルダに整理

## 必要なもの

- Android スマホ
- [Termux](https://termux.dev/) + PRoot (Ubuntu)
- [IP Webcam](https://play.google.com/store/apps/details?id=com.pas.webcam) アプリ
- Python 3, OpenCV, Ultralytics (YOLO)
- Claude Code

## ファイル構成

| ファイル | 役割 |
|---------|------|
| `keyframe.py` | メイン。録画→YOLO後処理→ベストフレーム抽出 |
| `crop_cals.py` | CALS規格(1280x960)クロップ |
| `rotate.py` | 90°回転（縦横補正） |
| `capture.sh` | インターバル撮影（旧方式） |
| `beep.wav` | 開始/終了通知音 |
| `camera.md` | Claude Code スキル定義（YOLO撮影） |
| `photo.md` | Claude Code スキル定義（1枚撮影） |

## 使い方

### Claude Code から

```
/camera        # 60秒 YOLO撮影
/camera 120    # 120秒
/photo         # 1枚撮影
```

### 単体実行

```bash
python3 keyframe.py 60   # 60秒録画→YOLO解析→ベストフレーム出力
```

## セットアップ

```bash
# PRoot内
pip install opencv-python-headless ultralytics pillow

# Termux側（通知音用）
pkg install termux-api
```

IP Webcam を起動してストリームURLを `keyframe.py` の `STREAM_URL` に設定。

## ライセンス

MIT
