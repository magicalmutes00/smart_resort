import { Link, useLocation } from 'react-router-dom';

export function BottomNav() {
  const location = useLocation();
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t">
      <div className="max-w-2xl mx-auto flex justify-around py-3">
        <Link to="/" className={location.pathname === '/' ? 'text-brand-600' : 'text-gray-500'}>Home</Link>
        <Link to="/menu" className={location.pathname === '/menu' ? 'text-brand-600' : 'text-gray-500'}>Menu</Link>
        <Link to="/cart" className={location.pathname === '/cart' ? 'text-brand-600' : 'text-gray-500'}>Cart</Link>
      </div>
    </nav>
  );
}
