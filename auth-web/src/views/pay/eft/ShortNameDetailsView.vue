<template>
  <v-container
    id="shortname-details"
    class="view-container"
  >
    <div class="view-header flex-column">
      <h1 class="view-header__title">
        Payment Details
      </h1>
      <p class="mt-3 mb-0">
        Review and verify payment details
      </p>
    </div>

    <ShortNameTransactions
      class="mb-4"
      :shortNameDetails="state.shortNameDetails"
    />

    <ShortNameAccountLinkage :shortNameDetails="state.shortNameDetails" />
  </v-container>
</template>
<script lang="ts">
import { PropType, defineComponent, onMounted, reactive } from '@vue/composition-api'
import PaymentService from '@/services/payment.services'
import ShortNameAccountLinkage from '@/components/pay/eft/ShortNameAccountLink.vue'
import ShortNameTransactions from '@/components/pay/eft/ShortNameTransactions.vue'

export default defineComponent({
  name: 'ShortNameMappingView',
  components: { ShortNameAccountLinkage, ShortNameTransactions },
  props: {
    shortNameId: {
      type: String as PropType<string>,
      default: null
    }
  },
  setup (props) {
    const state = reactive({
      shortNameDetails: {}
    })

    onMounted(async () => {
      await loadShortname(props.shortNameId)
    })

    async function loadShortname (shortnameId: string): Promise<void> {
      try {
        const response = await PaymentService.getEFTShortname(shortnameId)
        if (response?.data) {
          state.shortNameDetails = response.data
        } else {
          throw new Error('No response from getEFTShortname')
        }
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('Failed to getEFTShortname.', error)
      }
    }

    return {
      state
    }
  }
})
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

</style>
