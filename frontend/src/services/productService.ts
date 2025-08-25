export async function getFilteredProducts(filters: any) {
  const query = new URLSearchParams(filters).toString();
  const res = await fetch(`/api/produtos?${query}`);
  const data = await res.json();
  return data;
}
