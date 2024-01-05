<template>
  <v-form
    ref="form"
    data-test="form-govm-contact"
  >
    <p class="mb-9">
      Enter the IDIR email address of the ministry's employee.
      An email will be sent this user to verify and activate this account. This user will be the admin of this account.
    </p>
    <v-row>
      <v-col
        cols="12"
        class="py-0 mb-4"
      >
        <h4
          class="mb-1"
        >
          Account Admin Contact
        </h4>
      </v-col>
    </v-row>
    <!-- Email Address -->
    <v-row>
      <v-col
        cols="12"
        class="pt-0 pb-0"
      >
        <v-text-field
          v-model="emailAddress"
          filled
          label="Email Address"
          req
          persistent-hint
          data-test="email"
          readonly
        />
      </v-col>
    </v-row>
    <v-row>
      <v-col
        cols="12"
        class="pt-0 pb-0"
      >
        <v-text-field
          v-model="confirmedEmailAddress"
          filled
          label="Confirm Email Address"
          req
          persistent-hint
          data-test="confirm-email"
          readonly
        />
      </v-col>
    </v-row>
    <template v-if="emailAddress === ''">
      <span
        class="error-text mb-10"
      >
        Please contact BCROS support, no email in Keycloak for this account.
      </span>
    </template>
    <v-divider class="mt-7 mb-10" />
    <v-row>
      <v-col
        cols="12"
        class="form__btns py-0 d-inline-flex"
      >
        <v-btn
          large
          depressed
          color="default"
          data-test="btn-back"
          @click="goBack"
        >
          <v-icon
            left
            class="mr-2"
          >
            mdi-arrow-left
          </v-icon>
          <span>Back</span>
        </v-btn>
        <v-spacer />

        <v-btn
          large
          color="primary"
          class="save-continue-button mr-3"
          data-test="next-button"
          :disabled="emailAddress === ''"
          @click="createAccount"
        >
          <span>
            Create Account
          </span>
        </v-btn>
        <ConfirmCancelButton
          :showConfirmPopup="true"
          :isEmit="true"
          @click-confirm="cancel"
        />
      </v-col>
    </v-row>
  </v-form>
</template>

<script lang="ts">
import { defineComponent, onMounted, reactive, ref, toRefs } from '@vue/composition-api'
import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import NextPageMixin from '@/components/auth/mixins/NextPageMixin.vue'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
import { useUserStore } from '@/stores/user'

export default defineComponent({
  name: 'GovmContactInfoForm',
  components: {
    ConfirmCancelButton
  },
  mixins: [NextPageMixin, Steppable],
  emits: ['final-step-action'],
  setup (props, { root, emit }) {
    const userStore = useUserStore()
    const state = reactive({
      emailAddress: '',
      confirmedEmailAddress: '',
      userProfile: null
    })

    const formRef = ref(null)

    const getUserProfile = async (identifier) => {
      state.userProfile = await userStore.getUserProfile(identifier)
    }

    onMounted(async () => {
      getUserProfile('@me')
      state.emailAddress = state.userProfile?.email || ''
      state.confirmedEmailAddress = state.userProfile?.email || ''
    })

    const createAccount = () => {
      // email is readonly to show. no need to save
      emit('final-step-action')
    }

    const cancel = () => {
      root.$router.push('/')
    }

    const goBack = () => {
      // Vue 3 - get rid of MIXINS and use the composition-api instead.
      (props as any).stepBack()
    }

    return {
      ...toRefs(state),
      formRef,
      createAccount,
      cancel,
      goBack
    }
  }
})
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';
.legal-name {
  font-size: 1.25rem !important;
  font-weight: 700;
  letter-spacing: -0.02rem;
}
.error-text {
  color: $app-red;
}
</style>
