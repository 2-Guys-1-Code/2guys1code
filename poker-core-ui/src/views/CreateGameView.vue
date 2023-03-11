<template>
    <div>
        <h1>{{ $t('$vuetify.misc.startPokerGame') }}</h1>
        <v-form v-model="valid" fast-fail @submit.prevent>
            <v-row>
                <v-col cols="12">
                    <v-text-field v-model="maxPlayers" :rules="maxPalyerRules" :label="$t('$vuetify.game.maxPlayers')"
                        required></v-text-field>
                </v-col>
            </v-row>
            <v-row>
                <v-col cols="12">
                    <v-text-field v-model="code" :label="$t('$vuetify.game.identifier')" disabled required></v-text-field>
                </v-col>
            </v-row>
        </v-form>
    </div>
</template>

<script setup lang="ts">
import { makeid } from '@/helpers/helpers';
import { ref } from 'vue';
const maxPalyerRules = [(value: string) => {
    if (Number.isInteger(value)) return true
    console.log("Bad")
    return "no"
}]

const valid = ref(false)
const maxPlayers = ref(9)
const code = ref(makeid(6))
</script>

<style>
@media (min-width: 1024px) {
    .about {
        min-height: 100vh;
        display: flex;
        align-items: center;
    }
}
</style>
  