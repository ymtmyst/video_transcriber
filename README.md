# 動画文字起こしツール (Whisper版)

OpenAIのWhisperを使用した、無料で使える動画文字起こしツールです。
CPUとGPU (CUDA) の両方に対応しており、GPUを使用することで高速な処理が可能です。

## 目次
1. [前提条件](#前提条件)
2. [インストール方法](#インストール方法)
3. [使い方](#使い方)

## 前提条件

このツールを使用するには、以下が必要です。

1. **Python**: Python 3.8以降がインストールされていること。
2. **FFmpeg**: 音声処理のために別途インストールが必要です。
3. **CUDA Toolkit** (任意): NVIDIA製GPUを使用して高速化する場合に必要です。

### FFmpegのインストール (Windows)
Whisperは音声ファイルの読み込みにFFmpegを使用します。
`winget` コマンドが使える場合（Windows 10/11の最新版）は、PowerShellで以下を実行すると簡単にインストールできます。

```powershell
winget install Gyan.FFmpeg
```
インストール後、PowerShellを再起動してください。

## インストール方法

1. このフォルダでコマンドプロンプトやPowerShellを開きます。
2. 以下のコマンドを実行して、必要なライブラリをインストールします。

```bash
pip install -r requirements.txt
```

※ GPU (CUDA) を使用する場合は、PyTorchのGPU版を適切にインストールする必要があります。
基本的には上記コマンドで入りますが、もしGPUが認識されない場合は、[PyTorch公式サイト](https://pytorch.org/get-started/locally/) を参照して、ご自身の環境（CUDAバージョン）に合ったインストールコマンドを実行してください。
例: `pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`

## 使い方

以下のコマンドを実行して文字起こしを行います。

```bash
python transcribe.py "動画ファイルのパス.mp4"
```

### オプション

- `--model`: モデルのサイズを指定します。サイズが大きいほど精度が高いですが、処理が重くなります。
    - 選択肢: `tiny`, `base`, `small` (デフォルト), `medium`, `large`
    - 例: `python transcribe.py video.mp4 --model medium`
- `--device`: 使用するデバイスを指定します。
    - 選択肢: `auto` (デフォルト), `cuda`, `cpu`
    - 強制的にCPUを使いたい場合などは `--device cpu` を指定してください。

### 出力
処理が完了すると、動画ファイルと同じ場所に `[元のファイル名]_transcription.txt` というテキストファイルが作成されます。
