import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../lib/cart';
import { useTable } from '../lib/table';
import { api } from '../lib/api';

type OrderType = 'DINE_IN' | 'ROOM_SERVICE';

export function Checkout() {
  const { items, totalPrice, totalCount, clear } = useCart();
  const { tableNumber, tableCode } = useTable();
  const navigate = useNavigate();
  const [orderType, setOrderType] = useState<OrderType>('DINE_IN');
  const [tableStr, setTableStr] = useState(tableNumber || '');
  const [roomStr, setRoomStr] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handlePlaceOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    if (items.length === 0) { setError('Cart is empty'); return; }
    if (orderType === 'DINE_IN' && !tableStr.trim()) { setError('Please enter your table number'); return; }
    if (orderType === 'ROOM_SERVICE' && !roomStr.trim()) { setError('Please enter your room number'); return; }

    setLoading(true); setError('');
    try {
      const payload = {
        order_type: orderType,
        table_id: orderType === 'DINE_IN' ? (tableStr.trim() || tableNumber || undefined) : undefined,
        room_id: orderType === 'ROOM_SERVICE' ? (roomStr.trim() || undefined) : undefined,
        items: items.map(i => ({ menu_item_id: i.id, quantity: i.qty, notes: null })),
        notes: notes.trim() || undefined,
        special_instructions: undefined,
      };
      const res = await api.post('/orders/guest', payload);
      clear();
      navigate(`/order/${res.data.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to place order. Please try again.');
    } finally { setLoading(false); }
  };

  if (items.length === 0) {
    return (
      <div className="space-y-4">
        <h1 className="text-xl font-bold">Checkout</h1>
        <div className="bg-white rounded-xl p-6 text-center text-gray-500">
          <p>Your cart is empty.</p>
          <a href="/menu" className="text-brand-600 underline text-sm mt-2 inline-block">Browse menu</a>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">Checkout</h1>

      <form onSubmit={handlePlaceOrder} className="space-y-4">
        {/* Order type toggle */}
        <div className="bg-white rounded-xl p-4 shadow-sm">
          <div className="text-sm font-semibold mb-3">Order Type</div>
          <div className="flex gap-2">
            <button type="button" onClick={() => setOrderType('DINE_IN')}
              className={`flex-1 py-2 rounded-lg text-sm font-medium border ${orderType === 'DINE_IN' ? 'bg-brand-500 text-white border-brand-500' : 'bg-white text-gray-600 border-gray-200'}`}>
              🍽️ Dine In
            </button>
            <button type="button" onClick={() => setOrderType('ROOM_SERVICE')}
              className={`flex-1 py-2 rounded-lg text-sm font-medium border ${orderType === 'ROOM_SERVICE' ? 'bg-brand-500 text-white border-brand-500' : 'bg-white text-gray-600 border-gray-200'}`}>
              🛏️ Room Service
            </button>
          </div>
        </div>

        {/* Location input */}
        <div className="bg-white rounded-xl p-4 shadow-sm">
          {orderType === 'DINE_IN' ? (
            <div>
              <label className="block text-sm font-semibold mb-1">Table Number</label>
              <input type="text" value={tableStr} onChange={e => setTableStr(e.target.value)}
                placeholder={tableNumber ? `Table ${tableNumber}` : 'e.g. T-05'} required
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm" />
            </div>
          ) : (
            <div>
              <label className="block text-sm font-semibold mb-1">Room Number</label>
              <input type="text" value={roomStr} onChange={e => setRoomStr(e.target.value)}
                placeholder="e.g. 101" required
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm" />
            </div>
          )}
        </div>

        {/* Special instructions */}
        <div className="bg-white rounded-xl p-4 shadow-sm">
          <label className="block text-sm font-semibold mb-1">Special Instructions <span className="text-gray-400 font-normal">(optional)</span></label>
          <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={2}
            placeholder="Allergies, preferences, etc."
            className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm resize-none" />
        </div>

        {/* Order summary */}
        <div className="bg-white rounded-xl p-4 shadow-sm divide-y divide-gray-100">
          <div className="font-semibold text-sm pb-2">Order Summary</div>
          {items.map(i => (
            <div key={i.id} className="flex justify-between py-2 text-sm">
              <span>{i.qty} × {i.name}</span>
              <span className="font-medium">₹{(i.qty * i.price).toFixed(0)}</span>
            </div>
          ))}
          <div className="flex justify-between pt-2 font-bold">
            <span>Total</span>
            <span className="text-brand-600">₹{totalPrice.toFixed(0)}</span>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-3 text-xs text-red-700">{error}</div>
        )}

        <button type="submit" disabled={loading}
          className="w-full bg-brand-500 text-white py-3 rounded-xl font-bold shadow-md hover:bg-brand-600 transition disabled:opacity-60">
          {loading ? 'Placing order...' : `Place Order · ₹${totalPrice.toFixed(0)}`}
        </button>
      </form>
    </div>
  );
}
