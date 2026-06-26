import React, { useEffect, useState } from 'react';
import ReactDOM from 'react-dom/client';

const API = "http://130.185.122.76:8000";

const App = () => {
  const [user, setUser] = useState(null);
  const [dbUser, setDbUser] = useState(null);
  const [activeTab, setActiveTab] = useState('home');
  const [loading, setLoading] = useState(true);
  const [initData, setInitData] = useState("");

  const [shop, setShop] = useState([]);
  const [board, setBoard] = useState([]);
  const [games, setGames] = useState([]);
  const [groups, setGroups] = useState([]);

  useEffect(() => {
    const tg = window.Telegram?.WebApp;
    if (tg) {
      tg.expand();
      tg.ready();
      setInitData(tg.initData);
      const tgUser = tg.initDataUnsafe.user;
      setUser(tgUser);

      if (tgUser) {
        fetch(`${API}/api/user/${tgUser.id}`, {
          headers: { 'init-data': tg.initData }
        })
          .then(r => r.json())
          .then(data => {
            setDbUser(data);
            setLoading(false);
          })
          .catch(() => setLoading(false));
      } else {
        setLoading(false);
      }
    } else {
      setLoading(false);
    }
  }, []);

  async function claim() {
    const r = await fetch(`${API}/api/daily-claim/${user.id}`, {
      method: "POST",
      headers: { 'init-data': initData }
    });
    const j = await r.json();
    if (j.status === "success") {
      setDbUser({ ...dbUser, coins: j.coins });
      alert(`✅ ${j.reward} سکه گرفتی!`);
    } else {
      alert(`❌ ${j.message}`);
    }
  }

  async function loadShop() {
    const r = await fetch(`${API}/api/shop`, {
      headers: { 'init-data': initData }
    });
    const j = await r.json();
    setShop(j.items || []);
    setActiveTab("shop");
  }

  async function buyItem(itemId) {
    const r = await fetch(`${API}/api/shop/buy/${user.id}?item_id=${itemId}`, {
      method: "POST",
      headers: { 'init-data': initData }
    });
    const j = await r.json();
    if (j.status === "success") {
      setDbUser({ ...dbUser, coins: j.coins });
      alert(`✅ ${j.message}`);
    } else {
      alert(`❌ ${j.message || "خطا در خرید"}`);
    }
  }

  async function loadRank() {
    const r = await fetch(`${API}/api/leaderboard`, {
      headers: { 'init-data': initData }
    });
    setBoard(await r.json());
    setActiveTab("rank");
  }

  async function loadGames() {
    const r = await fetch(`${API}/api/games`, {
      headers: { 'init-data': initData }
    });
    setGames(await r.json());
    setActiveTab("games");
  }

  async function loadGroups() {
    const r = await fetch(`${API}/api/groups/${user.id}`, {
      headers: { 'init-data': initData }
    });
    setGroups(await r.json());
    setActiveTab("groups");
  }

  if (loading) return (
    <div className="flex items-center justify-center min-h-screen text-white bg-[#0f172a]">
      Loading SectorLand...
    </div>
  );

  return (
    <div className="min-h-screen p-4 pb-24 max-w-md mx-auto text-white bg-[#0f172a] font-sans rtl" dir="rtl">
      {/* Header Profile */}
      <div className="glass p-6 bg-gradient-to-br from-blue-600 to-purple-700 rounded-3xl mb-8 flex items-center gap-4 shadow-xl border border-white/10">
        <img
          className="w-20 h-20 rounded-2xl border-2 border-white/20 shadow-lg"
          src={user?.photo_url || `https://api.dicebear.com/7.x/bottts/svg?seed=${user?.id}`}
          alt="Avatar"
        />
        <div>
          <h2 className="text-xl font-bold">{user?.first_name}</h2>
          <p className="text-blue-100 text-sm opacity-90">
            سطح {dbUser?.level || 1} • {dbUser?.coins || 0} سکه
          </p>
          <div className="mt-1 text-xs bg-white/20 inline-block px-2 py-0.5 rounded-full">
             رتبه: {dbUser?.rank || '...'}
          </div>
        </div>
      </div>

      {/* Navigation Content */}
      {activeTab === "home" && (
        <div className="grid grid-cols-1 gap-4">
          <button className="glass p-5 w-full bg-white/5 border border-white/10 rounded-2xl flex items-center justify-between hover:bg-white/10 transition" onClick={claim}>
            <span className="flex items-center gap-3">🎁 <span>هدیه روزانه</span></span>
            <span className="text-yellow-400 font-bold">+۵۰ سکه</span>
          </button>
          <button className="glass p-5 w-full bg-white/5 border border-white/10 rounded-2xl flex items-center justify-between hover:bg-white/10 transition" onClick={loadShop}>
            <span className="flex items-center gap-3">🛒 <span>فروشگاه سکتور</span></span>
            <span className="text-blue-400">←</span>
          </button>
          <button className="glass p-5 w-full bg-white/5 border border-white/10 rounded-2xl flex items-center justify-between hover:bg-white/10 transition" onClick={loadRank}>
            <span className="flex items-center gap-3">🏆 <span>رتبه‌بندی کاربران</span></span>
            <span className="text-yellow-400">←</span>
          </button>
          <button className="glass p-5 w-full bg-white/5 border border-white/10 rounded-2xl flex items-center justify-between hover:bg-white/10 transition" onClick={loadGames}>
            <span className="flex items-center gap-3">🎮 <span>بازی‌های آنلاین</span></span>
            <span className="text-green-400">←</span>
          </button>
          <button className="glass p-5 w-full bg-white/5 border border-white/10 rounded-2xl flex items-center justify-between hover:bg-white/10 transition" onClick={loadGroups}>
            <span className="flex items-center gap-3">👥 <span>گروه‌های من</span></span>
            <span className="text-purple-400">←</span>
          </button>
        </div>
      )}

      {activeTab === "shop" && (
        <div className="animate-in fade-in duration-300">
          <button className="mb-4 text-gray-400 hover:text-white" onClick={() => setActiveTab("home")}>← بازگشت</button>
          <h2 className="text-2xl font-bold mb-6">🛒 فروشگاه</h2>
          <div className="grid grid-cols-1 gap-4">
            {shop.map(x => (
              <div className="glass p-4 bg-white/5 border border-white/10 rounded-2xl flex items-center justify-between" key={x.id}>
                <div>
                  <div className="font-bold">{x.name}</div>
                  <div className="text-yellow-500 text-sm">{x.price} سکه</div>
                </div>
                <button className="bg-blue-600 px-4 py-2 rounded-xl text-sm font-bold shadow-lg active:scale-95 transition" onClick={() => buyItem(x.id)}>خرید</button>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === "rank" && (
        <div className="animate-in fade-in duration-300">
          <button className="mb-4 text-gray-400 hover:text-white" onClick={() => setActiveTab("home")}>← بازگشت</button>
          <h2 className="text-2xl font-bold mb-6">🏆 برترین‌ها</h2>
          <div className="space-y-3">
            {board.map((x, idx) => (
              <div key={idx} className={`glass p-4 ${idx === 0 ? 'bg-yellow-500/10 border-yellow-500/50' : 'bg-white/5 border-white/10'} rounded-2xl flex items-center justify-between`}>
                <div className="flex items-center gap-4">
                  <span className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${idx === 0 ? 'bg-yellow-500 text-black' : 'bg-white/10'}`}>
                    {x.rank}
                  </span>
                  <div>
                    <div className="font-bold">{x.name}</div>
                    <div className="text-xs text-gray-400">سطح {x.level}</div>
                  </div>
                </div>
                <div className="text-yellow-500 font-bold">{x.coins.toLocaleString()} 💰</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === "games" && (
        <div className="animate-in fade-in duration-300">
          <button className="mb-4 text-gray-400 hover:text-white" onClick={() => setActiveTab("home")}>← بازگشت</button>
          <h2 className="text-2xl font-bold mb-6">🎮 بازی‌ها</h2>
          <div className="grid grid-cols-2 gap-4">
            {games.map(g => (
              <div className={`glass p-6 rounded-3xl border border-white/10 flex flex-col items-center justify-center gap-3 ${g.active ? 'bg-white/10' : 'bg-black/40 opacity-60'}`} key={g.id}>
                <div className="text-4xl">{g.id === 'snake' ? '🐍' : g.id === 'hokm' ? '🃏' : '❓'}</div>
                <div className="font-bold">{g.name}</div>
                {!g.active && <div className="text-xs bg-red-500/20 text-red-400 px-2 py-0.5 rounded-full">قفل شده</div>}
                {g.active && <button className="mt-2 bg-green-600 text-xs px-4 py-1 rounded-lg">شروع</button>}
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === "groups" && (
        <div className="animate-in fade-in duration-300">
          <button className="mb-4 text-gray-400 hover:text-white" onClick={() => setActiveTab("home")}>← بازگشت</button>
          <h2 className="text-2xl font-bold mb-6">👥 گروه‌های تحت مدیریت</h2>
          <div className="space-y-4">
            {groups.length === 0 ? (
              <div className="text-center py-10 text-gray-500">هیچ گروهی یافت نشد.</div>
            ) : groups.map(g => (
              <div className="glass p-4 bg-white/5 border border-white/10 rounded-2xl" key={g.id}>
                <div className="font-bold mb-3">{g.title}</div>
                <div className="flex gap-2 text-[10px]">
                  <span className={`px-2 py-1 rounded-md ${g.settings.ai ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}`}>AI</span>
                  <span className={`px-2 py-1 rounded-md ${g.settings.antispam ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}`}>AntiSpam</span>
                  <span className={`px-2 py-1 rounded-md ${g.settings.welcome ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}`}>Welcome</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
