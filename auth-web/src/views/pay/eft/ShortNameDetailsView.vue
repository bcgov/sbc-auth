<template>
  <v-container
    id="shortname-details"
    class="view-container"
  >
    <v-snackbar
      id="linked-account-snackbar"
      v-model="snackbar"
      :timeout="4000"
      transition="fade"
    >
      {{ snackbarText }}
    </v-snackbar>
    <div class="view-header flex-column">
      <h1 class="view-header__title">
        Payment Details
      </h1>
      <p class="mt-3 mb-0">
        Review and verify payment details
      </p>
    </div>

    <ShortNameAccountLinkage
      class="mb-12"
      :shortNameDetails="shortNameDetails"
      :highlightIndex="highlightIndex"
      @on-link-account="onLinkAccount"
    />

    <ShortNameTransactions
      :shortNameDetails="shortNameDetails"
    />
  </v-container>
</template>
<script lang="ts">
import { PropType, defineComponent, onMounted, reactive, toRefs } from '@vue/composition-api'
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
      shortNameDetails: {},
      highlightIndex: -1,
      snackbar: false,
      snackbarText: ''
    })

    onMounted(async () => {
      await loadShortname(props.shortNameId)
    })

    async function onLinkAccount () {
      await loadShortname(props.shortNameId)
      state.snackbarText = `Bank short name ${state.shortNameDetails.shortName} was successfully linked.`
      state.highlightIndex = 1 // highlight indexOf when multi-linking is implemented
      state.snackbar = true

      setTimeout(() => {
        state.highlightIndex = -1
      }, 4000)
    }

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
      ...toRefs(state),
      onLinkAccount
    }
  }
})
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

</style>
