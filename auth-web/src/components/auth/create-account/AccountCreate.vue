<template>
  <v-form
    ref="createAccountInfoForm"
    lazy-validation
    data-test="form-stepper-premium-wrapper"
  >
    <div
      v-display-mode
    >
      <fieldset class="org-business-type">
        <AccountBusinessType
          :govmAccount="govmAccount"
          :saving="saving"
          :premiumLinkedAccount="true"
          :bcolDuplicateNameErrorMessage="bcolDuplicateNameErrorMessage"
          :isEditAccount="isEditAccount"
          @update:org-business-type="updateOrgBusinessType"
          @valid="checkOrgBusinessTypeValid"
          @update:org-name-clear-errors="updateOrgNameAndClearErrors"
        />
      </fieldset>

      <fieldset>
        <legend class="mb-3">
          Mailing Address
        </legend>
        <BaseAddressForm
          ref="mailingAddress"
          :editing="true"
          :schema="baseAddressSchema"
          :address="address"
          @update:address="updateAddress"
          @valid="checkBaseAddressValidity"
        />
      </fieldset>

      <v-alert
        v-show="errorMessage"
        type="error"
        class="mb-6"
        data-test="div-premium-error"
      >
        {{ errorMessage }}
      </v-alert>
    </div>

    <v-divider class="mt-4 mb-10" />
    <v-row>
      <v-col
        cols="12"
        class="form__btns py-0 d-inline-flex"
      >
        <v-btn
          class="mr-3"
          large
          depressed
          color="primary"
          :loading="saving"
          :disabled="saving || !isFormValid"
          data-test="btn-stepper-premium-save"
          @click="save"
        >
          <span>Next
            <v-icon
              right
              class="ml-1"
            >mdi-arrow-right</v-icon>
          </span>
        </v-btn>
        <ConfirmCancelButton
          :showConfirmPopup="false"
          :target-route="cancelUrl"
          :newStyleStepper="true"
        />
      </v-col>
    </v-row>
  </v-form>
</template>

<script lang="ts">
import { OrgBusinessType, Organization } from '@/models/Organization'
import { computed, defineComponent, reactive, ref, toRefs } from '@vue/composition-api'
import AccountBusinessType from '@/components/auth/common/AccountBusinessType.vue'
import { Address } from '@/models/address'
import BaseAddressForm from '@/components/auth/common/BaseAddressForm.vue'
import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import { LoginSource } from '@/util/constants'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
import { addressSchema } from '@/schemas'
import { getActivePinia } from 'pinia'
import { useAuthStore } from 'sbc-common-components/src/stores'
import { useOrgStore } from '@/stores/org'

export default defineComponent({
  name: 'AccountCreate',
  components: {
    AccountBusinessType,
    BaseAddressForm,
    ConfirmCancelButton
  },
  mixins: [Steppable],
  props: {
    cancelUrl: {
      type: String,
      default: '/',
      required: false
    },
    readOnly: {
      type: Boolean,
      default: false
    },
    govmAccount: {
      type: Boolean,
      default: false
    },
    isEditAccount: {
      type: Boolean,
      default: false
    }
  },
  setup (props, { root }) {
    const { currentOrgAddress, isOrgNameAvailable, setCurrentOrganizationAddress, resetBcolDetails,
      setCurrentOrganizationBusinessType } = useOrgStore()
    const DUPL_ERROR_MESSAGE = 'An account with this name already exists. Try a different account name.'
    const createAccountInfoForm = ref<HTMLFormElement>()
    const baseAddressSchema = addressSchema
    const state = reactive({
      username: '',
      password: '',
      errorMessage: '',
      // New var since show as an error for text field errorMessage field is used for full form and network errors.
      bcolDuplicateNameErrorMessage: '',
      saving: false,
      isBaseAddressValid: true,
      orgNameReadOnly: true,
      orgBusinessTypeLocal: {},
      isOrgBusinessTypeValid: false,
      isExtraProvUser: computed(() => {
        const authStore = useAuthStore(getActivePinia())
        return authStore.currentLoginSource === LoginSource.BCEID
      }),
      isFormValid: computed(() => {
        return !!state.isOrgBusinessTypeValid && !state.errorMessage && !!state.isBaseAddressValid
      }),
      address: computed(() => currentOrgAddress)
    })

    function unlinkAccount () {
      resetBcolDetails()
    }

    function updateAddress (address: Address) {
      setCurrentOrganizationAddress(address)
    }

    function updateOrgNameAndClearErrors () {
      state.bcolDuplicateNameErrorMessage = ''
      state.errorMessage = ''
    }

    async function save () {
      goNext() // Uses mixin, requires this.
    }

    async function validateAccountNameUnique () {
      const available = await isOrgNameAvailable(
        { 'name': state.orgBusinessTypeLocal.name, 'branchName': state.orgBusinessTypeLocal.branchName })
      if (!available) {
        state.bcolDuplicateNameErrorMessage = DUPL_ERROR_MESSAGE
        state.orgNameReadOnly = false
        return false
      } else {
        state.orgNameReadOnly = true
        return true
      }
    }

    function cancel () {
      if (this.stepBack) {
        (props as any).stepBack() // Uses mixin, requires this.
      } else {
        root.$router.push({ path: '/home' })
      }
    }

    function goBack () {
      (props as any).stepBack() // Uses mixin, requires this.
    }

    async function goNext () {
      const isValidName = props.readOnly ? true : await validateAccountNameUnique()
      if (isValidName) {
        (props as any).stepForward()
      } else {
        state.errorMessage = DUPL_ERROR_MESSAGE
      }
    }

    function redirectToNext (organization?: Organization) {
      root.$router.push({ path: `/account/${organization.id}/` })
    }

    function checkBaseAddressValidity (isValid) {
      state.isBaseAddressValid = !!isValid
    }

    function updateOrgBusinessType (orgBusinessType: OrgBusinessType) {
      state.orgBusinessTypeLocal = orgBusinessType
      setCurrentOrganizationBusinessType(state.orgBusinessTypeLocal)
    }

    function checkOrgBusinessTypeValid (isValid) {
      state.isOrgBusinessTypeValid = !!isValid
    }

    return {
      ...toRefs(state),
      createAccountInfoForm,
      baseAddressSchema,
      save,
      cancel,
      goBack,
      goNext,
      updateAddress,
      updateOrgBusinessType,
      checkOrgBusinessTypeValid,
      checkBaseAddressValidity,
      redirectToNext,
      unlinkAccount,
      updateOrgNameAndClearErrors
    }
  }
})
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

// Tighten up some of the spacing between rows
[class^='col'] {
  padding-top: 0;
  padding-bottom: 0;
}

.form__btns {
  display: flex;
  justify-content: flex-end;
}

.bcol-acc__link-status {
  text-transform: uppercase;
  font-size: 0.9375rem;
}

.bcol-acc {
  margin-top: 1px;
  margin-bottom: 2px;
}

.bcol-acc__name {
  font-size: 1.125rem;
  font-weight: 700;
}

.bcol-acc__meta {
  margin: 0;
  padding: 0;
  list-style-type: none;

  li {
    position: relative;
    display: inline-block
  }

  li + li {
    &:before {
      content: ' | ';
      display: inline-block;
      position: relative;
      top: -2px;
      width: 2rem;
      vertical-align: top;
      text-align: center;
    }
  }
}

.bcol-auth {
  max-width: 40rem;

  ::v-deep .v-input__slot{
    align-items: flex-start;
  }
}

.bcol-auth__label {
  margin-left: 0.5rem;
  line-height: 1.5;
  color: var(--v-grey-darken4) !important;
}

.nv-list {
  margin: 0;
  padding: 0;
  list-style-type: none;
}

.nv-list-item {
  vertical-align: top;

  .name, .value {
    display: inline-block;
    vertical-align: top;
  }

  .name {
    min-width: 10rem;
    font-weight: 700;
  }
}

</style>
