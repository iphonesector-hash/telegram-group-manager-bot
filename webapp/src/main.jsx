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
      const rawInitData = tg.initData;
      setInitData(rawInitData);
      const tgUser = tg.initDataUnsafe.user;
      setUser(tgUser);

      if (tgUser) {
        fetch(`${API}/api/user/${tgUser.id}`, {
          headers: { 'init-data': rawInitData }
        })
          .then(r => r.json())
          .then(data => {
            if (data.id) {
              setDbUser(data);
            } else {
              console.error("User data error:", data);
            }
            setLoading(false);
          })
          .catch(err => {
            console.error("Fetch user error:", err);
            setLoading(false);
          });
      } else {
        setLoading(false);
      }
    } else {
      setLoading(false);
    }
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
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error(`API Call Failed [${endpoint}]:`, error);
      alert("⚠️ خطا در ارتباط با سرور. لطفاً دوباره تلاش کنید.");
      return null;
    }
  };

  async function claim() {
    const data = await apiFetch(`/api/daily-claim/${user.id}`, { method: "POST" });
    if (data) {
      if (data.status === "success") {
        setDbUser({ ...dbUser, coins: data.coins });
        alert(`✅ ${data.reward} سکه گرفتی!`);
      } else {
        alert(`❌ ${data.message}`);
      }
    }
  }

  async function loadShop() {
    setActiveTab("shop");
    const data = await apiFetch("/api/shop");
    if (data) setShop(data.items || []);
  }

  async function buyItem(itemId) {
    const data = await apiFetch(`/api/shop/buy/${user.id}?item_id=${itemId}`, { method: "POST" });
    if (data) {
      if (data.status === "success") {
        setDbUser({ ...dbUser, coins: data.coins });
        alert(`✅ ${data.message}`);
      } else {
        alert(`❌ ${data.message || "خطا در خرید"}`);
      }
    }
  }

  async function loadRank() {
    setActiveTab("rank");
    const data = await apiFetch("/api/leaderboard");
    if (data) setBoard(data);
  }

  async function loadGames() {
    setActiveTab("games");
    const data = await apiFetch("/api/games");
    if (data) setGames(data);
  }

  async function loadGroups() {
    setActiveTab("groups");
    const data = await apiFetch(`/api/groups/${user.id}`);
    if (data) setGroups(data);
  }

  if (loading) return (
    <div className="flex items-center justify-center min-h-screen text-white bg-[#0f172a]">
      <div className="animate-pulse text-xl">SectorLand Loading...</div>
    </div>
  );

  return (
    <div className="min-h-screen p-4 pb-32 max-w-md mx-auto text-white bg-[#0f172a] font-sans rtl" dir="rtl">
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

      {/* Main Content Areas */}
      <div className="tab-content transition-all duration-300">
        {activeTab === "home" && (
          <div className="grid grid-cols-1 gap-4 animate-in fade-in zoom-in-95">
            <div className="bg-white/5 p-6 rounded-3xl border border-white/10 text-center mb-4">
              <div className="text-4xl mb-2">👋</div>
              <h3 className="text-xl font-bold mb-1">سلام {user?.first_name}!</h3>
              <p className="text-gray-400 text-sm">به دنیای سکتور خوش اومدی.</p>
            </div>

            <button className="glass p-5 w-full bg-gradient-to-r from-yellow-500/20 to-orange-500/20 border border-yellow-500/30 rounded-2xl flex items-center justify-between" onClick={claim}>
              <span className="flex items-center gap-3 text-lg">🎁 <span>هدیه روزانه</span></span>
              <span className="text-yellow-400 font-bold">+۵۰ سکه</span>
            </button>

            <div className="grid grid-cols-2 gap-4 mt-2">
              <button className="glass p-6 bg-white/5 border border-white/10 rounded-3xl flex flex-col items-center gap-3" onClick={loadShop}>
                <span className="text-3xl">🛒</span>
                <span className="font-bold">فروشگاه</span>
              </button>
              <button className="glass p-6 bg-white/5 border border-white/10 rounded-3xl flex flex-col items-center gap-3" onClick={loadGames}>
                <span className="text-3xl">🎮</span>
                <span className="font-bold">بازی‌ها</span>
              </button>
              <button className="glass p-6 bg-white/5 border border-white/10 rounded-3xl flex flex-col items-center gap-3" onClick={loadRank}>
                <span className="text-3xl">🏆</span>
                <span className="font-bold">برترین‌ها</span>
              </button>
              <button className="glass p-6 bg-white/5 border border-white/10 rounded-3xl flex flex-col items-center gap-3" onClick={loadGroups}>
                <span className="text-3xl">👥</span>
                <span className="font-bold">گروه‌ها</span>
              </button>
            </div>
          </div>
        )}

        {activeTab === "shop" && (
          <div className="animate-in fade-in slide-in-from-left-4">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">🛒 فروشگاه</h2>
            <div className="grid grid-cols-1 gap-4">
              {shop.length > 0 ? shop.map(x => (
                <div className="glass p-4 bg-white/5 border border-white/10 rounded-2xl flex items-center justify-between" key={x.id}>
                  <div>
                    <div className="font-bold">{x.name}</div>
                    <div className="text-yellow-500 text-sm">{x.price} سکه</div>
                  </div>
                  <button className="bg-blue-600 px-5 py-2 rounded-xl text-sm font-bold active:scale-95 transition" onClick={() => buyItem(x.id)}>خرید</button>
                </div>
              )) : <div className="text-center py-10 opacity-50">درحال بارگذاری محصولات...</div>}
            </div>
          </div>
        )}

        {activeTab === "rank" && (
          <div className="animate-in fade-in slide-in-from-left-4">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">🏆 برترین‌ها</h2>
            <div className="space-y-3">
              {board.length > 0 ? board.map((x, idx) => (
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
              )) : <div className="text-center py-10 opacity-50">درحال بارگذاری رتبه‌بندی...</div>}
            </div>
          </div>
        )}

        {activeTab === "games" && (
          <div className="animate-in fade-in slide-in-from-left-4">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">🎮 بازی‌ها</h2>
            <div className="grid grid-cols-2 gap-4">
              {games.length > 0 ? games.map(g => (
                <div className={`glass p-6 rounded-3xl border border-white/10 flex flex-col items-center justify-center gap-3 ${g.active ? 'bg-white/10' : 'bg-black/40 opacity-60'}`} key={g.id}>
                  <div className="text-4xl">{g.id === 'snake' ? '🐍' : g.id === 'hokm' ? '🃏' : '❓'}</div>
                  <div className="font-bold">{g.name}</div>
                  {!g.active && <div className="text-xs bg-red-500/20 text-red-400 px-2 py-0.5 rounded-full">قفل شده</div>}
                  {g.active && <button className="mt-2 bg-green-600 text-xs px-4 py-1 rounded-lg">شروع</button>}
                </div>
              )) : <div className="text-center py-10 opacity-50 col-span-2">درحال بارگذاری بازی‌ها...</div>}
            </div>
          </div>
        )}

        {activeTab === "groups" && (
          <div className="animate-in fade-in slide-in-from-left-4">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">👥 گروه‌های من</h2>
            <div className="space-y-4">
              {groups.length === 0 ? (
                <div className="text-center py-10 text-gray-500">درحال بارگذاری یا هیچ گروهی یافت نشد.</div>
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

      {/* Persistent Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 p-4 bg-[#0f172a]/80 backdrop-blur-lg border-t border-white/5 z-50">
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

const NavButton = ({ icon, label, active, onClick }) => (
  <button
    onClick={onClick}
    className={`flex flex-col items-center justify-center py-2 px-1 rounded-2xl flex-1 transition-all duration-200 ${active ? 'bg-blue-600/20 text-blue-400 shadow-[0_0_15px_rgba(37,99,235,0.2)]' : 'text-gray-500 hover:text-gray-300'}`}
  >
    <span className="text-2xl mb-1">{icon}</span>
    <span className="text-[10px] font-bold">{label}</span>
  </button>
);

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
