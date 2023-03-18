<script setup lang="ts">
import PlayingCard from '../components/PlayingCard.vue'
</script>

<template>
  <main>
    <PlayingCard :rank="12" suit="H" />
    <PlayingCard :rank="1" suit="S" />
    <PlayingCard :rank="9" suit="C" />
    <PlayingCard :rank="3" suit="D" />
  </main>
</template>

<style scoped>
main div.playing-card {
  position: absolute;
}

main div:nth-child(1) {
  transform: rotate(-30deg) translate(-30%, 0);
}

main div:nth-child(2) {
  transform: rotate(-10deg) translate(-10%, 5%);
}

main div:nth-child(3) {
  transform: rotate(10deg) translate(10%, 5%);
}

main div:nth-child(4) {
  transform: rotate(30deg) translate(30%, 0);
}
</style>
