import { Link } from 'react-router-dom';

export function Home() {
  return (
    <div className="space-y-6">
      <header className="text-center pt-6">
        <h1 className="text-2xl font-bold text-brand-700">Welcome to Lake View Resort</h1>
        <p className="text-sm text-gray-500 mt-1">Order from your table, room, or lake seat</p>
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

      <section className="bg-white rounded-xl p-4">
        <h2 className="font-semibold mb-3">How it works</h2>
        <ol className="space-y-2 text-sm text-gray-600">
          <li>1. Browse the menu</li>
          <li>2. Add items to your cart</li>
          <li>3. Checkout and pay</li>
          <li>4. Track your order in real-time</li>
        </ol>
      </section>
    </div>
  );
}
