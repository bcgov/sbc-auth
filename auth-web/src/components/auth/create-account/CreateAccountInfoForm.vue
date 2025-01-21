<template>
  <v-form
    ref="createAccountInfoForm"
    lazy-validation
  >
    <AccountCreate
      :stepForward="stepForward"
      :stepBack="stepBack"
    />
  </v-form>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, ref, toRefs } from '@vue/composition-api'
import { Account } from '@/util/constants'
import AccountCreate from '@/components/auth/create-account/AccountCreate.vue'
import { Organization } from '@/models/Organization'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'

export default defineComponent({
  name: 'CreateAccountInfoForm',
  components: {
    AccountCreate
  },
  mixins: [Steppable],
  setup (props, { root }) {
    const createAccountInfoForm = ref<HTMLFormElement>()
    const state = reactive({
      username: '',
      password: '',
      errorMessage: '',
      saving: false,
      currentOrganization: computed(() => useOrgStore().currentOrganization),
      currentUser: computed(() => useUserStore().currentUser),
      userProfile: computed(() => useUserStore().userProfile)
    })

    const { createOrg, syncMembership, syncOrganization } = useOrgStore()

    function isFormValid (): boolean {
      return !!state.username && !!state.password
    }

    function redirectToNext (organization?: Organization) {
      root.$router.push({ path: `/account/${organization.id}/` })
    }

    const teamNameRules = [
      v => !!v || 'An account name is required'
    ]

    return {
      ...toRefs(state),
      isFormValid,
      createOrg,
      syncMembership,
      syncOrganization,
      createAccountInfoForm,
      redirectToNext,
      teamNameRules
    }
  }
})
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';

  // Tighten up some of the spacing between rows
  [class^="col"] {
    padding-top: 0;
    padding-bottom: 0;
  }

  .form__btns {
    display: flex;
    justify-content: flex-end;
  }

  .bcol-acc-label {
    font-size: 1.35rem;
    font-weight: 600;
  }

  .grant-access {
    font-size: 1rem !important;
  }
</style>
