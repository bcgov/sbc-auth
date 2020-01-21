<template>
  <v-container class="p-0">
    <header class="view-header mb-2">
      <h2 class="view-header__title">Account Info</h2>
    </header>
    <v-form ref="editAccountForm">
    <v-text-field dense filled clearable label="Account Name" v-model="orgName" v-on:keydown="enableBtn();"></v-text-field>
      <v-alert v-show="orgCreateMessage !== 'success'" class="mb-0"
               dense
               outlined
               type="error"
      >{{orgCreateMessage}}
      </v-alert>
    <div class="form__btns">
      <v-btn large color="primary" @click="updateOrgName()" :disabled="!touched || !isFormValid()" :loading="btnLabel == 'Saving'">
        <v-scroll-x-transition>
          <v-icon v-show="btnLabel == 'Saved'" class="mr-1">mdi-check</v-icon>
        </v-scroll-x-transition>
        {{btnLabel}}
      </v-btn>
    </div>
    </v-form>
  </v-container>
</template>

<script lang="ts">

import { Component, Vue } from 'vue-property-decorator'
import { CreateRequestBody, Organization } from '@/models/Organization'
import { mapActions, mapState } from 'vuex'
import OrgModule from '@/store/modules/org'
import { UserInfo } from '@/models/userInfo'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
  },
  methods: {
    ...mapActions('org', ['syncOrganizations', 'updateOrg'])
  },
  computed: {
    ...mapState('org', ['currentOrganization', 'orgCreateMessage'])
  }
})
export default class AccountInfo extends Vue {
  private orgStore = getModule(OrgModule, this.$store)
  readonly currentUser!: UserInfo
  errorMessage : string = ''
  isStaff: boolean = false
  btnLabel = 'Save'
  private readonly currentOrganization!: Organization
  private readonly syncOrganizations!: () => Organization[]
  private readonly updateOrg!: (requestBody: CreateRequestBody) => Organization
  orgName = ''
  private readonly orgCreateMessage
  private touched = false

  private isFormValid (): boolean {
    return !!this.orgName
  }

  async mounted () {
    this.orgStore.setOrgCreateMessage('success') // reset
    if (!this.currentOrganization) {
      await this.syncOrganizations()
    }
    this.orgName = this.currentOrganization.name
  }

  enableBtn () {
    this.btnLabel = 'Save'
    this.touched = true
    this.orgStore.setOrgCreateMessage('success') // reset
  }
  async updateOrgName () {
    this.btnLabel = 'Saving'
    const createRequestBody: CreateRequestBody = {
      name: this.orgName
    }
    await this.updateOrg(createRequestBody)
    if (this.orgCreateMessage === 'success') {
      this.btnLabel = 'Saved'
    } else {
      this.btnLabel = 'Save'
    }
    this.touched = false
  }

  private teamName: string = ''
  private teamType: string = 'BASIC'
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

  .test {
    font-size: 1rem;
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

  ::v-deep .v-tabs-bar {
    width: 100%;
  }

  .v-tab {
    justify-content: left;
  }

  .header-container {
    display: flex;
    flex-direction: row;
  }
</style>
