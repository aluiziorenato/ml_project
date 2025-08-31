// API Mercado Livre e ARIMA/SARIMA
// Funções para consumir endpoints obrigatórios

export async function fetchMLUserItems(userId: string) {
  // /users/{user_id}/items/search
  const res = await fetch(`https://api.mercadolibre.com/users/${userId}/items/search`);
  return res.json();
}

export async function fetchMLItemDetails(itemId: string) {
  // /items/{item_id}
  const res = await fetch(`https://api.mercadolibre.com/items/${itemId}`);
  return res.json();
}

export async function fetchMLItemPriceHistory(itemId: string) {
  // /items/{item_id}/price_history
  const res = await fetch(`https://api.mercadolibre.com/items/${itemId}/price_history`);
  return res.json();
}

export async function fetchMLSearch(keyword: string) {
  // /sites/MLB/search?q={keyword}
  const res = await fetch(`https://api.mercadolibre.com/sites/MLB/search?q=${encodeURIComponent(keyword)}`);
  return res.json();
}

export async function fetchMLCategory(categoryId: string) {
  // /categories/{category_id}/
  const res = await fetch(`https://api.mercadolibre.com/categories/${categoryId}`);
  return res.json();
}

export async function fetchPriceForecastARIMA(payload: any) {
  // Serviço ARIMA/SARIMA
  const res = await fetch('http://localhost:8006/api/prediction/price-forecast', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return res.json();
}
