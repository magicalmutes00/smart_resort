import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useTable } from '../lib/table';

export function QrPage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const code = params.get('code');
  const { setTable } = useTable();
  const [error, setError] = useState('');

  useEffect(() => {
    if (!code) { navigate('/'); return; }
    // Parse code like "TABLE-T-001" -> table number "T-001"
    const match = code.match(/TABLE-(T-\d+)/i);
    if (match) {
      const tableNum = match[1];
      setTable(tableNum, code);
      setTimeout(() => navigate('/menu'), 400);
    } else {
      setError('Invalid QR code. Please scan a table QR.');
    }
  }, [code, navigate, setTable]);

  if (error) {
    return (
      <div className="space-y-4 max-w-md mx-auto py-6 text-center">
        <div className="text-4xl">⚠️</div>
        <p className="text-red-600 font-semibold">{error}</p>
        <button onClick={() => navigate('/')} className="text-brand-600 underline text-sm">Go home</button>
      </div>
    );
  }

  return (
    <div className="space-y-3 text-center py-10">
      <div className="text-4xl">📱</div>
      <p className="font-semibold">Welcome!</p>
      <p className="text-sm text-gray-500">Loading your table menu…</p>
    </div>
  );
}
