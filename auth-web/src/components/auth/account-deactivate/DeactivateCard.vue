<template>
  <v-card class="py-4 px-4">
    <v-card-title
      data-test="title-deactivate"
      class="font-weight-bold mb-4"
    >
      When this account is deactivated...
    </v-card-title>

    <v-card-text>
      <div
        v-for="item in info"
        :key="item.title"
        class="d-flex ml-3 mt-1"
      >
        <div>
          <v-icon
            size="30"
            color="error"
            class="mt-1 mr-4"
          >
            mdi-alert-circle-outline
          </v-icon>
        </div>
        <div class="ml-3 mt-1">
          <h4 class="font-weight-bold">
            {{ t(item.title) }}
          </h4>
          <p v-if="item.description">
            {{ t(item.description) }}
          </p>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import { PropType, computed, defineComponent } from '@vue/composition-api'
import { Account } from '@/util/constants'
import { useI18n } from 'vue-i18n-composable'

export default defineComponent({
  name: 'DeactivateCard',
  props: {
    type: String as PropType<Account>
  },
  setup (props) {
    const { t } = useI18n()
    const infoArray = [
      { title: 'deactivateMemberRemovalTitle', description: 'deactivateMemberRemovalDesc' },
      { title: 'businessRemovalTitle', description: 'businessRemovalDesc' },
      { title: 'padRemovalTitle', type: Account.PREMIUM }
    ] as { title: string, description?: string, type?: Account }[]

    const info = computed(() => {
      return infoArray.filter(obj => !obj.type || obj.type === props.type)
    })

    return {
      infoArray,
      t,
      info
    }
  }
})
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';
</style>
