import whisper
import os
import sys
import warnings

# 特定の警告を無視（ユーザーを混乱させないため）
warnings.filterwarnings("ignore")

def transcribe_video(video_path, model_size="base", output_format="txt"):
    """
    動画ファイルから音声を文字起こしする関数 (GPU対応版)
    
    Args:
        video_path (str): 動画ファイルのパス
        model_size (str): 使用するWhisperモデルのサイズ (tiny, base, small, medium, large)
        output_format (str): 出力形式 (txt)
    """
    if not os.path.exists(video_path):
        print(f"エラー: ファイル '{video_path}' が見つかりません。")
        return

    print(f"モデル '{model_size}' をロード中... (初回はダウンロードに時間がかかります)")
    try:
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"使用デバイス: {device.upper()}")
        model = whisper.load_model(model_size, device=device)
    except Exception as e:
        print(f"モデルのロード中にエラーが発生しました: {e}")
        return

    print(f"文字起こしを開始します: {video_path}")
    print("動画の長さやPCの性能によっては時間がかかります...")
    
    try:
        # 文字起こし実行 (fp16=True はGPU使用時に高速化されますが、CPUではFalseにする必要があります)
        is_fp16 = (device == "cuda")
        result = model.transcribe(video_path, fp16=is_fp16)
        transcribed_text = result["text"]
        
        # ファイル名を作成
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_file = f"{base_name}_transcription.{output_format}"
        
        # utf-8エンコーディングで保存
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(transcribed_text.strip())
            
        print("-" * 30)
        print("完了しました！")
        print(f"出力ファイル: {os.path.abspath(output_file)}")
        print("-" * 30)
        
        # 最初の数文字を表示
        print("プレビュー (先頭100文字):")
        print(transcribed_text[:100] + "..." if len(transcribed_text) > 100 else transcribed_text)
        
    except Exception as e:
        print(f"処理中にエラーが発生しました: {e}")
        print("ヒント: FFmpegがインストールされていない可能性があります。")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python transcribe_gpu.py <動画ファイルのパス> [モデルサイズ]")
        print("例: python transcribe_gpu.py my_video.mp4 small")
    else:
        video_file = sys.argv[1]
        model = "base"
        if len(sys.argv) > 2:
            model = sys.argv[2]
            
        transcribe_video(video_file, model_size=model)
