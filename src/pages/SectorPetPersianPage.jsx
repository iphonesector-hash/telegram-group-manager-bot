import {useEffect} from 'react'
import SectorPetPage from './SectorPetPage'

const EXACT = new Map([
  ['SECTOR INVENTORY','دارایی‌های سکتور'],
  ['SECTOR MEMORY CIRCUIT','مدار حافظه سکتور'],
  ['REACTION PULSE','شکار پالس'],
  ['QUANTUM CIPHER','رمز کوانتومی'],
  ['CORE BALANCE','تعادل هسته'],
  ['Sector Unit','واحد سکتور'],
  ['Scrap Unit','واحد فرسوده'],
  ['Sector Koochooloo Beta','سکتور کوچولو · نسخه آزمایشی'],
])

function translateText(value){
  let text=String(value||'')
  if(EXACT.has(text.trim())) return text.replace(text.trim(),EXACT.get(text.trim()))
  text=text.replace(/\bXP\b/g,'امتیاز تجربه')
  text=text.replace(/\bCOMMON\b/gi,'معمولی').replace(/\bRARE\b/gi,'کمیاب').replace(/\bEPIC\b/gi,'حماسی').replace(/\bLEGENDARY\b/gi,'افسانه‌ای').replace(/\bMYTHIC\b/gi,'اسطوره‌ای')
  return text
}

function persianize(root){
  if(!root)return
  const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT)
  const nodes=[]
  while(walker.nextNode())nodes.push(walker.currentNode)
  nodes.forEach(node=>{const next=translateText(node.nodeValue);if(next!==node.nodeValue)node.nodeValue=next})
  root.querySelectorAll('[aria-label]').forEach(el=>{const current=el.getAttribute('aria-label');const next=translateText(current);if(next!==current)el.setAttribute('aria-label',next)})
}

export default function SectorPetPersianPage(){
  useEffect(function(){
    const root=document.querySelector('[data-sector-persian-root]')
    if(!root)return
    persianize(root)
    const observer=new MutationObserver(()=>persianize(root))
    observer.observe(root,{subtree:true,childList:true,characterData:true})
    return()=>observer.disconnect()
  },[])
  return <div data-sector-persian-root style={{display:'contents'}}><SectorPetPage/></div>
}
