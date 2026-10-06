"""Frame-by-frame manual annotation UI (in your browser) for validating iCatcher looks.

Run on the server, view on your laptop:
    python annotate_videos.py [--port 8765]
    ssh -L 8765:localhost:8765 <server>      # on your laptop, then open http://localhost:8765

Videos come from validation_selection.csv (made by select_validation_videos.py). Frames start unlabeled
and the iCatcher labels are never shown, so annotators code every frame (left / right / away) blind.

Multi-user use: every annotator enters a username. Videos are claimed a participant at a time: when a user
needs a new video they claim every selected video of the next unclaimed participant (video_claims.csv), and
work through all of that participant's videos in a row before moving on. Claimed videos are never offered
to anyone else. Annotations are written to
data/main/data_to_analyze/level-looks_source-manual_data.csv; each save re-reads that file under a lock
and only replaces the rows of the saved video, so simultaneous users (same server or separate servers)
never overwrite each other. The `reviewed` column records which frames the annotator has labeled
(unlabeled frames have an empty lookType), so a user resumes at the first unlabeled frame of their
first unfinished video.

Requires ffmpeg on PATH (or pip install imageio-ffmpeg) and pandas. No other dependencies.
"""
import argparse
import fcntl
import json
import os
import shutil
import subprocess
import tempfile
import threading
from contextlib import contextmanager
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import dotenv
import pandas as pd

dotenv.load_dotenv()

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]                 # Use if on SSH
# ROOT = Path(os.environ['SERVER_PATH']) # Use if connected to server volume
DATA_DIR = ROOT / 'data' / 'main' / 'data_to_analyze'
ICATCHER_CSV = DATA_DIR / 'level-looks_source-icatcher_data.csv'
MANUAL_CSV = DATA_DIR / 'level-looks_source-manual_data.csv'
VIDEO_DIR = ROOT / 'data' / 'raw' / 'original_videos' / 'mp4'
SELECTION_CSV = HERE / 'validation_selection.csv'
CLAIMS_CSV = HERE / 'video_claims.csv'        # Use if on SSH
# CLAIMS_CSV = DATA_DIR / 'video_claims.csv' # Use if connected to server volume
LOCK_FILE = HERE / '.annotate.lock'

SUBJ, TRIAL = 'SubjectInfo.subjID', 'Trials.trialID'
CLAIM_COLS = ['subjID', 'trialID', 'username', 'claimed_at']
LABELS = {'left', 'right', 'away'}
MAX_CACHED_VIDEOS = 8
# iCatcher's left/right are the mirror of what an annotator sees. The UI shows/accepts flipped labels;
# everything stored (manual csv) stays in the iCatcher convention so it compares directly with the iCatcher csv.
FLIP = {'left': 'right', 'right': 'left', 'away': 'away'}


@contextmanager
def file_lock():
    """Exclusive cross-process lock (flock) so concurrent annotators serialise their csv writes."""
    with open(LOCK_FILE, 'w') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def atomic_write_csv(df, path):
    tmp = path.with_name(f'{path.name}.{os.getpid()}.tmp')
    df.to_csv(tmp, index=False)
    os.replace(tmp, path)


def read_claims():
    if CLAIMS_CSV.exists():
        return pd.read_csv(CLAIMS_CSV, dtype=str)
    return pd.DataFrame(columns=CLAIM_COLS)


def read_manual():
    return pd.read_csv(MANUAL_CSV) if MANUAL_CSV.exists() else None


def video_mask(df, subj, trial):
    return (df[SUBJ] == subj) & (df[TRIAL] == trial)


def try_claim_participant(username, subj, trials):
    """Claim all of a participant's videos for username. Returns the newly claimed trials, or None if
    another user already holds any of this participant's videos."""
    with file_lock():
        claims = read_claims()
        owned = claims[claims.subjID == subj]
        if (owned.username != username).any():
            return None
        new = [t for t in trials if t not in set(owned.trialID)]
        if new:
            now = datetime.now().isoformat(timespec='seconds')
            rows = pd.DataFrame([[subj, t, username, now] for t in new], columns=CLAIM_COLS)
            atomic_write_csv(pd.concat([claims, rows], ignore_index=True), CLAIMS_CSV)
        return new


def save_video(df):
    """Replace this video's rows in the manual csv, keeping everything other users saved meanwhile."""
    subj, trial = df[SUBJ].iloc[0], df[TRIAL].iloc[0]
    with file_lock():
        manual = read_manual()
        if manual is not None:
            manual = manual[~video_mask(manual, subj, trial)]
            df = pd.concat([manual, df], ignore_index=True)
        atomic_write_csv(df, MANUAL_CSV)


def find_ffmpeg():
    exe = shutil.which('ffmpeg')
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        raise SystemExit('ffmpeg not found. Install it (conda install ffmpeg) or pip install imageio-ffmpeg.')


class Annotator:
    """Server-side state: selection, iCatcher rows, per-video jpeg frame cache."""

    def __init__(self, width):
        self.width = width
        self.ffmpeg = find_ffmpeg()
        self.selection = pd.read_csv(SELECTION_CSV)
        self.order = list(zip(self.selection.subjID, self.selection.trialID))
        self.participants = {}  # subj -> its selected trials, in selection order
        for subj, trial in self.order:
            self.participants.setdefault(subj, []).append(trial)
        keys = set(self.order)
        print('Loading iCatcher data...', flush=True)
        looks = pd.read_csv(ICATCHER_CSV)
        looks = looks[[k in keys for k in zip(looks[SUBJ], looks[TRIAL])]]
        # a few videos (e.g. VVI182, VVI188) have every frame row repeated 2-3x in the iCatcher csv
        looks = looks.drop_duplicates([SUBJ, TRIAL, 'frame'])
        self.icatcher = {(s, t): g.reset_index(drop=True) for (t, s), g in looks.groupby([TRIAL, SUBJ], sort=False)}
        self.cache = Path(tempfile.mkdtemp(prefix='icatcher_frames_'))
        self.cache_lock = threading.Lock()
        self.recent = []

    def frame_dir(self, key):
        """JPEG frames of a video (decoded once, frame k of the video == csv frame k+1)."""
        d = self.cache / f'{key[0]}_{key[1]}'
        with self.cache_lock:
            if not (d / 'done').exists():
                shutil.rmtree(d, ignore_errors=True)
                d.mkdir(parents=True)
                video = VIDEO_DIR / key[0] / f'{key[1]}_{key[0]}.mp4'
                # setpts=N/TB gives every frame a unique timestamp (some videos have duplicate pts, which the
                # mjpeg encoder rejects); -vsync 0 keeps every decoded frame so frame k == csv frame k+1.
                # Piped mjpeg is split on the JPEG end marker (0xFFD9 never occurs inside the entropy data).
                out = subprocess.run([self.ffmpeg, '-v', 'error', '-i', str(video), '-vsync', '0',
                                      '-vf', f'scale={self.width}:-2,setpts=N/TB', '-q:v', '3',
                                      '-f', 'image2pipe', '-c:v', 'mjpeg', '-'], capture_output=True)
                if out.returncode:
                    raise RuntimeError(f'ffmpeg failed on {video}: {out.stderr.decode()[-500:]}')
                for k, jpg in enumerate(out.stdout.split(b'\xff\xd9')[:-1]):
                    (d / f'{k + 1:04d}.jpg').write_bytes(jpg + b'\xff\xd9')
                (d / 'done').touch()
            if d in self.recent:
                self.recent.remove(d)
            self.recent.append(d)
            while len(self.recent) > MAX_CACHED_VIDEOS:
                shutil.rmtree(self.recent.pop(0), ignore_errors=True)
        return d

    def mine(self, user):
        """This user's claimed videos, grouped by participant (in claim order) and in selection order within."""
        claims = read_claims()
        c = claims[claims.username == user]
        subjs = list(dict.fromkeys(c.subjID))
        have = set(zip(c.subjID, c.trialID))
        return [(s, t) for s in subjs for t in self.participants.get(s, []) if (s, t) in have]

    def video_payload(self, mine, pos):
        key = mine[pos]
        n_frames = len(list(self.frame_dir(key).glob('*.jpg')))
        n = len(self.icatcher[key])
        manual = read_manual()
        saved = manual[video_mask(manual, *key)].reset_index(drop=True) if manual is not None else None
        labels = [None] * n
        if saved is not None and len(saved) == n:
            labels = [FLIP[x] if r else None for x, r in zip(saved.lookType, saved.reviewed)]
        subj_videos = [k for k in mine if k[0] == key[0]]
        return {'key': list(key), 'pos': pos, 'total': len(mine), 'frames': n_frames, 'labels': labels,
                'subj_pos': subj_videos.index(key), 'subj_total': len(self.participants[key[0]]),
                'subjs_done': len({k[0] for k in mine[:pos]} - {key[0]}), 'last_of_subj': key == subj_videos[-1]}

    def open(self, user, action, pos):
        """resume: first unfinished video of this user; next/prev: neighbour in their claimed list.
        Running off the end of the list claims the next unclaimed video."""
        mine = self.mine(user)
        if action == 'resume':
            manual = read_manual()
            pos = next((i for i, k in enumerate(mine) if manual is None or not self.done(manual, k)), None)
        elif action == 'next':
            pos = pos + 1 if pos + 1 < len(mine) else None
        else:
            pos = max(0, pos - 1)
        if pos is None:
            pos = self.claim_next(user, mine)
            if pos is None:
                return {'error': 'No unclaimed videos left.'}
        return self.video_payload(mine, pos)

    def done(self, manual, key):
        rows = manual[video_mask(manual, *key)]
        return len(rows) > 0 and bool(rows.reviewed.all())

    def claim_next(self, user, mine):
        """Claim the remaining videos of the next participant (finishing a partly claimed one first).
        Returns the position of its first newly claimed video in the user's list."""
        have = {s for s, _ in mine}
        subjs = sorted(self.participants, key=lambda s: s not in have)
        for subj in subjs:
            new = try_claim_participant(user, subj, self.participants[subj])
            if new:
                mine[:] = self.mine(user)
                return mine.index((subj, new[0]))
        return None

    def save(self, user, subj, trial, labels):
        key = (subj, trial)
        owner = read_claims().query('subjID == @subj and trialID == @trial').username
        if key not in self.icatcher or not len(owner) or owner.iloc[0] != user:
            return {'error': 'not your video'}
        df = self.icatcher[key].copy()
        if len(labels) != len(df) or not set(labels) <= LABELS | {None}:
            return {'error': 'bad payload'}
        df['original_lookType'] = df.lookType
        df['lookType'] = [FLIP[x] if x else None for x in labels]  # UI labels -> iCatcher convention
        df['group'] = (df.lookType != df.lookType.shift()).cumsum().astype(float)
        df['annotator'] = user
        df['reviewed'] = [int(x is not None) for x in labels]
        save_video(df)
        return {'ok': True}


def make_handler(app):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def send(self, body, ctype, code=200):
            self.send_response(code)
            self.send_header('Content-Type', ctype)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'max-age=3600' if ctype == 'image/jpeg' else 'no-store')
            self.end_headers()
            self.wfile.write(body)

        def send_json(self, obj, code=200):
            self.send(json.dumps(obj).encode(), 'application/json', code)

        def do_GET(self):
            url = urlparse(self.path)
            q = {k: v[0] for k, v in parse_qs(url.query).items()}
            try:
                if url.path == '/':
                    return self.send(PAGE.encode(), 'text/html; charset=utf-8')
                if url.path == '/frame':
                    key = (q['s'], q['t'])
                    if key not in app.icatcher:
                        return self.send(b'', 'text/plain', 404)
                    path = app.frame_dir(key) / f'{int(q["i"]) + 1:04d}.jpg'
                    return self.send(path.read_bytes(), 'image/jpeg')
                self.send(b'', 'text/plain', 404)
            except Exception as e:  # noqa: BLE001 - report to the browser instead of hanging
                self.send_json({'error': str(e)}, 500)

        def do_POST(self):
            try:
                body = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))) or b'{}')
                user = str(body.get('user', '')).strip().lower()
                if not user:
                    return self.send_json({'error': 'username required'}, 400)
                if self.path == '/api/open':
                    return self.send_json(app.open(user, body.get('action', 'resume'), int(body.get('pos', 0))))
                if self.path == '/api/save':
                    return self.send_json(app.save(user, body['subj'], body['trial'], body['labels']))
                self.send_json({'error': 'unknown endpoint'}, 404)
            except Exception as e:  # noqa: BLE001
                self.send_json({'error': str(e)}, 500)

    return Handler


PAGE = r"""<!doctype html>
<html><head><meta charset="utf-8"><title>iCatcher validation</title>
<style>
body{font-family:system-ui,sans-serif;margin:16px;background:#fafafa;color:#222}
#wrap{max-width:900px;margin:auto}
canvas{display:block;max-width:100%}
#video{border:8px solid #ddd;background:#000;width:100%;box-sizing:border-box}
#timeline{width:100%;height:48px;background:#fff;margin:8px 0;cursor:pointer}
button{font-size:14px;padding:6px 12px;margin-right:6px;cursor:pointer}
#info{font-weight:bold;margin-bottom:6px}
#status{margin:6px 0;color:#444}
#help{color:#555;font-size:13px;margin-top:8px;line-height:1.7}
kbd{background:#eee;border:1px solid #ccc;border-radius:3px;padding:0 4px}
.left{color:#1f77b4}.right{color:#ff7f0e}.away{color:#777}
</style></head><body><div id="wrap">
<div id="login"><h3>iCatcher validation</h3>Username: <input id="user" autofocus> <button id="go">Start</button></div>
<div id="app" hidden>
<div id="info"></div>
<canvas id="video" width="640" height="360"></canvas>
<canvas id="timeline" width="900" height="48"></canvas>
<div><button id="prevv">Prev video (b)</button><button id="nextv">Next video (n)</button>
<button id="play">Play/Pause (p)</button><button id="savebtn">Save (s)</button></div>
<div id="status"></div>
<div id="help">Every frame starts unlabeled; label each one yourself.<br>
<b class="left"><kbd>1</kbd>/<kbd>l</kbd> LEFT</b> &nbsp; <b class="right"><kbd>2</kbd>/<kbd>r</kbd> RIGHT</b> &nbsp;
<b class="away"><kbd>3</kbd>/<kbd>a</kbd> AWAY</b> &nbsp; (labels the frame, then advances)<br>
<kbd>Space</kbd> same label as previous frame &amp; next &nbsp; <kbd>Right</kbd>/<kbd>Left</kbd> move without labeling &nbsp;
<kbd>Up</kbd>/<kbd>Down</kbd> +/-10 frames<br>
<kbd>p</kbd> play: carries the current label onto unlabeled frames; press a label key to switch while playing<br>
<kbd>m</kbd> mark range start; the next label key labels mark..current frame &nbsp; Click the timeline to jump.
White = unlabeled. You get all videos of one participant in a row.</div></div></div>
<script>
const COLORS={left:'#1f77b4',right:'#ff7f0e',away:'#8c8c8c'},NONE='#ddd';
const KEYS={'1':'left','l':'left','2':'right','r':'right','3':'away','a':'away'};
let user='',v=null,imgs=[],i=0,mark=null,dirty=0,playing=null,msg='';
const $=id=>document.getElementById(id), vc=$('video'), tc=$('timeline');
function say(t){msg=t;$('status').textContent=t;}
const col=l=>l?COLORS[l]:NONE, nLabeled=()=>v.labels.filter(x=>x).length, complete=()=>v.labels.every(x=>x);

async function api(path,body){
  const r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user,...body})});
  return r.json();
}
async function openVideo(action){
  stop(); await save();
  say('Loading video (decoding frames)...');
  const d=await api('/api/open',{action,pos:v?v.pos:0});
  if(d.error){say(d.error);return;}
  v=d;mark=null;dirty=0;
  const n=v.labels.length;
  if(v.frames!==n) alert('Frame mismatch: video has '+v.frames+' frames, csv has '+n);
  const first=v.labels.indexOf(null);i=first<0?0:first;
  imgs=[];
  for(let k=0;k<v.frames;k++){const im=new Image();im.onload=()=>{if(k===i)draw()};im.src=`/frame?s=${v.key[0]}&t=${v.key[1]}&i=${k}`;imgs.push(im);}
  say(v.subj_pos===0&&!nLabeled()?`New participant ${v.key[0]}: ${v.subj_total} videos`:'');draw();
}
function draw(){
  const n=v.labels.length,lab=v.labels[i],im=imgs[Math.min(i,imgs.length-1)];
  if(im&&im.complete&&im.naturalWidth){vc.width=im.naturalWidth;vc.height=im.naturalHeight;
    const c=vc.getContext('2d');c.drawImage(im,0,0);
    if(lab){c.fillStyle=COLORS[lab];c.font='bold 40px sans-serif';c.fillText(lab.toUpperCase(),14,50);}}
  vc.style.borderColor=col(lab);
  const t=tc.getContext('2d'),W=tc.width,w=W/n;t.clearRect(0,0,W,48);
  for(let k=0;k<n;k++){t.fillStyle=v.labels[k]?COLORS[v.labels[k]]:'#fff';t.fillRect(k*w,0,w+1,40);}
  t.strokeStyle='#ccc';t.lineWidth=1;t.strokeRect(0,0,W,40);
  if(mark!==null){const a=Math.min(mark,i),b=Math.max(mark,i);t.strokeStyle='#000';t.lineWidth=3;t.strokeRect(a*w,1,(b-a+1)*w,38);}
  t.fillStyle='#000';t.fillRect((i+.5)*w-1.5,0,3,48);
  $('info').textContent=`Participant ${v.key[0]} (#${v.subjs_done+1} of yours)  video ${v.subj_pos+1}/${v.subj_total}: ${v.key[1]}  frame ${i+1}/${n}`;
  $('status').textContent=msg||`labeled ${nLabeled()}/${n}`+(mark!==null?`   range mark at frame ${mark+1}`:'');
}
async function save(){
  if(!v||!dirty)return;dirty=0;
  const d=await api('/api/save',{subj:v.key[0],trial:v.key[1],labels:v.labels});
  say(d.error?'SAVE FAILED: '+d.error:'saved '+new Date().toLocaleTimeString());
}
function goto(k){i=Math.max(0,Math.min(v.labels.length-1,k));msg='';draw();}
function advance(){
  if(i+1<v.labels.length){if(dirty>=50)save();return goto(i+1);}
  stop();draw();
  if(complete())save().then(()=>say(v.last_of_subj?`Participant ${v.key[0]} complete and saved - press n to start the next participant`
    :'Video complete and saved - press n for the next video of this participant'));
  else say(`${v.labels.length-nLabeled()} frames still unlabeled (white in the timeline)`);
}
function setLabel(k,val){if(v.labels[k]!==val){v.labels[k]=val;dirty++;}}
function label(val){
  let a=i,b=i;if(mark!==null){a=Math.min(mark,i);b=Math.max(mark,i);}
  for(let k=a;k<=b;k++)setLabel(k,val);
  if(mark!==null){i=b;mark=null;}
  if(!playing)advance();else draw();
}
function carry(){
  // label the current frame like the previous one; false if there is nothing to carry
  if(v.labels[i])return true;
  if(i===0||!v.labels[i-1]){say('Label this frame first (1/2/3)');return false;}
  setLabel(i,v.labels[i-1]);return true;
}
function stop(){if(playing){clearInterval(playing);playing=null;}}
function play(){if(playing)return stop();if(!carry())return;
  playing=setInterval(()=>{if(i+1>=v.labels.length)return advance();i++;if(!carry()){stop();draw();return;}msg='';draw();},33);}
function nextVideo(){if(!complete()&&!confirm('This video has unlabeled frames. Move on anyway?'))return;openVideo('next');}
document.addEventListener('keydown',e=>{
  if(!v||e.target.tagName==='INPUT'||e.ctrlKey||e.metaKey)return;
  const k=e.key;
  if(k===' '){e.preventDefault();if(carry())advance();}
  else if(k==='ArrowRight'){e.preventDefault();goto(i+1);}
  else if(k==='ArrowLeft'){e.preventDefault();goto(i-1);}
  else if(k==='ArrowUp'){e.preventDefault();goto(i+10);}
  else if(k==='ArrowDown'){e.preventDefault();goto(i-10);}
  else if(KEYS[k])label(KEYS[k]);
  else if(k==='m'){mark=mark===null?i:null;draw();}
  else if(k==='p')play();else if(k==='n')nextVideo();else if(k==='b')openVideo('prev');else if(k==='s')save();
});
tc.addEventListener('click',e=>{if(!v)return;const r=tc.getBoundingClientRect();goto(Math.floor((e.clientX-r.left)/r.width*v.labels.length));});
$('prevv').onclick=()=>openVideo('prev');$('nextv').onclick=nextVideo;$('play').onclick=play;$('savebtn').onclick=save;
window.addEventListener('beforeunload',()=>{if(v&&dirty)navigator.sendBeacon('/api/save',new Blob([JSON.stringify({user,subj:v.key[0],trial:v.key[1],labels:v.labels})],{type:'application/json'}));});
function start(){user=$('user').value.trim().toLowerCase();if(!user)return;localStorage.setItem('icatcher_user',user);
  $('login').hidden=true;$('app').hidden=false;openVideo('resume');}
$('go').onclick=start;$('user').addEventListener('keydown',e=>{if(e.key==='Enter')start();});
$('user').value=localStorage.getItem('icatcher_user')||'';
</script></body></html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=8765)
    ap.add_argument('--width', type=int, default=640, help='width of decoded frames in pixels')
    args = ap.parse_args()
    if not SELECTION_CSV.exists():
        raise SystemExit('Run select_validation_videos.py first.')

    app = Annotator(args.width)
    server = None
    for port in range(args.port, args.port + 50):
        try:
            server = ThreadingHTTPServer(('127.0.0.1', port), make_handler(app))
            break
        except OSError:
            continue
    if server is None:
        raise SystemExit(f'No free port in {args.port}-{args.port + 49}')
    port = server.server_address[1]
    print(f'\nReady. On your laptop run:\n  ssh -L {port}:localhost:{port} <this server>\n'
          f'then open http://localhost:{port} in your browser. Ctrl+C here to stop.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        shutil.rmtree(app.cache, ignore_errors=True)


if __name__ == '__main__':
    main()
