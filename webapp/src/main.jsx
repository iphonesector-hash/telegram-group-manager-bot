import React, { useEffect, useState, useRef } from 'react';
import ReactDOM from 'react-dom/client';
import { motion, AnimatePresence } from 'framer-motion';

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

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

  // Cooldowns
  const [dailyCooldown, setDailyCooldown] = useState(0);
  const [wheelCooldown, setWheelCooldown] = useState(0);

  useEffect(() => {
    const tg = window.Telegram?.WebApp;
    if (tg) {
      tg.expand();
      tg.ready();
      const rawInitData = tg.initData;
      setInitData(rawInitData);
      const tgUser = tg.initDataUnsafe.user;
      setUser(tgUser);

      if (tgUser) {
        fetch(`${API}/api/user/${tgUser.id}`, {
          headers: { 'init-data': rawInitData }
        })
          .then(r => {
            if (!r.ok) throw new Error(r.status);
            return r.json();
          })
          .then(data => {
            if (data.id) {
              setDbUser(data);
              setDailyCooldown(data.cooldowns?.daily || 0);
              setWheelCooldown(data.cooldowns?.wheel || 0);
            }
            setLoading(false);
          })
          .catch(err => {
            handleApiError(err, "دریافت اطلاعات کاربر");
            setLoading(false);
          });
      } else {
        setLoading(false);
      }
    } else {
      setLoading(false);
    }
  }, []);

  const handleApiError = (err, context) => {
    console.error(`API Error [${context}]:`, err);
    let msg = `خطا در ${context}. لطفاً دوباره تلاش کنید.`;
    if (err.message === "403") msg = "نشست تلگرام شما منقضی شده یا نامعتبر است.";
    if (err.message === "404") msg = "اطلاعات یافت نشد.";
    alert(`⚠️ ${msg}`);
  };

  useEffect(() => {
    const timer = setInterval(() => {
      setDailyCooldown(c => Math.max(0, c - 1));
      setWheelCooldown(c => Math.max(0, c - 1));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const apiFetch = async (endpoint, options = {}) => {
    try {
      const response = await fetch(`${API}${endpoint}`, {
        ...options,
        headers: {
          ...options.headers,
          'init-data': initData
        }
      });
      if (!response.ok) throw new Error(response.status);
      return await response.json();
    } catch (error) {
      handleApiError(error, endpoint);
      return null;
    }
  };

  async function claim() {
    if (dailyCooldown > 0) return;
    const data = await apiFetch(`/api/daily-claim/${user.id}`, { method: "POST" });
    if (data) {
      if (data.status === "success") {
        setDbUser({ ...dbUser, coins: data.coins });
        setDailyCooldown(data.cooldown);
      } else {
        alert(`❌ ${data.message}`);
      }
    }
  }

  const loadShop = async () => {
    setActiveTab("shop");
    const data = await apiFetch("/api/shop");
    if (data) setShop(data.items || []);
  }

  const loadRank = async () => {
    setActiveTab("rank");
    const data = await apiFetch("/api/leaderboard");
    if (data) setBoard(data);
  }

  const loadGames = async () => {
    setActiveTab("games");
    const data = await apiFetch("/api/games");
    if (data) setGames(data);
  }

  const loadGroups = async () => {
    setActiveTab("groups");
    const data = await apiFetch(`/api/groups/${user.id}`);
    if (data) setGroups(data);
  }

  const formatTime = (seconds) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  }

  if (loading) return (
    <div className="flex items-center justify-center min-h-screen text-white bg-[#0f172a]">
      <div className="animate-pulse text-xl">SectorLand Loading...</div>
    </div>
  );

  return (
    <div className="min-h-screen p-4 pb-32 max-w-md mx-auto text-white bg-[#0f172a] font-sans rtl" dir="rtl">
       <div className="glass p-6 bg-gradient-to-br from-blue-600 to-purple-700 rounded-3xl mb-6 flex items-center gap-4 shadow-xl border border-white/10">
        <img
          className="w-16 h-16 rounded-2xl border-2 border-white/20 shadow-lg"
          src={user?.photo_url || `https://api.dicebear.com/7.x/bottts/svg?seed=${user?.id}`}
          alt="Avatar"
        />
        <div>
          <h2 className="text-xl font-bold">{user?.first_name}</h2>
          <p className="text-blue-100 text-sm opacity-90">
            سطح {dbUser?.level || 1} • {dbUser?.coins || 0} سکه
          </p>
        </div>
      </div>

      <AnimatePresence mode="wait">
        {activeTab === 'home' && <HomeTab claim={claim} cooldown={dailyCooldown} formatTime={formatTime} nav={{loadShop, loadGames, loadRank, loadGroups}} />}
        {activeTab === 'shop' && <ShopTab items={shop} buyItem={(id) => apiFetch(`/api/shop/buy/${user.id}?item_id=${id}`, {method: 'POST'})} updateCoins={(c) => setDbUser({...dbUser, coins: c})} />}
        {activeTab === 'games' && <GamesTab user={user} dbUser={dbUser} setDbUser={setDbUser} cooldown={wheelCooldown} setWheelCooldown={setWheelCooldown} apiFetch={apiFetch} />}
        {activeTab === 'rank' && <RankTab board={board} />}
        {activeTab === 'groups' && <GroupsTab groups={groups} />}
      </AnimatePresence>

      <div className="fixed bottom-0 left-0 right-0 p-4 bg-[#0f172a]/90 backdrop-blur-xl border-t border-white/10 z-50">
        <div className="max-w-md mx-auto flex justify-between items-center gap-1">
          <NavButton icon="🏠" label="خانه" active={activeTab === 'home'} onClick={() => setActiveTab('home')} />
          <NavButton icon="🛒" label="فروشگاه" active={activeTab === 'shop'} onClick={loadShop} />
          <NavButton icon="🎮" label="بازی" active={activeTab === 'games'} onClick={loadGames} />
          <NavButton icon="🏆" label="رتبه" active={activeTab === 'rank'} onClick={loadRank} />
          <NavButton icon="👥" label="گروه" active={activeTab === 'groups'} onClick={loadGroups} />
        </div>
      </div>
    </div>
  );
};

const HomeTab = ({ claim, cooldown, formatTime, nav }) => (
  <motion.div initial={{opacity: 0, y: 20}} animate={{opacity: 1, y: 0}} exit={{opacity: 0, y: -20}} className="space-y-4">
    <div className="bg-white/5 p-8 rounded-3xl border border-white/10 text-center">
      <div className="text-5xl mb-4">✨</div>
      <h3 className="text-2xl font-bold mb-2">خوش اومدی!</h3>
      <p className="text-gray-400 text-sm">آماده‌ای برای ماجراجویی در سکتورلند؟</p>
    </div>

    <button
      disabled={cooldown > 0}
      className={`glass p-6 w-full rounded-2xl flex items-center justify-between transition ${cooldown > 0 ? 'opacity-50 grayscale cursor-not-allowed' : 'bg-gradient-to-r from-yellow-500/30 to-orange-500/30 active:scale-95 border-yellow-500/40'}`}
      onClick={claim}
    >
      <span className="flex items-center gap-3 text-lg font-bold">🎁 <span>هدیه روزانه</span></span>
      <span className="text-yellow-400 font-bold">{cooldown > 0 ? formatTime(cooldown) : '+۵۰ سکه'}</span>
    </button>

    <div className="grid grid-cols-2 gap-4">
      <MenuBtn icon="🛒" label="فروشگاه" onClick={nav.loadShop} color="from-indigo-500/20" />
      <MenuBtn icon="🎮" label="بازی‌ها" onClick={nav.loadGames} color="from-emerald-500/20" />
      <MenuBtn icon="🏆" label="برترین‌ها" onClick={nav.loadRank} color="from-amber-500/20" />
      <MenuBtn icon="👥" label="گروه‌ها" onClick={nav.loadGroups} color="from-pink-500/20" />
    </div>
  </motion.div>
);

const GamesTab = ({ user, dbUser, setDbUser, cooldown, setWheelCooldown, apiFetch }) => {
  const [subGame, setSubGame] = useState(null);

  if (subGame === 'wheel') return <WheelGame user={user} setDbUser={setDbUser} cooldown={cooldown} setWheelCooldown={setWheelCooldown} apiFetch={apiFetch} onBack={() => setSubGame(null)} />;
  if (subGame === 'dice') return <DiceGame user={user} dbUser={dbUser} setDbUser={setDbUser} apiFetch={apiFetch} onBack={() => setSubGame(null)} />;
  if (subGame === 'coin') return <CoinGame user={user} dbUser={dbUser} setDbUser={setDbUser} apiFetch={apiFetch} onBack={() => setSubGame(null)} />;

  return (
    <motion.div initial={{opacity: 0, x: 20}} animate={{opacity: 1, x: 0}} exit={{opacity: 0, x: -20}} className="grid grid-cols-2 gap-4">
      <GameCard icon="🎡" name="چرخونه شانس" onClick={() => setSubGame('wheel')} />
      <GameCard icon="🎲" name="تاس" onClick={() => setSubGame('dice')} />
      <GameCard icon="🪙" name="شیر یا خط" onClick={() => setSubGame('coin')} />
    </motion.div>
  );
};

const WheelGame = ({ user, setDbUser, cooldown, setWheelCooldown, apiFetch, onBack }) => {
  const [spinning, setSpinning] = useState(false);
  const [rotation, setRotation] = useState(0);
  const prizes = [10, 20, 50, 100, 200, 0, 5, 10];
  const colors = ['#3b82f6', '#1d4ed8', '#3b82f6', '#1d4ed8', '#3b82f6', '#1d4ed8', '#3b82f6', '#1d4ed8'];

  const spin = async () => {
    if (spinning || cooldown > 0) return;
    const res = await apiFetch(`/api/wheel-spin/${user.id}`, { method: 'POST' });
    if (res?.status === 'success') {
      setSpinning(true);
      const targetRotation = 360 * 5 + (360 - (res.index * 45));
      setRotation(targetRotation);
      setTimeout(() => {
        setSpinning(false);
        setDbUser(prev => ({...prev, coins: res.coins}));
        setWheelCooldown(res.cooldown);
        alert(`🎁 برنده شدی: ${res.reward} سکه!`);
        setRotation(targetRotation % 360);
      }, 4000);
    }
  };

  return (
    <div className="text-center">
      <button onClick={onBack} className="mb-4 text-sm opacity-60 flex items-center gap-1 mx-auto">🔙 بازگشت</button>
      <div className="relative w-64 h-64 mx-auto mb-8">
         <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-2 z-10 text-3xl">👇</div>
         <motion.div
           animate={{ rotate: rotation }}
           transition={{ duration: 4, ease: "circOut" }}
           className="w-full h-full rounded-full border-4 border-white/20 relative overflow-hidden shadow-2xl bg-slate-800"
         >
           {prizes.map((p, i) => (
             <div key={i} className="absolute w-full h-full" style={{ transform: `rotate(${i * 45}deg)` }}>
                <div className="absolute top-0 left-1/2 -translate-x-1/2 h-1/2 w-16 flex items-start justify-center pt-4 font-bold" style={{ clipPath: 'polygon(50% 0%, 0% 100%, 100% 100%)', background: colors[i] }}>
                  <span style={{ transform: `rotate(0deg)` }}>{p}</span>
                </div>
             </div>
           ))}
         </motion.div>
      </div>
      <button
        disabled={spinning || cooldown > 0}
        onClick={spin}
        className="bg-blue-600 px-10 py-3 rounded-2xl font-bold shadow-lg disabled:opacity-50"
      >
        {spinning ? 'در حال چرخش...' : cooldown > 0 ? 'فردا برگرد' : 'بچرخون!'}
      </button>
    </div>
  );
};

const DiceGame = ({ user, dbUser, setDbUser, apiFetch, onBack }) => {
  const [bet, setBet] = useState(10);
  const [rolling, setRolling] = useState(false);
  const [res, setRes] = useState(null);

  const roll = async () => {
    if (rolling || dbUser.coins < bet) return;
    setRolling(true);
    const data = await apiFetch(`/api/game/dice/${user.id}?bet=${bet}`, {method: 'POST'});
    setTimeout(() => {
      setRolling(false);
      if (data) {
        setRes(data.dice);
        setDbUser(prev => ({...prev, coins: data.coins}));
      }
    }, 1000);
  };

  return (
    <div className="text-center">
      <button onClick={onBack} className="mb-4 text-sm opacity-60 flex items-center gap-1 mx-auto">🔙 بازگشت</button>
      <div className="text-6xl mb-8 h-16 flex items-center justify-center">
        {rolling ? <motion.div animate={{rotate: 360}} transition={{repeat: Infinity, duration: 0.3}}>🎲</motion.div> : (res || '🎲')}
      </div>
      <div className="flex justify-center gap-2 mb-4">
        {[10, 50, 100].map(v => <button key={v} onClick={() => setBet(v)} className={`px-4 py-1 rounded-lg ${bet === v ? 'bg-blue-600' : 'bg-white/10'}`}>{v}</button>)}
      </div>
      <button onClick={roll} className="bg-green-600 px-10 py-3 rounded-2xl font-bold">بنداز!</button>
    </div>
  );
};

const CoinGame = ({ user, dbUser, setDbUser, apiFetch, onBack }) => {
  const [bet, setBet] = useState(10);
  const [side, setSide] = useState('heads');
  const [flipping, setFlipping] = useState(false);

  const flip = async () => {
    if (flipping || dbUser.coins < bet) return;
    setFlipping(true);
    const data = await apiFetch(`/api/game/coin/${user.id}?bet=${bet}&side=${side}`, {method: 'POST'});
    setTimeout(() => {
      setFlipping(false);
      if (data) {
        alert(data.win ? '🎉 برنده شدی!' : '💀 باختی!');
        setDbUser(prev => ({...prev, coins: data.coins}));
      }
    }, 1500);
  };

  return (
    <div className="text-center">
      <button onClick={onBack} className="mb-4 text-sm opacity-60 flex items-center gap-1 mx-auto">🔙 بازگشت</button>
      <div className="text-6xl mb-8">
        <motion.div animate={flipping ? {rotateY: 720} : {}} transition={{duration: 1.5}}>🪙</motion.div>
      </div>
      <div className="flex justify-center gap-4 mb-6">
        <button onClick={() => setSide('heads')} className={`px-6 py-2 rounded-xl ${side === 'heads' ? 'bg-yellow-500' : 'bg-white/10'}`}>شیر</button>
        <button onClick={() => setSide('tails')} className={`px-6 py-2 rounded-xl ${side === 'tails' ? 'bg-yellow-500' : 'bg-white/10'}`}>خط</button>
      </div>
      <button onClick={flip} className="bg-blue-600 px-10 py-3 rounded-2xl font-bold">پرتاب</button>
    </div>
  );
}

const ShopTab = ({ items, buyItem, updateCoins }) => (
  <motion.div initial={{opacity: 0}} animate={{opacity: 1}} className="space-y-4">
    <h2 className="text-xl font-bold">🛒 فروشگاه</h2>
    {items.map(item => (
      <div key={item.id} className="glass p-4 bg-white/5 border border-white/10 rounded-2xl flex justify-between items-center">
        <div>
          <div className="font-bold">{item.name}</div>
          <div className="text-yellow-400 text-sm">{item.price} سکه</div>
        </div>
        <button onClick={async () => {
          const data = await buyItem(item.id);
          if (data?.status === 'success') { updateCoins(data.coins); alert('✅ خریدی!'); }
        }} className="bg-blue-600 px-4 py-2 rounded-xl text-sm font-bold">خرید</button>
      </div>
    ))}
  </motion.div>
);

const RankTab = ({ board }) => (
  <motion.div initial={{opacity: 0}} animate={{opacity: 1}} className="space-y-3">
    <h2 className="text-xl font-bold mb-4">🏆 رتبه‌بندی</h2>
    {board.map((u, i) => (
      <div key={i} className="glass p-4 bg-white/5 rounded-2xl flex justify-between">
        <div className="flex gap-3">
           <span className="opacity-50">#{i+1}</span>
           <span className="font-bold">{u.name}</span>
        </div>
        <span className="text-yellow-400 font-bold">{u.coins}</span>
      </div>
    ))}
  </motion.div>
);

const GroupsTab = ({ groups }) => (
  <motion.div initial={{opacity: 0}} animate={{opacity: 1}} className="space-y-4">
    <h2 className="text-xl font-bold">👥 گروه‌های من</h2>
    {groups.map(g => (
      <div key={g.id} className="glass p-4 bg-white/5 rounded-2xl">
        <div className="font-bold mb-2">{g.title}</div>
        <div className="flex gap-2 text-[10px]">
           {Object.entries(g.settings).map(([k, v]) => (
             <span key={k} className={`px-2 py-0.5 rounded ${v ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>{k.toUpperCase()}</span>
           ))}
        </div>
      </div>
    ))}
  </motion.div>
);

const MenuBtn = ({ icon, label, onClick, color }) => (
  <button onClick={onClick} className={`glass p-6 bg-gradient-to-br ${color} to-transparent border border-white/10 rounded-3xl flex flex-col items-center gap-2 active:scale-95 transition shadow-lg`}>
    <span className="text-3xl">{icon}</span>
    <span className="font-bold text-sm">{label}</span>
  </button>
);

const GameCard = ({ icon, name, onClick }) => (
  <button onClick={onClick} className="glass p-8 bg-white/5 border border-white/10 rounded-3xl flex flex-col items-center gap-3 active:scale-95 transition shadow-lg">
    <span className="text-4xl">{icon}</span>
    <span className="font-bold text-sm">{name}</span>
  </button>
);

const NavButton = ({ icon, label, active, onClick }) => (
  <button
    onClick={onClick}
    className={`flex flex-col items-center justify-center py-2 px-1 rounded-2xl flex-1 transition-all duration-200 ${active ? 'bg-blue-600/20 text-blue-400 shadow-[0_0_20px_rgba(37,99,235,0.2)]' : 'text-gray-500'}`}
  >
    <span className="text-2xl mb-1">{icon}</span>
    <span className="text-[10px] font-extrabold uppercase tracking-tighter">{label}</span>
  </button>
);

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
