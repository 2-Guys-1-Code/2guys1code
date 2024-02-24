import { defineStore } from 'pinia'

export function makeGame(options) {
  let numberOfSeats
  let seats = []
  if (options.seats) {
    numberOfSeats = options.seats.length
    seats = options.seats
  } else {
    numberOfSeats = options.numberOfSeats ?? 3
    for (let i = 0; i < numberOfSeats; i++) {
      seats.push(null)
    }
  }
  
  return Object.assign({
    numberOfSeats,
    minimumPlayers: 2,
    status: 'waiting',
    seats: seats,
  }, options)
}

export const useGameStore = defineStore('game', {
  state: () => ({
    games: {},
  }),
  actions: {
    async syncGame(gameCode) {
      const res = await fetch(`/games/${gameCode}`, {
        method: 'GET',
      })

      if (!res.ok) {
        return Promise.reject(await res.json())
      }

      const data = await res.json()
      this.games[gameCode] = data
    },
    createGame(gameCode, options) {

      const seats = []
      for (let i = 0; i < options.numberOfSeats; i++) {
        seats.push(null)
      }
      this.games[gameCode] = makeGame(options)
    },
    joinGame(gameCode, player) {
      if (player === null || player === undefined) {
        throw new Error('Player must be provided')
      }

      const game = this.getGame(gameCode)
      const emptySeatIndex = game.seats.findIndex((seat) => seat === null)
      if (emptySeatIndex === -1) {
        throw new Error('No empty seat')
      }
      game.seats[emptySeatIndex] = player
    },
    leaveGame(gameCode, player) {
      if (player === null || player === undefined) {
        throw new Error('Player must be provided')
      }

      const game = this.getGame(gameCode)
      const seatIndex = game.seats.findIndex((seat) => {
        if  (player?.id !== null && player?.id !== undefined)  {
          return seat.id === player.id
        }
      
        return seat.name === player.name
      })
      if (seatIndex === -1) {
        throw new Error('Player not found')
      }
      game.seats[seatIndex] = null
    },
    async startGame(gameCode) {
      const res = await fetch(`/games/${gameCode}`, {
        method: 'PATCH',
        body: JSON.stringify({ status: 'started' }),
      })

      if (!res.ok) {
        return Promise.reject(await res.json())
      }

      const data = await res.json()
      this.games[gameCode] = data

      // const game = this.getGame(gameCode)
      // game.status = 'started'
    },
  },
  getters: {
    getGame: (state) => (gameCode) => {
      return state.games[gameCode] ?? null

      // let game = state.games[gameCode]
      // console.log(game)
      // if (game) {
      //   return game
      // }

      // // const response = await fetch(`/games/${gameCode}`, {
      // //   method: 'GET',
      // // })
      // // game = response.json()
      // game = Promise.resolve({
      //   minimumPlayers: 2,
      //   status: 'waiting',
      //   seats: [null, null, null]
      // })
      // state.games[gameCode] = game
      // return game
    },
  },
})
