IP Webcam (192.168.2.116:8080) からYOLOポストプロセス方式で撮影し、内容を判断して保存するか決めてください。
デフォルト60秒。引数で秒数指定可。

手順:
1. python3 /home/user/keyframe.py {秒数} をバックグラウンドで実行
   - Phase 1: 動画ストリーム録画（tmpファイルに保存、メモリ節約）
   - Phase 2: YOLO後処理（全フレーム解析→5秒窓ごとにベストスコアのフレーム採用）
   - 開始/終了時にビープ音（termux-media-player）
   - 接続待ちは自動リトライ
2. 完了後、/home/user/camera_tmp/ の全yolo写真を Read ツールで確認（並列で可）
3. 以下の基準で保存判断：
   - 保存する: 人物、動物、珍しい風景、事故・異常事態、面白いもの、特徴的なシーン
   - 保存しない: 地面だけ、ブレている、他の写真とほぼ同じ、特に何も写っていない
4. 保存する写真は python3 /home/user/crop_cals.py でクロップ後、/storage/emulated/0/Pictures/camera_archive/YYYYMMDD/ （日付フォルダ）と /home/user/camera_archive/ にコピー
5. 保存しない写真と一時ファイルは削除
6. 結果を簡潔に報告（何枚中何枚保存、保存した写真の内容）
7. /storage/emulated/0/Pictures/camera_archive/ のファイル数と合計サイズを表示（ストレージ監視）
