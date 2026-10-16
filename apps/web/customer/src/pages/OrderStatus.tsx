import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { api } from '../lib/api';

interface Order {
  id: string;
  order_number: string;
  status: string;
  order_type: string;
  total_amount: number;
  created_at: string;
}

const STATUS_LABELS: Record<string, { label: string; emoji: string; color: string }> = {
  CREATED: { label: 'Order received', emoji: '⏳', color: 'text-amber-600' },
  CONFIRMED: { label: 'Order confirmed', emoji: '✅', color: 'text-blue-600' },
  ACCEPTED: { label: 'Kitchen accepted', emoji: '👨‍🍳', color: 'text-blue-700' },
  PREPARING: { label: 'Being prepared', emoji: '🔥', color: 'text-orange-600' },
  READY: { label: 'Ready', emoji: '🛎️', color: 'text-green-600' },
  OUT_FOR_DELIVERY: { label: 'Out for delivery', emoji: '🛵', color: 'text-purple-600' },
  DELIVERED: { label: 'Delivered', emoji: '🎉', color: 'text-green-700' },
  COMPLETED: { label: 'Completed', emoji: '✅', color: 'text-gray-600' },
  CANCELLED: { label: 'Cancelled', emoji: '❌', color: 'text-red-600' },
};

export function OrderStatus() {
  const { id } = useParams();
  const [order, setOrder] = useState<Order | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    const fetchOrder = async () => {
      try {
        const res = await api.get(`/orders/${id}`);
        if (active) setOrder(res.data);
      } catch (err: any) {
        if (active) setError(err.response?.data?.detail || 'Failed to load order');
      }
    };
    fetchOrder();
    const interval = setInterval(fetchOrder, 5000);
    return () => { active = false; clearInterval(interval); };
  }, [id]);

  if (error) {
    return (
      <div className="space-y-4">
        <h1 className="text-xl font-bold">Order #{id?.slice(0, 8)}</h1>
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">{error}</div>
      </div>
    );
  }

  if (!order) {
    return <div className="text-center text-gray-500 py-8">Loading order…</div>;
  }

  const statusInfo = STATUS_LABELS[order.status] || { label: order.status, emoji: '⏳', color: 'text-gray-600' };

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">Order {order.order_number}</h1>
      <div className="bg-white rounded-xl p-6 shadow-sm">
        <div className="text-center">
          <div className="text-4xl mb-2">{statusInfo.emoji}</div>
          <p className={`font-bold text-lg ${statusInfo.color}`}>{statusInfo.label}</p>
          <p className="text-sm text-gray-500 mt-1">
            {order.order_type === 'DINE_IN' && 'Dine-in order'}
            {order.order_type === 'ROOM_SERVICE' && 'Room service order'}
            {order.order_type === 'TAKEOUT' && 'Takeout order'}
            {order.order_type === 'LAKE' && 'Lake seat order'}
            {order.order_type === 'DELIVERY' && 'Delivery order'}
          </p>
        </div>
      </div>
      <div className="bg-white rounded-xl p-4 shadow-sm flex justify-between text-sm">
        <span className="text-gray-500">Total</span>
        <span className="font-bold text-brand-600">₹{order.total_amount.toFixed(0)}</span>
      </div>
      <a href="/menu" className="block text-center text-brand-600 text-sm underline">Back to menu</a>
    </div>
  );
}
