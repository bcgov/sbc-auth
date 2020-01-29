<template>
  <v-container class="p-0">
    <header class="view-header">
      <h2 class="view-header__title">Account Info</h2>
    </header>
    <v-form ref="editAccountForm">
      <v-alert type="error" class="mb-6"
        v-show="orgCreateMessage !== 'success'">
        {{orgCreateMessage}}
      </v-alert>
      <v-text-field filled clearable required label="Account Name" :disabled="!canChangeAccountName()"
        :rules="accountNameRules"
        v-model="orgName"
        v-on:keydown="enableBtn();">
      </v-text-field>
      <div class="form__btns">
        <v-btn large class="save-btn"
          v-bind:class="{ 'disabled' : btnLabel == 'Saved' }"
          :color="btnLabel == 'Saved'? 'success' : 'primary'"
          :disabled="!isFormValid() || !canChangeAccountName()"
          :loading="btnLabel == 'Saving'"
          @click="updateOrgName()">
          <v-expand-x-transition>
            <v-icon v-show="btnLabel == 'Saved'">mdi-check</v-icon>
          </v-expand-x-transition>
          <span class="save-btn__label">{{btnLabel}}</span>
        </v-btn>
      </div>
    </v-form>
  </v-container>
</template>

<script lang="ts">

import { Component, Vue } from 'vue-property-decorator'
import { CreateRequestBody, Member, MembershipType, Organization } from '@/models/Organization'
import { mapActions, mapGetters, mapState } from 'vuex'
import OrgModule from '@/store/modules/org'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
  },
  methods: {
    ...mapActions('org', ['syncOrganizations', 'updateOrg'])
  },
  computed: {
    ...mapState('org', ['currentOrganization', 'orgCreateMessage']),
    ...mapGetters('org', ['myOrgMembership'])
  }
})
export default class AccountInfo extends Vue {
  private orgStore = getModule(OrgModule, this.$store)
  private btnLabel = 'Save'
  private readonly currentOrganization!: Organization
  private readonly syncOrganizations!: () => Organization[]
  private readonly updateOrg!: (requestBody: CreateRequestBody) => Organization
  private readonly myOrgMembership!: Member
  private orgName = ''
  private readonly orgCreateMessage
  private touched = false

  private isFormValid (): boolean {
    return !!this.orgName
  }

  private async mounted () {
    this.orgStore.setOrgCreateMessage('success') // reset
    if (!this.currentOrganization) {
      await this.syncOrganizations()
    }
    this.orgName = this.currentOrganization.name
  }

  private canChangeAccountName (): boolean {
    switch (this.myOrgMembership.membershipTypeCode) {
      case MembershipType.Owner:
        return true
      default:
        return false
    }
  }

  private enableBtn () {
    this.btnLabel = 'Save'
    this.touched = true
    this.orgStore.setOrgCreateMessage('success') // reset
  }

  private async updateOrgName () {
    this.btnLabel = 'Saving'
    const createRequestBody: CreateRequestBody = {
      name: this.orgName
    }
    await this.updateOrg(createRequestBody)
    if (this.orgCreateMessage === 'success') {
      this.$store.commit('updateHeader')
      this.btnLabel = 'Saved'
    } else {
      this.btnLabel = 'Save'
    }
    this.touched = false
  }

  private readonly accountNameRules = [
    v => !!v || 'An account name is required'
  ]
}
</script>

<style lang="scss" scoped>
  @import "$assets/scss/theme.scss";

  .v-application p {
    margin-bottom: 3rem;
  }

  .nav-bg {
    background-color: $gray0;
  }

  .v-list--dense .v-list-item .v-list-item__title {
    font-weight: 700;
  }

  .form__btns {
    display: flex;
    flex-direction: row;
    justify-content: flex-end;
    align-items: center;
    margin-top: 2rem;

    .v-btn {
      width: 6rem;
    }
  }

  .account-nav-container {
    height: 100%;
    border-right: 1px solid #eeeeee;
  }

  .header-container {
    display: flex;
    flex-direction: row;
  }

  .save-btn.disabled {
    pointer-events: none;
  }

  .save-btn__label {
    padding-left: 0.2rem;
    padding-right: 0.2rem;
  }
</style>
