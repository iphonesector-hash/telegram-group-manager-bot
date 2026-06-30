import React, { useEffect, useState } from 'react';
import ReactDOM from 'react-dom/client';
import { motion, AnimatePresence } from 'framer-motion';

const API = import.meta.env.VITE_API_URL || "http://130.185.122.76:8000";

const App = () => {
  const [user, setUser] = useState(null);
  const [dbUser, setDbUser] = useState(null);
  const [activeTab, setActiveTab] = useState('home');
  const [loading, setLoading] = useState(true);
  const [cooldown, setCooldown] = useState(0);

  useEffect(() => {
    const tg = window.Telegram?.WebApp;
    if (tg) {
      tg.expand();
      const tgUser = tg.initDataUnsafe.user;
      setUser(tgUser);
      if (tgUser) {
        fetch(`${API}/api/user/${tgUser.id}`, { headers: { 'init-data': tg.initData } })
          .then(r => r.json()).then(d => {
            if (d.id) { setDbUser(d); setCooldown(d.cooldowns?.wheel || 0); }
            setLoading(false);
          }).catch(() => setLoading(false));
      } else setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (cooldown > 0) {
      const timer = setInterval(() => setCooldown(c => Math.max(0, c - 1)), 1000);
      return () => clearInterval(timer);
    }
  }, [cooldown]);

  const apiFetch = async (url, opt = {}) => {
    const res = await fetch(`${API}${url}`, { ...opt, headers: { ...opt.headers, 'init-data': window.Telegram.WebApp.initData } });
    return res.json();
  };

  if (loading) return <div className="p-10 text-center">Loading...</div>;

  return (
    <div className="min-h-screen bg-[#0d0d0f] text-white p-4 pb-24 rtl" dir="rtl">
      <div className="p-6 bg-gradient-to-br from-blue-600/20 to-purple-600/20 rounded-3xl mb-6">
        <h2 className="text-xl font-bold">{user?.first_name}</h2>
        <p className="opacity-70">سطح {dbUser?.level} • {dbUser?.coins} سکه</p>
      </div>

      <AnimatePresence mode="wait">
        {activeTab === 'home' && <Home onNav={setActiveTab} />}
        {activeTab === 'games' && <Games user={user} setDbUser={setDbUser} cooldown={cooldown} setCooldown={setCooldown} fetch={apiFetch} />}
      </AnimatePresence>

      <div className="fixed bottom-0 left-0 right-0 p-4 bg-black/50 backdrop-blur-md flex justify-around border-t border-white/5">
        <button onClick={() => setActiveTab('home')}>🏠 خانه</button>
        <button onClick={() => setActiveTab('games')}>🎮 بازی</button>
      </div>
    </div>
  );
};

const Home = ({ onNav }) => (
  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
    <div className="grid grid-cols-2 gap-4">
      <button onClick={() => onNav('games')} className="glass p-10 flex flex-col items-center"><span>🎡</span><b>گردونه</b></button>
      <button className="glass p-10 opacity-50 cursor-not-allowed"><span>🛒</span><b>بزودی</b></button>
    </div>
  </motion.div>
);

const Games = ({ user, setDbUser, cooldown, setCooldown, fetch }) => {
  const [spinning, setSpinning] = useState(false);
  const [rot, setRot] = useState(0);
  const prizes = [10, 20, 50, 100, 200, 0, 5, 10];
  const colors = ['#3b82f6', '#1d4ed8', '#3b82f6', '#1d4ed8', '#3b82f6', '#1d4ed8', '#3b82f6', '#1d4ed8'];

  const spin = async () => {
    if (spinning || cooldown > 0) return;
    const res = await fetch(`/api/wheel-spin/${user.id}`, { method: 'POST' });
    if (res.status === 'success') {
      setSpinning(true);
      const target = 360 * 5 + (360 - (res.index * 45));
      setRot(target);
      setTimeout(() => {
        setSpinning(false);
        setDbUser(p => ({ ...p, coins: res.coins }));
        setCooldown(res.cooldown);
        setRot(target % 360);
        alert(`🎁 ${res.reward} سکه!`);
      }, 4000);
    }
  };

  return (
    <div className="text-center">
      <div className="relative w-64 h-64 mx-auto mb-10">
        <div className="absolute top-[-10px] left-1/2 -translate-x-1/2 z-10">👇</div>
        <motion.div
          animate={{ rotate: rot }}
          transition={{ duration: 4, ease: "circOut" }}
          className="w-full h-full rounded-full border-4 border-white/10 relative overflow-hidden bg-slate-800"
          style={{ transform: 'translateZ(0)' }} // FIXED: Force GPU layer to prevent black rendering in WebViews
        >
          {prizes.map((p, i) => (
            <div key={i} className="absolute w-full h-full" style={{ transform: `rotate(${i * 45}deg)` }}>
              <div className="absolute top-0 left-1/2 -translate-x-1/2 h-1/2 w-32 origin-bottom"
                   style={{
                     background: colors[i],
                     clipPath: 'polygon(50% 100%, 0% 0%, 100% 0%)',
                     transform: 'translateZ(0)' // FIXED: Hardware acceleration fix for black artifacts
                   }}>
                <span className="absolute top-4 left-1/2 -translate-x-1/2 font-bold">{p}</span>
              </div>
            </div>
          ))}
        </motion.div>
      </div>
      <button onClick={spin} disabled={spinning || cooldown > 0} className="bg-blue-600 px-10 py-3 rounded-full font-bold disabled:opacity-50">
        {spinning ? 'صبر کنید...' : cooldown > 0 ? 'فردا بیا' : 'بچرخون!'}
      </button>
    </div>
  );
};

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
