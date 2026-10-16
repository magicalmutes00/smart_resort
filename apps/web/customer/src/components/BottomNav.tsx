import { Link, useLocation } from 'react-router-dom';
import { useCart } from '../lib/cart';

export function BottomNav() {
  const location = useLocation();
  const { totalCount } = useCart();
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t">
      <div className="max-w-2xl mx-auto flex justify-around py-3">
        <Link to="/" className={location.pathname === '/' ? 'text-brand-600' : 'text-gray-500'}>Home</Link>
        <Link to="/menu" className={location.pathname.startsWith('/menu') ? 'text-brand-600' : 'text-gray-500'}>Menu</Link>
        <Link to="/cart" className={`relative ${location.pathname === '/cart' ? 'text-brand-600' : 'text-gray-500'}`}>
          Cart
          {totalCount > 0 && (
            <span className="absolute -top-1 -right-3 bg-brand-500 text-white text-[10px] font-bold rounded-full min-w-[18px] h-[18px] px-1 flex items-center justify-center">
              {totalCount}
            </span>
          )}
        </Link>
      </div>
    </nav>
  );
}
