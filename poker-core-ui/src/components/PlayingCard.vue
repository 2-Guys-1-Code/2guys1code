<script setup lang="ts">
import { computed, ref } from 'vue'
const suitSymbolMapping: object = {
  H: '♥',
  D: '♦',
  C: '♣',
  S: '♠'
}
const suitColorMapping: object = {
  H: 'red',
  D: 'red',
  C: 'black',
  S: 'black'
}
const props = defineProps({
  suit: { type: String, default: null },
  rank: { type: Number, default: null }
})
const rankDisplay = computed(() => {
  switch (localRank.value) {
    case 1:
      return 'A'
    case 11:
      return 'J'
    case 12:
      return 'Q'
    case 13:
      return 'K'
    default:
      return localRank
  }
})
const suitSymbol = computed(() => {
  return suitSymbolMapping[localSuit.value as keyof object]
})
const suitColor = computed(() => {
  return suitColorMapping[localSuit.value as keyof object]
})

const localSuit = ref(props.suit)
const localRank = ref(props.rank)
const clickIt = () => {
  localSuit.value = Object.keys(suitSymbolMapping)[Math.floor(Math.random() * 4)]
  localRank.value = Math.floor(Math.random() * 13 + 1)
}
</script>

<template>
  <v-sheet
    border
    rounded="lg"
    class="playing-card"
    color="grey-lighten-3"
    height="350"
    width="250"
    @click="clickIt"
  >
    <div class="card-value card-value_top-left" :class="`card-symbol_${suitColor}`">
      <div class="card-value-rank">{{ rankDisplay }}</div>
      <div class="card-value-suit" :class="`card-symbol_${localSuit}`"></div>
    </div>
    <div class="card-value card-value_bottom-right" :class="`card-symbol_${suitColor}`">
      <div class="card-value-rank">{{ rankDisplay }}</div>
      <div class="card-value-suit" :class="`card-symbol_${localSuit}`"></div>
    </div>
    <span
      class="card-symbol card-symbol_middle"
      :class="`card-symbol_${suitColor} card-symbol_${localSuit}`"
    >
    </span>
  </v-sheet>
</template>

<style scoped>
.playing-card {
  position: relative;
  user-select: none;
}

.card-value {
  font-size: 3em;
  line-height: normal;
  position: absolute;
}

.card-value_top-left {
  top: 0;
  left: 0;
}

.card-value_bottom-right {
  transform: rotate(180deg);
  bottom: 0;
  right: 0;
}

.card-value-suit {
  position: absolute;
  top: 1em;
  left: 0;
}

.card-symbol_red {
  color: red;
}

.card-symbol_black {
  color: black;
}

.card-symbol_H:before {
  /* content: url(../assets/hearts.svg); */
  content: '♥';
}

.card-symbol_D:before {
  content: '♦';
}

.card-symbol_C:before {
  content: '♣';
}

.card-symbol_S:before {
  content: '♠';
}

.card-symbol_middle {
  font-size: 5em;
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
}
</style>
