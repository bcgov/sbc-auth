<template>
  <v-alert
    class="px-8 py-7"
    :icon="false"
    prominent
    type="error"
  >
    <div class="account-alert">
      <div class="d-flex flex-row align-center">
        <v-icon
          large
        >
          mdi-alert-circle-outline
        </v-icon>
        <div
          class="flex-fill ml-7"
        >
          <div class="font-weight-bold">
            Account Deactivated
          </div>
        </div>
        <div
          class="flex-0-0"
        >
          {{ deactivatedDate }}
        </div>
      </div>
    </div>
  </v-alert>
</template>

<script lang="ts">
import moment from 'moment'
import { defineComponent, computed } from '@vue/composition-api'
import { useOrgStore } from '@/stores/org'
import CommonUtils from '@/util/common-util'

export default defineComponent({
  name: 'AccountInactiveAlert',
  setup() {
    const orgStore = useOrgStore()
    const currentOrganization = computed(() => orgStore.currentOrganization)
    const formatDate = CommonUtils.formatDisplayDate

    const deactivatedDate = computed(() => {
      return currentOrganization.value?.modified
        ? formatDate(moment(currentOrganization.value.modified))
        : ''
    })

    return {
      deactivatedDate
    }
  }
})
</script>
