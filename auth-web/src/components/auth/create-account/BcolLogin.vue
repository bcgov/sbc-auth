<template>
  <v-form
    ref="form"
    lazy-validation
    data-test="form-bcol-login"
  >
    <fieldset>
      <legend class="mb-3">
        BC Online Prime Contact Details
        <v-tooltip
          bottom
          color="grey darken-4"
        >
          <template #activator="{ on }">
            <v-icon
              color="grey darken-4"
              tabindex="0"
              v-on="on"
            >
              mdi-help-circle-outline
            </v-icon>
          </template>
          <div class="bcol-tooltip__msg py-2">
            BC Online Prime Contacts are users who have authority to manage account settings for a BC Online Account.
          </div>
        </v-tooltip>
      </legend>
      <v-row>
        <v-col
          :cols="hideLinkBtn ? 6 : 4 "
          class="py-0 pr-0"
        >
          <v-text-field
            v-model.trim="username"
            dense
            filled
            label="User ID"
            :rules="usernameRules"
            req
            data-test="input-user-id"
          />
        </v-col>
        <v-col
          :cols="hideLinkBtn?6:4"
          class="py-0 pr-0"
        >
          <v-text-field
            v-model.trim="password"
            dense
            filled
            label="Password"
            type="password"
            req
            :rules="passwordRules"
            data-test="input-user-password"
          />
        </v-col>
        <v-col
          v-if="!hideLinkBtn"
          cols="4"
          class="py-0"
        >
          <v-btn
            large
            depressed
            color="primary"
            class="link-account-btn"
            data-test="dialog-save-button"
            :loading="isLoading"
            :disabled="!isFormValid || isLoading"
            @click="linkAccounts()"
          >
            Link Account
          </v-btn>
        </v-col>
      </v-row>
    </fieldset>
  </v-form>
</template>

<script lang="ts">
import { BcolAccountDetails, BcolProfile } from '@/models/bcol'
import { computed, defineComponent, onMounted, reactive, ref, toRefs, watch } from '@vue/composition-api'
import { useOrgStore } from '@/stores'

export default defineComponent({
  name: 'BcolLogin',
  props: {
    hideLinkBtn: {
      type: Boolean,
      default: false
    }
  },
  emits: ['emit-bcol-info', 'account-link-successful'],
  setup (props, { emit }) {
    const state = reactive({
      username: '',
      password: '',
      errorMessage: '',
      isLoading: false,
      isFormValid: computed(() => !!state.username && !!state.password)
    })

    const usernameRules = [
      v => !!v || 'Username is required'
    ]
    const passwordRules = [
      value => !!value || 'Password is required',
      value => (value?.trim().length <= 8) || 'Use only first 8 characters for password'
    ]

    const form = ref(null)

    const emitBcolInfo = () => {
      const bcolInfo: BcolProfile = {
        userId: state.username,
        password: state.password
      }
      emit('emit-bcol-info', bcolInfo)
    }

    watch(() => [state.username, state.password], () => {
      emitBcolInfo()
    })

    onMounted(() => {
      state.password = ''
    })

    const resetForm = () => {
      state.password = ''
      state.errorMessage = ''
      form.value?.resetValidation()
    }

    return {
      ...toRefs(state),
      usernameRules,
      passwordRules,
      form,
      resetForm
    }
  }
})
</script>

<style lang="scss" scoped>
  .bcol-tooltip__msg {
    max-width: 20rem;
    line-height: 1.5;
    font-size: 0.9375rem;
  }

  .v-icon {
    margin-top: -2px;
    font-size: 1.25rem !important;
  }

  .v-btn.link-account-btn {
    font-size: 0.875rem !important;
    font-weight: 700;
  }

  .v-tooltip__content:before {
    content: ' ';
    position: absolute;
    top: -20px;
    left: 50%;
    margin-left: -10px;
    width: 20px;
    height: 20px;
    border-width: 10px 10px 10px 10px;
    border-style: solid;
    border-color: transparent transparent var(--v-grey-darken4) transparent;
  }
</style>
