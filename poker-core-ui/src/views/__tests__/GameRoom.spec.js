import { describe, expect, it, vi, afterEach, afterAll, beforeAll, beforeEach } from 'vitest'
import { flushPromises } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import GameRoom from '../GameRoom.vue'
import { useGameStore, makeGame } from '@/stores/game'
import { http, HttpResponse } from 'msw'
import { server } from '@/tests/mocks/node'

const gameCode = '1234'
const mountLocal = async (props = {}, options = {}) => {
  const wrapper = mount(GameRoom, {
    props: {
      gameCode: gameCode,
        ...props
    },
    ...options
  })
  await wrapper.vm.$nextTick();
  return wrapper
}

describe('Game Room', () => {
  beforeAll(() => {
    setActivePinia(createPinia())

    server.listen()
  })

  beforeEach(async () => {})

  afterEach(() => {
    vi.restoreAllMocks()
    server.resetHandlers()
    useGameStore().$reset()
  })

  afterAll(() => {
    server.close()
  })

  it.each([3, 5])('creates a seat for each player', async (numberOfSeats) => {
    const syncGamehandler = http.get('/games/:gameCode', () => {
      return HttpResponse.json(makeGame({ numberOfSeats }))
    })
    server.use(syncGamehandler)

    const wrapper = await mountLocal()
    await flushPromises()

    const seats = wrapper.findAllComponents({name: 'Seat'})
    expect(seats.length).toBe(numberOfSeats)
    seats.forEach((seat) => {
        expect(seat.vm.status).toBe('empty')
    })
  })

  it('can handle an error when fetching the game', async () => {
    const syncGamehandler = http.get('/games/:gameCode', () => {
      return HttpResponse.json({ message: 'Game not found' }, { status: 404, statusText: 'Not Found' })
    })
    server.use(syncGamehandler)

    const wrapper = await mountLocal()
    const notifySpy = vi.spyOn(wrapper.vm.$notify, 'error')
    await flushPromises()

    expect(notifySpy).toHaveBeenCalledTimes(1)
    expect(notifySpy).toHaveBeenCalledWith('Failed to sync game: Game not found')
  })

  it('assigns the first available seat when joining', async () => {
    const wrapper = await mountLocal()
    await flushPromises()

    await useGameStore().joinGame(gameCode, { name: 'player1' })
    await wrapper.vm.$nextTick();
  
    const seats = wrapper.findAllComponents({ name: 'Seat' })
    expect(seats.length).toBe(3)
    expect(seats.at(0).vm.status).toBe('ready')
    expect(seats.at(1).vm.status).toBe('empty')
    expect(seats.at(2).vm.status).toBe('empty')
  })
  
  it('raises an error when joining with a null player', async () => {
    const wrapper = await mountLocal()
    await flushPromises()

    expect(() => useGameStore().joinGame(gameCode, null)).toThrowError('Player must be provided')
  })

  it('leaves the game', async () => {
    const syncGamehandler = http.get('/games/:gameCode', () => {
      return HttpResponse.json(makeGame({ seats: [{ name: 'player1' }, { name: 'player2' }, { name: 'player3' }] }))
    })
    server.use(syncGamehandler)

    const wrapper = await mountLocal()
    await flushPromises()

    await useGameStore().leaveGame(gameCode, { name: 'player2' })
    await wrapper.vm.$nextTick();

    const seats = wrapper.findAllComponents({ name: 'Seat' })
    expect(seats.length).toBe(3)
    expect(seats.at(0).vm.status).toBe('ready')
    expect(seats.at(1).vm.status).toBe('empty')
    expect(seats.at(2).vm.status).toBe('ready')
  })

  it('can handle players with the same name', async () => {
    const syncGamehandler = http.get('/games/:gameCode', () => {
      return HttpResponse.json(makeGame({ seats: [{ name: 'player', id: 1 }, { name: 'player', id: 2 }, { name: 'player', id: 3 }] }))
    })
    server.use(syncGamehandler)

    const wrapper = await mountLocal()
    await flushPromises()
    
    await useGameStore().leaveGame(gameCode, { name: 'player', id: 2 })
    await wrapper.vm.$nextTick();
    
    const seats = wrapper.findAllComponents({ name: 'Seat' })
    expect(seats.length).toBe(3)
    expect(seats.at(0).vm.status).toBe('ready')
    expect(seats.at(1).vm.status).toBe('empty')
    expect(seats.at(2).vm.status).toBe('ready')
  })
  
  it('raises an error when leaving with a null player', async () => {
    const wrapper = await mountLocal()
    await flushPromises()

    await useGameStore().joinGame(gameCode, { name: 'player1' })
    await wrapper.vm.$nextTick();

    expect(() => useGameStore().leaveGame(gameCode, null)).toThrowError('Player must be provided')
  })
  
  it('allows starting the game when the minimum number of players has been reached', async () => {
    const syncGamehandler = http.get('/games/:gameCode', () => {
      return HttpResponse.json(makeGame({ seats: [{ name: 'player1', id: 1 }, null, null] }))
    })
    server.use(syncGamehandler)

    const wrapper = await mountLocal()
    await flushPromises()

    const startGameButton = wrapper.find('[data-test="button_start-game"]')
    expect(startGameButton.exists()).toBe(true)
    expect(startGameButton.element.disabled).toBe(true)

    await useGameStore().joinGame(gameCode, { name: 'player2', id: 2 })
    await wrapper.vm.$nextTick();

    expect(startGameButton.element.disabled).toBe(false)
  })
 
  it('allows starting the game when the minimum number of players has been reached', async () => {
    const game = makeGame({ seats: [{ name: 'player1', id: 1 }, { name: 'player2', id: 2 }, null] });
    const syncGamehandler = http.get('/games/:gameCode', () => {
      return HttpResponse.json(game)
    })
    const startGameHandler = http.patch('/games/:gameCode', async () => {
      return HttpResponse.json(Object.assign({}, game, { status: 'started' }))
    })
    server.use(syncGamehandler)
    server.use(startGameHandler)

    const wrapper = await mountLocal()
    await flushPromises()

    const startGameButton = wrapper.find('[data-test="button_start-game"]')
    expect(startGameButton.element.disabled).toBe(false)

    await startGameButton.trigger('click')
    await flushPromises()
    expect(useGameStore().getGame(gameCode).status).toBe('started')
  })
 
  it('handles errors if the game cannot be started', async () => {
    useGameStore().$reset()
    const game = { numberOfSeats: 3, minimumPlayers: 2, seats: [{ name: 'player1', id: 1 }, { name: 'player2', id: 2 }, null], status: 'waiting' };
    const syncGamehandler = http.get('/games/:gameCode', () => {
      return HttpResponse.json(game)
    })
    const startGameHandler = http.patch('/games/:gameCode', async () => {
      return HttpResponse.json({ message: 'Can\'t do that bruv' }, { status: 400, statusText: 'Bad Request' })
    })
    server.use(syncGamehandler)
    server.use(startGameHandler)

    const wrapper = await mountLocal()
    const notifySpy = vi.spyOn(wrapper.vm.$notify, 'error')
    await flushPromises()
    await wrapper.vm.$nextTick();

    const startGameButton = wrapper.find('[data-test="button_start-game"]')
    expect(startGameButton.element.disabled).toBe(false)

    await startGameButton.trigger('click')
    await flushPromises()
    expect(useGameStore().getGame(gameCode).status).toBe('waiting')

    expect(notifySpy).toHaveBeenCalledTimes(1)
    expect(notifySpy).toHaveBeenCalledWith('Failed to start game: Can\'t do that bruv')
  })

  // Now test for what happens once the game is started (e.g. cards are dealt, etc.)
})