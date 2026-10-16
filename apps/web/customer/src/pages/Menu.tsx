import { useQuery } from '@tanstack/react-query';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { api } from '../lib/api';
import { useCart } from '../lib/cart';
import { useTable } from '../lib/table';

export function Menu() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const category = params.get('category');
  const { add, updateQty, items } = useCart();
  const { tableNumber } = useTable();

  const { data: categoriesData, isLoading: catsLoading } = useQuery({
    queryKey: ['menu-categories'],
    queryFn: () => api.get('/menu/categories'),
    retry: 1,
    refetchOnWindowFocus: false,
  });

  // Fetch items per category for grouping
  const categoryIds: string[] = categoriesData?.data?.data?.map((c: any) => c.id) ?? [];

  const categoryItemsQueries = useQuery({
    queryKey: ['menu-by-category', categoryIds],
    queryFn: async () => {
      const results = await Promise.all(
        categoryIds.map(catId =>
          api.get('/menu/items', { params: { category: catId } }).then(r => ({
            catId,
            items: r.data?.data ?? [],
          }))
        )
      );
      return results;
    },
    enabled: categoryIds.length > 0,
    retry: 1,
    refetchOnWindowFocus: false,
  });

  const categories: Array<{ id: string; name: string }> = categoriesData?.data?.data ?? [];
  const qtyOf = (id: string) => items.find(i => i.id === id)?.qty ?? 0;

  const setCategory = (id: string | null) => {
    const next = new URLSearchParams(params);
    if (id) next.set('category', id);
    else next.delete('category');
    navigate(`/menu?${next.toString()}`);
  };

  const isLoading = catsLoading || categoryItemsQueries.isLoading;
  const isError = catsLoading === false && categoryItemsQueries.isError;
  const error = categoryItemsQueries.error;

  const allItemsByCategory = categoryItemsQueries.data ?? [];

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">Menu</h1>
      {tableNumber && (
        <div className="bg-brand-50 border border-brand-200 rounded-xl px-4 py-2 flex items-center gap-2 text-sm text-brand-800">
          <span>🍽️</span>
          <span className="font-medium">Table {tableNumber}</span>
        </div>
      )}

      {/* Category filter chips */}
      <div className="flex gap-2 overflow-x-auto -mx-4 px-4 pb-1">
        <button
          onClick={() => setCategory(null)}
          className={`shrink-0 px-3 py-1.5 rounded-full text-xs font-semibold border transition ${
            !category
              ? 'bg-brand-500 text-white border-brand-500'
              : 'bg-white text-gray-600 border-gray-200 hover:border-brand-300'
          }`}
        >
          All
        </button>
        {categories.map(c => (
          <button
            key={c.id}
            onClick={() => setCategory(c.id)}
            className={`shrink-0 px-3 py-1.5 rounded-full text-xs font-semibold border transition ${
              category === c.id
                ? 'bg-brand-500 text-white border-brand-500'
                : 'bg-white text-gray-600 border-gray-200 hover:border-brand-300'
            }`}
          >
            {c.name}
          </button>
        ))}
      </div>

      {isLoading && (
        <div className="text-center text-gray-500 py-8">Loading…</div>
      )}

      {isError && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-sm">
          <div className="font-semibold text-amber-800 mb-1">Can't reach the menu service</div>
          <div className="text-amber-700 mb-3">The backend server isn't responding.</div>
          <button
            onClick={() => categoryItemsQueries.refetch()}
            className="bg-amber-600 text-white px-4 py-2 rounded-lg text-sm font-semibold"
          >
            Retry
          </button>
        </div>
      )}

      {!isLoading && !isError && allItemsByCategory.length === 0 && (
        <div className="bg-white rounded-xl p-6 text-center text-gray-500">
          <div className="text-2xl mb-2">🍽️</div>
          <p>No items available yet</p>
        </div>
      )}

      {/* Category sections */}
      {allItemsByCategory.map(({ catId, items: catItems }) => {
        if (catItems.length === 0) return null;
        const catName = categories.find(c => c.id === catId)?.name ?? catId;
        return (
          <section key={catId}>
            <h2 className="font-semibold text-sm text-gray-500 uppercase tracking-wide mb-2">
              {catName}
            </h2>
            <div className="space-y-2">
              {(catItems as any[]).map((item: any) => {
                const qty = qtyOf(item.id);
                return (
                  <div key={item.id} className="bg-white rounded-xl p-4 flex items-center justify-between shadow-sm">
                    <div className="flex-1 pr-3">
                      <div className="font-semibold">{item.name}</div>
                      {item.description && (
                        <div className="text-xs text-gray-500">{item.description}</div>
                      )}
                      <div className="text-sm font-semibold text-brand-600 mt-1">
                        ₹{item.base_price}
                      </div>
                    </div>
                    {qty === 0 ? (
                      <button
                        onClick={() => add({ id: item.id, name: item.name, price: item.base_price })}
                        className="bg-brand-500 text-white px-4 py-2 rounded-lg text-sm font-semibold"
                      >
                        Add
                      </button>
                    ) : (
                      <div className="flex items-center gap-2 bg-brand-50 rounded-lg px-2 py-1">
                        <button
                          onClick={() => updateQty(item.id, qty - 1)}
                          className="w-8 h-8 rounded-md bg-white text-brand-700 font-bold shadow-sm"
                          aria-label="Decrease"
                        >
                          −
                        </button>
                        <span className="w-6 text-center font-semibold text-brand-700">
                          {qty}
                        </span>
                        <button
                          onClick={() => updateQty(item.id, qty + 1)}
                          className="w-8 h-8 rounded-md bg-brand-500 text-white font-bold shadow-sm"
                          aria-label="Increase"
                        >
                          +
                        </button>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </section>
        );
      })}
    </div>
  );
}
