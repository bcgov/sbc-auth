<template>
  <v-container class="center-container">
    <nav
      class="crumbs py-6"
      aria-label="breadcrumb"
    >
      <div>
        <router-link :to="accountInfoUrl">
          <v-icon
            small
            color="primary"
            class="mr-1"
          >
            mdi-arrow-left
          </v-icon>
          <span>Back to Account</span>
        </router-link>
      </div>
    </nav>
    <div class="view-header flex-column">
      <h1 class="view-header__title">
        {{ $t(isGovmUser ? 'govm_tos_title' : 'tos_title') }}
      </h1>
    </div>

    <v-card class="mt-5 py-4 px-4">
      <v-card-text>
        <TermsOfUse
          @tos-version-updated="false"
        />
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent } from '@vue/composition-api'
import { LoginSource } from '@/util/constants'
import TermsOfUse from '@/components/auth/common/TermsOfUse.vue'
import { storeToRefs } from 'pinia'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'

export default defineComponent({
  name: 'AccountTermsOfUse',
  components: {
    TermsOfUse
  },
  setup () {
    const { currentOrganization } = storeToRefs(useOrgStore())
    const { currentUser } = storeToRefs(useUserStore())

    const accountInfoUrl = computed(() => `/account/${currentOrganization.value?.id}/settings`)
    const isGovmUser = computed(() => currentUser.value?.loginSource?.toUpperCase() === LoginSource.IDIR.toUpperCase())

    return {
      accountInfoUrl,
      isGovmUser
    }
  }
})
</script>

<style lang="scss" scoped>
.crumbs a {
  font-size: 0.875rem;
  text-decoration: none;

  i {
    margin-top: -2px;
  }
}

.crumbs a:hover {
  span {
    text-decoration: underline;
  }
}
</style>
