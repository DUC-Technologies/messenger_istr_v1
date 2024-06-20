"use client";

import { useEffect, useState } from "react";
import { Button, Table, withTableSelection } from '@gravity-ui/uikit';
import { useQuery } from "react-query";
import { fetchCoins } from '@/app/utils/api/fetchCoins';
import { Coin, Coins } from '@/app/utils/types';

const columns = [
  { id: 'r', name: 'Ранг' },
  { id: 'n', name: 'Название' },
  { id: 's', name: 'Символ' },
  { id: 'pu', name: 'Цена' },
  { id: 'p24', name: 'Изменение (24ч)' },
];

const CoinTable = withTableSelection(Table);

const getRowId = (row: Coin) => row.r.toString();

export default function Home(): JSX.Element {
  const [page, setPage] = useState<number>(0);
  const { data, isLoading, isError } = useQuery(
    ['coins', page],
    () => fetchCoins(page),
    {
      keepPreviousData: true,
    }
  );
  const [selectedIds, setSelectedIds] = useState<number[]>([1]);

  if (isLoading) {
    return <h3> Идёт загрузка </h3>;
  }

  if (isError) {
    return <h3> Ошибка при получении данных </h3>;
  }

  if (!data || data.length === 0) {
    return <h3> Нет данных </h3>;
  }

  return (
    <>
      <CoinTable
        data={data}
        columns={columns}
        getRowId={getRowId}
        selectedIds={selectedIds}
        onSelectionChange={setSelectedIds}
      />
      <Button
        view="action"
        size="l"
        onClick={() => setPage(page - 1)}
        disabled={page === 0}
      >
        -
      </Button>
      <Button
        view="action"
        size="l"
        onClick={() => setPage(page + 1)}
      >
        +
      </Button>
    </>
  );
}
