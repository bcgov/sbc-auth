<template>
  <v-card
    flat
    outlined
    class="account-select-list"
  >
    <template v-for="(org, index) in accounts">
      <div
        :key="org.id"
        class="account-select-list-row d-flex justify-space-between align-center pa-6"
      >
        <div class="d-flex align-center">
          <v-avatar
            tile
            color="#4d7094"
            size="32"
            class="user-avatar"
          >
            <strong>{{ org.name && org.name.slice(0,1) && org.name.slice(0,1).toUpperCase() }}</strong>
          </v-avatar>
          <div class="text-left ml-3">
            <h4 class="font-weight-bold">
              {{ org.name }}
            </h4>
            <p
              v-if="org.addressLine"
              class="mb-0"
            >
              {{ org.addressLine }}
            </p>
          </div>
        </div>
        <v-btn
          large
          color="primary"
          :title="actionLabel"
          data-test="goto-access-account-button"
          @click="$emit('select', org.id)"
        >
          {{ actionLabel }}
          <v-icon right>
            mdi-chevron-right
          </v-icon>
        </v-btn>
      </div>
      <v-divider
        v-if="index < accounts.length - 1"
        :key="`divider-${org.id}`"
      />
    </template>
  </v-card>
</template>

<script lang="ts">
import { PropType, defineComponent } from '@vue/composition-api'
import { OrgWithAddress } from '@/models/Organization'

export default defineComponent({
  name: 'AccountSelectList',
  props: {
    accounts: {
      type: Array as PropType<OrgWithAddress[]>,
      default: () => []
    },
    actionLabel: {
      type: String,
      required: true
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';

.account-select-list {
  border-radius: 6px;
  border-color: $gray3;
  text-align: left;
}

.user-avatar {
  margin-right: 0.75rem;
  color: var(--v-accent-lighten5);
  border-radius: 0.15rem;
  font-size: 1.1875rem;
  font-weight: 700;
}
</style>
