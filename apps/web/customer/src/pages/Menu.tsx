import { useQuery } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
import { api } from '../lib/api';

export function Menu() {
  const [params] = useSearchParams();
  const category = params.get('category');

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['menu', category],
    queryFn: () => api.get('/menu/items', { params: { category } }),
    retry: 1,
    refetchOnWindowFocus: false,
  });

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">Menu</h1>

      {isLoading && (
        <div className="text-center text-gray-500 py-8">Loading…</div>
      )}

      {isError && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-sm">
          <div className="font-semibold text-amber-800 mb-1">
            Can't reach the menu service
          </div>
          <div className="text-amber-700 mb-3">
            The backend server isn't responding. Make sure the FastAPI
            backend is running on port 8000.
          </div>
          <div className="text-xs text-amber-600 mb-3 font-mono">
            {(error as any)?.message || 'Connection refused'}
          </div>
          <button
            onClick={() => refetch()}
            className="bg-amber-600 text-white px-4 py-2 rounded-lg text-sm font-semibold"
          >
            Retry
          </button>
        </div>
      )}

      {!isLoading && !isError && data?.data?.data?.length === 0 && (
        <div className="bg-white rounded-xl p-6 text-center text-gray-500">
          <div className="text-2xl mb-2">🍽️</div>
          <p>No items in this category yet</p>
        </div>
      )}

      {data?.data?.data?.map((item: any) => (
        <div
          key={item.id}
          className="bg-white rounded-xl p-4 flex items-center justify-between shadow-sm"
        >
          <div>
            <div className="font-semibold">{item.name}</div>
            <div className="text-xs text-gray-500">{item.description}</div>
            <div className="text-sm font-semibold text-brand-600 mt-1">
              ₹{item.base_price}
            </div>
          </div>
          <button className="bg-brand-500 text-white px-4 py-2 rounded-lg text-sm font-semibold">
            Add
          </button>
        </div>
      ))}
    </div>
  );
}
