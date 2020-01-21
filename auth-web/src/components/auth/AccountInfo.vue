<template>
  <v-container class="p-0">
    <header class="view-header mb-2">
      <h2 class="view-header__title">Account Info</h2>
    </header>
    <v-form ref="editAccountForm">
    <v-text-field dense filled clearable label="Account Name" v-model="orgName"></v-text-field>
    <div class="form__btns">
      <v-btn large color="primary" @click="updateOrgName()" :disabled="!isFormValid()" :loading="btnLabel == 'Saving'">
        <!--
        <v-progress-circular
                indeterminate
                color="green" v-show="btnLabel == 'Saving'"
        >Saving</v-progress-circular>
        -->
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
    ...mapState('org', ['currentOrganization'])
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

  private isFormValid (): boolean {
    return !!this.orgName
  }

  async mounted () {
    if (!this.currentOrganization) {
      await this.syncOrganizations()
    }
    this.orgName = this.currentOrganization.name
  }

  async updateOrgName () {
    this.btnLabel = 'Saving'
    const createRequestBody: CreateRequestBody = {
      name: this.orgName
    }
    this.updateOrg(createRequestBody)
    this.btnLabel = 'Saved'
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
