<template>
  <div
    id="short-name-financial-dialog"
  >
    <ModalDialog
      ref="modalDialog"
      max-width="720"
      :show-icon="false"
      :showCloseIcon="true"
      dialog-class="lookup-dialog"
      :title="dialogTitle()"
      @close-dialog="resetAccountLinkingDialog"
    >
      <template #text>
        <p v-if="isDialogTypeEmail">
          Enter the contact email provided in the client's Direct Deposit Application form
        </p>
        <p v-if="isDialogTypeCasSupplierNumber">
          Enter the supplier number created in CAS for this short name
        </p>
        <v-text-field
          v-if="isDialogTypeEmail"
          v-model="email"
          filled
          label="Email Address"
          persistent-hint
          :rules="emailAddressRules"
        />
        <v-text-field
          v-if="isDialogTypeCasSupplierNumber"
          v-model="casSupplierNumber"
          filled
          label="CAS Supplier Number"
          persistent-hint
        />
      </template>
      <template #actions>
        <div class="d-flex align-center justify-center w-100 h-100 ga-3">
          <v-btn
            large
            outlined
            color="outlined"
            data-test="dialog-ok-button"
            @click="cancelAndResetAccountLinkingDialog()"
          >
            Cancel
          </v-btn>
          <v-btn
            large
            color="primary"
            data-test="dialog-ok-button"
            :disabled="isFormInvalid()"
            @click="patchShortName()"
          >
            Save
          </v-btn>
        </div>
      </template>
    </ModalDialog>
  </div>
</template>
<script lang="ts">
import { Ref, computed, defineComponent, reactive, ref, toRefs, watch } from '@vue/composition-api'
import CommonUtils from '@/util/common-util'
import { EFTShortnameResponse } from '@/models/eft-transaction'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import PaymentService from '@/services/payment.services'

export default defineComponent({
  name: 'ShortNameFinancialDialog',
  components: { ModalDialog },
  props: {
    isShortNameFinancialDialogOpen: {
      type: Boolean,
      default: false
    },
    shortName: {
      default: {}
    },
    shortNameFinancialDialogType: {
      type: String,
      default: ''
    }
  },
  emits: ['on-patch', 'close-short-name-email-dialog'],
  setup (props, { emit }) {
    const emailAddressRules = CommonUtils.emailRules(true)
    const modalDialog: Ref<InstanceType<typeof ModalDialog>> = ref(null)
    const accountLinkingErrorDialog: Ref<InstanceType<typeof ModalDialog>> = ref(null)
    const state = reactive<any>({
      email: '',
      casSupplierNumber: '',
      isDialogTypeEmail: computed(() => props.shortNameFinancialDialogType === 'EMAIL'),
      isDialogTypeCasSupplierNumber: computed(() => props.shortNameFinancialDialogType === 'CAS_SUPPLIER_NUMBER')
    })

    function isFormInvalid () {
      if (state.isDialogTypeEmail) {
        return !state.email || emailAddressRules.some(rule => rule(state.email) !== true)
      } else if (state.isDialogTypeCasSupplierNumber) {
        return !state.casSupplierNumber
      }
      return true
    }

    function openAccountLinkingDialog (item: EFTShortnameResponse, dialogType) {
      state.shortName = item
      if (dialogType === 'EMAIL') {
        state.email = state.shortName.email
      } else if (dialogType === 'CAS_SUPPLIER_NUMBER') {
        state.casSupplierNumber = state.shortName.casSupplierNumber
      }
      modalDialog.value.open()
    }

    function dialogTitle () {
      if (state.isDialogTypeEmail) {
        return 'Email'
      } else if (state.isDialogTypeCasSupplierNumber) {
        return 'CAS Supplier Number'
      }
    }

    function resetAccountLinkingDialog () {
      state.email = ''
      state.casSupplierNumber = ''
      emit('close-short-name-email-dialog')
    }

    function cancelAndResetAccountLinkingDialog () {
      modalDialog.value.close()
      resetAccountLinkingDialog()
    }

    async function patchShortName () {
      if (state.isDialogTypeEmail) {
        await PaymentService.patchEFTShortName(state.shortName.id, { email: state.email })
      } else if (state.isDialogTypeCasSupplierNumber) {
        await PaymentService.patchEFTShortName(state.shortName.id, { casSupplierNumber: state.casSupplierNumber })
      }
      emit('on-patch')
      cancelAndResetAccountLinkingDialog()
    }

    watch(() => props.isShortNameFinancialDialogOpen, (shortNameNewValue) => {
      if (shortNameNewValue && props.shortName) {
        openAccountLinkingDialog(props.shortName, props.shortNameFinancialDialogType)
      }
    })

    return {
      ...toRefs(state),
      modalDialog,
      accountLinkingErrorDialog,
      openAccountLinkingDialog,
      resetAccountLinkingDialog,
      cancelAndResetAccountLinkingDialog,
      patchShortName,
      emailAddressRules,
      dialogTitle,
      isFormInvalid
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';
@import '@/assets/scss/actions.scss';
@import '@/assets/scss/ShortnameTables.scss';

.actions-dropdown_item {
  cursor: pointer;
  padding: 0.5rem 1rem;
  &:hover {
    background-color: $gray1;
    color: $app-blue !important;
  }
}

h4 {
  color: black;
}

.important {
  background-color: #fff7e3;
  border: 2px solid #fcba19;
  color: #495057;
  font-size: 14px;
}

.w-100 {
  width: 100%;
}

.h-100 {
  height: 100%;
}

.ga-3 {
  gap: 12px;
}

::v-deep {
  .v-btn.v-btn--outlined {
      border-color: var(--v-primary-base);
      color: var(--v-primary-base);
  }
}

</style>
