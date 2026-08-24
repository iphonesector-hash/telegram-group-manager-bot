import React from 'react'

const PACKS={
 mission:['missions-v3','daily_crystal'],boss:['missions-v3','crystal_golem'],story:['story-v3','awakening'],
 visit:['social-v3','visit'],gift:['social-v3','gift'],duel:['social-v3','duel'],bond:['social-v3','bond'],
 memory:['social-v3','memory_record'],archive:['social-v3','memory_archive'],profile:['social-v3','profile'],share:['social-v3','share_card'],
 happy:['emotions-v3','happy'],sad:['emotions-v3','sad'],angry:['emotions-v3','angry'],sleepy:['emotions-v3','sleepy'],
 hungry:['emotions-v3','hungry'],sick:['emotions-v3','sick'],dirty:['emotions-v3','dirty'],low_energy:['emotions-v3','low_energy'],
 excited:['emotions-v3','excited'],love:['emotions-v3','love'],confused:['emotions-v3','confused'],offline:['emotions-v3','offline']
}

export default function SectorFeatureArt({kind='mission',compact=false,className=''}){
 const [dir,file]=PACKS[kind]||PACKS.mission
 return <img className={className} src={`/assets/sector/${dir}/${file}.webp`} alt="" loading="lazy" style={{display:'block',width:'100%',height:compact?112:220,objectFit:'cover',borderRadius:16}}/>
}

export function StoryPathArt({path='engineer'}){
 const file=['engineer','guardian','explorer','commander'].includes(path)?path:'awakening'
 return <img src={`/assets/sector/story-v3/${file}.webp`} alt="" loading="lazy" style={{display:'block',width:'100%',height:150,objectFit:'cover',borderRadius:14}}/>
}
