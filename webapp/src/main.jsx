import React, { useEffect, useState } from 'react';
import ReactDOM from 'react-dom/client';

const API = "http://130.185.122.76:8000";

const App = () => {

  const [user,setUser] = useState(null);
  const [dbUser,setDbUser] = useState(null);
  const [activeTab,setActiveTab] = useState('home');
  const [loading,setLoading] = useState(true);

  const [shop,setShop] = useState([]);
  const [board,setBoard] = useState([]);
  const [games,setGames] = useState([]);


  useEffect(()=>{

    const tg = window.Telegram?.WebApp;

    if(tg){

      tg.expand();
      tg.ready();

      const tgUser = tg.initDataUnsafe.user;

      setUser(tgUser);


      if(tgUser){

        fetch(`${API}/api/user/${tgUser.id}`)
        .then(r=>r.json())
        .then(data=>{
          setDbUser(data);
          setLoading(false);
        })
        .catch(()=>{
          setLoading(false);
        });

      } else {
        setLoading(false);
      }

    } else {
      setLoading(false);
    }

  },[]);



  async function claim(){

    const r = await fetch(
      `${API}/api/daily-claim/${user.id}`,
      {
        method:"POST"
      }
    );

    const j = await r.json();

    alert(
      j.message ||
      `+${j.reward} سکه گرفتی`
    );

  }



  async function loadShop(){

    const r = await fetch(
      `${API}/api/shop`
    );

    const j = await r.json();

    setShop(j.items || []);

    setActiveTab("shop");

  }



  async function loadRank(){

    const r = await fetch(
      `${API}/api/leaderboard`
    );

    setBoard(await r.json());

    setActiveTab("rank");

  }



  async function loadGames(){

    const r = await fetch(
      `${API}/api/games`
    );

    setGames(await r.json());

    setActiveTab("games");

  }



  if(loading)
    return (
      <div className="flex items-center justify-center min-h-screen">
        Loading SectorLand...
      </div>
    );



  return (

<div className="min-h-screen p-4 pb-24 max-w-md mx-auto">


<div className="glass p-6 premium-gradient mb-8 flex items-center gap-4">

<img
className="w-20 h-20 rounded-2xl"
src={
user?.photo_url ||
"https://api.dicebear.com/7.x/bottts/svg?seed="+user?.id
}
/>

<div>

<h2 className="text-xl font-bold">
{user?.first_name}
</h2>

<p>
سطح {dbUser?.level || 1}
 • {dbUser?.coins || 0} سکه
</p>

</div>

</div>



{activeTab==="home" && (

<div className="space-y-5">


<button
className="glass p-5 w-full"
onClick={claim}
>
🎁 دریافت هدیه روزانه ۵۰ سکه
</button>



<button
className="glass p-5 w-full"
onClick={loadShop}
>
🛒 فروشگاه
</button>



<button
className="glass p-5 w-full"
onClick={loadRank}
>
🏆 رتبه بندی
</button>



<button
className="glass p-5 w-full"
onClick={loadGames}
>
🎮 بازی ها
</button>


</div>

)}





{activeTab==="shop" && (

<div>

<button onClick={()=>setActiveTab("home")}>
← برگشت
</button>


<h2 className="text-2xl">
فروشگاه
</h2>


{shop.map(x=>

<div className="glass p-4" key={x.id}>

{x.name}

<br/>

{x.price} سکه

</div>

)}

</div>

)}




{activeTab==="rank" && (

<div>

<button onClick={()=>setActiveTab("home")}>
← برگشت
</button>


<h2>
🏆 رتبه بندی
</h2>


{board.map(x=>

<div key={x.rank}>

#{x.rank}
{" "}
{x.name}
{" "}
{x.coins}

</div>

)}

</div>

)}




{activeTab==="games" && (

<div>

<button onClick={()=>setActiveTab("home")}>
← برگشت
</button>


<h2>
🎮 بازی ها
</h2>


{games.map(g=>

<div className="glass p-4" key={g.id}>

{g.name}

{" "}

{g.active ? "✅" : "🔒"}

</div>

)}

</div>

)}




</div>

)

};


ReactDOM.createRoot(
document.getElementById('root')
).render(<App/>);
