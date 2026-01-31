import argparse
import os
import torch
import whisper
import warnings
import sys

# Suppress warnings
warnings.filterwarnings("ignore")

def main():
    parser = argparse.ArgumentParser(description="動画ファイルから自動で文字起こしを行います (OpenAI Whisper使用)")
    parser.add_argument("file_path", help="文字起こしを行いたい動画または音声ファイルのパス")
    parser.add_argument("--model", default="small", choices=["tiny", "base", "small", "medium", "large"], help="使用するモデルのサイズ (デフォルト: small)")
    parser.add_argument("--device", default="auto", choices=["auto", "cuda", "cpu"], help="使用するデバイス (デフォルト: auto)")
    parser.add_argument("--verbose", action="store_true", help="詳細なログを出力します")

    args = parser.parse_args()

    # Device selection logic
    device = args.device
    if device == "auto":
        if torch.cuda.is_available():
            device = "cuda"
        else:
            device = "cpu"
    
    print(f"========================================")
    print(f"  動画文字起こしツール (Whisper)")
    print(f"========================================")
    print(f"モード設定:")
    print(f"  - デバイス: {device} (CUDA利用可能: {torch.cuda.is_available()})")
    print(f"  - モデル  : {args.model}")
    print(f"  - ファイル: {args.file_path}")
    print(f"========================================")

    if device == "cuda":
        print(f"GPU情報: {torch.cuda.get_device_name(0)}")
    elif device == "cpu" and torch.cuda.is_available():
        print("注意: GPUが利用可能ですが、cpuモードが選択されています。")

    if not os.path.exists(args.file_path):
        print(f"[エラー] 指定されたファイルが見つかりません: {args.file_path}")
        sys.exit(1)

    try:
        print("\nモデルをロード中... (初回はダウンロードに時間がかかります)")
        model = whisper.load_model(args.model, device=device)
    except Exception as e:
        print(f"[エラー] モデルのロードに失敗しました: {e}")
        sys.exit(1)

    print("\n文字起こしを実行中... (これには時間がかかる場合があります)")
    try:
        # decode_options can be added if needed
        result = model.transcribe(args.file_path, verbose=args.verbose)
    except Exception as e:
        print(f"[エラー] 文字起こし処理中にエラーが発生しました。\n詳細: {e}")
        if "ffmpeg" in str(e).lower():
            print("\n[ヒント] FFmpegが見つからない可能性があります。FFmpegをインストールし、PATHに通してください。")
        sys.exit(1)

    # Save output
    base_name = os.path.splitext(args.file_path)[0]
    output_txt = f"{base_name}_transcription.txt"
    
    try:
        with open(output_txt, "w", encoding="utf-8") as f:
            f.write(result["text"])
        
        print(f"\n[成功] 文字起こしが完了しました！")
        print(f"保存先: {output_txt}")
        
    except Exception as e:
        print(f"[エラー] ファイルの保存に失敗しました: {e}")

if __name__ == "__main__":
    main()
