import { useParams } from 'react-router-dom';

export function OrderStatus() {
  const { id } = useParams();
  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">Order #{id}</h1>
      <div className="bg-white rounded-xl p-6">
        <div className="text-center">
          <div className="text-2xl mb-2">⏳</div>
          <p className="font-semibold">Order placed</p>
          <p className="text-sm text-gray-500">Waiting for kitchen to accept</p>
        </div>
      </div>
    </div>
  );
}
