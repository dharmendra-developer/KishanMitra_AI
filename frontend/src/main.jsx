import React,{useState} from "react";
import {createRoot} from "react-dom/client";
import axios from "axios";
import "./style.css";

const API="http://localhost:4000/api";

function App(){
 const [page,setPage]=useState("Dashboard"),[user,setUser]=useState(null),[result,setResult]=useState(null),[msg,setMsg]=useState("");
 const [chat,setChat]=useState(""),[answer,setAnswer]=useState("");
 const [form,setForm]=useState({ph:7,nitrogen:80,phosphorus:40,potassium:60,moisture:35,crop:"Rice",season:"Kharif",water:"medium"});
 const nav=["Dashboard","AI Crop Doctor","Weather","Soil Health","Irrigation","Crop Recommendation","Mandi","Government Schemes","Farm Calculator","AI Chatbot"];

 async function cropDoctor(e){const fd=new FormData();fd.append("image",e.target.files[0]);setMsg("Analyzing...");const r=await axios.post(API+"/crop-doctor",fd);setResult(r.data);setMsg("")}
 async function post(path,data){const r=await axios.post(API+path,data);setResult(r.data)}
 async function ask(){const r=await axios.post(API+"/chat",{message:chat});setAnswer(r.data.answer)}
 function Dashboard(){return <><h1>🌾 KisanMitra AI</h1><p className="lead">From Seed to Harvest — Smart decisions for farmers.</p><div className="cards">{[["🌱","Current Crop","Rice"],["🌦️","Weather","31°C"],["💧","Irrigation","Check moisture"],["🦠","Disease Alerts","1 review"],["📈","Mandi","Prices rising"],["💰","Estimated Profit","₹48,500"]].map(x=><div className="card"><b>{x[0]} {x[1]}</b><strong>{x[2]}</strong></div>)}</div></>}
 function Content(){
  if(page==="Dashboard")return <Dashboard/>;
  if(page==="AI Crop Doctor")return <><h2>🦠 AI Crop Doctor</h2><p>Upload a clear crop/leaf photo.</p><input type="file" accept="image/*" onChange={cropDoctor}/>{msg&&<p>{msg}</p>}{result&&<div className="result"><h3>{result.crop} — {result.disease}</h3><p>Severity: {result.severity} | Confidence: {(result.confidence*100).toFixed(0)}%</p><ul>{result.treatment?.map(t=><li>{t}</li>)}</ul><small>AI output is advisory; follow local agricultural guidance and expert verification when needed.</small></div></>;
  if(page==="Weather")return <><h2>🌦️ Smart Weather</h2><div className="result"><h3>31°C · Partly Cloudy</h3><p>Humidity 68% · Wind 12 km/h · Rain chance 42%</p><b>Advisory:</b> Check soil moisture before irrigation.</div></>;
  if(page==="Soil Health")return <Tool title="🧪 Soil Health" path="/soil" fields={["ph","nitrogen","phosphorus","potassium"]} form={form} setForm={setForm} post={post}/>;
  if(page==="Irrigation")return <Tool title="💧 Smart Irrigation" path="/irrigation" fields={["crop","moisture"]} form={form} setForm={setForm} post={post}/>;
  if(page==="Crop Recommendation")return <Tool title="🌱 Crop Recommendation" path="/crop-recommendation" fields={["ph","season","water"]} form={form} setForm={setForm} post={post}/>;
  if(page==="Mandi")return <><h2>📈 Mandi Prices</h2><button onClick={async()=>setResult((await axios.get(API+"/market")).data)}>Load Prices</button>{result?.markets&&<div className="table">{result.markets.map(m=><p><b>{m.crop}</b> — {m.price} {m.unit} — {m.trend}</p>)}</div>}</>;
  if(page==="Government Schemes")return <><h2>🏛️ Government Schemes</h2><button onClick={async()=>setResult((await axios.get(API+"/schemes")).data)}>Load Schemes</button>{Array.isArray(result)&&result.map(s=><div className="result"><h3>{s.name}</h3><p>{s.description}</p><small>{s.documents}</small></div>)}</>;
  if(page==="Farm Calculator")return <Calculator/>;
  if(page==="AI Chatbot")return <><h2>🤖 AI Farming Assistant</h2><input value={chat} onChange={e=>setChat(e.target.value)} placeholder="Ask about irrigation, disease..." /><button onClick={ask}>Ask</button>{answer&&<div className="result">{answer}</div></>;
 }
 return <div className="app"><aside><div className="logo">🌾 KisanMitra</div>{nav.map(n=><button className={page===n?"active":""} onClick={()=>{setPage(n);setResult(null)}}>{n}</button>)}</aside><main>{Content()}</main></div>
}
function Tool({title,path,fields,form,setForm,post}){return <><h2>{title}</h2>{fields.map(f=><input value={form[f]} onChange={e=>setForm({...form,[f]:e.target.value})} placeholder={f}/>) }<button onClick={()=>post(path,form)}>Get AI Recommendation</button><pre>{/* result is shown through a simple browser console in MVP; extend UI as needed */}</pre></>}
function Calculator(){const [x,setX]=useState({seed:0,fertilizer:0,pesticide:0,labour:0,irrigation:0,other:0,production:0,price:0});const total=Object.values(x).slice(0,6).reduce((a,b)=>a+Number(b),0),rev=Number(x.production)*Number(x.price);return <><h2>💰 Farm Profit Calculator</h2>{Object.keys(x).map(k=><input value={x[k]} onChange={e=>setX({...x,[k]:e.target.value})} placeholder={k}/>)}<div className="result"><b>Total Cost: ₹{total.toFixed(2)}</b><br/>Revenue: ₹{rev.toFixed(2)}<br/>Estimated Profit: ₹{(rev-total).toFixed(2)}</div></>}
createRoot(document.getElementById("root")).render(<App/>);
