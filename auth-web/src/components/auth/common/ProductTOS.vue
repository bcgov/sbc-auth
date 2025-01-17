<template>
  <div>
    <div>
      <h4>Terms of Service</h4>
      <p>
        I confirm, I <strong>{{ userName }}</strong> am an authorized prime admin for this account.<br>
        I declare that this account <strong>{{ orgName }}</strong> and all team members act as a solicitor,
        or name search company approved by the Vital Statistics agency.
      </p>
    </div>
    <v-checkbox
      v-if="canAcceptTos"
      v-model="termsAccepted"
      color="primary"
      class="terms-checkbox align-checkbox-label--top ma-0 pa-0"
      hide-details
      required
      data-test="check-termsAccepted"
      @change="tosChanged"
    >
      <template #label>
        <span class="label-color ml-2">{{ $t('willsRegistryTosIagree') }}</span>
      </template>
    </v-checkbox>
    <div
      v-if="istosTouched && !termsAccepted"
      class="terms-error mt-2"
      color="error"
    >
      <v-icon
        color="error"
        class="error-color mr-1"
      >
        mdi-alert-circle
      </v-icon>
      <span> Confirm to the terms to request</span>
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, toRefs, watch } from '@vue/composition-api'
import { Role } from '@/util/constants'
import { useUserStore } from '@/stores/user'

export default defineComponent({
  name: 'ProductTOS',
  props: {
    userName: {
      type: String,
      default: ''
    },
    orgName: {
      type: String,
      default: ''
    },
    isTOSAlreadyAccepted: {
      type: Boolean,
      default: false
    },
    isApprovalFlow: {
      type: Boolean,
      default: false
    }
  },
  emits: ['tos-status-changed'],
  setup (props, { emit }) {
    const userStore = useUserStore()
    const state = reactive({
      termsAccepted: false,
      istosTouched: false,
      canAcceptTos: computed(() => !userStore.currentUser.roles.includes(Role.ContactCentreStaff))
    })

    watch(() => props.isTOSAlreadyAccepted, (newTos, oldTos) => {
      if (newTos !== oldTos) {
        state.termsAccepted = newTos
      }
    })

    const tosChanged = () => {
      state.istosTouched = true
      emit('tos-status-changed', state.termsAccepted)
      return state.termsAccepted
    }

    onMounted(() => {
      state.termsAccepted = props.isTOSAlreadyAccepted
    })

    return {
      ...toRefs(state),
      tosChanged
    }
  }
})
</script>

<style lang="scss" scoped>
.label-color {
  color:  rgba(0,0,0,.87) !important;
}

.terms-error{
  color: var(--v-error-base) !important;
  font-size: 16px;
  font-weight: bold;
  display: flex;
}
.error-color{
  color: var(--v-error-base) !important;
}
</style>
