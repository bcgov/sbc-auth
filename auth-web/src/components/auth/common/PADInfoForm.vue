<template>
  <div v-can:CHANGE_PAD_INFO.disable.card>
    <template v-if="isAcknowledgeNeeded">
      <p class="mb-6">
        The Canadian Payment Association requires a confirmation period
        of (3) days prior to your first pre-authorized debit deduction.
        The administrator of this account will receive a written confirmation
        of your pre-authorized debit agreement prior to the first deduction.
      </p>
      <p class="mb-10 font-weight-bold">
        {{ padInfoSubtitle }}
      </p>
    </template>
    <v-form ref="preAuthDebitForm">
      <section>
        <header class="mb-4 d-flex align-content-center">
          <div
            data-test="pad-info-form-title"
            class="mr-1 font-weight-bold"
          >
            Banking Information
          </div>
          <v-btn
            small
            icon
            color="primary"
            class="help-btn"
            aria-label="How to locate your banking information"
            @click.stop="bankInfoDialog = true"
          >
            <v-icon>mdi-help-circle-outline</v-icon>
          </v-btn>
          <v-dialog
            v-model="bankInfoDialog"
            max-width="800"
          >
            <v-card class="bank-info-dialog-content">
              <v-card-title>
                <h2 class="title font-weight-bold">
                  How to locate your account information
                </h2>
                <v-btn
                  icon
                  @click="bankInfoDialog = false"
                >
                  <v-icon>mdi-close</v-icon>
                </v-btn>
              </v-card-title>
              <v-card-text>
                <v-img
                  src="../../../assets/img/cheque-sample.jpg"
                  lazy-src
                />
                <ol class="my-4">
                  <li>Cheque number - not required</li>
                  <li>Transit (branch) number - 5 digits</li>
                  <li>Bank (institution) number - 3 digits</li>
                  <li>Bank account number - as shown on your cheque</li>
                </ol>
              </v-card-text>
            </v-card>
          </v-dialog>
        </header>
        <v-row class="bank-information">
          <v-col
            cols="6"
            class="py-0"
          >
            <v-text-field
              v-model="transitNumber"
              v-mask="'#####'"
              label="Transit Number"
              filled
              hint="5 digits"
              persistent-hint
              :rules="transitNumberRules"
              data-test="input-transitNumber"
            />
          </v-col>
          <v-col
            cols="6"
            class="py-0"
          >
            <v-text-field
              v-model="institutionNumber"
              v-mask="'###'"
              label="Institution Number"
              filled
              hint="3 digits"
              persistent-hint
              :rules="institutionNumberRules"
              data-test="input-institutionNumber"
            />
          </v-col>
          <v-col
            cols="12"
            class="py-0"
          >
            <v-text-field
              v-model="accountNumber"
              v-mask="accountMask"
              label="Account Number"
              filled
              hint="7 to 12 digits"
              persistent-hint
              :rules="accountNumberRules"
              data-test="input-accountNumber"
            >
              >
            </v-text-field>
          </v-col>
        </v-row>
        <v-row
          v-if="isAcknowledgeNeeded"
          class="acknowledge-needed"
        >
          <v-col class="pt-2 pl-6 pb-0">
            <v-checkbox
              v-model="isAcknowledged"
              hide-details
              class="align-checkbox-label--top"
              data-test="check-isAcknowledged"
              @change="emitPreAuthDebitInfo"
            >
              <template #label>
                {{ acknowledgementLabel }}
              </template>
            </v-checkbox>
          </v-col>
        </v-row>
        <v-row
          v-if="isTOSNeeded"
          class="tos-needed"
        >
          <v-col class="pt-6 pl-6">
            <div class="terms-container">
              <TermsOfUseDialog
                :isAlreadyAccepted="isTOSAccepted"
                :tosText="'terms and conditions'"
                :tosType="'termsofuse_pad'"
                :tosHeading="'Business Pre-Authorized Debit Terms and Conditions Agreement BC Registries and Online Services'"
                :tosCheckBoxLabelAppend="'of the Business Pre-Authorized Debit Terms and Conditions for BC Registry Services'"
                @terms-acceptance-status="updateTermsAccepted($event)"
              />
            </div>
          </v-col>
        </v-row>
      </section>
    </v-form>
  </div>
</template>

<script lang="ts">
import { ComputedRef, computed, defineComponent, nextTick, onMounted, reactive, ref, toRefs, watch } from '@vue/composition-api'
import CommonUtils from '@/util/common-util'
import { PADInfo } from '@/models/Organization'
import TermsOfUseDialog from '@/components/auth/common/TermsOfUseDialog.vue'
import { mask } from 'vue-the-mask'
import { useOrgStore } from '@/stores/org'

// FUTURE: remove this in vue 3
interface PADInfoFormState {
  accountNumber: string,
  bankInfoDialog: boolean,
  institutionNumber: string,
  isAcknowledged: boolean,
  isTOSAccepted: boolean,
  isTouched: boolean,
  ready: boolean,
  transitNumber: string,
  showPremiumPADInfo: ComputedRef<boolean>,
  acknowledgementLabel: ComputedRef<string>,
  padInfoSubtitle: ComputedRef<string>
}

export default defineComponent({
  name: 'PADInfoForm',
  components: { TermsOfUseDialog },
  directives: { mask },
  props: {
    isAcknowledgeNeeded: { type: Boolean, default: true },
    isChangeView: { type: Boolean, default: false },
    isInitialAcknowledged: { type: Boolean, default: false },
    isInitialTOSAccepted: { type: Boolean, default: false },
    isTOSNeeded: { type: Boolean, default: true },
    padInformation: { default: () => { return {} as PADInfo } }
  },
  emits: ['emit-pre-auth-debit-info', 'is-pre-auth-debit-form-valid', 'is-pad-info-touched'],
  setup (props, { emit }) {
    // refs
    const preAuthDebitForm = ref(null) as HTMLFormElement
    const orgStore = useOrgStore()
    const currentOrgPADInfo = computed(() => orgStore.currentOrgPADInfo)

    // static vars
    const accountMask = CommonUtils.accountMask()

    const institutionNumberRules = [
      v => !!v || 'Institution Number is required',
      v => (v.length === 3) || 'Institution Number should be 3 digits'
    ]
    const transitNumberRules = [
      v => !!v || 'Transit Number is required',
      v => (v.length >= 4) || 'Transit Number should be minimum of 4 digits'
    ]

    const state = (reactive<PADInfoFormState>({
      accountNumber: '',
      bankInfoDialog: false,
      institutionNumber: '',
      isAcknowledged: props.isInitialAcknowledged,
      isTOSAccepted: false,
      isTouched: false,
      ready: false,
      transitNumber: '',
      showPremiumPADInfo: computed((): boolean => props.isChangeView),
      acknowledgementLabel: computed((): string => {
        return (state.showPremiumPADInfo)
          ? 'I understand that services will continue to be billed to the linked BC Online account until the mandatory' +
          ' (3) day confirmation period has ended.'
          : 'I understand that this account will not be able to perform any transactions until the mandatory' +
          ' (3) day confirmation period for pre-authorized debit has ended.'
      }),
      padInfoSubtitle: computed((): string => {
        return (state.showPremiumPADInfo)
          ? 'Services will continue to be billed to the linked BC Online account until the mandatory' +
          ' (3) day confirmation period has ended.'
          : 'This account will not be able to perform any transactions until the mandatory' +
          ' (3) day confirmation period has ended.'
      })
    }) as unknown) as PADInfoFormState

    const accountNumberRules = computed((): ((v: any) => true | string)[] => {
      const rules: ((v: any) => true | string)[] = [
        v => !!v || 'Account Number is required',
        v => (v.length >= 7 && v.length <= 12) || 'Account Number should be between 7 to 12 digits'
      ]
      if (state.isTouched) {
        rules.push(v => (!v.includes('X') || 'Edited payment information should not contain masked digits (i.e. XXX)'))
      }
      return rules
    })

    // emits
    const emitIsPreAuthDebitFormValid = () => {
      const acknowledge = (props.isAcknowledgeNeeded) ? state.isAcknowledged : true
      const tosAccepted = (props.isTOSNeeded) ? state.isTOSAccepted : true
      emit('is-pre-auth-debit-form-valid', (preAuthDebitForm.value?.validate() && tosAccepted && acknowledge) || false)
    }

    const emitIsPadInfoTouched = () => { emit('is-pad-info-touched', state.isTouched) }

    const emitPreAuthDebitInfo = async () => {
      const padInfo: PADInfo = {
        bankTransitNumber: state.transitNumber,
        bankInstitutionNumber: state.institutionNumber,
        bankAccountNumber: state.accountNumber,
        isTOSAccepted: state.isTOSAccepted,
        isAcknowledged: state.isAcknowledged
      }
      emitIsPreAuthDebitFormValid()
      orgStore.setCurrentOrganizationPADInfo(padInfo)
      state.isTouched = true
      emitIsPadInfoTouched()
      emit('emit-pre-auth-debit-info', padInfo)
    }

    // watch bank info
    watch(() => [state.accountNumber, state.institutionNumber, state.transitNumber], () => {
      // only trigger after component has initialized (values are updated in mounted)
      if (state.ready) {
        // must reaccept tos after changing bank info
        state.isTOSAccepted = false
        emitPreAuthDebitInfo()
      }
    }, { deep: true })

    // methods
    const updateTermsAccepted = (isAccepted: boolean) => {
      state.isTOSAccepted = isAccepted
      state.isTouched = true
      emitPreAuthDebitInfo()
    }

    // setup
    onMounted(async () => {
      const padInfo = (Object.keys(props.padInformation).length)
        ? props.padInformation : currentOrgPADInfo.value as PADInfo
      state.accountNumber = padInfo?.bankAccountNumber || ''
      state.institutionNumber = padInfo?.bankInstitutionNumber || ''
      state.transitNumber = padInfo?.bankTransitNumber || ''
      state.isTOSAccepted = props.isInitialTOSAccepted || (padInfo?.isTOSAccepted || false)
      orgStore.setCurrentOrganizationPADInfo(padInfo)
      await nextTick()
      if (state.isTOSAccepted) emitIsPreAuthDebitFormValid()
      state.ready = true
    })

    return {
      accountMask,
      accountNumberRules,
      institutionNumberRules,
      transitNumberRules,
      ...toRefs(state),
      preAuthDebitForm,
      updateTermsAccepted,
      emitPreAuthDebitInfo,
      emitIsPreAuthDebitFormValid,
      emitIsPadInfoTouched
    }
  }
})
</script>

<style lang="scss" scoped>
  .align-checkbox-label--top {
    ::v-deep {
      .v-input__slot {
        align-items: flex-start;
      }
    }
  }

  .v-input--checkbox {
    color: var(--v-grey-darken4) !important;
  }

  ::v-deep {
    .v-input--checkbox .v-label {
      color: var(--v-grey-darken4) !important;
    }
  }

  .help-btn {
    margin-top: -2px;
  }
</style>
