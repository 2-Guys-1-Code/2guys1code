<template>
  <div>
    <h1>{{ $t('$vuetify.misc.startPokerGame') }}</h1>
    <v-form ref="form" v-model="valid" @submit.prevent="submit">
      <v-row>
        <v-col cols="12">
          <v-text-field
            v-model="maxPlayers"
            :rules="[required, validateBetween(2, 9)]"
            :label="$t('$vuetify.game.maxPlayers')"
            required
            data-test="field-max-players"
            type="number"
          ></v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <v-text-field
            v-model="code"
            :label="$t('$vuetify.game.identifier')"
            disabled
            required
            data-test="field-game-code"
          ></v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <v-btn
            block
            :loading="loading"
            :disabled="loading"
            data-test="button-create-game"
            type="submit"
            >{{ $t('$vuetify.misc.startPokerGame') }}</v-btn
          >
        </v-col>
      </v-row>
    </v-form>
  </div>
</template>

<script lang="ts">
import { makeid } from '@/helpers/helpers'
import { ref } from 'vue'
import { VForm } from 'vuetify/components'

export default {
  setup() {
    const valid = ref(false)
    const loading = ref(false)
    const maxPlayers = ref(9)
    const code = ref(makeid(6))

    return {
      valid,
      loading,
      maxPlayers,
      code
    }
  },
  methods: {
    required(value: string) {
      if (!value) return this.$t('$vuetify.validation.required')
      return true
    },
    validateBetween(min: number, max: number) {
      return (value: string) => {
        const intVal = parseInt(value)
        console.log(intVal)
        if (intVal > max) return this.$t('$vuetify.validation.maxNumber', { limit: max })
        if (intVal < min) return this.$t('$vuetify.validation.minNumber', { limit: min })
        return true
      }
    },
    async submit() {
      const { valid } = await (this.$refs.form as typeof VForm).validate()

      if (!valid) return

      this.loading = true
      setTimeout(() => (this.loading = false), 3000)
    }
  }
}
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
