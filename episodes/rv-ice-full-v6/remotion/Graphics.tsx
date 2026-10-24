import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';

const ink='#252b2e';
const muted='#747b7e';
const teal='#437e82';
const amber='#d29a4d';
const red='#ab4e42';
export const font='"Yu Gothic", "Meiryo", sans-serif';
type IconKind='water'|'can'|'fuel'|'gas'|'battery'|'engine'|'heat'|'wheel'|'rv'|'station'|'city';

export const Icon:React.FC<{kind:IconKind;size?:number;opacity?:number}> = ({kind,size=110,opacity=1}) => <svg viewBox="0 0 140 140" width={size} height={size} style={{opacity,overflow:'visible'}} fill="none" stroke={ink} strokeWidth={3.8} strokeLinecap="round" strokeLinejoin="round">
  {kind==='water'&&<><path d="M49 19h40v16l12 13v65q-1 10-12 10H44q-10-1-10-12V51l15-16z" fill="#9fc7d4"/><path d="M52 18h34v13H52z" fill="#384952"/><path d="M43 67h49v44H43z" fill="#b9dce5" stroke="#6999ac"/><path d="M59 69v41M76 69v41" stroke="#80b2c5"/><path d="M89 45q14 2 12 21H88z" fill="#d7e9e9"/><path d="M44 44l5-4" stroke="#f7ffff"/></>}
  {kind==='can'&&<><path d="M36 32h69v78q-2 11-34 12-34-1-35-12z" fill="#bfcbc8"/><path d="M38 50h65v45H38z" fill="#d49c51" strokeWidth={2}/><ellipse cx={70} cy={32} rx={35} ry={10} fill="#dfe1d7"/><ellipse cx={70} cy={32} rx={24} ry={5} stroke="#8e9998" strokeWidth={2}/><path d="M39 108q32 12 64 0" stroke="#7e8d8c"/><path d="M46 54v37" stroke="#eed1a3"/></>}
  {kind==='fuel'&&<><path d="M32 30q0-8 8-8h39q8 0 8 8v90H29V38z" fill="#b9c9c4"/><path d="M41 35h35v30H41z" fill="#e1e9df"/><path d="M42 80h31M41 90h24"/><path d="M87 45q29 3 27 25v29q0 13-13 10-8-2-8-12V78" stroke={teal}/><path d="M100 27l15 13-4 23-12-8 5-14z" fill="#4e6468"/><path d="M24 121h69" strokeWidth={5}/></>}
  {kind==='gas'&&<><path d="M49 34v-9h39v9M60 23v-9h17v9" fill="#8c9897"/><path d="M45 39q-14 13-13 32v39q0 14 38 14t38-14V71q1-22-18-34z" fill="#b9c9bf"/><path d="M34 79h72M35 105h70" stroke="#7c9691"/><path d="M51 51q-10 8-9 22" stroke="#e8eee1"/><path d="M61 85q12-18 21 0 5 10-7 16-15 1-14-16" fill={amber} strokeWidth={2}/></>}
  {kind==='battery'&&<><path d="M29 37h81v76H29z" fill="#b0c2ba"/><path d="M40 23h17v14H40zM83 23h17v14H83z" fill="#5f7775"/><path d="M42 60h17M50 52v17M85 61h14"/><path d="M75 73L59 95h15l-7 17 23-28H75z" fill={amber} strokeWidth={2}/></>}
  {kind==='engine'&&<><path d="M28 58h19V41h39v10h22l14 17v32H98l-9 13H50l-11-13H25z" fill="#aabbb7"/><path d="M13 62v33M13 78h13M54 25h31M68 25v15"/><path d="M48 64h42v30H48z" fill="#d6dfd4"/><path d="M57 72h23M58 82h15" stroke="#69817b"/></>}
  {kind==='heat'&&<><path d="M27 66h87v54H27z" fill="#b7c4b9"/><path d="M39 80h61M39 93h61M39 106h61" stroke="#718881"/><path d="M43 52q-14-13 1-25t0-22M72 52q-13-13 1-25t0-22M101 52q-14-13 1-25t0-22" stroke={amber} strokeWidth={5}/></>}
  {kind==='wheel'&&<><ellipse cx={70} cy={72} rx={43} ry={49} fill="#4d5a5c"/><ellipse cx={70} cy={72} rx={25} ry={31} fill="#aab6ae"/><circle cx={70} cy={72} r={9} fill="#667c7b"/><path d="M35 40l12 6M28 57l12 4M28 84l12-2M34 104l12-7M90 33l10 11M100 53l10 6M101 86l11-2M93 106l12-6" stroke="#253438"/><path d="M17 123h108" stroke="#c6d1cf" strokeWidth={8}/></>}
  {kind==='rv'&&<><path d="M12 40h79l19 23h18v43H12z" fill="#e5d8ba"/><path d="M17 78h107v9H17z" fill={teal} strokeWidth={1.5}/><path d="M24 49h25v22H24zM60 49h22v22H60zM94 53l13 18H94z" fill="#93afb8"/><path d="M61 77h23v30H61z" fill="#ded0ae"/><circle cx={37} cy={108} r={13} fill="#445256"/><circle cx={107} cy={108} r={13} fill="#445256"/><circle cx={37} cy={108} r={5} fill="#aebbb7"/><circle cx={107} cy={108} r={5} fill="#aebbb7"/><path d="M17 32h31M53 32h31" stroke={teal} strokeWidth={6}/></>}
  {kind==='station'&&<><path d="M14 38h110l-6 18H18z" fill="#c9b28a"/><path d="M24 57v65M116 57v65" strokeWidth={7}/><path d="M35 82h44v41H35z" fill="#a5bfc0"/><path d="M42 89h28v16H42z" fill="#d6e3df"/><path d="M82 85q22-1 18 22"/><path d="M28 25h64v13H28z" fill="#e4d9be"/></>}
  {kind==='city'&&<><path d="M10 123V67h32v56M42 123V26h37v97M79 123V48h42v75" fill="#a8b9ba"/><path d="M51 39h18M51 53h18M51 68h18M51 83h18M51 98h18M88 61h23M88 77h23M88 93h23M18 80h15M18 96h15" stroke="#e4e7dc" strokeWidth={5}/></>}
</svg>;

const Title:React.FC<{children:React.ReactNode}> = ({children}) => <div style={{position:'absolute',top:114,left:130,right:130,textAlign:'center',fontSize:78,fontWeight:800,letterSpacing:2,lineHeight:1.3}}>{children}</div>;
const Note:React.FC<{children:React.ReactNode}> = ({children}) => <div style={{position:'absolute',bottom:135,left:140,right:140,textAlign:'center',fontSize:40,fontWeight:600,color:muted,lineHeight:1.5}}>{children}</div>;
const Paper:React.FC<{children:React.ReactNode}> = ({children}) => <AbsoluteFill lang="ja" style={{background:'#f2efe5',color:ink,fontFamily:font,backgroundImage:'radial-gradient(ellipse at 55% 45%, #f8f5ec 0%, #efecdf 100%)'}}>{children}</AbsoluteFill>;
const Arrow:React.FC<{path:string;color?:string}> = ({path,color=teal}) => <path d={path} fill="none" stroke={color} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round"/>;

export const SupplyBoard:React.FC = () => <Paper>
  <Title>出発時の備蓄</Title>
  <div style={{position:'absolute',left:265,top:310,right:265}}>
    <div style={{height:185,display:'flex',alignItems:'center'}}><div style={{fontSize:45,width:220,fontWeight:600}}>飲み水</div><div style={{display:'flex',gap:5}}>{Array.from({length:8},(_,i)=><Icon key={i} kind="water" size={84}/>)}</div><div style={{marginLeft:'auto',fontSize:80,fontWeight:800}}>40 L</div></div>
    <div style={{height:185,display:'flex',alignItems:'center'}}><div style={{fontSize:45,width:220,fontWeight:600}}>食料</div><div style={{display:'flex',gap:15}}>{Array.from({length:4},(_,i)=><Icon key={i} kind="can" size={94}/>)}</div><div style={{marginLeft:'auto',fontSize:78,fontWeight:800}}>20日分</div></div>
    <div style={{height:175,display:'flex',alignItems:'center'}}><div style={{fontSize:45,width:220,fontWeight:600}}>ガソリン</div><Icon kind="fuel" size={114}/><div style={{display:'flex',gap:10,marginLeft:26}}>{Array.from({length:7},(_,i)=><div key={i} style={{width:44,height:66,background:'#6e9891',border:'3px solid #3b5555',borderRadius:'5px 5px 2px 2px'}}/>)}</div><div style={{marginLeft:'auto',fontSize:78,fontWeight:800}}>満タン</div></div>
  </div>
  <Note>ひとり分の備蓄。ここから、減っていく。</Note>
</Paper>;

export const EnergyDiagram:React.FC = () => <Paper>
  <Title>残量は、ひとつではない</Title>
  <svg viewBox="0 0 1920 1080" style={{position:'absolute',inset:0,width:'100%',height:'100%'}}>
    <Arrow path="M470 530V585m-15-17 15 17 15-17"/>
    <Arrow path="M1075 520v30h205v35m-15-17 15 17 15-17"/>
    <Arrow path="M1485 520v30h-205"/>
    <path d="M795 300v435" stroke="#d7d2c4" strokeWidth={3}/>
  </svg>
  <div style={{position:'absolute',left:350,top:290,width:240,textAlign:'center'}}><Icon kind="fuel" size={145}/><div style={{fontSize:45,fontWeight:700,marginTop:7}}>ガソリン</div></div>
  <div style={{position:'absolute',left:355,top:590,width:230,textAlign:'center'}}><Icon kind="engine" size={145}/><div style={{fontSize:50,fontWeight:800}}>走行</div></div>
  <div style={{position:'absolute',left:955,top:285,width:240,textAlign:'center'}}><Icon kind="gas" size={145}/><div style={{fontSize:45,fontWeight:700}}>ガス</div></div>
  <div style={{position:'absolute',left:1345,top:285,width:280,textAlign:'center'}}><Icon kind="battery" size={145}/><div style={{fontSize:45,fontWeight:700}}>生活用電気</div></div>
  <div style={{position:'absolute',left:1160,top:600,width:240,textAlign:'center'}}><Icon kind="heat" size={145}/><div style={{fontSize:50,fontWeight:800}}>暖房</div></div>
  <Note>この車の暖房には、ガスと電気が必要。</Note>
</Paper>;

export const MobilityBoard:React.FC = () => <Paper>
  <Title>十九日目の状態</Title>
  <div style={{position:'absolute',left:380,top:300,right:330}}>
    {([{kind:'fuel',label:'ガソリン',value:'残っている',color:teal},{kind:'engine',label:'エンジン',value:'かかる',color:teal},{kind:'wheel',label:'車体',value:'動かない',color:red}] as const).map((x,i)=><div key={x.label} style={{height:170,display:'flex',alignItems:'center',borderBottom:i<2?'2px solid #ddd8cb':undefined}}><Icon kind={x.kind} size={120}/><div style={{marginLeft:35,fontSize:50,fontWeight:600}}>{x.label}</div><div style={{marginLeft:'auto',fontSize:66,fontWeight:800,color:x.color}}>{x.value}</div></div>)}
  </div>
  <Note>燃料計だけでは、出口は分からない。</Note>
</Paper>;

export const RouteDiagram:React.FC = () => <Paper>
  <Title>残された道</Title>
  <svg viewBox="0 0 1920 1080" style={{position:'absolute',inset:0,width:'100%',height:'100%'}}>
    <path d="M1190 270q-50 130 0 250t-5 265" stroke="#b7d3da" strokeWidth={150} fill="none"/>
    <path d="M275 530h1370" stroke="#b5b6ac" strokeWidth={78}/><path d="M275 530h1370" stroke="#f8f4e9" strokeWidth={5} strokeDasharray="20 22"/>
    <path d="M1100 485h185M1100 575h185" stroke={ink} strokeWidth={8}/>
    <path d="M1128 500l130 60m0-60-130 60" stroke={red} strokeWidth={14} strokeLinecap="round"/>
    <path d="M850 665H360m30-22-30 22 30 22" stroke={teal} strokeWidth={8} fill="none" strokeLinecap="round" strokeLinejoin="round"/>
    <circle cx={855} cy={530} r={12} fill={teal}/>
  </svg>
  <div style={{position:'absolute',left:230,top:310,width:230,textAlign:'center'}}><div style={{fontSize:42,fontWeight:600,marginBottom:10}}>給油所</div><Icon kind="station" size={130}/></div>
  <div style={{position:'absolute',left:750,top:315,width:220,textAlign:'center'}}><div style={{fontSize:42,fontWeight:800,marginBottom:12}}>現在地</div><Icon kind="rv" size={160}/></div>
  <div style={{position:'absolute',left:1050,top:620,width:280,textAlign:'center',fontSize:46,fontWeight:800,color:red}}>橋・通行不可</div>
  <div style={{position:'absolute',left:1475,top:310,width:210,textAlign:'center'}}><div style={{fontSize:42,fontWeight:600,marginBottom:10}}>街</div><Icon kind="city" size={130}/></div>
  <div style={{position:'absolute',left:485,top:715,fontSize:44,fontWeight:700,color:teal}}>引き返す道は残っている</div>
  <Note>街へ戻る道が、ここで途切れた。</Note>
</Paper>;

export const DayCard:React.FC<{day:number;subtitle:string}> = ({day,subtitle}) => {
  const frame=useCurrentFrame();
  return <AbsoluteFill lang="ja" style={{background:'#161a1c',fontFamily:font,alignItems:'center',justifyContent:'center',color:'#f4f1e7'}}>
    <div style={{fontSize:34,color:'#c3b798',letterSpacing:5,marginBottom:28,opacity:interpolate(frame,[0,4],[0,1],{extrapolateRight:'clamp'})}}>{subtitle}</div>
    <div style={{fontSize:154,fontWeight:800,letterSpacing:8,lineHeight:1.1}}>{day}日目</div>
  </AbsoluteFill>;
};
