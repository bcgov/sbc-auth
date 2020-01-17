<template>
  <v-container class="p-0">
    <header class="view-header mb-2">
      <h2 class="view-header__title">Account Info</h2>
    </header>
    <v-text-field dense filled clearable label="Account Name"></v-text-field>
    <div class="form__btns">
      <v-btn large disabled color="primary">Save</v-btn>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { mapActions, mapGetters, mapState } from 'vuex'
import OrgModule from '@/store/modules/org'
import { Organization } from '@/models/Organization'
import { Role } from '@/util/constants'
import { UserInfo } from '@/models/userInfo'
import UserManagement from '@/components/auth/UserManagement.vue'

@Component({
  components: {
    UserManagement
  }
})
export default class AccountInfo extends Vue {
  readonly currentUser!: UserInfo
  errorMessage : string = ''
  isStaff: boolean = false

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
