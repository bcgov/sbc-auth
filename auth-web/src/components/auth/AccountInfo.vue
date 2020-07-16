<template>
  <v-container class="pa-0">
    <header class="view-header mb-10">
      <h2 class="view-header__title">Account Information</h2>
    </header>
    <AccountInfoSummary v-can:VIEW_ACCOUNT.show></AccountInfoSummary>
    <AccountInfoEdit v-can:CHANGE_ORG_NAME.show></AccountInfoEdit>
  </v-container>
</template>

<script lang="ts">
import { Component, Mixins, Vue, Watch } from 'vue-property-decorator'
import { mapActions, mapMutations, mapState } from 'vuex'
import AccountInfoEdit from '@/components/auth/AccountInfoEdit.vue'
import AccountInfoSummary from '@/components/auth/AccountInfoSummary.vue'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    AccountInfoEdit,
    AccountInfoSummary
  }
})
export default class AccountInfo extends Vue {

}
</script>
