<template>
  <div>
    <h1>{{ $t('$vuetify.misc.startPokerGame') }}</h1>
    <v-form ref="form" v-model="valid" @submit.prevent="submit">
      <v-row>
        <v-col cols="12">
          <text-field
            v-model="maxPlayers"
            :rules="[validateBetween(2, 9)]"
            :max-errors="5"
            :label="$t('$vuetify.game.maxPlayers')"
            :required="true"
            data-test="field-max-players"
            type="number"
            @update:model-value="log"
          ></text-field>
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
          <!-- This is a test to allow for translating strings returned from functions before a locale is changed -->
          <!-- For example, validation rules must only return string-like types, so something like this could be returned and the results translated after the fact -->
          {{ reapplyPlaceholders('$vuetify.validation.maxNumber{limit:99}{another:something}') }}
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
import { makeid, reapplyPlaceholders } from '@/helpers/helpers'
import { ref } from 'vue'
import TextField from '@/components/UI/inputs/TextField.vue'
import { validateBetween } from '@/helpers/validation'
import { VForm } from 'vuetify/components'

export default {
  components: {
    TextField,
  },
  setup() {
    const valid = ref(false)
    const loading = ref(false)
    const maxPlayers = ref(9)
    const code = ref(makeid(6))

    return {
      valid,
      loading,
      maxPlayers,
      code,
    }
  },
  methods: {
    validateBetween,
    reapplyPlaceholders,
    log(e) {
      console.log('outer', e)
    },
    async submit() {
      const { valid } = await (this.$refs.form as typeof VForm).validate()

      if (!valid) return

      this.loading = true
      setTimeout(() => (this.loading = false), 3000)
    },
  },
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
