from pathlib import Path
import subprocess, json, datetime, tempfile
import whisper
from TTS.api import TTS
from pydub import AudioSegment

SAMPLE_RATE = 22050
def _log(msg, log):
    ts=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log,'a',encoding='utf-8') as f: f.write(f"[{ts}] {msg}\n")
    print(msg)

def extract_audio(video,wav,log):
    _log("Extracting audio...",log)
    subprocess.run(["ffmpeg","-y","-i",video,"-ac","1","-ar","16000",wav],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)

def transcribe(wav,log):
    _log("Transcribing...",log)
    model=whisper.load_model("small")
    return model.transcribe(wav,fp16=False)["segments"]

def write_srt(segs,srt,log):
    _log("Writing SRT...",log)
    def ts(t):
        h=int(t//3600); m=int((t%3600)//60); s=t%60
        return f"{h:02d}:{m:02d}:{s:06.3f}".replace('.',',')
    with open(srt,'w',encoding='utf-8') as f:
        for i,s in enumerate(segs,1):
            f.write(f"{i}\n{ts(s['start'])} --> {ts(s['end'])}\n{s['text'].strip()}\n\n")

def synthesize(segs,voice,log):
    _log("Synthesizing TTS...",log)
    tts=TTS(model_name="tts_models/en/vctk/vits",progress_bar=False,gpu=False)
    timeline=AudioSegment.silent(0,frame_rate=SAMPLE_RATE); last=0
    for s in segs:
        tmp=Path(tempfile.mkstemp(suffix='.wav')[1])
        tts.tts_to_file(text=s['text'], speaker=voice, file_path=str(tmp))
        clip=AudioSegment.from_wav(tmp)
        gap=int(s['start']*1000)-last
        if gap>0: timeline+=AudioSegment.silent(gap,frame_rate=SAMPLE_RATE)
        timeline+=clip
        last=int(s['start']*1000)+len(clip)
        tmp.unlink()
    return timeline

def mux(video,dub_wav,srt,out,log):
    _log("Muxing...",log)
    subprocess.run([
        "ffmpeg","-y","-i",video,"-i",dub_wav,
        "-map","0:v:0","-map","1:a:0",
        "-c:v","copy","-c:a","aac",
        "-metadata:s:a:0","language=eng",
        out
    ],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)

def run_pipeline(video,outdir='output',voice='p225'):
    out=Path(outdir); out.mkdir(parents=True,exist_ok=True)
    log=out/'logfile.log'
    wav=out/'audio_tmp.wav'
    extract_audio(video,str(wav),log)
    segs=transcribe(str(wav),log)
    (out/'transcript.json').write_text(json.dumps(segs,indent=2,ensure_ascii=False))
    srt=out/'subtitles.srt'; write_srt(segs,str(srt),log)
    dub=synthesize(segs,voice,log); dub_path=out/'dubbed.wav'; dub.export(dub_path,format='wav')
    mkv=out/'video_dubbed.mkv'; mux(video,str(dub_path),str(srt),str(mkv),log)
    _log("Done.",log); return mkv