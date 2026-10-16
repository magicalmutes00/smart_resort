import { Routes, Route, Navigate } from 'react-router-dom';
import { Home } from './pages/Home';
import { Menu } from './pages/Menu';
import { Cart } from './pages/Cart';
import { Checkout } from './pages/Checkout';
import { OrderStatus } from './pages/OrderStatus';
import { QrPage } from './pages/QrPage';
import { BottomNav } from './components/BottomNav';

function App() {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <main className="flex-1 max-w-2xl mx-auto w-full px-4 py-4 pb-24">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/menu" element={<Menu />} />
          <Route path="/cart" element={<Cart />} />
          <Route path="/checkout" element={<Checkout />} />
          <Route path="/login" element={<Navigate to="/checkout" replace />} />
          <Route path="/order/:id" element={<OrderStatus />} />
          <Route path="/qr" element={<QrPage />} />
        </Routes>
      </main>
      <BottomNav />
    </div>
  );
}

export default App;
