# GPU用セットアップスクリプト

Write-Host "以前のPyTorchをアンインストールしています..."
pip uninstall -y torch torchvision torchaudio

Write-Host "GPU(CUDA)対応版のPyTorchをインストールしています..."
Write-Host "※ファイルサイズが大きいため（約2GB〜）、時間がかかります。"
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126

Write-Host "インストールが完了しました。"
Write-Host "GPUが認識されているか確認します..."
python -c "import torch; print(f'GPU Available: {torch.cuda.is_available()}'); print(f'Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}')"
