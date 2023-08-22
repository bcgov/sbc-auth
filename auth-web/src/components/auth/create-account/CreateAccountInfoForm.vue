<template>
  <v-form
    ref="createAccountInfoForm"
    lazy-validation
  >
    <account-create-premium
      v-if="isPremium()"
      :stepForward="stepForward"
      :stepBack="stepBack"
    />
    <account-create-basic
      v-if="!isPremium()"
      :stepForward="stepForward"
      :stepBack="stepBack"
    />
  </v-form>
</template>

<script lang="ts">
import { Component, Mixins } from 'vue-property-decorator'
import { CreateRequestBody, Member, Organization } from '@/models/Organization'
import { mapActions, mapState } from 'pinia'
import { Account } from '@/util/constants'
import AccountCreateBasic from '@/components/auth/create-account/AccountCreateBasic.vue'
import AccountCreatePremium from '@/components/auth/create-account/AccountCreatePremium.vue'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
import { getModule } from 'vuex-module-decorators'
import { useOrgStore } from '@/store/org'
import { useUserStore } from '@/store/user'

@Component({
  components: {
    AccountCreatePremium,
    AccountCreateBasic
  },
  computed: {
    ...mapState(useOrgStore, ['currentOrganization']),
    ...mapState(useUserStore, ['userProfile', 'currentUser'])
  },
  methods: {
    ...mapActions(useOrgStore, ['createOrg', 'syncMembership', 'syncOrganization'])
  }
})
export default class CreateAccountInfoForm extends Mixins(Steppable) {
  private username = ''
  private password = ''
  private errorMessage: string = ''
  private saving = false
  private readonly createOrg!: (requestBody: CreateRequestBody) => Promise<Organization>
  private readonly syncMembership!: (orgId: number) => Promise<Member>
  private readonly syncOrganization!: (orgId: number) => Promise<Organization>
  private readonly currentOrganization!: Organization
  private readonly currentUser!: KCUserProfile

  $refs: {
      createAccountInfoForm: HTMLFormElement
    }

  private readonly teamNameRules = [
    v => !!v || 'An account name is required']

  private isFormValid (): boolean {
    return !!this.username && !!this.password
  }

  isPremium () {
    return this.currentOrganization.orgType === Account.PREMIUM
  }

  private redirectToNext (organization?: Organization) {
    this.$router.push({ path: `/account/${organization.id}/` })
  }
}
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
