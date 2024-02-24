<template>
  <div>
    <v-form ref="form" v-model="valid">
      <v-row>
        <v-col cols="12">
          <h1>{{ $t('$vuetify.login.title_signup') }}</h1>
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
          <text-field v-model="password" :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
            :rules="[validatePassword]" :max-errors="5" :label="$t('$vuetify.login.field-label_password')"
            :required="true" data-test="field_password" :type="showPassword ? 'text' : 'password'"
            @click:appendInner="showPassword = !showPassword"></text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <!-- TODO: This field does not validate when the password field changes -->
          <text-field v-model="passwordConfirm" data-test="field_password-confirm"
            :append-inner-icon="showPasswordConfirm ? 'mdi-eye' : 'mdi-eye-off'"
            :rules="[validatePasswordsMatch(password)]" :max-errors="5"
            :label="$t('$vuetify.login.field-label_password-confirm')"
            @click:appendInner="showPasswordConfirm = !showPasswordConfirm"
            :type="showPasswordConfirm ? 'text' : 'password'" :required="true"></text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <v-btn block :loading="loading" :disabled="loading" data-test="button_submit" type="submit" @click="submit">{{
            loading ? 'loading' : $t('$vuetify.login.button_signup') }}</v-btn>
        </v-col>
        <!-- <v-col cols="6">
                    <v-btn block :loading="loading" :disabled="loading" data-test="button-submit" type="submit"
                        @click="submitFail">{{
                            loading ? 'loading' : 'FAIL' }}</v-btn>
                </v-col> -->
      </v-row>
      <v-row>
        <v-col cols="12">
          {{ $t('$vuetify.login.message_login-prompt') }} <RouterLink to="/login">{{
            $t('$vuetify.login.link_login')
          }}
          </RouterLink>
        </v-col>
      </v-row>
      <!-- <v-row>
          <v-col cols="12">
            <v-text-field v-model="code" :label="$t('$vuetify.game.identifier')" disabled required
              data-test="field-game-code"></v-text-field>
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="12">
            <v-btn block :loading="loading" :disabled="loading" data-test="button-create-game" type="submit">{{
              $t('$vuetify.misc.startPokerGame') }}</v-btn>
          </v-col>
        </v-row> -->
    </v-form>
  </div>
</template>
    
<script lang="ts">
import { ref } from 'vue'
import TextField from '@/components/UI/inputs/TextField.vue'
import { validateBetween, validatePassword, validatePasswordsMatch } from '@/helpers/validation'
import { VForm } from 'vuetify/components'
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
          signup: async () => {
            return fetch('https://httpbin.org/json', {
              method: 'GET',
            }).then((response) => response.json())

            debugger;
            const json = await response.json()

            if (!response.ok) {
              console.log('not ok')
              return Promise.reject(response)
            }


            console.log('signup')
            return Promise.resolve(response)
          },
          // signupFail: async () => {

          //     console.log('submit failure')
          //     const response = fetch('https://httpbin.org/hidden-basic-auth/:user/:passwd', {
          //         method: 'GET',
          //         mode: "no-cors", // no-cors, *cors, same-origin
          //     })

          //     if (!response.ok) {
          //         console.log('not ok')
          //         return Promise.reject('Failed to sign up')
          //     }


          //     console.log('signup')
          //     return Promise.resolve(response)
          // },
        }
      },
    },
  },
  setup(props) {
    const valid = ref(false)
    const loading = ref(false)
    const userStore = useUserstore()
    const username = ref(null)
    const password = ref(null)
    const passwordConfirm = ref(null)
    // const username = ref('a')
    // const password = ref('Ab123456!')
    // const passwordConfirm = ref('Ab123456!')
    const showPassword = ref(false)
    const showPasswordConfirm = ref(false)

    return {
      valid,
      loading,
      username,
      password,
      showPassword,
      passwordConfirm,
      showPasswordConfirm,
      userStore,
      repo: props.repoFactory(),
    }
  },
  methods: {
    validateBetween,
    validatePassword,
    validatePasswordsMatch,
    async submit() {
      const { valid } = await (this.$refs.form as typeof VForm).validate()

      if (!valid) return

      this.loading = true

      this.repo.signup({
        username: this.username,
        password: this.password,
      }).then((response) => {
        this.userStore.user = response
        // TODO: Translate
        this.$notify.success('Successfully registered')
        this.$router.push(this.$route.query.redirect || '/')
      }).catch((e) => {
        // TODO: Translate
        let msg = 'Failed to register'
        msg += e ? `: ${e}` : ''
        this.$notify.error(msg)
      }).finally(() => {
        this.loading = false
      })
    },
    // async submitFail() {
    //     this.repo.signupFail({
    //         username: this.username,
    //         password: this.password,
    //     }).then((response) => {
    //         console.log(response)
    //         // this.$router.push({ name: 'login' })
    //         this.$notify.success('Successfully signed up')
    //     }).catch((e) => {
    //         console.log(e)
    //         const msg = e || 'Failed to sign up'
    //         this.$notify.error(msg)
    //     }).finally(() => {
    //         this.loading = false
    //     })
    // }
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
    