import {useEffect,useMemo,useRef,useState} from 'react'
import SectorIcon from '../ui/SectorIcon'
import '../../styles/native-arcade.css'

const DIR={up:[-1,0],down:[1,0],left:[0,-1],right:[0,1]}
const ICONS=['◈','✦','⬡','◇','◆','✧','◉','⌁']
function emptyBoard(){return Array.from({length:16},()=>0)}
function addTile(source){const board=[...source],empty=board.map((v,i)=>v?null:i).filter(v=>v!==null);if(empty.length)board[empty[Math.floor(Math.random()*empty.length)]]=Math.random()<.9?2:4;return board}
function initial2048(){return addTile(addTile(emptyBoard()))}
function slideLine(line){const values=line.filter(Boolean),out=[];let gain=0;for(let i=0;i<values.length;i++){if(values[i]===values[i+1]){out.push(values[i]*2);gain+=values[i]*2;i++}else out.push(values[i])}while(out.length<4)out.push(0);return [out,gain]}
function move2048(board,direction){const next=emptyBoard();let gain=0;for(let n=0;n<4;n++){let ids=direction==='left'||direction==='right'?[0,1,2,3].map(c=>n*4+c):[0,1,2,3].map(r=>r*4+n);if(direction==='right'||direction==='down')ids=ids.reverse();const [line,g]=slideLine(ids.map(i=>board[i]));gain+=g;ids.forEach((id,i)=>next[id]=line[i])}return [next,gain,next.some((v,i)=>v!==board[i])]}

function Game2048({finish}){
 const [board,setBoard]=useState(initial2048),[score,setScore]=useState(0),touch=useRef(null)
 function move(dir){setBoard(old=>{const [next,gain,changed]=move2048(old,dir);if(!changed)return old;setScore(v=>v+gain);return addTile(next)})}
 function reset(){setBoard(initial2048());setScore(0)}
 return <div className="native-game native-2048" onTouchStart={e=>{const t=e.touches[0];touch.current=[t.clientX,t.clientY]}} onTouchEnd={e=>{if(!touch.current)return;const t=e.changedTouches[0],dx=t.clientX-touch.current[0],dy=t.clientY-touch.current[1];if(Math.max(Math.abs(dx),Math.abs(dy))>24)move(Math.abs(dx)>Math.abs(dy)?dx>0?'right':'left':dy>0?'down':'up')}}><header><span>امتیاز <b>{score.toLocaleString('fa-IR')}</b></span><button onClick={reset}>شروع دوباره</button></header><div className="native-2048__grid">{board.map((v,i)=><i key={i} data-value={Math.min(v,2048)}>{v||''}</i>)}</div><div className="native-game__dpad"><button onClick={()=>move('up')}>↑</button><span><button onClick={()=>move('right')}>→</button><button onClick={()=>move('down')}>↓</button><button onClick={()=>move('left')}>←</button></span></div><button className="btn btn-primary" disabled={score<16} onClick={()=>finish(Math.min(1_000_000,score))}>ثبت رکورد {score.toLocaleString('fa-IR')}</button></div>
}

function Snake({finish}){
 const [snake,setSnake]=useState([[7,5],[7,4],[7,3]]),[food,setFood]=useState([4,8]),[dir,setDir]=useState('right'),[running,setRunning]=useState(true),score=(snake.length-3)*100,dirRef=useRef(dir);dirRef.current=dir
 function turn(next){const opposite={up:'down',down:'up',left:'right',right:'left'};if(opposite[dirRef.current]!==next){dirRef.current=next;setDir(next)}}
 function reset(){setSnake([[7,5],[7,4],[7,3]]);setFood([4,8]);dirRef.current='right';setDir('right');setRunning(true)}
 useEffect(()=>{if(!running)return;const id=setInterval(()=>setSnake(old=>{const [dr,dc]=DIR[dirRef.current],head=[old[0][0]+dr,old[0][1]+dc];if(head[0]<0||head[0]>=14||head[1]<0||head[1]>=10||old.some(x=>x[0]===head[0]&&x[1]===head[1])){setRunning(false);return old}const ate=head[0]===food[0]&&head[1]===food[1],next=[head,...old];if(!ate)next.pop();else{let cell;do{cell=[Math.floor(Math.random()*14),Math.floor(Math.random()*10)]}while(next.some(x=>x[0]===cell[0]&&x[1]===cell[1]));setFood(cell)}return next}),155);return()=>clearInterval(id)},[running,food])
 const cells=useMemo(()=>Array.from({length:140},(_,i)=>{const r=Math.floor(i/10),c=i%10,isHead=snake[0][0]===r&&snake[0][1]===c,isBody=snake.some(x=>x[0]===r&&x[1]===c),isFood=food[0]===r&&food[1]===c;return <i key={i} className={isHead?'head':isBody?'body':isFood?'food':''}/>}),[snake,food])
 return <div className="native-game native-snake"><header><span>رکورد <b>{score.toLocaleString('fa-IR')}</b></span><button onClick={reset}>شروع دوباره</button></header><div className="native-snake__grid">{cells}</div><div className="native-game__dpad"><button onClick={()=>turn('up')}>↑</button><span><button onClick={()=>turn('right')}>→</button><button onClick={()=>turn('down')}>↓</button><button onClick={()=>turn('left')}>←</button></span></div>{!running?<button className="btn btn-primary" onClick={()=>finish(Math.min(1_000_000,score))}>ثبت رکورد نهایی</button>:<small>برای ثبت رکورد بازی را تا پایان ادامه بده.</small>}</div>
}

function Memory({finish}){
 const cards=useMemo(()=>[...ICONS,...ICONS].sort(()=>Math.random()-.5),[]),[open,setOpen]=useState([]),[done,setDone]=useState([]),[moves,setMoves]=useState(0),started=useRef(Date.now())
 function pick(i){if(open.length===2||open.includes(i)||done.includes(i))return;const next=[...open,i];setOpen(next);if(next.length===2){setMoves(v=>v+1);setTimeout(()=>{if(cards[next[0]]===cards[next[1]])setDone(v=>[...v,...next]);setOpen([])},520)}}
 const complete=done.length===cards.length,seconds=Math.max(1,Math.floor((Date.now()-started.current)/1000)),score=Math.max(100,10000-moves*180-seconds*12)
 return <div className="native-game native-memory"><header><span>حرکت <b>{moves.toLocaleString('fa-IR')}</b></span><span>جفت‌ها <b>{done.length/2}/{cards.length/2}</b></span></header><div className="native-memory__grid">{cards.map((x,i)=><button key={i} className={open.includes(i)||done.includes(i)?'open':''} onClick={()=>pick(i)}>{open.includes(i)||done.includes(i)?x:'?'}</button>)}</div>{complete?<button className="btn btn-primary" onClick={()=>finish(Math.min(100_000,score))}>ثبت رکورد {score.toLocaleString('fa-IR')}</button>:<small>تمام جفت‌ها را پیدا کن تا نتیجه ثبت شود.</small>}</div>
}

export default function SectorNativeArcade({game,busy,onClose,onFinish}){
 const title={core2048:'2048 سکتور',sector_snake:'مار هسته‌ای',sector_memory:'حافظه کوانتومی'}[game?.id]||'Sector Arcade'
 return <div className="native-arcade" role="dialog" aria-modal="true"><section><header><div><small>IN-APP VERIFIED GAME</small><h2>{title}</h2></div><button onClick={onClose} aria-label="بستن">×</button></header>{game?.id==='core2048'?<Game2048 finish={onFinish}/>:game?.id==='sector_snake'?<Snake finish={onFinish}/>:<Memory finish={onFinish}/>}<footer><SectorIcon name="shield" size={15}/>{busy?'در حال ثبت امن رکورد…':'امتیاز با توکن یک‌بارمصرف در لیگ ثبت می‌شود.'}</footer></section></div>
}
