import { useEffect, useState } from 'react'
import { Activity, ArrowDownRight, ArrowUpRight, Bell, ChevronDown, CircleHelp, Command, Fuel, Gauge, MapPin, MoreHorizontal, Plus, Search, Settings2, Truck, Wrench } from 'lucide-react'

const API = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const rows = [
  { id: 'VH-2048', name: 'Volvo FH16', type: 'Тягач · 2023', driver: 'Алексей Морозов', route: 'Екатеринбург → Пермь', status: 'В пути', tone: 'green', fuel: '78%', mileage: '128 402 км' },
  { id: 'VH-2031', name: 'КамАЗ 54901', type: 'Тягач · 2022', driver: 'Иван Петров', route: 'Тюмень → Екатеринбург', status: 'В пути', tone: 'green', fuel: '62%', mileage: '96 810 км' },
  { id: 'VH-1987', name: 'Scania R500', type: 'Тягач · 2021', driver: 'Дмитрий Волков', route: 'На базе · Екатеринбург', status: 'На обслуживании', tone: 'amber', fuel: '34%', mileage: '214 090 км' },
  { id: 'VH-2102', name: 'MAN TGX', type: 'Тягач · 2024', driver: 'Не назначен', route: 'На базе · Екатеринбург', status: 'Свободен', tone: 'gray', fuel: '91%', mileage: '42 600 км' },
]

export default function App() {
  const [api, setApi] = useState('checking')
  useEffect(() => { fetch(`${API}/api/v1/health`).then(r => r.ok ? setApi('online') : setApi('offline')).catch(() => setApi('offline')) }, [])
  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark"><Command size={19} strokeWidth={2.4} /></div><span>fleet<span className="brand-light">core</span></span></div>
      <div className="workspace"><div className="workspace-avatar">NF</div><div><strong>North Fleet</strong><small>Основной парк</small></div><ChevronDown size={15} /></div>
      <div className="nav-label">РАБОЧЕЕ ПРОСТРАНСТВО</div>
      <nav><a className="active"><Gauge size={17}/> Обзор</a><a><Truck size={17}/> Транспорт <span className="nav-count">24</span></a><a><MapPin size={17}/> Маршруты</a><a><Activity size={17}/> Мониторинг</a><a><Wrench size={17}/> Обслуживание <span className="nav-dot"/></a></nav>
      <div className="nav-label nav-label-lower">УПРАВЛЕНИЕ</div>
      <nav><a><Fuel size={17}/> Расход топлива</a><a><Settings2 size={17}/> Настройки</a></nav>
      <div className="sidebar-bottom"><div className="help-card"><div className="help-icon"><CircleHelp size={17}/></div><strong>Нужна помощь?</strong><p>Загляните в центр поддержки FleetCore.</p><button>Открыть поддержку <ArrowUpRight size={13}/></button></div><div className="profile"><div className="profile-avatar">АМ</div><div><strong>Андрей Михайлов</strong><small>Администратор</small></div><MoreHorizontal size={17}/></div></div>
    </aside>
    <main className="main"><header className="topbar"><div className="crumb">Рабочее пространство <span>/</span> <strong>Обзор</strong></div><div className="top-actions"><div className="search"><Search size={15}/><span>Поиск...</span><kbd>⌘ K</kbd></div><button className="icon-button notification"><Bell size={17}/><i/></button><div className="top-avatar">АМ</div></div></header>
      <div className="content"><div className="page-heading"><div><div className="eyebrow"><span className={`api-dot ${api}`}/>{api === 'online' ? 'ВСЕ СИСТЕМЫ РАБОТАЮТ' : api === 'checking' ? 'ПОДКЛЮЧЕНИЕ К API' : 'API НЕДОСТУПНО'}</div><h1>Обзор автопарка</h1><p>Доброе утро, Андрей. Вот что происходит с вашим парком сегодня.</p></div><button className="primary-button"><Plus size={16}/> Добавить транспорт</button></div>
        <section className="stats"><article className="stat-card"><div className="stat-top"><span>Всего транспорта</span><span className="stat-icon teal"><Truck size={17}/></span></div><div className="stat-value">24 <small>ед.</small></div><div className="stat-foot"><span className="trend"><ArrowUpRight size={13}/> 8.2%</span><span>к прошлому месяцу</span></div><div className="sparkline"><svg viewBox="0 0 180 34" preserveAspectRatio="none"><path d="M0 28 C20 26 22 15 42 20 S64 25 81 16 S106 21 121 10 S147 20 160 8 S172 10 180 3"/></svg></div></article>
          <article className="stat-card"><div className="stat-top"><span>На линии</span><span className="stat-icon green"><Activity size={17}/></span></div><div className="stat-value">18 <small>ед.</small></div><div className="stat-foot"><span className="neutral">75%</span><span>от всего парка</span></div><div className="bar-track"><div className="bar-fill"/></div></article>
          <article className="stat-card"><div className="stat-top"><span>Требуют внимания</span><span className="stat-icon amber"><Wrench size={17}/></span></div><div className="stat-value">3 <small>ед.</small></div><div className="stat-foot"><span className="warning-text">2 плановых</span><span>· 1 просрочено</span></div><div className="attention-line"><span/><span/><span/></div></article>
          <article className="stat-card"><div className="stat-top"><span>Пробег за месяц</span><span className="stat-icon blue"><MapPin size={17}/></span></div><div className="stat-value">48 290 <small>км</small></div><div className="stat-foot"><span className="trend"><ArrowUpRight size={13}/> 12.4%</span><span>к прошлому месяцу</span></div><div className="sparkline blue-line"><svg viewBox="0 0 180 34" preserveAspectRatio="none"><path d="M0 27 C18 22 25 29 39 18 S60 21 75 13 S99 18 114 9 S132 16 148 6 S167 9 180 1"/></svg></div></article></section>
        <section className="operations"><div className="section-head"><div><h2>Транспорт</h2><p>Состояние и активность вашего автопарка</p></div><div className="section-tools"><button className="filter-button"><span className="filter-dot"/> Все статусы <ChevronDown size={14}/></button><button className="text-button">Весь транспорт <ArrowUpRight size={14}/></button></div></div>
          <div className="table-wrap"><table><thead><tr><th>ТРАНСПОРТ</th><th>ВОДИТЕЛЬ</th><th>ТЕКУЩИЙ МАРШРУТ</th><th>СТАТУС</th><th>ТОПЛИВО</th><th></th></tr></thead><tbody>{rows.map(row=><tr key={row.id}><td><div className="vehicle-cell"><div className="vehicle-icon"><Truck size={17}/></div><div><strong>{row.name}</strong><small>{row.id} <span>·</span> {row.type}</small></div></div></td><td className="driver-cell">{row.driver}</td><td className="route-cell"><MapPin size={13}/>{row.route}</td><td><span className={`status ${row.tone}`}><i/>{row.status}</span></td><td><div className="fuel-cell"><span>{row.fuel}</span><div className="fuel-track"><i style={{width: row.fuel}}/></div></div></td><td><button className="row-menu"><MoreHorizontal size={17}/></button></td></tr>)}</tbody></table></div><div className="table-footer"><span>Показано <strong>4</strong> из <strong>24</strong> транспортных средств</span><button>Перейти к списку <ArrowUpRight size={13}/></button></div>
        </section>
        <footer><span>© 2025 FleetCore</span><span className="footer-status"><i/> Синхронизировано только что</span><span>Версия 0.1.0</span></footer>
      </div>
    </main>
  </div>
}
