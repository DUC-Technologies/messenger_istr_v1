import axios from 'axios';
import { Coins } from '../types';

export async function fetchCoins(skip: number): Promise<Coins> {
  const {data} = await axios.get(`https://api.coin-stats.com/v4/coins?skip=${skip * 10}&limit=10`);
  return data.coins;
}