import { useCart } from '../lib/cart';
import { useNavigate } from 'react-router-dom';

export function Cart() {
  const { items, remove, updateQty, totalCount, totalPrice } = useCart();
  const navigate = useNavigate();

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">Your Cart</h1>

      {items.length === 0 ? (
        <div className="bg-white rounded-xl p-6 text-center text-gray-500">
          <p>Your cart is empty</p>
          <a href="/menu" className="text-brand-600 underline text-sm mt-2 inline-block">Browse menu</a>
        </div>
      ) : (
        <>
          <div className="bg-white rounded-xl shadow-sm divide-y divide-gray-100">
            {items.map(i => (
              <div key={i.id} className="flex items-center justify-between p-4">
                <div>
                  <div className="font-semibold">{i.name}</div>
                  <div className="text-xs text-gray-500">₹{i.price} each</div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1 bg-brand-50 rounded-lg px-1.5 py-0.5">
                    <button
                      onClick={() => updateQty(i.id, i.qty - 1)}
                      className="w-7 h-7 rounded bg-white text-brand-700 font-bold shadow-sm text-sm"
                    >−</button>
                    <span className="w-5 text-center font-semibold text-brand-700 text-sm">{i.qty}</span>
                    <button
                      onClick={() => updateQty(i.id, i.qty + 1)}
                      className="w-7 h-7 rounded bg-brand-500 text-white font-bold shadow-sm text-sm"
                    >+</button>
                  </div>
                  <div className="font-semibold text-brand-600 w-16 text-right">₹{(i.qty * i.price).toFixed(0)}</div>
                  <button onClick={() => remove(i.id)} className="text-red-500 text-xs font-medium">Remove</button>
                </div>
              </div>
            ))}
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm flex items-center justify-between">
            <div>
              <div className="text-sm text-gray-500">Subtotal</div>
              <div className="font-bold text-lg">₹{totalPrice.toFixed(0)}</div>
            </div>
            <div className="text-sm text-gray-500">{totalCount} item{totalCount !== 1 ? 's' : ''}</div>
          </div>
          <button
            onClick={() => navigate('/checkout')}
            className="w-full bg-brand-500 text-white py-3 rounded-xl font-bold shadow-md hover:bg-brand-600 transition"
          >
            Proceed to Checkout
          </button>
        </>
      )}
    </div>
  );
}
