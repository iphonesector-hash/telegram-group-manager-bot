import React, { useEffect, useState } from 'react';
import ReactDOM from 'react-dom/client';

const App = () => {
  const [user, setUser] = useState(null);
  const [dbUser, setDbUser] = useState(null);
  const [activeTab, setActiveTab] = useState('home');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (window.Telegram && window.Telegram.WebApp) {
      const tg = window.Telegram.WebApp;
      tg.expand();
      tg.ready();
      const tgUser = tg.initDataUnsafe.user;
      setUser(tgUser);

      if (tgUser) {
        fetch(`http://130.185.122.76:8000/api/user/${tgUser.id}`)
          .then(res => res.json())
          .then(data => {
            setDbUser(data);
            setLoading(false);
          })
          .catch(() => setLoading(false));
      } else {
        setLoading(false);
      }
    }
  }, []);

  if (loading) return <div className="flex items-center justify-center min-h-screen">Loading SectorLand...</div>;

  return (
    <div className="min-h-screen p-4 pb-24 max-w-md mx-auto">
      {/* Profile Card */}
      <div className="glass p-6 premium-gradient mb-8 flex items-center gap-4">
         <div className="w-20 h-20 rounded-2xl overflow-hidden border-4 border-white border-opacity-20 shadow-xl">
           <img src={user?.photo_url || 'https://api.dicebear.com/7.x/bottts/svg?seed=' + user?.id} alt="avatar" />
         </div>
         <div>
            <h2 className="text-xl font-bold">{user?.first_name}</h2>
            <p className="text-white text-opacity-70 text-sm">سطح {dbUser?.level || 1} • {dbUser?.xp || 0} XP</p>
            <div className="bg-black bg-opacity-20 rounded-full h-1.5 w-32 mt-2">
               <div className="bg-white h-full rounded-full" style={{width: '30%'}}></div>
            </div>
         </div>
      </div>

      {activeTab === 'home' && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div className="glass p-5 flex flex-col items-center justify-center gap-2 card-hover" onClick={() => setActiveTab('wallet')}>
              <div className="w-12 h-12 bg-yellow-500 bg-opacity-20 rounded-full flex items-center justify-center text-2xl shadow-inner">💰</div>
              <span className="font-bold">کیف پول</span>
              <span className="text-xs text-yellow-500">{dbUser?.coins || 0} سکه</span>
            </div>
            <div className="glass p-5 flex flex-col items-center justify-center gap-2 card-hover" onClick={() => setActiveTab('games')}>
              <div className="w-12 h-12 bg-indigo-500 bg-opacity-20 rounded-full flex items-center justify-center text-2xl">🎮</div>
              <span className="font-bold">بازی‌ها</span>
              <span className="text-xs text-indigo-400">۳ بازی فعال</span>
            </div>
            <div className="glass p-5 flex flex-col items-center justify-center gap-2 card-hover" onClick={() => setActiveTab('shop')}>
              <div className="w-12 h-12 bg-pink-500 bg-opacity-20 rounded-full flex items-center justify-center text-2xl">🛒</div>
              <span className="font-bold">فروشگاه</span>
              <span className="text-xs text-pink-400">بسته است</span>
            </div>
            <div className="glass p-5 flex flex-col items-center justify-center gap-2 card-hover">
              <div className="w-12 h-12 bg-green-500 bg-opacity-20 rounded-full flex items-center justify-center text-2xl">🤖</div>
              <span className="font-bold">سکتور بات</span>
              <span className="text-xs text-green-500">آنلاین</span>
            </div>
          </div>

          <div className="glass p-5">
             <div className="flex justify-between items-center mb-4">
                <h3 className="font-bold">هدیه روزانه</h3>
                <span className="text-xs text-gray-400">هر ۲۴ ساعت</span>
             </div>
             <button className="w-full premium-gradient py-3 rounded-xl font-bold shadow-lg active:scale-95 transition-all">دریافت هدیه ۵۰ سکه</button>
          </div>
        </div>
      )}

      {activeTab === 'games' && (
        <div className="space-y-4">
           <button onClick={() => setActiveTab('home')} className="mb-2 text-indigo-400 font-bold flex items-center gap-2"><span>←</span> بازگشت</button>
           <h2 className="text-2xl font-bold mb-6">مرکز بازی‌ها</h2>
           <div className="glass p-4 flex justify-between items-center card-hover">
              <div className="flex items-center gap-3">
                 <span className="text-3xl">🐍</span>
                 <div>
                    <p className="font-bold">مار بازی (Snake)</p>
                    <p className="text-xs text-gray-400">رکورد شما: ۲۵۰</p>
                 </div>
              </div>
              <button className="bg-indigo-600 px-6 py-2 rounded-xl text-sm font-bold shadow-md">شروع</button>
           </div>
           <div className="glass p-4 flex justify-between items-center card-hover opacity-60">
              <div className="flex items-center gap-3">
                 <span className="text-3xl">♠️</span>
                 <div>
                    <p className="font-bold">حکم آنلاین</p>
                    <p className="text-xs text-gray-400">بزودی...</p>
                 </div>
              </div>
              <span className="text-xs bg-gray-700 px-3 py-1 rounded-full">غیرفعال</span>
           </div>
        </div>
      )}

      {activeTab === 'shop' && (
        <div className="space-y-4">
           <button onClick={() => setActiveTab('home')} className="mb-2 text-indigo-400 font-bold flex items-center gap-2"><span>←</span> بازگشت</button>
           <h2 className="text-2xl font-bold mb-6">فروشگاه سکتور</h2>
           <div className="glass p-8 flex flex-col items-center justify-center text-center gap-4">
              <div className="text-6xl grayscale">🔒</div>
              <h3 className="text-xl font-bold">فروش بسته است</h3>
              <p className="text-gray-400 text-sm">در حال حاضر بخش فروش غیرفعال می‌باشد. بزودی با سرویس‌های جدید باز خواهیم گشت.</p>
           </div>
        </div>
      )}

      {/* Footer Nav */}
      <div className="fixed bottom-6 left-4 right-4 glass p-3 flex justify-around items-center shadow-2xl">
        <button className={`text-2xl ${activeTab === 'home' ? 'text-indigo-400 scale-110' : 'text-gray-500'}`} onClick={() => setActiveTab('home')}>🏠</button>
        <button className="text-2xl text-gray-500">🏆</button>
        <button className="text-2xl text-gray-500">🎡</button>
        <button className="text-2xl text-gray-500" onClick={() => setActiveTab('admin')}>🛡</button>
      </div>
    </div>
  );
};

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
