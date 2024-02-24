import { http, HttpResponse } from 'msw'

export const handlers = [
  http.get('https://api.example.com/user', () => {
    return HttpResponse.json({
      firstName: 'John',
      lastName: 'Maverick',
    })
  }),
  http.get(`/games/:gameCode`, () => {
    return HttpResponse.json({ 
      numberOfSeats: 3, 
      minimumPlayers: 2, 
      seats: [null, null, null] 
    })
  })
]