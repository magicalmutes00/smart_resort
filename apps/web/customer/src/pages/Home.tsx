import { Link } from 'react-router-dom';
import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

const TABLES = [
  { code: 'TABLE-T-001', label: 'T-001' },
  { code: 'TABLE-T-002', label: 'T-002' },
  { code: 'TABLE-T-003', label: 'T-003' },
  { code: 'TABLE-T-004', label: 'T-004' },
  { code: 'TABLE-T-005', label: 'T-005' },
  { code: 'TABLE-T-006', label: 'T-006' },
  { code: 'TABLE-T-007', label: 'T-007' },
];

export function Home() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const code = params.get('code');
  useEffect(() => {
    if (code) navigate(`/qr?code=${encodeURIComponent(code)}`);
  }, [code, navigate]);

  return (
    <div className="space-y-6">
      <header className="text-center pt-6">
        <h1 className="text-2xl font-bold text-brand-700">Welcome to Lake View Resort</h1>
        <p className="text-sm text-gray-500 mt-1">Scan your table QR or browse categories</p>
      </header>

      <section className="grid grid-cols-2 gap-3">
        <Link to="/menu" className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition">
          <div className="text-2xl mb-2">🍽️</div>
          <div className="font-semibold">Restaurant</div>
          <div className="text-xs text-gray-500">Main kitchen menu</div>
        </Link>
        <Link to="/menu?category=tea" className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition">
          <div className="text-2xl mb-2">🫖</div>
          <div className="font-semibold">Tea Stall</div>
          <div className="text-xs text-gray-500">Tea, coffee, snacks</div>
        </Link>
        <Link to="/menu?category=beverages" className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition">
          <div className="text-2xl mb-2">🥤</div>
          <div className="font-semibold">Drinks</div>
          <div className="text-xs text-gray-500">Juices & sodas</div>
        </Link>
        <Link to="/menu?category=desserts" className="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition">
          <div className="text-2xl mb-2">🍰</div>
          <div className="font-semibold">Desserts</div>
          <div className="text-xs text-gray-500">Sweet treats</div>
        </Link>
      </section>

      <section>
        <h2 className="font-semibold mb-3">Your Tables</h2>
        <div className="grid grid-cols-4 gap-2">
          {TABLES.map(t => (
            <a key={t.code} href={`/?code=${t.code}`} className="bg-white rounded-xl p-3 text-center shadow-sm hover:shadow-md transition border border-brand-100">
              <div className="text-lg">🍽️</div>
              <div className="text-xs font-medium text-brand-700">{t.label}</div>
            </a>
          ))}
        </div>
      </section>

      <section className="bg-white rounded-xl p-4">
        <h2 className="font-semibold mb-3">How it works</h2>
        <ol className="space-y-2 text-sm text-gray-600">
          <li>1. Scan your table QR</li>
          <li>2. Browse the menu</li>
          <li>3. Add items to your cart</li>
          <li>4. Checkout and pay</li>
          <li>5. Track your order in real-time</li>
        </ol>
      </section>
    </div>
  );
}
