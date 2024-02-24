<template>
  <div class="gameRoom">
    <Seat v-for="(player, index) in game?.seats" :key="index" :player="player">
    </Seat>
    <v-btn :disabled="occupiedSeats.length < game?.minimumPlayers" @click="startGame" data-test="button_start-game">{{
      $t('$vuetify.gameRoom.button_start-game') }}</v-btn>
  </div>
</template>
<style scoped></style>

<script setup lang="js">
import { ref, computed, watch, onBeforeUnmount } from 'vue'
import { storeToRefs } from 'pinia'
import Seat from '@/components/Seat.vue'
import { useGameStore } from '@/stores/game'
import { useCounterStore } from '@/stores/counter'
import { useNotify } from '@/plugins/notify'

const props = defineProps({
  gameCode: {
    type: String,
    required: true
  },
})

const $notify = useNotify()
const store = useGameStore()
store.syncGame(props.gameCode).catch((e) => {
  // TODO: Translate
  let msg = 'Failed to sync game'
  msg += e.message ? `: ${e.message}` : ''
  $notify.error(msg)
})
// const game = store.getGame(props.gameCode)

const game = computed(() => {
  const game = store.getGame(props.gameCode)

  if (!game) {
    return Object.assign({
      minimumPlayers: 2,
      status: 'waiting',
    }, {
      seats: [],
    })
  }

  return game
})

const occupiedSeats = computed(() => {
  return game.value?.seats.filter(seat => seat)
})

const startGame = () => {
  store.startGame(props.gameCode).catch((e) => {
    // TODO: Translate
    let msg = 'Failed to start game'
    msg += e.message ? `: ${e.message}` : ''
    $notify.error(msg)
  })
}
</script>
