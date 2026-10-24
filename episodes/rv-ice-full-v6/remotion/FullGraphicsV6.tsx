import React from 'react';
import {AbsoluteFill} from 'remotion';
import {DayCard,EnergyDiagram,Icon,MobilityBoard,RouteDiagram,SupplyBoard,font} from './Graphics';

type Card={id:string;kind:string;title:string;day?:number|string;onScreen?:string};
const ink='#252b2e', teal='#437e82', red='#ab4e42', gray='#747b7e';
const Base:React.FC<{title:string;note?:string;children:React.ReactNode}>=({title,note,children})=><AbsoluteFill lang="ja" style={{background:'#f2efe5',color:ink,fontFamily:font,backgroundImage:'radial-gradient(ellipse at 55% 45%,#f8f5ec,#efecdf)'}}><div style={{position:'absolute',top:110,left:125,right:125,textAlign:'center',fontWeight:800,fontSize:72,lineHeight:1.35}}>{title}</div>{children}{note&&<div style={{position:'absolute',bottom:125,left:125,right:125,textAlign:'center',fontSize:39,fontWeight:600,color:gray,lineHeight:1.5}}>{note}</div>}</AbsoluteFill>;
const Label:React.FC<{x:number;y:number;children:React.ReactNode;size?:number;color?:string}>=({x,y,children,size=43,color=ink})=><text x={x} y={y} fill={color} textAnchor="middle" style={{fontFamily:font,fontSize:size,fontWeight:700}}>{children}</text>;
const Arrow:React.FC<{d:string;color?:string}>=({d,color=teal})=><path d={d} fill="none" stroke={color} strokeWidth={7} strokeLinecap="round" strokeLinejoin="round"/>;

const ResourceRows:React.FC<{card:Card}>=({card})=>{
  const presets:Record<string,{label:string;kind:'can'|'water'|'fuel'|'gas'|'battery';value:string;filled:number}[]>={
    'card-018':[{label:'食料',kind:'can',value:'約29日分',filled:5},{label:'飲み水',kind:'water',value:'+20 L',filled:4},{label:'ガソリン',kind:'fuel',value:'減少中',filled:4}],
    'card-038':[{label:'生活用電気',kind:'battery',value:'回復',filled:4},{label:'ガソリン',kind:'fuel',value:'消費',filled:3},{label:'ガス',kind:'gas',value:'残あり',filled:4}],
    'card-064':[{label:'食料',kind:'can',value:'約18日分',filled:3},{label:'ガソリン',kind:'fuel',value:'別々に記録',filled:3},{label:'ガス・電気',kind:'battery',value:'合計しない',filled:3}],
    'card-107':[{label:'食料',kind:'can',value:'約14日分',filled:3},{label:'ガソリン',kind:'fuel',value:'約1/4',filled:1},{label:'水道',kind:'water',value:'使用不可',filled:0}],
    'card-135':[{label:'食料',kind:'can',value:'約7日分',filled:1},{label:'ガス',kind:'gas',value:'減少',filled:1},{label:'水道',kind:'water',value:'未復旧',filled:0}],
  };
  const rows=presets[card.id]||presets['card-064'];
  const notes:Record<string,string>={'card-018':'補給はできた。運ぶ手間も増えた。','card-038':'電気を戻すために、ガソリンを使った。','card-064':'使う場所も、減り方も違う。','card-107':'走らない日にも、燃料は減っていた。','card-135':'一か月を越えても、次の補給が必要。'};
  return <Base title={card.title} note={notes[card.id]}><div style={{position:'absolute',left:255,right:255,top:310}}>{rows.map((row,i)=><div key={row.label} style={{height:176,display:'flex',alignItems:'center'}}><div style={{width:320,fontSize:44,fontWeight:600}}>{row.label}</div><div style={{display:'flex',gap:18}}>{Array.from({length:5},(_,j)=><Icon key={j} kind={row.kind} size={83} opacity={j<row.filled?1:.16}/>)}</div><div style={{marginLeft:'auto',fontSize:64,fontWeight:800,color:row.filled?ink:red}}>{row.value}</div></div>)}</div></Base>;
};

const ParkingMap:React.FC<{late:boolean}>=({late})=><Base title={late?'十七日目・同じ場所':'九日目・最初の駐車位置'} note={late?'風下に集まった雪が、出口を狭めていく。':'風は弱い。今は、出口も開いている。'}>
 <svg viewBox="0 0 1920 1080" style={{position:'absolute',inset:0,width:'100%',height:'100%'}}>
  <rect x={450} y={300} width={1030} height={155} rx={3} fill="#c6c6b8" stroke={ink} strokeWidth={5}/><Label x={960} y={400}>倉庫</Label>
  <Arrow d="M220 335H375m-23-18 23 18-23 18"/><Label x={280} y={290} size={35}>風</Label>
  <path d="M500 490q160-65 320 5t300 0 290 0" fill="none" stroke="#d3e0dc" strokeWidth={late?72:16} strokeLinecap="round"/>
  <path d="M680 650H1650" stroke={late?'#d2dcd6':'#b5b6ac'} strokeWidth={92} strokeLinecap="round"/>
  {late&&<><path d="M1350 575q70-75 145-12t145 10v150h-290z" fill="#d6e1de" stroke="#a6bdbb" strokeWidth={4}/><path d="M1440 595l95 90m0-90-95 90" stroke={red} strokeWidth={10}/></>}
  {!late&&<Arrow d="M1090 650h470m-25-20 25 20-25 20"/>}
  <Label x={1480} y={780} color={late?red:teal}>{late?'雪で狭まる出口':'開いている出口'}</Label>
  <Label x={890} y={800}>同じ駐車位置</Label>
 </svg>
 <div style={{position:'absolute',left:730,top:515}}><Icon kind="rv" size={285}/></div>
</Base>;

const SnowComparison:React.FC=()=> <Base title="積雪の変化" note="同じ場所にいても、出られる条件は変わる。"><div style={{position:'absolute',left:130,right:130,top:350,display:'flex',gap:50}}>{[{day:'9日目',depth:25,label:'浅い雪'},{day:'13日目',depth:85,label:'タイヤの下半分'},{day:'19日目',depth:145,label:'通路が埋まる'}].map((x,i)=><div key={x.day} style={{width:520,textAlign:'center',position:'relative',height:410}}><div style={{fontSize:48,fontWeight:800,marginBottom:35}}>{x.day}</div><Icon kind="rv" size={320}/><div style={{position:'absolute',left:30,right:30,bottom:45,height:x.depth,background:'#d2dfdb',borderTop:'4px solid #a2b8b7',borderRadius:'55% 35% 0 0'}}/><div style={{position:'absolute',left:0,right:0,bottom:-35,fontSize:39,fontWeight:700,color:i===2?red:gray}}>{x.label}</div></div>)}</div></Base>;

const BatteryDiagram:React.FC=()=> <Base title="同じバッテリーにつながるもの" note="小さな消費も、同じ残量から引かれていた。"><div style={{position:'absolute',left:790,top:280,width:340,textAlign:'center'}}><Icon kind="battery" size={150}/><div style={{fontSize:44,fontWeight:700}}>生活用バッテリー</div></div><svg viewBox="0 0 1920 1080" style={{position:'absolute',inset:0,width:'100%',height:'100%'}}><path d="M960 510v55M360 565h1200M360 565v60M760 565v60M1160 565v60M1560 565v60" stroke={teal} strokeWidth={6} fill="none"/></svg><div style={{position:'absolute',left:160,right:160,top:650,display:'flex',justifyContent:'space-between'}}>{[{label:'暖房ファン',icon:'heat'},{label:'外灯',icon:'battery'},{label:'電話の充電',icon:'battery'},{label:'室内灯',icon:'battery'}].map(x=><div key={x.label} style={{width:400,textAlign:'center'}}><Icon kind={x.icon as 'heat'|'battery'} size={105}/><div style={{fontSize:42,fontWeight:700,marginTop:15}}>{x.label}</div></div>)}</div></Base>;

const WalkingMap:React.FC=()=> <Base title="行きと帰りの条件" note="変わったのは距離ではなく、見通しだった。"><div style={{position:'absolute',left:150,right:150,top:350,display:'flex',gap:100}}>{['行き','帰り'].map((name,i)=><div key={name} style={{width:760,height:400,textAlign:'center',position:'relative',overflow:'hidden'}}><div style={{fontSize:48,fontWeight:800,marginBottom:65}}>{name}・約100 m</div><div style={{position:'absolute',left:45,top:150}}><Icon kind="rv" size={180}/></div><div style={{position:'absolute',right:45,top:150}}><Icon kind="station" size={180}/></div><svg width={760} height={110} style={{position:'absolute',left:0,top:270}}><path d="M100 20H650" stroke="#9caca8" strokeWidth={5} strokeDasharray="12 12"/></svg>{i===1&&<div style={{position:'absolute',left:10,right:10,top:130,height:220,background:'linear-gradient(90deg,rgba(228,235,230,.35),rgba(221,229,224,.97) 45%,rgba(221,229,224,.97) 65%,rgba(228,235,230,.35))'}}/>}<div style={{position:'absolute',bottom:5,left:0,right:0,fontSize:42,fontWeight:700,color:i?red:teal}}>{i?'車が見えない':'車が見える'}</div></div>)}</div></Base>;

const StorageDiagram:React.FC=()=> <Base title="道具は、すぐ出せるか" note="備えはある。荷物をどかさなければ、使えない。"><svg viewBox="0 0 1920 1080" style={{position:'absolute',inset:0,width:'100%',height:'100%'}}><rect x={460} y={330} width={1000} height={100} rx={25} fill="#c2c2b3" stroke={ink} strokeWidth={5}/><rect x={485} y={430} width={950} height={340} fill="#d5c5a5" stroke={ink} strokeWidth={5}/><path d="M520 700h870" stroke="#cf8e3f" strokeWidth={35}/><Label x={960} y={830} size={47}>ベッドの下の脱出用の板</Label><Arrow d="M1530 530v170m-18-23 18 23 18-23" color={red}/></svg><div style={{position:'absolute',left:570,top:455,display:'flex',gap:60}}><Icon kind="water" size={180}/><Icon kind="can" size={180}/><Icon kind="water" size={180}/><Icon kind="can" size={180}/></div></Base>;

const LocationComparison:React.FC=()=> <Base title="二つの駐車場所" note="静かさだけで、正解とは決めない。"><div style={{position:'absolute',left:200,right:200,top:340,display:'flex',gap:140}}>{[{title:'倉庫の裏',lines:['風は弱い','雪が集まる','高い壁が空を隠す']},{title:'事務所の前',lines:['風は強い','空が開いている','次の日も確認する']}].map((x,i)=><div key={x.title} style={{width:690,textAlign:'center'}}><Icon kind="rv" size={160}/><div style={{fontSize:52,fontWeight:800,margin:'20px 0 32px'}}>{x.title}</div>{x.lines.map((line,j)=><div key={line} style={{fontSize:41,fontWeight:600,color:j===1?(i?teal:red):gray,marginTop:21}}>{line}</div>)}</div>)}</div></Base>;

const ProgressMap:React.FC=()=> <Base title="二十七日目・取り戻した出口" note="数メートル進んだ。先の道は、まだ確認中。"><svg viewBox="0 0 1920 1080" style={{position:'absolute',inset:0,width:'100%',height:'100%'}}><path d="M290 610h1360" stroke="#bec9c3" strokeWidth={100}/><Arrow d="M700 480h300m-23-18 23 18-23 18"/><Label x={850} y={420} size={50}>数メートル</Label><path d="M1300 610h330" stroke="#eff0e5" strokeWidth={35} strokeDasharray="20 15"/><Label x={1460} y={770} color={gray}>先は未確認</Label></svg><div style={{position:'absolute',left:320,top:455,opacity:.35}}><Icon kind="rv" size={270}/></div><div style={{position:'absolute',left:930,top:455}}><Icon kind="rv" size={270}/></div></Base>;

const RuleCard:React.FC<{card:Card}>=({card})=>{
 const lines:Record<string,{icon:'water'|'rv'|'heat';headline:string;note:string}>= {
  'card-021':{icon:'water',headline:'残量と、使える量は別。',note:'水はある。蛇口からは出ない。'},
  'card-052':{icon:'rv',headline:'今夜の静けさと、明日の出口。',note:'一晩の快適さだけでは、場所を選べない。'},
  'card-088':{icon:'heat',headline:'排気は、見落とさない。',note:'雪が戻る。点検も、一度では終わらない。'},
  'card-140':{icon:'rv',headline:'今日の出口を描く。',note:'残量と、出発できる条件を確かめる。'},
 };
 const data=lines[card.id]||lines['card-140'];
 return <Base title="三十日間で覚えたこと" note={data.note}><div style={{position:'absolute',top:350,left:120,right:120,textAlign:'center'}}><Icon kind={data.icon} size={175}/><div style={{fontSize:69,fontWeight:800,lineHeight:1.5,marginTop:55}}>{data.headline}</div></div></Base>;
};

export const FullGraphicsV6:React.FC<{card:Card}>=({card})=>{
 if(card.kind==='day')return <DayCard day={Number(card.day)} subtitle={card.id.startsWith('v5-')?card.title:''}/>;
 if(card.id==='v5-004')return <SupplyBoard/>;
 if(card.id==='v5-006'||card.id==='card-006')return <EnergyDiagram/>;
 if(card.id==='v5-010'||card.id==='card-096')return <MobilityBoard/>;
 if(card.id==='v5-018')return <RouteDiagram/>;
 if(card.kind==='resources')return <ResourceRows card={card}/>;
 if(card.kind==='site')return <ParkingMap late={card.id==='card-080'}/>;
 if(card.kind==='snow')return <SnowComparison/>;
 if(card.kind==='storage')return <StorageDiagram/>;
 if(card.kind==='comparison')return <LocationComparison/>;
 if(card.id==='card-035')return <BatteryDiagram/>;
 if(card.id==='card-075')return <WalkingMap/>;
 if(card.id==='card-125')return <ProgressMap/>;
 return <RuleCard card={card}/>;
};
