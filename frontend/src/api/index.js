export const getTweets = async (page = 1, size = 20) => {
  const response = await fetch(`/api/tweets?page=${page}&size=${size}`)
  if (!response.ok) throw new Error('Failed to fetch tweets')
  return response.json()
}

export const startSync = async (username) => {
  const response = await fetch('/api/sync', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username })
  })
  if (!response.ok) throw new Error('Failed to trigger sync')
  return response.json()
}