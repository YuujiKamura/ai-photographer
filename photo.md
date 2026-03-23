IP Webcam (192.168.2.116:8080) から1枚撮影し、自動で保存してください。

手順:
1. curl で http://192.168.2.116:8080/photo.jpg を取得し /home/user/camera_tmp/photo.jpg に保存
2. python3 /home/user/rotate.py で回転（90° CW）
3. Read ツールで回転後の画像を確認し、被写体が中央に来るよう crop top 値を判断
4. python3 /home/user/crop_cals.py /home/user/camera_tmp/photo.jpg {top値} でCALSサイズ(1280x960)にクロップ
5. タイムスタンプ付きで /storage/emulated/0/Pictures/camera_archive/YYYYMMDD/ （日付フォルダ）と /home/user/camera_archive/ にコピー
6. 一時ファイル削除
7. Read ツールで最終画像を表示
8. 写っている内容を簡潔に説明
