<template>
  <div>
    <v-form ref="form" v-model="valid">
      <v-row>
        <v-col cols="12">
          <h1>{{ $t('$vuetify.login.title_login') }}</h1>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <text-field v-model="username" :max-errors="5" :label="$t('$vuetify.login.field-label_username')"
            :required="true" data-test="field_username" type="text"></text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <text-field v-model="password" :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'" :max-errors="5"
            :label="$t('$vuetify.login.field-label_password')" :required="true" data-test="field_password"
            :type="showPassword ? 'text' : 'password'" @click:appendInner="showPassword = !showPassword"></text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <v-btn block :loading="loading" :disabled="loading" data-test="button_submit" type="submit" @click="submit">{{
            $t('$vuetify.login.button_login') }}</v-btn>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          {{ $t('$vuetify.login.message_signup-prompt') }} <RouterLink to="/signup">{{ $t('$vuetify.login.link_signup')
          }}
          </RouterLink>
        </v-col>
      </v-row>
    </v-form>
  </div>
</template>
  
<script lang="ts">
import { ref } from 'vue'
import TextField from '@/components/UI/inputs/TextField.vue'
import { VForm } from 'vuetify/components'
import { validateBetween, validatePassword } from '@/helpers/validation'
import { useUserstore } from '@/stores/user'

export default {
  components: {
    TextField,
  },
  props: {
    repoFactory: {
      type: Function,
      default() {
        console.log('instantiating real')
        return {
          login: (data) => {
            delete data.password
            return new Promise(resolve => setTimeout(() => {
              return resolve(data)
            }, 1000))
          },
        }
      },
    },
  },
  setup(props) {
    const valid = ref(false)
    const loading = ref(false)
    const showPassword = ref(false)
    const username = ref(null)
    const password = ref(null)
    const userStore = useUserstore()

    return {
      valid,
      loading,
      username,
      password,
      showPassword,
      userStore,
      repo: props.repoFactory(),
    }
  },
  methods: {
    validateBetween,
    validatePassword,
    async submit() {
      const { valid } = await (this.$refs.form as typeof VForm).validate()

      if (!valid) return

      this.loading = true

      this.repo.login({ username: this.username, password: this.password }).then((response) => {
        this.userStore.user = response
        // TODO: Translate
        this.$notify.success('Successfully signed in')
        this.$router.push(this.$route.query.redirect || '/')
      }).catch((e) => {
        // TODO: Translate
        let msg = 'Failed to sign in'
        msg += e ? `: ${e}` : ''
        this.$notify.error(msg)
      }).finally(() => {
        this.loading = false
      })
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
  