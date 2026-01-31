@echo off
echo GPU対応版のPyTorchをダウンロードしてインストールします...
echo ※データ量が多いため（約2.5GB）、完了まで数分かかります。そのままお待ちください。
echo.

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

echo.
echo インストールが完了しました。
echo 確認のため、以下のコマンドを実行して True が表示されるか確認してください。
python -c "import torch; print('GPU有効:', torch.cuda.is_available())"
pause
