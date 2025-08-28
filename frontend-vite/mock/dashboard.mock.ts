import { MockMethod } from 'vite-plugin-mock';

export default [
  {
    url: '/api/dashboard/metrics',
    method: 'get',
    response: () => [
      { name: 'Jan', uv: 400, pv: 2400, amt: 2400 },
      { name: 'Feb', uv: 300, pv: 1398, amt: 2210 },
      { name: 'Mar', uv: 200, pv: 9800, amt: 2290 },
      { name: 'Apr', uv: 278, pv: 3908, amt: 2000 },
    ],
  },
  {
    url: '/api/dashboard/table',
    method: 'get',
    response: ({ query }) => {
      const allRows = [
        { id: 1, name: 'Produto A', value: 100 },
        { id: 2, name: 'Produto B', value: 200 },
        { id: 3, name: 'Produto C', value: 300 },
        { id: 4, name: 'Produto D', value: 400 },
      ];
      if (query && query.search) {
        return allRows.filter(row => row.name.toLowerCase().includes(query.search.toLowerCase()));
      }
      return allRows;
    },
  },
] as MockMethod[];
