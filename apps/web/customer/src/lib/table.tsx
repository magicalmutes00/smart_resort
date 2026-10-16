import { createContext, useContext, useState, ReactNode, useEffect } from 'react';

interface TableContextType {
  tableNumber: string | null;
  tableCode: string | null;
  setTable: (number: string, code: string) => void;
  clearTable: () => void;
}

const TableContext = createContext<TableContextType | null>(null);

export function TableProvider({ children }: { children: ReactNode }) {
  const [tableNumber, setTableNumber] = useState<string | null>(() => sessionStorage.getItem('table_number'));
  const [tableCode, setTableCode] = useState<string | null>(() => sessionStorage.getItem('table_code'));

  useEffect(() => {
    if (tableNumber) sessionStorage.setItem('table_number', tableNumber);
    else sessionStorage.removeItem('table_number');
    if (tableCode) sessionStorage.setItem('table_code', tableCode);
    else sessionStorage.removeItem('table_code');
  }, [tableNumber, tableCode]);

  const setTable = (number: string, code: string) => {
    setTableNumber(number);
    setTableCode(code);
  };
  const clearTable = () => {
    setTableNumber(null);
    setTableCode(null);
  };

  return (
    <TableContext.Provider value={{ tableNumber, tableCode, setTable, clearTable }}>
      {children}
    </TableContext.Provider>
  );
}

export function useTable() {
  const ctx = useContext(TableContext);
  if (!ctx) throw new Error('useTable must be inside TableProvider');
  return ctx;
}
